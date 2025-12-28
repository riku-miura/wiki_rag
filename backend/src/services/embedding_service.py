from typing import List
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        # Initialize model - this will download it if not present
        # In Lambda, we might want to load from a specific path or layer
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of texts.
        
        Args:
            texts (List[str]): List of text chunks
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            return []
            
        embeddings = self.model.encode(texts)
        # Convert numpy arrays to lists for JSON serialization
        return [embedding.tolist() for embedding in embeddings]

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()
