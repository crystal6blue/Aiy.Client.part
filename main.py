from fastapi import FastAPI
from db.database import engine, Base
from api.user_routes import router as user_router
from api.chat_routes import router as chat_router
from api.message_routes import router as message_router

# Create tables in PostgreSQL
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI PostgreSQl To Do App")

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(chat_router, prefix="/chats", tags=["Chats"])
app.include_router(message_router, prefix="/messages", tags=["Messages"])

@app.get("/")
def root():
    return {"message": "Application is running"}