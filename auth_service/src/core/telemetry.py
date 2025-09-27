import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased, ParentBased
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor


def setup_tracing(service_name: str = "auth_service"):
    # Самплинг: в dev собираем всё (1.0). На проде лучше снизить.
    sampler = ParentBased(TraceIdRatioBased(float(os.getenv("OTEL_SAMPLING_RATIO", "1.0"))))

    resource = Resource.create({
        "service.name": os.getenv("OTEL_SERVICE_NAME", service_name),
        "service.version": "1.0.0",
        "deployment.environment": os.getenv("ENVIRONMENT", "dev"),
    })

    provider = TracerProvider(resource=resource, sampler=sampler)
    trace.set_tracer_provider(provider)

    exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4318/v1/traces"),
        timeout=5
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))


def instrument_app(app):
    # Прокидываем x-request-id в спаны
    def server_request_hook(span, scope):
        if not span:
            return
        headers = dict(scope.get("headers") or [])
        req_id = None
        for k, v in headers.items():
            if k.decode().lower() == "x-request-id":
                req_id = v.decode()
                break
        if req_id:
            span.set_attribute("request.id", req_id)


    FastAPIInstrumentor.instrument_app(
        app,
        server_request_hook=server_request_hook,
        excluded_urls="(/health|/ping)"
    )
    RedisInstrumentor().instrument()
