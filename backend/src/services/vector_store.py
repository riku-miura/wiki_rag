import faiss
import numpy as np
import os
import pickle
from typing import List, Optional, Tuple

class VectorStoreService:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
    
    def add_vectors(self, vectors: List[List[float]]):
        """
        Adds vectors to the FAISS index.
        
        Args:
            vectors (List[List[float]]): List of embedding vectors
        """
        if not vectors:
            return
            
        vectors_np = np.array(vectors).astype('float32')
        self.index.add(vectors_np)
        
    def save_local(self, directory: str, session_id: str) -> str:
        """
        Saves the index to a local file.
        
        Args:
            directory (str): Directory to save to
            session_id (str): RAG session ID
            
        Returns:
            str: Path to the saved index file
        """
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, f"{session_id}.index")
        faiss.write_index(self.index, file_path)
        return file_path

    def load_local(self, file_path: str):
        """
        Loads an index from a local file.
        
        Args:
            file_path (str): Path to the index file
        """
        self.index = faiss.read_index(file_path)

    def search(self, query_vector: List[float], top_k: int = 5) -> Tuple[List[float], List[int]]:
        """
        Searches the index for similar vectors.
        
        Args:
            query_vector (List[float]): Query embedding vector
            top_k (int): Number of results to return
            
        Returns:
            Tuple[List[float], List[int]]: (Distances, Indices)
        """
        query_np = np.array([query_vector]).astype('float32')
        distances, indices = self.index.search(query_np, top_k)
        return distances[0].tolist(), indices[0].tolist()
