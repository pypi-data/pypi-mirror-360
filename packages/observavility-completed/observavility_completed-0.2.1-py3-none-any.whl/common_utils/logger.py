""" 
#common_utils/common_utils/logger.py

Módulo de logging estructurado compartido.

Uso:
    from common_utils.logger import get_logger
    logger = get_logger()                       # toma SERVICE_NAME del entorno
    # --o--
    logger = get_logger("payments-service")     # lo fuerzas por parámetro
"""

from __future__ import annotations
import logging
import os
import structlog
from functools import lru_cache
from opentelemetry.trace import get_current_span


def _configure_structlog(service_name: str) -> structlog.stdlib.BoundLogger:
    """Devuelve un logger BoundLogger con la config estándar JSON."""
    # Logging base de Python
    if not logging.getLogger().handlers:
        logging.basicConfig(format="%(message)s", level=logging.INFO)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            add_trace_context, 
            structlog.processors.format_exc_info, 
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger(service_name=service_name)

def add_trace_context(logger, method_name, event_dict):
    """Agrega trace_id y span_id desde el contexto actual."""
    span = get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, '032x')
        event_dict["span_id"] = format(ctx.span_id, '016x')
    else:
        event_dict["trace_id"] = "N/A"
        event_dict["span_id"] = "N/A"
    return event_dict

@lru_cache(maxsize=None)
def _cached_logger(service_name: str) -> structlog.stdlib.BoundLogger:  # pragma: no cover
    """Crea (o recupera) un logger por nombre de servicio."""
    return _configure_structlog(service_name)


def get_logger(service_name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Devuelve un logger listo para usar.

    - Si `service_name` viene en argumento lo usa.
    - Si no, lee la variable de entorno SERVICE_NAME.
    - Si tampoco existe, usa 'unknown-service'.
    """
    service_name = service_name or os.getenv("SERVICE_NAME", "unknown-service")
    return _cached_logger(service_name)
