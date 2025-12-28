import sys
import os
import shutil
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend/src'))

from services.rag_builder import RagBuilderService
from models.rag_session import RagStatus

def test_rag_pipeline():
    print("Starting local RAG pipeline test...")
    
    # Mock S3 Client to avoid AWS calls
    mock_s3 = MagicMock()
    mock_s3.upload_file.return_value = True
    mock_s3.bucket_name = "test-bucket"
    
    # Initialize Service
    service = RagBuilderService("test-bucket")
    service.s3_client = mock_s3
    
    # Mock Wikipedia Fetcher to avoid network calls
    service.wiki_fetcher = MagicMock()
    service.wiki_fetcher.fetch_article.return_value = (
        "Python (programming language)", 
        "Python is a high-level, general-purpose programming language." * 50 # 3000 chars
    )
    
    # Mock Embedding (optional, but speeds up test)
    # Using real embedding service for now to verify data shape
    
    # Run Build
    print("Building RAG session...")
    session = service.build_rag_session("https://en.wikipedia.org/wiki/Python_(programming_language)")
    
    # Verify Results
    print(f"Session Status: {session.status}")
    print(f"Session ID: {session.session_id}")
    print(f"Chunk Count: {session.chunk_count}")
    print(f"S3 Path: {session.s3_index_path}")
    
    if session.status == RagStatus.READY:
        print("SUCCESS: RAG Session created successfully.")
    else:
        print(f"FAILURE: RAG Session failed with error: {session.metadata.error_message}")
        sys.exit(1)

if __name__ == "__main__":
    test_rag_pipeline()
