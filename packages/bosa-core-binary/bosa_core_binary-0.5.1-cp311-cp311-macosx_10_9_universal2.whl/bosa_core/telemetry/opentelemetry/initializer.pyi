from _typeshed import Incomplete
from fastapi import FastAPI as FastAPI

class FastAPIConfig:
    """Configuration class for FastAPI application."""
    app: Incomplete
    def __init__(self, app: FastAPI) -> None:
        """Initializes FastAPIConfig with a FastAPI application.

        Args:
            app (FastAPI): The FastAPI application to configure.
        """

class OpenTelemetryConfig:
    """Configuration-based initializer for OpenTelemetry with FastAPI and Langchain support."""
    endpoint: Incomplete
    port: Incomplete
    attributes: Incomplete
    fastapi_config: Incomplete
    use_langchain: Incomplete
    use_httpx: Incomplete
    use_requests: Incomplete
    provider: Incomplete
    def __init__(self, endpoint: str = '', port: int = 0, attributes: dict[str, str] = None, fastapi_config: FastAPIConfig | None = None, use_langchain: bool = False, use_httpx: bool = True, use_requests: bool = True) -> None:
        """Initializes OpenTelemetryConfig with optional attributes.

        Args:
            endpoint (str): The OTLP endpoint (for external exporters).
            port (int): The OTLP port (for external exporters).
            attributes (dict[str, str]): Additional resource attributes.
            fastapi_config (FastAPI | None): The FastAPI fastapi_config (if using FastAPI tracing).
            use_langchain (bool): Whether to use Langchain tracing.
            use_httpx (bool): Whether to use httpx for tracing.
            use_requests (bool): Whether to use requests for tracing.
        """

def init_otel_with_external_exporter(initializer: OpenTelemetryConfig) -> None:
    """Initializes OpenTelemetry with an external exporter.

    This method initializes OpenTelemetry with an external exporter (OTLP)
        and instruments FastAPI and Langchain if applicable.
    """
def init_otel_sentry(initializer: OpenTelemetryConfig):
    """Initializes OpenTelemetry tracing.

    This method initializes OpenTelemetry with Sentry and instruments FastAPI and Langchain if applicable.
    """
