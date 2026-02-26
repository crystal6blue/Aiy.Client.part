from unittest.mock import MagicMock, patch
import sys
import os

# Mock redis before importing our modules
mock_redis = MagicMock()
mock_redis_module = MagicMock()
sys.modules['redis'] = mock_redis_module
import redis
mock_redis_module.Redis.return_value = mock_redis
# Ensure RedisError is a subclass of Exception for catching
class MockRedisError(Exception): pass
mock_redis_module.RedisError = MockRedisError

from utils.rate_limiter import rate_limiter
from utils.user_logger import log_user_action, get_user_logs
from fastapi import Request, HTTPException

def test_rate_limiter_initialization():
    assert rate_limiter is not None
    print("Rate limiter initialized correctly")

def test_user_logging():
    log_user_action("test_action", {"key": "value"}, user_uuid="test-uuid")
    mock_redis.lpush.assert_called()
    mock_redis.ltrim.assert_called_with("user_logs:user_uuid:test-uuid", 0, 99)

if __name__ == "__main__":
    # Simple manual run if pytest is not used
    print("Running manual tests...")
    try:
        test_rate_limiter_initialization()
        print("Rate limiter test passed!")
        test_user_logging()
        print("User logging test passed!")
    except Exception as e:
        print(f"Tests failed: {e}")
        import traceback
        traceback.print_exc()
