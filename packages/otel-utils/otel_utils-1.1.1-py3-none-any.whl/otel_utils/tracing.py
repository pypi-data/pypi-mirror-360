import functools
from contextlib import contextmanager
from typing import Optional, Iterator, Any, Dict
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, Span, SpanKind


class Tracer:
    """
    Advanced tracing utility that supports complex and nested traces.
    """

    def __init__(self, service_name: str):
        self._tracer = trace.get_tracer(service_name)

    @contextmanager
    def start_as_current_span(
            self,
            name: str,
            context: Optional[Any] = None,
            kind: Optional[SpanKind] = SpanKind.INTERNAL,
            attributes: Optional[Dict[str, Any]] = None,
            links: Optional[list] = None
    ) -> Iterator[Span]:
        """
        Creates a span and sets it as the current span in the context.
        Properly handles the context propagation from external sources.
        """
        with self._tracer.start_as_current_span(
                name,
                context=context,
                attributes=attributes,
                kind=kind,
                links=links
        ) as span:
            yield span

    @contextmanager
    def create_span(
            self,
            name: str,
            attributes: Optional[Dict[str, Any]] = None,
            kind: Optional[SpanKind] = SpanKind.INTERNAL,
            links: Optional[list] = None
    ) -> Iterator[Span]:
        """
        Creates a custom span that can be used in a 'with' context.
        Useful for complex operations that need granular control.
        """
        with self._tracer.start_as_current_span(
                name,
                attributes=attributes,
                kind=kind,
                links=links
        ) as span:
            yield span

    def trace(self, name: Optional[str] = None, attributes: Optional[Dict] = None):
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self._tracer.start_as_current_span(
                        name or func.__name__,
                        attributes=attributes,
                        kind=SpanKind.SERVER
                ) as span:
                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR), str(e))
                        span.record_exception(e)
                        raise

            return async_wrapper

        return decorator
