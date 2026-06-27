from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qmodels
from app.config import settings
from typing import List, Dict, Any, Optional


class QdrantService:
    """
    Service for managing vector storage in Qdrant.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QdrantService, cls).__new__(cls)
            cls._instance._client = None
        return cls._instance

    def init_client(self):
        """Initialize the async Qdrant client."""
        self._client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )

    async def close_client(self):
        """Close the Qdrant client connection."""
        if self._client:
            await self._client.close()

    async def ensure_collection(self, name: str, vector_size: int = 384):
        """
        Ensures that a collection exists in Qdrant. If not, it creates it.

        Args:
            name (str): Name of the collection.
            vector_size (int): Dimensionality of the vectors.
        """
        if not self._client:
            raise RuntimeError(
                "Qdrant client not initialized. Call init_client() first."
            )

        collections = await self._client.get_collections()
        exists = any(c.name == name for c in collections.collections)

        if not exists:
            await self._client.create_collection(
                collection_name=name,
                vectors_config=qmodels.VectorParams(
                    size=vector_size, distance=qmodels.Distance.COSINE
                ),
            )

    async def search(
        self, collection: str, query_vector: list[float], top_k: int = 5
    ) -> list[str]:
        """
        Search for top_k matches in the specified collection.
        Returns a list of text strings extracted from the payloads.
        """
        if not self._client:
            raise RuntimeError(
                "Qdrant client not initialized. Call init_client() first."
            )

        search_result = await self._client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
        )

        return [hit.payload.get("text", "") for hit in search_result if hit.payload]

    async def upsert_chunks(
        self,
        collection: str,
        chunks: List[str],
        embeddings: List[List[float]],
        doc_id: int,
        metadata: Dict[str, Any],
    ):
        """
        Upserts chunks and their embeddings into a Qdrant collection.

        Args:
            collection (str): Collection name.
            chunks (List[str]): Text chunks.
            embeddings (List[List[float]]): Embedding vectors.
            doc_id (int): ID of the source document.
            metadata (Dict[str, Any]): Metadata to associate with each point.
        """
        if not self._client:
            raise RuntimeError(
                "Qdrant client not initialized. Call init_client() first."
            )

        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            # Create a unique ID for each chunk by combining doc_id and index
            # Qdrant IDs can be UUIDs or integers. We'll use a simple integer mapping
            # for the purpose of this implementation, but in production,
            # a more robust ID generation would be needed.
            point_id = int(f"{doc_id}_{i}".replace("_", ""))  # Simplistic ID generation

            points.append(
                qmodels.PointStruct(
                    id=point_id, vector=vector, payload={**metadata, "text": chunk}
                )
            )

        await self._client.upsert(
            collection_name=collection,
            points=points,
        )


# Singleton instance at module level
qdrant_service = QdrantService()


# For compatibility with main.py
def init_client():
    qdrant_service.init_client()


async def close_client():
    await qdrant_service.close_client()
