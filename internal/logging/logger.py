import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

from loguru import logger as _base_logger

_configured: bool = False


def _build_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    extra = record.get("extra") or {}

    service = extra.get("service", "unknown")

    payload: Dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": service,
        "level": record["level"].name,
        "message": record["message"],
    }

    trace_id = extra.get("trace_id")
    if trace_id is not None:
        payload["trace_id"] = trace_id

    error_type = extra.get("error_type")
    if error_type is not None:
        payload["error_type"] = error_type

    # Merge remaining extra keys (except reserved ones)
    for key, value in extra.items():
        if key not in {"service", "trace_id", "error_type"}:
            payload[key] = value

    return payload


def _stdout_sink():
    def _sink(message):
        record = message.record
        payload = _build_payload(record)
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return _sink


def _file_sink(log_file: str):
    def _sink(message):
        record = message.record
        payload = _build_payload(record)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return _sink


class SqlAlchemyToLoguruHandler(logging.Handler):
    """
    Bridge SQLAlchemy's standard-logging records into our Loguru JSON logger.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = _base_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        _base_logger.bind(service="db").opt(exception=record.exc_info).log(
            level, record.getMessage()
        )


class SystemToLoguruHandler(logging.Handler):
    """
    Bridge selected system/framework loggers (uvicorn, fastapi, etc.)
    into our Loguru JSON logger.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = _base_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        _base_logger.bind(service=record.name).opt(
            exception=record.exc_info
        ).log(level, record.getMessage())


def get_logger(service: str):
    """
    Returns a Loguru logger that writes JSON logs
    both to stdout and to `logs/app.log` with the shared schema.
    """
    global _configured

    if not _configured:
        _configured = True

        log_dir = os.getenv("LOG_DIR", "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app.log")

        _base_logger.add(_stdout_sink(), level="INFO")
        _base_logger.add(_file_sink(log_file), level="INFO")

        # Route SQLAlchemy logs into the same file
        sa_logger = logging.getLogger("sqlalchemy")
        sa_logger.setLevel(logging.INFO)
        sa_logger.addHandler(SqlAlchemyToLoguruHandler())

        # Route key system/framework loggers into the same file
        for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
            sys_logger = logging.getLogger(name)
            sys_logger.addHandler(SystemToLoguruHandler())

    # We rely on the bound "service" extra for per-service labels
    return _base_logger.bind(service=service)
