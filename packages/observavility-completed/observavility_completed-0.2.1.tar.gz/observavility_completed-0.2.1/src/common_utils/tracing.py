"""
#common_utils/common_utils/tracing.py

Tracing compartido (OpenTelemetry), para apps FastAPI con SQLAlchemy y clientes HTTP.

Uso:
    from common_utils.tracing import setup_tracing
    setup_tracing(app=app, engine=engine)  # solo una vez
"""

import os
from typing import Optional
from functools import lru_cache

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor


@lru_cache(maxsize=None)
def setup_tracing(app=None, engine=None, service_name: Optional[str] = None):
    """
    Inicializa y configura tracing completo (solo una vez por proceso).

    Args:
        app: instancia FastAPI (opcional, si aplica)
        engine: SQLAlchemy engine (opcional)
        service_name: nombre explícito del servicio, o se usa $SERVICE_NAME
    """
    service_name = service_name or os.getenv("SERVICE_NAME", "unknown-service")

    resource = Resource.create({"service.name": service_name})
    tracer_provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4317"),
        insecure=True
    )

    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(tracer_provider)

    if app:
        FastAPIInstrumentor.instrument_app(app)

    if engine:
        SQLAlchemyInstrumentor().instrument(engine=engine)
    else:
        SQLAlchemyInstrumentor().instrument()

    RequestsInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
