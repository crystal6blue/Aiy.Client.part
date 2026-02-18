from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from db.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    request_metadata = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    chat = relationship("Chat", back_populates="messages")

    created_at = Column(DateTime, default=datetime.now)