"""
OpenTelemetry Setup (Step 15) — Traces, Logs, and Metrics instrumentation.
Exports to OTLP endpoint (Grafana Alloy / SigNoz collector).
Set OTEL_EXPORTER_OTLP_ENDPOINT in environment (default: http://localhost:4317).
"""

import os
import logging
import functools
import time

# Guard: opentelemetry packages are optional; degrade gracefully if absent
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.resources import Resource
    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False

SERVICE_NAME    = "finance-advisor"
OTEL_ENDPOINT   = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

logger = logging.getLogger(SERVICE_NAME)

if _OTEL_AVAILABLE:
    resource = Resource(attributes={"service.name": SERVICE_NAME})

    # Tracer
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True))
    )
    trace.set_tracer_provider(tracer_provider)
    tracer = trace.get_tracer(SERVICE_NAME)

    # Meter
    metric_reader    = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=OTEL_ENDPOINT, insecure=True))
    meter_provider   = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    meter = metrics.get_meter(SERVICE_NAME)

    analysis_counter   = meter.create_counter("finance.analysis.count", description="Number of customer analyses run")
    chat_counter       = meter.create_counter("finance.chat.count", description="Number of chatbot interactions")
    analysis_duration  = meter.create_histogram("finance.analysis.duration_ms", description="Analysis latency in ms")


def traced(span_name: str = None):
    """Decorator to wrap a function in an OTel span."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            name = span_name or fn.__name__
            if not _OTEL_AVAILABLE:
                return fn(*args, **kwargs)
            with tracer.start_as_current_span(name) as span:
                start = time.time()
                result = fn(*args, **kwargs)
                elapsed_ms = (time.time() - start) * 1000
                span.set_attribute("duration_ms", elapsed_ms)
                return result
        return wrapper
    return decorator


def record_analysis(customer_name: str, duration_ms: float):
    if not _OTEL_AVAILABLE:
        return
    analysis_counter.add(1, {"customer": customer_name})
    analysis_duration.record(duration_ms, {"customer": customer_name})
    logger.info("Analysis completed", extra={"customer": customer_name, "duration_ms": duration_ms})


def record_chat(customer_name: str):
    if not _OTEL_AVAILABLE:
        return
    chat_counter.add(1, {"customer": customer_name})
