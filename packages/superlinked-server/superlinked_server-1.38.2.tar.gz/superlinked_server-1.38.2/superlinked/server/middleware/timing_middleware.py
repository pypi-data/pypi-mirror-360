# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from collections.abc import Awaitable, Callable

import structlog
from asgi_correlation_id.context import correlation_id
from beartype.typing import cast
from fastapi import FastAPI, Request, Response
from uvicorn._types import HTTPScope
from uvicorn.protocols.utils import get_path_with_query_string

from superlinked.framework.common.telemetry.telemetry_registry import TelemetryRegistry

access_logger = structlog.stdlib.get_logger("api.access")


def add_timing_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        structlog.contextvars.clear_contextvars()
        request_id = correlation_id.get()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter_ns()
        response = Response(status_code=500)
        try:
            response = await call_next(request)
        except Exception:
            structlog.get_logger("api.error").exception("Uncaught exception")
            raise
        process_time = time.perf_counter_ns() - start_time
        duration_ms = process_time / 1_000_000  # Convert nanoseconds to milliseconds
        status_code = response.status_code
        url = get_path_with_query_string(cast(HTTPScope, request.scope))
        client_host = request.client.host if request.client else "no-client"
        client_port = request.client.port if request.client else "no-client"
        http_method = request.method
        http_version = request.scope["http_version"]
        access_logger.info(
            "[%s] %s HTTP/%s - %s",
            http_method,
            url,
            http_version,
            status_code,
            url=str(request.url),
            status_code=status_code,
            method=http_method,
            request_id=request_id,
            version=http_version,
            client_ip=client_host,
            client_port=client_port,
            duration=f"{duration_ms:.2f} ms",
        )

        telemetry_registry = TelemetryRegistry()
        labels = {"path": request.url.path, "method": request.method, "status_code": str(status_code)}
        telemetry_registry.record_metric("http_requests_total", 1, labels)
        telemetry_registry.record_metric("http_request_duration_ms", duration_ms, labels)

        response.headers["X-Process-Time"] = str(process_time / 10**9)
        return response
