from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.Chat import Chat
from models.Message import Message

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/new/{user_id}")
def create_chat(user_id: int, request_type: str = "text", db: Session = Depends(get_db)):
    new_chat = Chat(user_id=user_id, requestType=request_type)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

@router.post("/{chat_id}/messages")
def send_message(chat_id: int, content: str, db: Session = Depends(get_db)):
    new_msg = Message(chat_id=chat_id, content=content)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg