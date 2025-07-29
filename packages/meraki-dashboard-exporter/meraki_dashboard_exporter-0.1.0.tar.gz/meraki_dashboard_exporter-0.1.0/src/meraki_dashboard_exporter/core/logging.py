"""Structured logging configuration."""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING, Any

import structlog
from structlog.types import EventDict, Processor

if TYPE_CHECKING:
    from .config import Settings


def setup_logging(settings: Settings) -> None:
    """Configure structured logging with structlog using logfmt format.

    Parameters
    ----------
    settings : Settings
        Application settings containing log level.

    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )

    # Processors for structlog with logfmt output
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.dict_tracebacks,
        structlog.processors.LogfmtRenderer(),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def add_otel_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add OpenTelemetry context to log entries.

    Parameters
    ----------
    logger : Any
        The logger instance.
    method_name : str
        The name of the log method called.
    event_dict : EventDict
        The event dictionary to process.

    Returns
    -------
    EventDict
        The processed event dictionary with OTEL context.

    """
    # This will be populated by OTEL instrumentation when enabled
    from opentelemetry import trace

    span = trace.get_current_span()
    if span and span.is_recording():
        span_context = span.get_span_context()
        event_dict["trace_id"] = format(span_context.trace_id, "032x")
        event_dict["span_id"] = format(span_context.span_id, "016x")
        event_dict["trace_flags"] = format(span_context.trace_flags, "02x")

    return event_dict


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get a configured logger instance.

    Parameters
    ----------
    name : str | None
        Logger name, defaults to module name if not provided.

    Returns
    -------
    structlog.BoundLogger
        Configured logger instance.

    """
    return structlog.get_logger(name)
