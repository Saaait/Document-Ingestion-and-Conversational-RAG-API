from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class DocumentUploadResponse(BaseModel):
    """
    Response schema for document upload.
    """

    document_id: int
    filename: str
    status: str
    message: str


class ChatRequest(BaseModel):
    """
    Request schema for sending a message to the RAG agent.
    """

    session_id: str
    message: str


class BookingInfo(BaseModel):
    """
    Schema for capturing booking information from the conversation.
    """

    user_name: Optional[str] = None
    email: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    service: Optional[str] = None


class ChatResponse(BaseModel):
    """
    Response schema for RAG agent chat.
    """

    session_id: str
    answer: str
    sources: List[str] = Field(default_factory=list)
    booking_info: Optional[BookingInfo] = None
