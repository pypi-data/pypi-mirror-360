import logging
import logging.config
from enum import StrEnum
from typing import Any, Iterable, Optional

import structlog
from structlog.processors import LogfmtRenderer


class LogLevel(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class LogFormat(StrEnum):
    JSON = "json"
    LOGFMT = "logfmt"
    CONSOLE = "console"


LOG_FORMATS = [f.value for f in LogFormat]
LOG_LEVELS = [f.value for f in LogLevel]


shared_processors: list[structlog.types.Processor] = [
    # Add the name of the logger to event dict.
    structlog.stdlib.add_logger_name,
    # Add log level to event dict.
    structlog.stdlib.add_log_level,
    # Add a timestamp in ISO 8601 format.
    structlog.processors.TimeStamper(fmt="iso"),
    # If the "exc_info" key in the event dict is either true or a
    # sys.exc_info() tuple, remove "exc_info" and render the exception
    # with traceback into the "exception" key.
    structlog.processors.format_exc_info,
]


def configure_structlog(
    *,
    configure_logging: bool = True,
    log_format: LogFormat | structlog.types.Processor = LogFormat.CONSOLE,
    log_level: LogLevel = LogLevel.INFO,
    extra_processors: Optional[Iterable[structlog.typing.Processor]] = None,
    extra_loggers: Optional[dict[str, dict[str, Any]]] = None,
    disable_existing_loggers: bool = False,
) -> None:
    """
    Helper method to configure Structlog.
    """

    extra_loggers = extra_loggers or {}
    extra_processors = extra_processors or []

    if extra_processors:
        _format_exc_info_index = shared_processors.index(
            structlog.processors.format_exc_info
        )
        for index, proc in enumerate(extra_processors):
            shared_processors.insert(_format_exc_info_index + index, proc)

    processor: structlog.types.Processor

    if isinstance(log_format, LogFormat):
        if log_format == LogFormat.CONSOLE:
            processor = structlog.dev.ConsoleRenderer(colors=True)
        elif log_format == LogFormat.JSON:
            processor = structlog.processors.JSONRenderer()
        elif log_format == LogFormat.LOGFMT:
            processor = LogfmtRenderer()
        else:
            raise RuntimeError(f"Invalid log format {format}")
    else:
        processor = log_format

    if configure_logging:
        config = {
            "version": 1,
            "disable_existing_loggers": disable_existing_loggers,
            "formatters": {
                "default": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": processor,
                    "foreign_pre_chain": shared_processors,
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": log_level.value.upper(),
                    "propagate": True,
                },
                **extra_loggers,
            },
        }

        logging.config.dictConfig(config)

    structlog_processors: list[structlog.types.Processor] = [
        # Merge contextvars into the event dict.
        structlog.contextvars.merge_contextvars,
        # If log level is too low, abort pipeline and throw away log entry.
        structlog.stdlib.filter_by_level,
        # Add shared processors to the processor chain.
        *shared_processors,
        # Perform %-style formatting.
        structlog.stdlib.PositionalArgumentsFormatter(),
        # If the "stack_info" key in the event dict is true, remove it and
        # render the current stack trace in the "stack" key.
        structlog.processors.StackInfoRenderer(),
        # If some value is in bytes, decode it to a unicode str.
        structlog.processors.UnicodeDecoder(),
    ]

    if configure_logging:
        # Prepare event dict for `ProcessorFormatter`.
        structlog_processors.append(
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter
        )
    else:
        structlog_processors.append(processor)

    structlog.configure(
        processors=structlog_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
