import os
import json
import shutil
from typing import List, Optional, Generator, Dict
from uuid import UUID

from ..models.query import Query, RetrievedChunk, LatencyMetrics, QueryMetadata
from ..models.rag_session import RagStatus
from ..services.llm_service import LLMService
from ..services.embedding_service import EmbeddingService
from ..services.vector_store import VectorStoreService
from ..utils.s3_client import S3Client

class ChatService:
    def __init__(self, session_id: str, rag_bucket_name: Optional[str] = None):
        self.session_id = str(UUID(session_id)) # Validation
        self.llm_service = LLMService()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()
        self.s3_client = S3Client(rag_bucket_name) if rag_bucket_name else None
        
        # In-memory storage for this session instance (Lambda warm start optimization)
        self.chunk_map: Dict[int, str] = {}
        self._load_resources()

    def _load_resources(self):
        """
        Downloads index and chunks from S3 to local /tmp and loads them.
        """
        tmp_dir = f"/tmp/{self.session_id}"
        os.makedirs(tmp_dir, exist_ok=True)
        
        index_key = f"indices/{self.session_id}/index.faiss"
        chunks_key = f"indices/{self.session_id}/chunks.json"
        
        local_index_path = os.path.join(tmp_dir, "index.faiss")
        local_chunks_path = os.path.join(tmp_dir, "chunks.json")
        
        if self.s3_client:
            # Download if not exists (caching for warm starts)
            if not os.path.exists(local_index_path):
                self.s3_client.download_file(index_key, local_index_path)
            if not os.path.exists(local_chunks_path):
                self.s3_client.download_file(chunks_key, local_chunks_path)
        
        # Load Vector Store
        if os.path.exists(local_index_path):
            self.vector_store.load_local(local_index_path)
            
        # Load Chunks
        if os.path.exists(local_chunks_path):
            with open(local_chunks_path, 'r') as f:
                chunks_data = json.load(f)
                self.chunk_map = {item['position']: item['content'] for item in chunks_data}

    def process_query(self, query_text: str) -> Generator[str, None, None]:
        """
        Orchestrates the RAG flow: Retrieve -> Augment -> Generate
        """
        # 1. Embed Query
        query_embedding_list = self.embedding_service.generate_embeddings([query_text])
        if not query_embedding_list:
             yield "Error: Could not process query."
             return
             
        query_vector = query_embedding_list[0]

        # 2. Retrieve context
        distances, indices = self.vector_store.search(query_vector, top_k=3)
        
        retrieved_texts = []
        for idx in indices:
            # FAISS returns -1 for not found/padding
            if idx != -1 and idx in self.chunk_map:
                retrieved_texts.append(self.chunk_map[idx])
        
        context_text = "\n\n".join(retrieved_texts)
        if not context_text:
            context_text = "No relevant context found in this document."

        # 3. Call LLM with streaming
        for chunk in self.llm_service.stream_response(query_text, context_text):
            yield chunk

        # TODO: Persist query/chat history to DynamoDB
