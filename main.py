from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from internal.adapters.postgres.database import engine
from internal.api.routes import router
from internal.logging.logger import get_logger

app = FastAPI()
app.include_router(router)

logger = get_logger("api")


def run_migrations() -> None:
    """
    Apply SQL migrations from ../migrations if present.
    """
    try:
        project_root = Path(__file__).resolve().parent
        migrations_dir = project_root / "migrations"
        up_path = migrations_dir / "001_create_all_tables_up.sql"

        if not up_path.is_file():
            logger.info("migrations_file_not_found", path=str(up_path))
            return

        sql = up_path.read_text(encoding="utf-8").strip()
        if not sql:
            logger.info("migrations_file_empty", path=str(up_path))
            return

        # Execute each statement separately to avoid multi-statement issues.
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        if not statements:
            logger.info("migrations_no_statements", path=str(up_path))
            return

        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))

        logger.info("migrations_applied", path=str(up_path))
    except Exception as exc:
        logger.error(
            "migrations_failed",
            error_type=type(exc).__name__,
            detail=str(exc),
        )
        raise


@app.on_event("startup")
async def log_startup():
    run_migrations()
    logger.info("app_started")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler to ensure any unhandled error
    (including DB errors) is logged in JSON.
    """
    logger.error(
        "unhandled_exception",
        error_type=type(exc).__name__,
        path=str(request.url.path),
        method=request.method,
        detail=str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
