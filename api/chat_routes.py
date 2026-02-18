from utils.logger_conf import logger
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from services.chat_service import ChatService
from services.message_service import MessageService

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/new/{user_id}")
def create_chat(user_id: int, request_type: str = "text", db: Session = Depends(get_db)):
    logger.info(f"Creating new chat for user {user_id} with type {request_type}")
    chat = ChatService.create_chat(db, user_id=user_id, request_type=request_type)
    logger.success(f"Chat created successfully: ID {chat.id}")
    return chat

@router.post("/{chat_id}/messages")
def send_message(chat_id: int, content: str, db: Session = Depends(get_db)):
    logger.info(f"Sending message to chat {chat_id}")
    message = MessageService.create_message(db, chat_id=chat_id, content=content)
    logger.success(f"Message sent successfully: ID {message.id}")
    return message