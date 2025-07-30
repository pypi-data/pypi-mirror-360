import json
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Optional

from opentelemetry import trace


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {"timestamp": datetime.utcnow().isoformat(), "level": record.levelname, "service": record.name,
                      "message": record.getMessage()}

        ignored_attrs = {
            'args', 'exc_info', 'exc_text', 'msg', 'message', 'levelname',
            'levelno', 'pathname', 'filename', 'module', 'stack_info',
            'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
            'name', 'thread', 'threadName', 'processName', 'process',
            'levelname', 'getMessage',
            'otelTraceID', 'otelSpanID', 'otelTraceSampled', 'otelServiceName'
        }

        if hasattr(record, "otelTraceID"):
            log_record["trace_id"] = getattr(record, "otelTraceID")
            log_record["dd.trace_id"] = getattr(record, "otelTraceID")
        if hasattr(record, "otelSpanID"):
            log_record["span_id"] = getattr(record, "otelSpanID")
            log_record["dd.span_id"] = getattr(record, "otelSpanID")

        for key, value in record.__dict__.items():
            if key not in ignored_attrs and not key.startswith('_'):
                if key == 'context' and value:
                    log_record[key] = value
                elif key == 'service_name' and 'service' in log_record and log_record['service'] == value:
                    pass
                elif value is not None and value != '':
                    log_record[key] = value

        if "environment" in log_record:
            log_record["env"] = log_record.pop("environment")

        return json.dumps(log_record)


class DefaultAttributesFilter(logging.Filter):
    def __init__(self, default_attributes):
        super().__init__()
        self.default_attributes = default_attributes

    def filter(self, record):
        for k, v in self.default_attributes.items():
            if not hasattr(record, k):
                setattr(record, k, v)
        return True


class StructuredLogger:
    """
    Logger that produces structured logs with tracing context.
    """

    def __init__(
            self,
            service_name: str,
            default_attributes: Optional[Dict[str, Any]] = None,
            environment: Optional[str] = None
    ):
        self.logger = logging.getLogger(service_name)
        self.service_name = service_name
        self.default_attributes = default_attributes or {}
        if environment:
            self.default_attributes['environment'] = environment
        self.logger.propagate = False

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JsonFormatter())
            self.logger.addHandler(handler)
        self.logger.addFilter(DefaultAttributesFilter(self.default_attributes))

    def _get_trace_context(self) -> Dict[str, str]:
        span = trace.get_current_span()
        if span.is_recording():
            ctx = span.get_span_context()
            return {
                "trace_id": format(ctx.trace_id, "032x"),
                "span_id": format(ctx.span_id, "016x")
            }
        return {}

    def _log(
            self,
            level: int,
            message: str,
            *args,
            **kwargs
    ):
        operation = kwargs.pop("operation", None)
        status = kwargs.pop("status", None)
        context = kwargs.copy() if kwargs else None
        extra_data = {}
        extra_data['service_name'] = self.service_name
        if operation:
            extra_data["operation"] = operation
        if status:
            extra_data["status"] = status
        if context:
            extra_data["context"] = context
        trace_ctx = self._get_trace_context()
        if trace_ctx and not hasattr(logging.getLogRecordFactory(), "otelTraceID"):
            trace_id_hex = trace_ctx.get("trace_id")
            span_id_hex = trace_ctx.get("span_id")
            if trace_id_hex and span_id_hex:
                try:
                    trace_id_dec = str(int(trace_id_hex, 16))
                    span_id_dec = str(int(span_id_hex, 16))
                    extra_data["dd.trace_id"] = trace_id_dec
                    extra_data["dd.span_id"] = span_id_dec
                except Exception:
                    extra_data["dd.trace_id"] = trace_id_hex
                    extra_data["dd.span_id"] = span_id_hex
            extra_data["trace_id"] = trace_id_hex
            extra_data["span_id"] = span_id_hex
        self.logger.log(level, message, extra=extra_data)

    def debug(self, message: str, *args, **kwargs):
        self._log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)

    @contextmanager
    def operation_context(
            self,
            operation_name: str,
            **context
    ):
        try:
            self.info(
                f"Iniciando {operation_name}",
                operation=operation_name,
                status="started",
                **context
            )
            yield
            self.info(
                f"Completado {operation_name}",
                operation=operation_name,
                status="completed",
                **context
            )
        except Exception as e:
            self.error(
                f"Error en {operation_name}: {str(e)}",
                operation=operation_name,
                status="failed",
                error=str(e),
                **context
            )
            raise e
