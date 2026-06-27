# Document Intelligence Platform RAG Backend

## Project Overview
API for document ingestion and conversational RAG. The system parses documents, chunks text, and stores embeddings in a vector database to provide context aware AI responses with persistent session memory and automated booking extraction.

## Tech Stack
- **Framework**: FastAPI, Uvicorn
- **Database**: PostgreSQL (SQLAlchemy, asyncpg)
- **Vector Store**: Qdrant
- **Memory**: Redis
- **LLM**: OpenRouter (via OpenAI SDK)
- **Embeddings**: Sentence Transformers
- **Parsing**: PyMuPDF
- **Migrations**: Alembic

## Architecture

### Upload Flow
`File` $\rightarrow$ `Text Extraction (PyMuPDF)` $\rightarrow$ `Chunking (Fixed/Sentence)` $\rightarrow$ `Embedding Generation` $\rightarrow$ `Qdrant (Vectors) + PostgreSQL (Metadata)`

### Chat Flow
`User Message` $\rightarrow$ `Embedding Generation` $\rightarrow$ `Qdrant Search (Top-K)` $\rightarrow$ `Prompt Construction (Context + History)` $\rightarrow$ `LLM Generation` $\rightarrow$ `Redis (Memory) + PostgreSQL (Booking Extraction)`

## Environment Variables
- `DATABASE_URL`: PostgreSQL connection string.
- `QDRANT_URL`: Qdrant server URL.
- `QDRANT_API_KEY`: API key for Qdrant (Optional).
- `REDIS_URL`: Redis server connection string.
- `OPENROUTER_API_KEY`: API key for LLM access via OpenRouter.
- `EMBEDDING_MODEL`: Model name for embeddings (Default: `sentence-transformers/all-MiniLM-L6-v2`).

## Features
- **Chunking Strategies**:
  - `fixed`: Splits text into fixed-size chunks with overlap to maintain context.
  - `sentence`: Groups text by sentence boundaries to avoid cutting mid-thought.
- **Multi-turn Conversation**: Uses Redis to store and retrieve conversation history per session.
- **Booking Extraction**: LLM identifies and extracts appointment details from the conversation.
- **Booking Storage**: Extracted booking data is saved to PostgreSQL for business use.
