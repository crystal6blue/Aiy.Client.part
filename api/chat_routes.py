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

@router.post("/new", dependencies=[Depends(rate_limiter)])
def create_chat(request: Request, request_type: str = "text", db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user_id = current_user.id
    logger.bind(service="application", track=f"user_uuid:{current_user.uuid}").info(f"{request.method} {request.url.path} | Creating new chat with type {request_type}")
    chat = ChatService.create_chat(db, user_id=user_id, request_type=request_type)
    log_user_action("create_chat", {"chat_id": chat.id, "type": request_type}, user_uuid=current_user.uuid)
    logger.bind(service="application", track=f"user_uuid:{current_user.uuid}").success(f"Chat created successfully: ID {chat.id}")
    return chat

@router.post("/{chat_id}/messages", dependencies=[Depends(rate_limiter)])
def send_message(request: Request, chat_id: int, content: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user_id = current_user.id
    logger.bind(service="application", track=f"user_uuid:{current_user.uuid}").info(f"{request.method} {request.url.path} | Sending message to chat {chat_id}")
    message = MessageService.create_message(db, chat_id=chat_id, content=content)
    log_user_action("send_message", {"chat_id": chat_id, "message_id": message.id}, user_uuid=current_user.uuid)
    logger.bind(service="application", track=f"user_uuid:{current_user.uuid}").success(f"Message sent successfully: ID {message.id}")
    return message