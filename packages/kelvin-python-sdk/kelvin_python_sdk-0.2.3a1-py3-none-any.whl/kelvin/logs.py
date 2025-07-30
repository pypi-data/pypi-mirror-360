"""Logging formatter."""

from __future__ import annotations

from typing import Any

import structlog


def configure_logger(*args: Any, **initial_values: Any) -> None:
    """Configure structlog."""

    if not structlog.is_configured():
        structlog.configure_once(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.processors.dict_tracebacks,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.JSONRenderer(),
            ],
            cache_logger_on_first_use=True,
        )


logger = structlog.get_logger()
