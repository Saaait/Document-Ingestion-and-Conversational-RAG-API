from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_db
from app.models.sql_models import Document
from app.models.schemas import DocumentUploadResponse
from app.utils.file_parser import extract_text
from app.services import chunking, embeddings, qdrant

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    chunk_strategy: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a document, process it (extract, chunk, embed), and store it in SQL and Qdrant.
    """
    # 1. Extract text
    text = await extract_text(file)

    # 2. Create document record in SQL
    new_doc = Document(
        filename=file.filename, chunk_strategy=chunk_strategy, status="processing"
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    doc_id = new_doc.id

    try:
        # 3. Chunk text
        if chunk_strategy == "fixed":
            chunks = chunking.fixed_size_chunk(text)
        elif chunk_strategy == "sentence":
            chunks = chunking.sentence_chunk(text)
        else:
            raise HTTPException(
                status_code=400, detail=f"Invalid chunk strategy: {chunk_strategy}"
            )

        # 4. Generate embeddings
        vectors = embeddings.embedding_service.embed(chunks)

        # 5. Store in Qdrant
        # Use a fixed collection name for documents
        collection_name = "documents"
        await qdrant.qdrant_service.ensure_collection(collection_name)

        metadata = {"filename": file.filename, "doc_id": doc_id}
        await qdrant.qdrant_service.upsert_chunks(
            collection=collection_name,
            chunks=chunks,
            embeddings=vectors,
            doc_id=doc_id,
            metadata=metadata,
        )

        # 6. Update status to completed
        new_doc.status = "completed"
        await db.commit()

        return DocumentUploadResponse(
            document_id=doc_id,
            filename=file.filename,
            status="completed",
            message="Document successfully processed and indexed.",
        )

    except Exception as e:
        # Update status to failed
        new_doc.status = "failed"
        await db.commit()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, detail=f"Internal server error during processing: {str(e)}"
        )


@router.get("/")
async def list_documents(db: AsyncSession = Depends(get_db)):
    """
    List all uploaded documents.
    """
    result = await db.execute(select(Document))
    documents = result.scalars().all()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "status": doc.status,
            "chunk_strategy": doc.chunk_strategy,
            "upload_time": doc.upload_time,
        }
        for doc in documents
    ]


@router.get("/{doc_id}")
async def get_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get details of a specific document.
    """
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "chunk_strategy": doc.chunk_strategy,
        "upload_time": doc.upload_time,
    }
