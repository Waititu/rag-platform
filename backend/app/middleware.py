import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


logger = logging.getLogger("rag-platform")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4()),
        )

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "%s %s -> %s request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            request_id,
        )

        return response
