from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.background import BackgroundTask
import logging
import json
import re
from typing import Any, Callable, List, Tuple, Union

DEFAULT_MAX_LOG_SIZE = 10000
DEFAULT_LOG_FORMAT = "PATH: {path} | METHOD: {method} | STATUS: {status_code} | REQUEST: {request} | RESPONSE: {response}"
ALLOWED_MEDIA_TYPES = {None, "application/json", "text/plain", "text/html"}
logger = logging.getLogger(__name__)


def create_path_matcher(pattern: str) -> Callable[[str], bool]:
    """
    Creates a path matcher function from a glob-style pattern:
     - '*' matches any single segment (i.e. any run of chars except '.')
     - matches either exactly or with any number of leading segments
    """
    # Escape dots, then turn '*' into “any run of non-dot chars”
    regex_body = re.escape(pattern).replace(r"\*", "[^.]*")
    # Allow an optional “anything.” prefix
    full_regex = re.compile(rf"^(?:.*\.)?{regex_body}$")
    return lambda path: bool(full_regex.match(path))


DEFAULT_PATTERN_MAP = [
    # ("similarVehicles.*.vehicles", lambda lst: {"size": len(lst)}),
    # ("password", lambda _: "[REMOVED]"),
    ("similarVehicles.*.vehicles", lambda lst: {"size": len(lst), "first_element": lst[0] if lst else None}),
]


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        log_format: Union[str, Callable] = DEFAULT_LOG_FORMAT,
        max_log_size: int = DEFAULT_MAX_LOG_SIZE,
        pattern_map: List[Tuple[str, Callable]] = [],
    ):
        super().__init__(app)
        self.max_log_size = max_log_size
        self.log_format = log_format

        self.summary_map = []
        for pattern, summary_fn in pattern_map:
            matcher_fn = create_path_matcher(pattern)
            self.summary_map.append((matcher_fn, summary_fn))

    def _format_log(self, path, method, status_code, req, res):
        """Format the log message according to the specified format."""
        # If a custom formatter function is provided, use it
        if callable(self.log_format):
            return self.log_format(path=path, method=method, status_code=status_code, request=req, response=res)
        else:  # is string
            return self.log_format.format(path=path, method=method, status_code=status_code, request=req, response=res)

    def _process(self, data: bytes, media_type: str = None) -> str:
        # Skip logging binary content for non-text media types
        if media_type not in ALLOWED_MEDIA_TYPES:
            return f"[{media_type}] - Content not logged"
        # Decode and process text
        text = data.decode("utf-8", errors="ignore")
        try:
            payload = json.loads(text)

            def apply(node: Any, path: List[str] = []) -> Any:
                if not isinstance(node, (dict, list)):
                    return node
                path = path or []
                path_str = ".".join(path)

                for pattern_fn, summary_fn in self.summary_map:
                    if pattern_fn(path_str):
                        return summary_fn(node)

                if isinstance(node, dict):
                    return {k: apply(v, path + [k]) for k, v in node.items()}
                if isinstance(node, list):
                    return [apply(v, path + ["*"]) for v in node]
                return node

            summarized = apply(payload)
            dumped = json.dumps(summarized, ensure_ascii=False)
            if len(dumped) > self.max_log_size:
                return f"Content too large [{len(dumped)} chars]"
            return dumped
        except Exception:
            text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
            if len(text) > self.max_log_size:
                return text[: self.max_log_size] + "…"
            return text

    def _log_info(
        self,
        method: str,
        path: str,
        req_bytes: bytes,
        req_type: str,
        res_bytes: bytes,
        res_type: str,
        status_code: int,
    ):
        if method.upper() == "OPTIONS":
            return

        req = self._process(req_bytes, req_type)
        res = self._process(res_bytes, res_type)
        msg = self._format_log(path, method, status_code, req, res)

        if 200 <= status_code < 300:
            logger.info(msg)
        elif 400 <= status_code < 500:
            logger.warning(msg)
        else:
            logger.error(msg)

    async def dispatch(self, request: Request, call_next):
        req_body = await request.body()
        try:
            response = await call_next(request)
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            response = Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        except Exception as e:
            body = str(e).encode("utf-8")
            response = JSONResponse(content={"detail": str(e)}, status_code=500)
            return response
        finally:
            # Pass request media type to logging
            response.background = BackgroundTask(
                self._log_info,
                method=request.method,
                path=request.url.path,
                req_bytes=req_body,
                req_type=(request.headers.get("content-type") or "").split(";")[0] or None,
                res_bytes=body,
                res_type=(response.headers.get("content-type") or "").split(";")[0] or None,
                status_code=response.status_code,
            )
        return response
