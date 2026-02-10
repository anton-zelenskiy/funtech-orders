import logging
import sys

import structlog
from structlog.types import EventDict, Processor
from structlog.dev import ConsoleRenderer


def add_app_name(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    event_dict["app"] = "funtech-orders"
    return event_dict


def setup_logging(log_level: str = "INFO") -> None:
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_app_name,
        structlog.stdlib.ExtraAdder(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        ConsoleRenderer(colors=True),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
