import logging
import sys
import os
from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logger.remove()

    # 1. CONSOLE (Colorful)
    logger.add(sys.stdout, colorize=True, level="DEBUG")

    # 2. DATABASE LOG (Only SQL queries)
    logger.add(
        "logs/database.log",
        filter=lambda r: "sqlalchemy" in r["name"],
        level="DEBUG"
    )

    # 3. ACCESS LOG (Only HTTP Traffic/Uvicorn)
    logger.add(
        "logs/access.log",
        filter=lambda r: "uvicorn" in r["name"],
        level="INFO"
    )

    # 4. RESULTS JSON (Only Experiment Results)
    logger.add(
        "logs/results.json",
        format="{message}",
        filter=lambda r: "RESULT:" in r["message"]
    )

    # 5. SYSTEM LOG (Everything else: App logic, Errors, Startup)
    def system_filter(record):
        # Only log if it's NOT database, NOT access, and NOT a result
        is_db = "sqlalchemy" in record["name"]
        is_access = "uvicorn" in record["name"]
        is_result = "RESULT:" in record["message"]
        return not (is_db or is_access or is_result)

    logger.add("logs/system.log", filter=system_filter, level="DEBUG")

    # Bridge standard logging to Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in ["uvicorn", "uvicorn.access", "sqlalchemy.engine"]:
        _logger = logging.getLogger(name)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False