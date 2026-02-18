from sqlalchemy.orm import Session
from models.Chat import Chat

class ChatService:
    @staticmethod
    def get_chat(db: Session, chat_id: int):
        return db.query(Chat).filter(Chat.id == chat_id).first()

    @staticmethod
    def create_chat(db: Session, user_id: int, request_type: str = "text"):
        new_chat = Chat(user_id=user_id, requestType=request_type)
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)
        return new_chat

    @staticmethod
    def get_user_chats(db: Session, user_id: int):
        return db.query(Chat).filter(Chat.user_id == user_id).all()
