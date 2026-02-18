from utils.logger_conf import logger
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from services.user_service import UserService

router = APIRouter()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/test-user")
def create_test_user(username: str, email: str, db: Session = Depends(get_db)):
    logger.info(f"Attempting to create test user: {username} ({email})")
    try:
        new_user = UserService.create_user(db, username=username, email=email)
        logger.success(f"User created successfully: ID {new_user.id}")
        return {"status": "success", "user_id": new_user.id}
    except Exception as e:
        logger.error(f"Error creating test user: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
def get_all_users(db: Session = Depends(get_db)):
    logger.debug("Fetching all users")
    users = UserService.get_all_users(db)
    return users


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    logger.debug(f"Fetching user with ID: {user_id}")
    user = UserService.get_user(db, user_id)
    if not user:
        logger.warning(f"User not found: ID {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Attempting to delete user with ID: {user_id}")
    success = UserService.delete_user(db, user_id)
    if not success:
        logger.warning(f"Failed to delete user: ID {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logger.success(f"User deleted successfully: ID {user_id}")
    return {"message": f"User {user_id} deleted"}