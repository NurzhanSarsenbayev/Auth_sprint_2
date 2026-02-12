import logging

from core.config import settings
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
from requests.exceptions import ConnectionError as RequestsConnectionError

logger = logging.getLogger("app")


def setup_tracing(service_name: str = "content_service"):
    sampler = ParentBased(TraceIdRatioBased(settings.otel_sampling_ratio))

    resource = Resource.create(
        {
            "service.name": settings.otel_service_name or service_name,
            "service.version": "1.0.0",
            "deployment.environment": settings.environment,
        }
    )

    provider = TracerProvider(resource=resource, sampler=sampler)
    trace.set_tracer_provider(provider)

    exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_endpoint,
        timeout=5,
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    logger.info(f"📡 OpenTelemetry инициализирован для {settings.otel_service_name}")


def instrument_app(app):
    def server_request_hook(span, scope):
        if not span:
            return
        headers = dict(scope.get("headers") or [])
        for k, v in headers.items():
            if k.decode().lower() == "x-request-id":
                span.set_attribute("request.id", v.decode())
                break

    FastAPIInstrumentor.instrument_app(
        app,
        server_request_hook=server_request_hook,
        excluded_urls="(/health|/ping)",
    )

    RedisInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
    ElasticsearchInstrumentor().instrument()


def shutdown_tracing():
    provider = trace.get_tracer_provider()
    if isinstance(provider, TracerProvider):
        try:
            provider.shutdown()
        except RequestsConnectionError:
            logger.warning("⚠️ Jaeger недоступен, трейсы не выгружены")
        except Exception as e:
            logger.warning(f"⚠️ Telemetry exporter shutdown error: {e}")
