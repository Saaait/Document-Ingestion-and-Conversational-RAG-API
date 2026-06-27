from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Document(Base):
    """
    SQLAlchemy model for documents uploaded to the platform.
    """

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    chunk_strategy = Column(String, nullable=False)
    status = Column(String, default="pending")


class Conversation(Base):
    """
    SQLAlchemy model for chat messages and history.
    """

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class Booking(Base):
    """
    SQLAlchemy model for captured bookings.
    """

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    user_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    date = Column(String, nullable=True)
    time = Column(String, nullable=True)
    service = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
