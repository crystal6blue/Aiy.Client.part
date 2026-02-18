from utils.logger_conf import setup_logging
setup_logging()

from api.chat_routes import router as chat_router
from api.message_routes import router as message_router
from utils.logger_conf import logger
from fastapi import FastAPI
from db.database import engine, Base
from api.user_routes import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI PostgreSQl To Do App")
logger.info("Starting FastAPI application...") # Goes to system.log

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(chat_router, prefix="/chats", tags=["Chats"])
app.include_router(message_router, prefix="/messages", tags=["Messages"])

@app.get("/")
def root():
    return {"message": "Application is running"}