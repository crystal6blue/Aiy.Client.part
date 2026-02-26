from utils.logger_conf import logger
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.database import get_db
from services.user_service import UserService
from utils.rate_limiter import rate_limiter
from utils.user_logger import log_user_action, get_user_logs

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = UserService.decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = UserService.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    request.state.user = user
    return user

@router.post("/login")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = UserService.get_user_by_email(db, email=form_data.username)
    if not user or not UserService.verify_password(form_data.password, user.hashed_password):
        if user:
            logger.bind(service="application", track=f"user_uuid:{user.uuid}").info(f"{request.method} {request.url.path} | login_failed")
            log_user_action("login_failed", {"reason": "incorrect_password"}, user_uuid=user.uuid)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = UserService.create_access_token(data={"sub": user.email})
    logger.bind(service="application", track=f"user_uuid:{user.uuid}").info(f"{request.method} {request.url.path} | login_success")
    log_user_action("login_success", user_uuid=user.uuid)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", dependencies=[Depends(rate_limiter)])
def read_users_me(request: Request, current_user=Depends(get_current_user)):
    logger.bind(service="application", track=f"user_uuid:{current_user.uuid}").info(f"{request.method} {request.url.path} | view_profile")
    log_user_action("view_profile", user_uuid=current_user.uuid)
    return current_user

@router.get("/logs")
def read_user_logs(current_user=Depends(get_current_user)):
    return get_user_logs(f"user_uuid:{current_user.uuid}")

@router.post("/test-user")
def create_test_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    logger.info(f"Attempting to create test user: {username} ({email})")
    try:
        new_user = UserService.create_user(db, username=username, email=email, password=password)
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