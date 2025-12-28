import os
import shutil
import uuid
from typing import List, Optional
from datetime import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..models.rag_session import RagSession, RagStatus, RagMetadata
from ..models.text_chunk import TextChunk, ChunkMetadata
from ..services.wikipedia_fetcher import WikipediaFetcher
from ..services.embedding_service import EmbeddingService
from ..services.vector_store import VectorStoreService
from ..utils.s3_client import S3Client

class RagBuilderService:
    def __init__(self, rag_bucket_name: str):
        self.wiki_fetcher = WikipediaFetcher()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()
        self.s3_client = S3Client(rag_bucket_name) if rag_bucket_name else None
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

    def build_rag_session(self, source_url: str) -> RagSession:
        """
        Orchestrates the RAG build process.
        """
        # 1. Create Session
        session = RagSession(
            source_url=source_url,
            status=RagStatus.PROCESSING,
            metadata=RagMetadata(
                article_title="Pending",
                content_size=0
            )
        )
        
        try:
            # 2. Fetch Content
            title, content = self.wiki_fetcher.fetch_article(source_url)
            session.metadata.article_title = title
            session.metadata.content_size = len(content)
            
            # 3. Chunk Content
            chunks_text = self.text_splitter.split_text(content)
            session.chunk_count = len(chunks_text)
            
            # 4. Generate Embeddings
            embeddings = self.embedding_service.generate_embeddings(chunks_text)
            
            # 5. Create Vector Index
            self.vector_store.add_vectors(embeddings)
            
            # 6. Save Index Locally
            tmp_dir = f"/tmp/{session.session_id}"
            os.makedirs(tmp_dir, exist_ok=True)
            index_path = self.vector_store.save_local(tmp_dir, str(session.session_id))
            
            # Save chunks metadata for simple retrieval (Phase 1/2)
            chunks_data = [
                {"chunk_id": str(uuid.uuid4()), "position": i, "content": text}
                for i, text in enumerate(chunks_text)
            ]
            import json
            chunks_path = os.path.join(tmp_dir, "chunks.json")
            with open(chunks_path, "w") as f:
                json.dump(chunks_data, f)
            
            # 7. Upload to S3
            s3_key_index = f"indices/{session.session_id}/index.faiss"
            s3_key_chunks = f"indices/{session.session_id}/chunks.json"
            
            if self.s3_client:
                if not self.s3_client.upload_file(index_path, s3_key_index):
                    raise Exception("Failed to upload index to S3")
                if not self.s3_client.upload_file(chunks_path, s3_key_chunks):
                    raise Exception("Failed to upload chunks to S3")
                    
                session.s3_index_path = f"s3://{self.s3_client.bucket_name}/{s3_key_index}"
            
            # Cleanup
            shutil.rmtree(tmp_dir, ignore_errors=True)
            
            # 8. Update Session Status
            session.status = RagStatus.READY
            session.updated_at = datetime.utcnow()
            
        except Exception as e:
            session.status = RagStatus.FAILED
            session.metadata.error_message = str(e)
            session.updated_at = datetime.utcnow()
            
        return session
