from utils.logger_conf import logger
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.database import get_db
from services.chat_service import ChatService
from services.message_service import MessageService
from api.user_routes import get_current_user
from utils.rate_limiter import rate_limiter
from utils.user_logger import log_user_action

router = APIRouter()

@router.get("/{chat_id}", dependencies=[Depends(rate_limiter)])
def get_chat_with_messages(request: Request, chat_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # This retrieves the chat and all associated messages via the relationship
    logger.bind(service="application", track=f"user_uuid:{current_user.uuid}").debug(f"{request.method} {request.url.path} | Retrieving chat with messages for chat_id: {chat_id}")
    chat_details = ChatService.get_chat_details(db, chat_id)
    if not chat_details:
        logger.bind(service="application", track=f"user_uuid:{current_user.uuid}").warning(f"{request.method} {request.url.path} | Chat not found: ID {chat_id}")
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Optional: verify chat belongs to user if models support it
    # if chat_details.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this chat")

    log_user_action("view_chat", {"chat_id": chat_id}, user_uuid=current_user.uuid)
    return chat_details

# 1. CREATE Message with File/Audio & Metadata
@router.post("/{chat_id}/send", dependencies=[Depends(rate_limiter)])
async def create_message(
    request: Request,
    chat_id: int,
    content: str = "placeholder content",
    # request_metadata: str = Form(...), # Your metadata string
    # file: UploadFile = File(None),      # Optional file/audio
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.bind(service="application", track=f"user_uuid:{current_user.uuid}").info(f"{request.method} {request.url.path} | Creating message for chat {chat_id}")
    message = MessageService.create_message(db, chat_id=chat_id, content=content)
    log_user_action("send_message_full", {"chat_id": chat_id, "message_id": message.id}, user_uuid=current_user.uuid)
    logger.bind(service="application", track=f"user_uuid:{current_user.uuid}").success(f"Message created: ID {message.id}")
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