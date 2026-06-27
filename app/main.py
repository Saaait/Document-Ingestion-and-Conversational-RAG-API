from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api import documents, chat
from app.database import engine
from app.services import qdrant


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler for the FastAPI application.
    Initializes database connections and vector store clients.
    """
    # Initialize DB connection
    async with engine.connect() as conn:
        pass

    # Initialize Qdrant client
    qdrant.init_client()

    yield

    # Cleanup
    await engine.dispose()
    await qdrant.close_client()


app = FastAPI(
    title="Document Intelligence Platform RAG API",
    description="FastAPI backend for Document Ingestion and Conversational RAG",
    lifespan=lifespan,
)

# Include Routers
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Document Intelligence Platform RAG API is running",
    }
