from fastapi import FastAPI
from internal.api.routes import router
import uvicorn
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    logger.info("Starting storage system")

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )