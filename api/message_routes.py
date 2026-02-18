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



@router.get("/{chat_id}")
def get_chat_with_messages(chat_id: int, db: Session = Depends(get_db)):
    # This retrieves the chat and all associated messages via the relationship
    logger.debug(f"Retrieving chat with messages for chat_id: {chat_id}")
    chat = ChatService.get_chat(db, chat_id)
    if not chat:
        logger.warning(f"Chat not found: ID {chat_id}")
        raise HTTPException(status_code=404, detail="Chat not found")
    return {
        "chat_id": chat.id,
        "type": chat.requestType,
        "messages": chat.messages  # SQLAlchemy automatically loads these
    }

# 1. CREATE Message with File/Audio & Metadata
@router.post("/{chat_id}/send")
async def create_message(
    chat_id: int,
    content: str = "placeholder content",
    # request_metadata: str = Form(...), # Your metadata string
    # file: UploadFile = File(None),      # Optional file/audio
    db: Session = Depends(get_db)
):
    logger.info(f"Creating message for chat {chat_id}")
    message = MessageService.create_message(db, chat_id=chat_id, content=content)
    logger.success(f"Message created: ID {message.id}")
    return message

# 2. GET all messages for a specific chat
@router.get("/chat/{chat_id}")
def get_messages_by_chat(chat_id: int, db: Session = Depends(get_db)):
    """Retrieve all messages in a conversation."""
    logger.debug(f"Fetching messages for chat {chat_id}")
    return MessageService.get_messages_by_chat(db, chat_id)

# 3. UPDATE Message content or metadata
@router.put("/{message_id}")
def update_message(message_id: int, content: str = None, request_metadata: str = None, db: Session = Depends(get_db)):
    """Update message details."""
    logger.info(f"Updating message {message_id}")
    msg = MessageService.update_message(db, message_id, content=content, request_metadata=request_metadata)
    if not msg:
        logger.warning(f"Message update failed: ID {message_id} not found")
        raise HTTPException(status_code=404, detail="Message not found")
    logger.success(f"Message {message_id} updated successfully")
    return msg

# 4. DELETE Message
@router.delete("/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    logger.info(f"Attempting to delete message {message_id}")
    success = MessageService.delete_message(db, message_id)
    if not success:
        logger.warning(f"Message delete failed: ID {message_id} not found")
        raise HTTPException(status_code=404, detail="Message not found")
    logger.success(f"Message {message_id} deleted successfully")
    return {"status": "Deleted", "id": message_id}