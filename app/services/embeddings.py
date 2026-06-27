from sentence_transformers import SentenceTransformer
from app.config import settings
from typing import List

class EmbeddingService:
    """
    Service for generating text embeddings using SentenceTransformers.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Load model from settings
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self._initialized = True

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of texts.

        Args:
            texts (List[str]): List of text chunks to embed.

        Returns:
            List[List[float]]: List of embedding vectors.
        """
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

# Singleton instance at module level
embedding_service = EmbeddingService()
