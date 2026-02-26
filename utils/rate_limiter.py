import time
from fastapi import Request, HTTPException, Depends
from utils.redis_client import get_redis
from utils.logger_conf import logger
from services.user_service import UserService
from db.database import SessionLocal
import jwt

def rate_limiter(request: Request):
    redis = get_redis()
    
    # Identify user: use user.uuid if authenticated, otherwise use UUID from header or fallback to IP
    user = getattr(request.state, "user", None)
    
    # If user is not already set by get_current_user (happens if rate_limiter runs first)
    if not user:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = UserService.decode_access_token(token)
            if payload:
                email = payload.get("sub")
                if email:
                    # Use a fresh DB session to get the user
                    db = SessionLocal()
                    try:
                        user = UserService.get_user_by_email(db, email)
                    finally:
                        db.close()
    
    if user and hasattr(user, "uuid"):
        identifier = f"user_uuid:{user.uuid}"
        track = f"user_uuid:{user.uuid}"
    else:
        # For unauthenticated users, try to get UUID from header, fallback to IP
        client_uuid = request.headers.get("X-User-UUID")
        if client_uuid:
            identifier = f"guest_uuid:{client_uuid}"
            track = f"guest_uuid:{client_uuid}"
        else:
            ip = request.client.host
            identifier = f"ip:{ip}"
            track = f"ip:{ip}"
    
    key = f"rate_limit:{identifier}"
    limit = 10
    period = 60  # 1 minute
    
    try:
        # sliding window counter using Redis
        current_time = time.time()
        pipeline = redis.pipeline()
        # Remove timestamps older than the window
        pipeline.zremrangebyscore(key, 0, current_time - period)
        # Count remaining timestamps
        pipeline.zcard(key)
        # Add current timestamp
        pipeline.zadd(key, {str(current_time): current_time})
        # Set expiry for the key to cleanup
        pipeline.expire(key, period)
        
        results = pipeline.execute()
        request_count = results[1]
        
        if request_count >= limit:
            logger.bind(service="redis", track=track).warning(f"Rate limit exceeded for {identifier}: {request_count + 1} requests in {period}s")
            raise HTTPException(status_code=429, detail="Too many requests. Limit is 10 per minute.")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.bind(service="redis").error(f"Rate limiter error: {e}")
        # In case of redis failure, we allow the request but log the error
        return
