from fastapi import FastAPI

from app.logging.logging_config import setup_logging
from app.routers import llm_router
from app.middleware.rate_limit import setup_rate_limiter

app = FastAPI(title="LLM API")

setup_logging()

setup_rate_limiter(app)
app.include_router(llm_router.router)