from sqlalchemy.orm import Session
from models.Message import Message

class MessageService:
    @staticmethod
    def get_message(db: Session, message_id: int):
        return db.query(Message).filter(Message.id == message_id).first()

    @staticmethod
    def get_messages_by_chat(db: Session, chat_id: int):
        return db.query(Message).filter(Message.chat_id == chat_id).all()

    @staticmethod
    def create_message(db: Session, chat_id: int, content: str, request_metadata: str = None, file_path: str = None):
        new_msg = Message(
            chat_id=chat_id,
            content=content,
            request_metadata=request_metadata,
            file_path=file_path
        )
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)
        return new_msg

    @staticmethod
    def update_message(db: Session, message_id: int, content: str = None, request_metadata: str = None):
        msg = db.query(Message).filter(Message.id == message_id).first()
        if msg:
            if content:
                msg.content = content
            if request_metadata:
                msg.request_metadata = request_metadata
            db.commit()
            db.refresh(msg)
            return msg
        return None

    @staticmethod
    def delete_message(db: Session, message_id: int):
        msg = db.query(Message).filter(Message.id == message_id).first()
        if msg:
            db.delete(msg)
            db.commit()
            return True
        return False
