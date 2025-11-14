import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger
from app.middleware.utils import Colors, get_method_color, get_status_color


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming requests, the response status code and their processing time."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = int((time.perf_counter() - start) * 1000 * 1000 * 1000) / 1000

        # Log response
        short_method = request.method[:5] if request.method != "OPTIONS" else "OPT.."
        logger.info(
            f"| {get_status_color(response.status_code)}{response.status_code}{Colors.Reset} | {process_time:>13}µs | {get_method_color(request.method)}{short_method:<5}{Colors.Reset} | {request.url.path}"
        )

        # Add custom header with processing time
        response.headers["X-Process-Time"] = f"{process_time}"

        return response
