import logging
import platform
from dataclasses import dataclass
from typing import Optional, Dict, Any, Literal

from opentelemetry import trace, metrics
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter as GRPCLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter as GRPCMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GRPCSpanExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter as HTTPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter as HTTPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HTTPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from otel_utils.logging import JsonFormatter, StructuredLogger


@dataclass
class OtelConfig:
    """Configuration for OpenTelemetry instrumentation."""
    service_name: str
    environment: str
    otlp_endpoint: Optional[str] = None
    protocol: Literal["grpc", "http"] = "grpc"
    additional_resources: Optional[Dict[str, Any]] = None
    trace_sample_rate: float = 1.0
    metric_export_interval_ms: int = 30000
    log_level: int = logging.INFO
    enable_console_logging: bool = True
    json_logging: bool = True

    @property
    def trace_endpoint(self) -> Optional[str]:
        if not self.otlp_endpoint:
            return None
        return f"{self.otlp_endpoint}/v1/traces" if self.protocol == "http" else self.otlp_endpoint

    @property
    def metric_endpoint(self) -> Optional[str]:
        if not self.otlp_endpoint:
            return None
        return f"{self.otlp_endpoint}/v1/metrics" if self.protocol == "http" else self.otlp_endpoint

    @property
    def log_endpoint(self) -> Optional[str]:
        if not self.otlp_endpoint:
            return None
        return f"{self.otlp_endpoint}/v1/logs" if self.protocol == "http" else self.otlp_endpoint


class OtelConfigurator:
    """Central Configurator for OpenTelemetry."""

    def __init__(self, config: OtelConfig):
        self.config = config
        self._setup_resource()
        self._setup_tracing()
        self._setup_metrics()
        self._setup_logging()

    def _get_exporters(self):
        """Get the appropriate exporters based on the protocol."""
        if not self.config.otlp_endpoint:
            return None, None, None

        if self.config.protocol == "grpc":
            return (
                GRPCSpanExporter(endpoint=self.config.trace_endpoint),
                GRPCMetricExporter(endpoint=self.config.metric_endpoint),
                GRPCLogExporter(endpoint=self.config.log_endpoint)
            )
        else:
            return (
                HTTPSpanExporter(endpoint=self.config.trace_endpoint),
                HTTPMetricExporter(endpoint=self.config.metric_endpoint),
                HTTPLogExporter(endpoint=self.config.log_endpoint)
            )

    def _setup_resource(self) -> None:
        """Set up the base resource with the service attributes."""
        resource_attributes = {
            "service.name": self.config.service_name,
            "deployment.environment": self.config.environment,
            "host.name": platform.node(),
        }
        if self.config.additional_resources:
            resource_attributes.update(self.config.additional_resources)

        self.resource = Resource.create(resource_attributes)

    def _setup_tracing(self) -> None:
        """Set up the tracing system."""
        tracer_provider = TracerProvider(resource=self.resource)

        if self.config.otlp_endpoint:
            span_exporter, _, _ = self._get_exporters()
            span_processor = BatchSpanProcessor(span_exporter)
            tracer_provider.add_span_processor(span_processor)

        trace.set_tracer_provider(tracer_provider)

    def _setup_metrics(self) -> None:
        """Set up the metrics system."""
        if self.config.otlp_endpoint:
            _, metric_exporter, _ = self._get_exporters()
            metric_reader = PeriodicExportingMetricReader(
                metric_exporter,
                export_interval_millis=self.config.metric_export_interval_ms
            )
            meter_provider = MeterProvider(resource=self.resource, metric_readers=[metric_reader])
        else:
            meter_provider = MeterProvider(resource=self.resource)

        metrics.set_meter_provider(meter_provider)

    def _setup_logging(self) -> None:
        """
        Set up the logging system with OpenTelemetry integration.
        """
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        service_logger = logging.getLogger(self.config.service_name)
        for handler in service_logger.handlers[:]:
            service_logger.removeHandler(handler)

        for logger_name in logging.root.manager.loggerDict:
            if not logger_name.startswith(('uvicorn', 'fastapi')):
                logger = logging.getLogger(logger_name)
                for handler in logger.handlers[:]:
                    logger.removeHandler(handler)

        logging.getLogger('opentelemetry').setLevel(logging.ERROR)

        logger_provider = LoggerProvider(resource=self.resource)
        if self.config.otlp_endpoint:
            _, _, log_exporter = self._get_exporters()
            logger_provider.add_log_record_processor(
                BatchLogRecordProcessor(log_exporter)
            )

        set_logger_provider(logger_provider)

        self.logger = StructuredLogger(
            self.config.service_name,
            environment=self.config.environment
        )

        if self.config.enable_console_logging:
            console_handler = logging.StreamHandler()

            if self.config.json_logging:
                formatter = JsonFormatter()
            else:
                formatter = logging.Formatter(
                    '[%(asctime)s] %(levelname)s [%(name)s] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )

            console_handler.setFormatter(formatter)

            root_logger.addHandler(console_handler)
            root_logger.setLevel(self.config.log_level)

            service_logger.propagate = True
            service_logger.handlers = []

        LoggingInstrumentor().instrument(
            logger_provider=logger_provider,
            set_logging_format=False,
            log_level=self.config.log_level,
            tracer_provider=trace.get_tracer_provider(),
            meter_provider=metrics.get_meter_provider(),
        )


def get_logger(service_name: str = None, config: OtelConfig = None) -> StructuredLogger:
    if config:
        configurator = OtelConfigurator(config)
        return configurator.logger

    return StructuredLogger(service_name or "default-service")
