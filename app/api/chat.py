from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.sql_models import Booking
from app.models.schemas import ChatRequest, ChatResponse
from app.services.memory import redis_memory
from app.services.llm import llm_service
from app.services.qdrant import qdrant_service
from app.services.embeddings import embedding_service
from typing import List

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat_query(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Conversational RAG query endpoint.
    """
    session_id = request.session_id
    user_message = request.message

    # 1. Load history from Redis
    history = redis_memory.get_history(session_id)
    # print(f"HISTORY: {history}")

    # 2. Embed the user query
    # embedding_service.embed expects List[str] and returns List[List[float]]
    vector = embedding_service.embed([user_message])[0]

    # 3. Search Qdrant for relevant chunks
    sources = await qdrant_service.search(
        collection="documents", query_vector=vector, top_k=5
    )
    context_text = "\n\n".join(sources)

    # 4. Build prompt
    messages = [
        {
            "role": "system",
            "content": f"You are a helpful assistant. Use the context below to answer questions about the business. Also use the conversation history to answer personal questions like names mentioned earlier.\n\nContext:\n{context_text}",
        }
    ]

    # Add historical messages
    messages.extend(history)

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    # 5. Call LLM
    answer = llm_service.chat(messages)

    # 6. Save user + assistant messages to Redis
    redis_memory.add_message(session_id, "user", user_message)
    redis_memory.add_message(session_id, "assistant", answer)

    # 7. Extract BookingInfo from full conversation
    # The full conversation includes history + current exchange
    full_conversation = history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": answer},
    ]

    booking_info = llm_service.extract_booking(full_conversation)

    if booking_info and any(getattr(booking_info, f) is not None for f in ["user_name", "email", "date", "time", "service"]):
        booking = Booking(
            session_id=session_id,
            user_name=booking_info.user_name,
            email=booking_info.email,
            date=booking_info.date,
            time=booking_info.time,
            service=booking_info.service,
        )
        db.add(booking)
        await db.commit()

    return ChatResponse(
        session_id=session_id, answer=answer, sources=sources, booking_info=booking_info
    )
