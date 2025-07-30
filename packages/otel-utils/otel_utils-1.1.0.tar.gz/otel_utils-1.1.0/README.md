# OpenTelemetry Utils

A Python library designed to simplify application instrumentation using OpenTelemetry. This library provides an abstraction layer that makes instrumentation more intuitive and less intrusive in your business logic.

## Features

- Simplified OpenTelemetry configuration
- Intuitive API for distributed tracing
- Utilities for metrics and structured logging
- OpenTelemetry Collector integration
- Complete context propagation support
- Full compatibility with asynchronous applications

## Installation

```bash
pip install otel-utils
```

## Basic Usage

### Initial Configuration
```python
from otel_utils import OtelConfig, OtelConfigurator

config = OtelConfig(
    service_name="my-service",
    environment="production",
    otlp_endpoint="http://localhost:4318",  # Optional
    protocol="http",                        # "http" or "grpc", default "grpc"
    trace_sample_rate=1.0,                  # Sampling rate, default 1.0
    metric_export_interval_ms=30000,        # Metrics export interval
    log_level=logging.INFO,                 # Logging level
    enable_console_logging=True,            # Enable console logging
    additional_resources={                   # Optional additional resources
        "deployment.region": "us-east-1",
        "team.name": "backend"
    }
)

OtelConfigurator(config)
```

### Tracing
```python
from otel_utils import Tracer

tracer = Tracer("my-service")

# Using the decorator
@tracer.trace("my_operation")
async def my_function():
    # Your code here
    pass

# Using the context manager
with tracer.create_span("my_operation") as span:
    span.set_attribute("key", "value")
    # Your code here
```

### Metrics
```python
from otel_utils import Metrics

metrics = Metrics("my-service")

# Simple counter
counter = metrics.get_counter("requests_total")
counter.add(1, {"endpoint": "/api/v1/resource"})

# Histogram for latencies
with metrics.measure_duration("request_duration"):
    # Your code here
    pass
```

### Structured Logging
```python
from otel_utils import StructuredLogger

logger = StructuredLogger("my-service")

with logger.operation_context("process_order", order_id="123"):
    logger.info("Starting processing")
    # Your code here
```

## OpenTelemetry Collector Integration

This library is designed to work seamlessly with the OpenTelemetry Collector. Telemetry data is sent using the OTLP protocol, which is the OpenTelemetry standard.

### Collector Configuration with HTTP
```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318

exporters:
  # configure your exporters here

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [your-exporter]
```

### Collector Configuration with gRPC
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

exporters:
  # configure your exporters here

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [your-exporter]
```

## Best Practices

### Separation of Concerns
Keep instrumentation separate from business logic by creating domain-specific abstractions. Your business code should remain clean and focused on its primary responsibilities.

### Consistent Naming
Use coherent naming conventions for spans, metrics, and logs across your services. This makes it easier to correlate and analyze telemetry data.

### Relevant Context
Include useful contextual information in spans and logs, but be mindful of sensitive data. Focus on information that aids debugging and monitoring.

### Appropriate Granularity
Don't instrument everything. Focus on significant operations that provide value for monitoring and debugging. Consider the overhead and noise ratio when adding instrumentation.

## Development

To set up the development environment:
    
```bash
# Create virtualenv
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Contributing

1. Create a feature branch (`git checkout -b feature/new-feature`)
2. Commit your changes (`git commit -am 'Add new feature'`)
3. Push to the branch (`git push origin feature/new-feature`)
4. Create a Pull Request