from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.Chat import Chat

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- CHAT OPERATIONS ---

@router.get("/{chat_id}")
def get_chat_with_messages(chat_id: int, db: Session = Depends(get_db)):
    # This retrieves the chat and all associated messages via the relationship
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
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
    # request_metadata: str = Form(...), # Your metadata string
    # file: UploadFile = File(None),      # Optional file/audio
    # db: Session = Depends(get_db)
):

    # TODO: Implement file saving logic
    # TODO: Implement AI Audio-to-Text call
    return {"status": "Placeholder: Message created", "chat_id": chat_id}

# 2. GET all messages for a specific chat
@router.get("/chat/{chat_id}")
def get_messages_by_chat(chat_id: int, db: Session = Depends(get_db)):
    """Retrieve all messages in a conversation."""
    # TODO: db.query(Message).filter(...)
    return []

# 3. UPDATE Message content or metadata
@router.put("/{message_id}")
def update_message(message_id: int, request_metadata: str, db: Session = Depends(get_db)):
    """Update message details."""
    # TODO: Implement update logic
    return {"status": "Placeholder: Updated", "id": message_id}

# 4. DELETE Message
@router.delete("/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    # TODO: Implement delete logic and file cleanup
    return {"status": "Placeholder: Deleted", "id": message_id}