"""
Structured Logging Configuration
────────────────────────────────
Configures structlog to work seamlessly with the standard library logging module.
Outputs queryable, structured JSON in production and pretty colorized logs in development/testing.
"""

import logging
import sys

import structlog
from structlog.types import EventDict, Processor


def add_app_context(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add static application details to all logs."""
    event_dict["service"] = "linkforge"
    return event_dict


def configure_logging(env: str = "development", debug: bool = True) -> None:
    """
    Setup logging configuration.
    Configures both structlog and standard logging.
    """
    log_level = logging.DEBUG if debug else logging.INFO

    # Shared processors for both standard library and structlog formatters
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        add_app_context,
    ]

    if env.lower() == "production":
        # Production: structured JSON log format
        processors = [*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter]
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(),
            ],
        )
    else:
        # Development/Testing: pretty-printed colored log format
        processors = [*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter]
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(colors=True),
            ],
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure the standard library handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)

    # Prevent logs from bubbling up twice or being output in other formats
    for uvicorn_logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(uvicorn_logger_name)
        uv_logger.handlers = []
        uv_logger.propagate = True

    # Adjust verbosity for noisy libraries
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
