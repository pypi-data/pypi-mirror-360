"""
response_utils.py

This module provides a utility function to standardize API responses
sent from backend to frontend in a consistent, structured format.

Key functionality:
- Enforces keyword-only arguments for clarity and safety
- Standardizes fields like request ID, data, status, message, and timestamp
- Suitable for JSON-based API responses

Author: Paavan Boddeda
Organization: ennVee TechnoGroup
"""

from typing import Union, Optional, List
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.types import ASGIApp
from datetime import datetime
from ennvee_commons import get_logger
import uuid
import json


# def response_middleware(
#     *,
#     req_id: str,
#     data: Union[dict, list, None],
#     is_success: bool,
#     message: str = "",
#     status_code: int = 200
# ) -> dict:
#     """
#     Format API responses in a consistent structure.

#     Args:
#         req_id (str): Unique ID of the request for tracing/logging.
#         data (dict or list or None): The response payload to send to frontend.
#         is_success (bool): Indicates if the operation was successful.
#         message (str, optional): Optional descriptive message (default is empty string).
#         status_code (int, optional): Optional HTTP-like status code (default is 200).

#     Returns:
#         dict: A standardized response dictionary with metadata.

#     Example:
#         >>> format_response(
#         ...     req_id="abc123",
#         ...     data={"user": "Alice"},
#         ...     is_success=True
#         ... )
#         {
#             "request_id": "abc123",
#             "success": True,
#             "data": {"user": "Alice"},
#             "message": "",
#             "status_code": 200,
#             "timestamp": "2025-06-30T12:34:56Z"
#         }
#     """
#     return {
#         "request_id": req_id,
#         "success": is_success,
#         "data": data,
#         "message": message,
#         "status_code": status_code if is_success else (500 if status_code == 200 else status_code),
#         "timestamp": datetime.utcnow().isoformat() + "Z"
#     }
    
loggerinfo = get_logger(log_file="logs/system.log")

    
"""
===============================================================================
RequestMiddleware
===============================================================================
Reusable FastAPI middleware that:

- Logs each incoming request with:
    - Method, URL, headers, client IP
    - Request timestamp
- Automatically attaches a `request_id` to the request state
- Can be used with response middleware to provide full lifecycle tracking

Note: This does NOT modify the response structure — it focuses only on request side.
===============================================================================
"""
class RequestMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate and log incoming HTTP requests.

    Features:
    - Generates a unique request ID if missing.
    - Rejects requests from blacklisted IP addresses.
    - Stores metadata in request.state for use by other middlewares or route handlers.
    """

    def __init__(self, app: ASGIApp, blacklist_ips: Optional[List[str]] = None):
        """
        Initialize middleware with optional list of blacklisted IPs.

        Parameters:
        - app (ASGIApp): The FastAPI or Starlette application.
        - blacklist_ips (List[str], optional): List of IPs to deny access from.
        """
        super().__init__(app)
        self.blacklist_ips = set(blacklist_ips or [])

    async def dispatch(self, request: Request, call_next):
        """
        This method intercepts each incoming HTTP request.

        It performs the following steps:
        1. Extract client IP from request.
        2. Generate a request ID (UUID) if none exists in the headers.
        3. Store IP and request ID in request.state for downstream access.
        4. Block requests if IP is blacklisted.
        5. Log basic request metadata.
        6. Proceed to the next middleware or route handler.
        """

        # Step 1: Capture client IP address from the request object.
        client_ip = request.client.host

        # Step 2: Generate or extract a unique request ID.
        # This helps with traceability across logs and response tracking.
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Step 3: Store useful metadata in request.state to be accessed later
        # by other middlewares, route handlers, or response formatters.
        request.state.request_id = request_id
        request.state.client_ip = client_ip

        # Step 4: Deny the request early if the client IP is in the blacklist.
        if client_ip in self.blacklist_ips:
            loggerinfo.warning(
                f"[Blocked] Blacklisted IP attempted access: {client_ip}, Request-ID: {request_id}"
            )
            return JSONResponse(
                status_code=403,
                content={
                    "request_id": request_id,
                    "success": False,
                    "message": "Access denied: IP is blacklisted",
                    "data": None
                }
            )

        # Step 5: Log the incoming request details (for observability).
        
        loggerinfo.info(
            f"[Request] Method={request.method}, Path={request.url.path}, IP={client_ip}, Request-ID={request_id}, Headers={dict(request.headers)}"
        )

        # Step 6: Continue processing to the next middleware or route.
        return await call_next(request)


# -------------------------------------------**Response Middleware**-------------------------------------------

"""
===============================================================================
ResponseFormatterMiddleware
===============================================================================
Reusable FastAPI middleware that:

- Wraps every JSON API response in a standardized structure
- Attaches request and response metadata:
    - request_id
    - request_time
    - response_time
    - duration in milliseconds
- Handles exceptions gracefully with structured error responses
- Skips formatting for Swagger UI, ReDoc, OpenAPI, and non-JSON responses

Ideal for enterprise applications that require traceable, predictable responses
for logging, debugging, and frontend consistency.

Usage:
    from ennvee_commons.res_middleware_utils import ResponseFormatterMiddleware
    app.add_middleware(ResponseFormatterMiddleware)
===============================================================================
"""


class ResponseMiddleware(BaseHTTPMiddleware):
    """
    Middleware that intercepts FastAPI responses and formats them with
    common metadata for standardized output.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """
        Main method that intercepts and wraps each response.

        It captures timing, handles exceptions, and returns responses
        in a uniform format.
        """
        
        # Step 1: Generate or extract a unique request ID from the header
        # If not present, generate a UUID (used for tracing/logging)
        
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        
        # Step 2: Capture the request start time (UTC) for duration calculation
        
        request_time = datetime.utcnow()

        
        # Step 3: Skip wrapping for Swagger UI, ReDoc, OpenAPI, and docs redirect
        # These routes return HTML or static assets that shouldn't be wrapped
        
        skip_paths = ["/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)

        try:
            
            # Step 4: Proceed to the actual route handler and capture the response
            
            response = await call_next(request)

            
            # Step 5: If the content is not JSON, do not format it
            # Allow HTML, static files, and other types to return unmodified
            
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                return response

            
            # Step 6: Read and buffer the full response body (only once allowed)
            
            body = [chunk async for chunk in response.body_iterator]
            raw_body = b"".join(body).decode("utf-8")

            
            # Step 7: Try to parse the response body as JSON
            # If it fails, treat it as plain text
            
            try:
                data = json.loads(raw_body) if raw_body else None
            except json.JSONDecodeError:
                data = raw_body

            
            # Step 8: Capture response time and compute processing duration
            
            response_time = datetime.utcnow()
            duration_ms = (response_time - request_time).total_seconds() * 1000

            
            # Step 9: Determine if the response status indicates success
            
            success = 200 <= response.status_code < 300

            
            # Step 10: Create a uniform response structure with metadata
            
            formatted = {
                "request_id": request_id,
                "success": success,
                "data": data,
                "message": "",
                "status_code": response.status_code,
                "request_time": request_time.isoformat() + "Z",
                "response_time": response_time.isoformat() + "Z",
                "duration_ms": round(duration_ms, 2)
            }
            
            loggerinfo.info(
                f"[Response] Request-ID={request_id}, Status={response.status_code}, Duration={round(duration_ms, 2)}ms, Path={request.url.path}, Response={formatted}"
            )


            return JSONResponse(content=formatted, status_code=response.status_code)

        except Exception as e:
            
            loggerinfo.error(
                f"[Error] Request-ID={request_id}, Exception={str(e)}, Path={request.url.path}"
            )
            
            # Step 11: In case of unexpected error, return a formatted 500 response
            
            response_time = datetime.utcnow()
            duration_ms = (response_time - request_time).total_seconds() * 1000

            error_response = {
                "request_id": request_id,
                "success": False,
                "data": None,
                "message": str(e),
                "status_code": 500,
                "request_time": request_time.isoformat() + "Z",
                "response_time": response_time.isoformat() + "Z",
                "duration_ms": round(duration_ms, 2)
            }
            


            return JSONResponse(content=error_response, status_code=500)
