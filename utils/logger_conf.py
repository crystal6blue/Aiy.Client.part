import logging
import sys
import os
import json
from datetime import datetime
from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # Determine service based on logger name
        service = "system"
        if "sqlalchemy" in record.name:
            service = "database"
        elif "uvicorn" in record.name:
            service = "system"
        elif "redis" in record.name:
            service = "redis"
        
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).bind(service=service).log(level, record.getMessage())

def serialize(record):
    service = record["extra"].get("service")
    if not service:
        # Fallback logic for loguru-native logs
        name = record["name"]
        if "sqlalchemy" in name:
            service = "database"
        elif "redis" in name:
            service = "redis"
        elif "uvicorn" in name or name == "main":
            service = "system"
        else:
            service = "application"

    subset = {
        "timestamp": record["time"].isoformat(),
        "service": service,
        "level": record["level"].name,
        "message": record["message"],
        "track": record["extra"].get("track", ""),
        "error_type": ""
    }
    
    if record["exception"]:
        subset["error_type"] = record["exception"].type.__name__
        # Append traceback to message to keep everything in JSON
        import traceback
        exc_text = "".join(traceback.format_exception(record["exception"].type, record["exception"].value, record["exception"].traceback))
        subset["message"] = f"{subset['message']}\n{exc_text}"

    return json.dumps(subset) + "\n"

def setup_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logger.remove()

    def json_injector(record):
        record["extra"]["json_format"] = serialize(record)
        return True

    # 1. CONSOLE (Keep colorful for dev)
    logger.add(sys.stdout, colorize=True, level="DEBUG")

    # 2. Unified JSON Log File
    logger.add(
        "logs/app.log",
        format="{extra[json_format]}",
        filter=json_injector,
        level="DEBUG",
        rotation="10 MB",
        backtrace=False,
        diagnose=False,
        catch=False
    )

    # Bridge standard logging to Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    # List of all loggers we want to intercept
    loggers = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "sqlalchemy.dialects",
        "sqlalchemy.orm",
    ]
    # Capture all unhandled exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).critical("Unhandled exception")

    sys.excepthook = handle_exception

    for name in loggers:
        _logger = logging.getLogger(name)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False