from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from opentelemetry import metrics
from opentelemetry.metrics import Observation, CallbackOptions, Counter, Histogram, _Gauge as Gauge
import time


class Metrics:
    """
    Advanced metrics utility that supports different types of measurements
    and asynchronous callbacks.
    """

    def __init__(self, service_name: str):
        self._meter = metrics.get_meter(service_name)
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}
        self._counters: Dict[str, Counter] = {}

    def create_histogram(
            self,
            name: str,
            description: str = "",
            unit: str = "1",
            boundaries: List[float] = None
    ):
        """
        Create a histogram with custom limits for distributions of values.
        """
        return self._meter.create_histogram(
            name=name,
            description=description,
            unit=unit,
            boundaries=boundaries
        )

    @contextmanager
    def measure_duration(
            self,
            name: str,
            attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Measures the duration of a operation and records it as a histogram.
        """
        start_time = time.monotonic()
        try:
            yield
        finally:
            duration = time.monotonic() - start_time
            self.get_histogram(name).record(
                duration,
                attributes=attributes
            )

    def observe_async(
            self,
            name: str,
            description: str = "",
            callback: callable = None
    ):
        """
        Log metrics asynchronously using a callback.
        Useful for metrics that need to be calculated or queried.
        """
        def observer_callback(options: CallbackOptions) -> List[Observation]:
            """
            Callback function for observable gauge metrics.

            Args:
                options: CallbackOptions object containing timing and context information
                        for when the observation is being made. Though not used here,
                        it's part of the OpenTelemetry interface and can be useful for:
                        - Accessing timestamp of the observation
                        - Getting the current context
                        - Handling collection-specific parameters

            Returns:
                List[Observation]: A list containing the current observation value.
                Returns [Observation(0)] in case of errors to maintain metric continuity.
            """
            try:
                value = callback()
                return [Observation(value)]
            except Exception:
                return [Observation(0)]

        self._meter.create_observable_gauge(
            name,
            callbacks=[observer_callback],
            description=description
        )

    def get_counter(self, name: str, description: str = "", unit: str = "1"):
        """Gets or creates a counter."""
        if name not in self._counters:
            self._counters[name] = self._meter.create_counter(
                name=name,
                description=description,
                unit=unit
            )
        return self._counters[name]

    def get_histogram(self, name: str, description: str = "", unit: str = "1"):
        """Gets or creates a histogram."""
        if name not in self._histograms:
            self._histograms[name] = self._meter.create_histogram(
                name=name,
                description=description,
                unit=unit
            )
        return self._histograms[name]

    def get_gauge(self, name: str, description: str = "", unit: str = "1"):
        """Gets or creates a gauge."""
        if name not in self._gauges:
            self._gauges[name] = self._meter.create_gauge(
                name=name,
                description=description,
                unit=unit
            )
        return self._gauges[name]