import json
from datetime import datetime
from utils.redis_client import get_redis
from utils.logger_conf import logger

def log_user_action(action: str, details: dict = None, user_uuid: str = None, ip: str = None):
    redis = get_redis()
    
    if user_uuid:
        identifier = f"user_uuid:{user_uuid}"
    elif ip:
        identifier = f"ip:{ip}"
    else:
        # Fallback if neither provided
        return

    log_key = f"user_logs:{identifier}"
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details or {}
    }
    
    try:
        # Push to a list in Redis
        redis.lpush(log_key, json.dumps(log_entry))
        # Keep only last 100 logs per user
        redis.ltrim(log_key, 0, 99)
        
        # Also log to system log for persistence/visibility
        # Use structured logging to match the new JSON format
        logger.bind(service="application", track=identifier).info(f"Action: {action} | Details: {details}")
    except Exception as e:
        logger.bind(service="redis").error(f"Failed to log user action to Redis: {e}")

def get_user_logs(identifier: str, limit: int = 50):
    redis = get_redis()
    log_key = f"user_logs:{identifier}"
    try:
        logs = redis.lrange(log_key, 0, limit - 1)
        return [json.loads(log) for log in logs]
    except Exception as e:
        logger.bind(service="redis").error(f"Failed to fetch user logs from Redis: {e}")
        return []
