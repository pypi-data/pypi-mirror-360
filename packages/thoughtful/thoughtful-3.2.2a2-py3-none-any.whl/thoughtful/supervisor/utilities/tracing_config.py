"""Light-weight helper to configure an OpenTelemetry TracerProvider.

This module offers a single idempotent `initialize_tracing` function so that
production code can enable OTLP/console exporters *without* pulling in the
full `utilities.telemetry` wrapper.

If you call `initialize_tracing` multiple times only the first invocation
has an effect.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, ResourceAttributes
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

logger = logging.getLogger(__name__)

_INITIALIZED = False


def initialize_tracing(
    *,
    endpoint: str,
    service_name: str = "thoughtful-supervisor",
    headers: Optional[Dict[str, str]] = None,
    enable_console_export: bool = False,
) -> None:
    """Configure a global :class:`TracerProvider`.

    Nothing happens if the function has been called before in this process.

    Args:
        endpoint (str): The OTLP endpoint URL. Must be a valid HTTP/HTTPS URL.
        service_name (str): The name of the service for tracing.
        headers (Dict[str, str], optional): Headers to include in OTLP requests.
        enable_console_export (bool): Whether to also export spans to console.

    Raises:
        ValueError: If the endpoint URL is invalid or unreachable.
    """
    global _INITIALIZED
    if _INITIALIZED:
        logger.debug("Tracing already initialized – skipping")
        return

    # Validate endpoint URL format
    if not endpoint.startswith(("http://", "https://")):
        raise ValueError(
            f"Invalid OTLP endpoint URL: {endpoint}. Must start with http:// or https://"
        )

    try:
        resource = Resource.create({ResourceAttributes.SERVICE_NAME: service_name})
        provider = TracerProvider(resource=resource)

        # Create exporter with error handling
        exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers or {})
        provider.add_span_processor(BatchSpanProcessor(exporter))

        if enable_console_export:
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        trace.set_tracer_provider(provider)
        _INITIALIZED = True
        logger.info("OpenTelemetry tracing initialized – OTLP endpoint=%s", endpoint)
    except Exception as e:
        logger.error("Failed to initialize OpenTelemetry tracing: %s", str(e))
        raise ValueError(
            f"Failed to initialize tracing with endpoint {endpoint}: {str(e)}"
        )
