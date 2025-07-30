# blackbox_logger/logger.py

import json
import os
import time
from .masking import mask_sensitive_data
from .loggers.file_logger import setup_file_logger
from .loggers.sqlite_logger import SQLiteLogger

# Configuration from env vars
MAX_LOG_LENGTH = int(os.getenv("BLACKBOX_MAX_LOG_LENGTH", 5000))
SKIP_HTML_JS = os.getenv("BLACKBOX_SKIP_HTML_JS", "true").lower() == "true"
EXCLUDED_PATHS = [
    "/admin/", "/jsi18n/", "/static/", "/media/", "/favicon.ico",
    "/robots.txt", "/health", "/metrics", "/swagger", "/redoc",
    "/docs", "/sentry-debug/", "/__debug__/", "/auth/token/refresh/", "/.well-known/",
]

file_logger = setup_file_logger()
sqlite_logger = SQLiteLogger()

class HTTPLogger:
    def __init__(self, get_user=None, get_client_ip=None, custom_mask_fields=None):
        self.get_user = get_user or self._default_get_user
        self.get_client_ip = get_client_ip or self._default_get_ip
        self.custom_mask_fields = custom_mask_fields

    def _default_get_user(self, headers, request=None):
        try:
            if hasattr(request, "user"):
                return str(request.user) if request.user.is_authenticated else "Anonymous"
            if hasattr(request, "state") and hasattr(request.state, "user"):
                return str(request.state.user)
        except Exception:
            pass
        return "Unknown"

    def _default_get_ip(self, request):
        try:
            if hasattr(request, "META"):
                x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
                if x_forwarded_for:
                    return x_forwarded_for.split(",")[0]
                return request.META.get("REMOTE_ADDR", "Unknown")
            if hasattr(request, "headers") and hasattr(request, "remote_addr"):
                return request.headers.get("X-Forwarded-For", request.remote_addr)
            if hasattr(request, "client"):
                return request.client.host
        except Exception:
            pass
        return "Unknown"

    def _extract_files_from_multipart(self, body, headers):
        import email
        from email.parser import BytesParser
        from email.policy import default
        content_type = headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return None
        # Parse multipart body to extract file names
        try:
            msg = BytesParser(policy=default).parsebytes(
                b"Content-Type: " + content_type.encode() + b"\r\n\r\n" + body
            )
            files = {}
            for part in msg.iter_parts():
                cd = part.get("Content-Disposition", "")
                if "filename=" in cd:
                    name = part.get_param('name', header='content-disposition')
                    filename = part.get_param('filename', header='content-disposition')
                    files[name] = filename
            return files
        except Exception:
            return None

    def _replace_files_in_json(self, data):
        # Recursively replace file-like dicts with just their filename
        if isinstance(data, dict):
            new_data = {}
            for k, v in data.items():
                if isinstance(v, dict) and 'filename' in v:
                    new_data[k] = v['filename']
                else:
                    new_data[k] = self._replace_files_in_json(v)
            return new_data
        elif isinstance(data, list):
            return [self._replace_files_in_json(i) for i in data]
        return data

    def log_request(self, method, path, headers, body, request):
        if any(path.startswith(excluded) for excluded in EXCLUDED_PATHS):
            return
        user = self.get_user(dict(request.headers), request)
        user_agent = request.headers.get("User-Agent", "Unknown")
        client_ip = self.get_client_ip(request)

        content_type = headers.get("Content-Type", "").lower()
        masked_body = None
        if "multipart/form-data" in content_type:
            files = self._extract_files_from_multipart(body, headers)
            masked_body = {"files": files} if files else "[multipart/form-data]"
        else:
            try:
                parsed_body = json.loads(body)
                parsed_body = self._replace_files_in_json(parsed_body)
                masked_body = mask_sensitive_data(parsed_body, self.custom_mask_fields)
            except Exception:
                masked_body = body.decode("utf-8", errors="ignore") if isinstance(body, bytes) else str(body)

        msg = f"[REQUEST] {method} {path} | User: {user} | IP: {client_ip} | User-Agent: {user_agent} | Payload: {masked_body}"
        file_logger.info(msg)
        sqlite_logger.log("request", method, path, user, client_ip, user_agent, masked_body)

    def log_response(self, method, path, headers, response_body, status_code, request, duration=None):
        if any(path.startswith(excluded) for excluded in EXCLUDED_PATHS):
            return
        user = self.get_user(dict(request.headers), request)
        user_agent = request.headers.get("User-Agent", "Unknown")
        client_ip = self.get_client_ip(request)

        content_type = headers.get("Content-Type", "").lower()
        is_html_or_js = ("html" in content_type or "javascript" in content_type or path.endswith(".html"))

        if SKIP_HTML_JS and is_html_or_js:
            parsed_response = "[HTML/JS content skipped]"
        elif "multipart/form-data" in content_type:
            files = self._extract_files_from_multipart(response_body, headers)
            parsed_response = {"files": files} if files else "[multipart/form-data]"
        else:
            try:
                parsed_response = json.loads(response_body)
                parsed_response = self._replace_files_in_json(parsed_response)
            except Exception:
                parsed_response = (
                    response_body.decode("utf-8", errors="ignore")
                    if isinstance(response_body, bytes)
                    else str(response_body)
                )

        if isinstance(parsed_response, str) and len(parsed_response) > MAX_LOG_LENGTH:
            parsed_response = f"[Response too large to log — {len(parsed_response)} characters]"

        timing_info = f" | Duration: {duration:.2f}s" if duration else ""

        msg = f"[RESPONSE] {method} {path} | User: {user} | IP: {client_ip} | User-Agent: {user_agent} | Status: {status_code}{timing_info} | Response: {parsed_response}"
        file_logger.info(msg)
        sqlite_logger.log("response", method, path, user, client_ip, user_agent, parsed_response, status_code)

    def decorator(self, view_func):
        def wrapper(request, *args, **kwargs):
            start_time = time.time()
            self.log_request(request.method, request.path, dict(request.headers), request.body, request)
            response = view_func(request, *args, **kwargs)
            duration = time.time() - start_time
            self.log_response(request.method, request.path, dict(response.headers), response.content, response.status_code, request, duration)
            return response
        return wrapper