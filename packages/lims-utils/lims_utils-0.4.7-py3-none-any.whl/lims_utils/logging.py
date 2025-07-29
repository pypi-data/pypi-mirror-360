import logging
from typing import List

from fastapi import Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException

app_logger = logging.getLogger("uvicorn")
uvicorn_logger = logging.getLogger("uvicorn.access")


class EndpointFilter(logging.Filter):
    def __init__(self, paths_to_ignore=["/api/docs", "/docs"]):
        self.paths_to_ignore = paths_to_ignore

    def filter(self, record: logging.LogRecord) -> bool:
        if type(record.args) is not tuple:
            return True

        return not record.args or record.args[2] not in self.paths_to_ignore


def register_loggers(paths_to_ignore: List[str] = ["/api/docs", "/docs"]):
    """Register Uvicorn error and access logs, filtering out calls to /docs by default"""
    uvicorn_logger.addFilter(EndpointFilter(paths_to_ignore=paths_to_ignore))

    logging.basicConfig(format="%(levelname)s: %(message)s")
    app_logger.setLevel("INFO")


async def log_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler, takes HTTP exception and prints more details about the context
    of the exception before reraising it"""
    if exc.status_code != 401:
        user = "Unknown user"
        try:
            user = request.state.__getattr__("user")
        except AttributeError:
            pass
        finally:
            app_logger.warning(
                "%s @ %s: %s",
                user,
                request.url,
                exc.detail,
            )
    return await http_exception_handler(request, exc)
