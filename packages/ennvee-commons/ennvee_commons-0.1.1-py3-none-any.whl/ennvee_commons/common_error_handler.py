"""
common_error_handler.py

Comprehensive function-based error handling for consistent service responses.
Provides reusable functions for common error scenarios: validation, auth, API,
resource issues, conflicts, rate limits, timeouts, and more.

Author: Paavan Boddeda
Organization: ennVee TechnoGroup
"""

import traceback


def format_error(message: str, code: str = "SERVICE_ERROR") -> dict:
    """
    Returns a standardized error response format.

    Args:
        message (str): The error message to return.
        code (str): A unique code identifying the error type (default is "SERVICE_ERROR").

    Returns:
        dict: A dictionary with keys: "status", "code", and "message" representing the error.
    """
    return {
        "status": "error",
        "code": code,
        "message": message
    }

# 1. Input/validation-related errors

def validation_error(message: str) -> dict:
    """
    Handles errors related to input validation failure.

    Args:
        message (str): The error message describing the validation issue.

    Returns:
        dict: A dictionary with a standardized error response for validation failure.
    """
    return format_error(message, "VALIDATION_ERROR")

def missing_parameter_error(param_name: str) -> dict:
    """
    Handles errors when a required parameter is missing.

    Args:
        param_name (str): The name of the missing parameter.

    Returns:
        dict: A dictionary with an error message indicating the missing parameter.
    """
    return format_error(f"Missing required parameter: {param_name}", "MISSING_PARAMETER")

def invalid_format_error(field: str) -> dict:
    """
    Handles errors related to invalid data format for a specific field.

    Args:
        field (str): The field with the invalid format.

    Returns:
        dict: A dictionary with an error message indicating the invalid format for the field.
    """
    return format_error(f"Invalid format for: {field}", "INVALID_FORMAT")

def unsupported_type_error(field: str, expected_type: str) -> dict:
    """
    Handles errors related to unsupported data types for a specific field.

    Args:
        field (str): The field with the unsupported type.
        expected_type (str): The expected data type.

    Returns:
        dict: A dictionary with an error message indicating the unsupported type for the field.
    """
    return format_error(f"Unsupported type for {field}, expected {expected_type}", "UNSUPPORTED_TYPE")

# 2. Authentication & Authorization errors

def authentication_error(message: str = "Authentication failed") -> dict:
    """
    Handles errors when authentication fails.

    Args:
        message (str): A custom message for authentication failure (default is "Authentication failed").

    Returns:
        dict: A dictionary with an error message related to authentication failure.
    """
    return format_error(message, "AUTHENTICATION_ERROR")

def unauthorized_error(action: str = "access this resource") -> dict:
    """
    Handles errors when the user is unauthorized to perform a specific action.

    Args:
        action (str): The action the user is trying to perform (default is "access this resource").

    Returns:
        dict: A dictionary with an error message indicating that the user is not authorized.
    """
    return format_error(f"You are not authorized to {action}", "UNAUTHORIZED")

def forbidden_error(message: str = "Access to this resource is forbidden") -> dict:
    """
    Handles errors when access to a specific resource is forbidden.

    Args:
        message (str): The error message (default is "Access to this resource is forbidden").

    Returns:
        dict: A dictionary with an error message indicating forbidden access.
    """
    return format_error(message, "FORBIDDEN")

# 3. Resource errors

def not_found_error(resource: str) -> dict:
    """
    Handles errors when a resource cannot be found.

    Args:
        resource (str): The name of the resource that was not found.

    Returns:
        dict: A dictionary with an error message indicating the resource was not found.
    """
    return format_error(f"{resource} not found", "NOT_FOUND")

def already_exists_error(resource: str) -> dict:
    """
    Handles errors when a resource already exists (e.g., trying to create a duplicate).

    Args:
        resource (str): The name of the resource that already exists.

    Returns:
        dict: A dictionary with an error message indicating the resource already exists.
    """
    return format_error(f"{resource} already exists", "ALREADY_EXISTS")

def conflict_error(resource: str, reason: str = "") -> dict:
    """
    Handles errors related to a conflict, such as when trying to create or modify a resource
    that conflicts with another existing one.

    Args:
        resource (str): The name of the conflicting resource.
        reason (str): The reason for the conflict (optional).

    Returns:
        dict: A dictionary with an error message indicating the conflict.
    """
    msg = f"Conflict with {resource}" + (f": {reason}" if reason else "")
    return format_error(msg, "CONFLICT_ERROR")

# 4. External system/API errors

def api_request_error(message: str) -> dict:
    """
    Handles errors related to external API requests.

    Args:
        message (str): A message describing the error encountered during the API request.

    Returns:
        dict: A dictionary with an error message related to the external API request.
    """
    return format_error(message, "API_REQUEST_ERROR")

def timeout_error(service_name: str = "external service") -> dict:
    """
    Handles errors when a request to an external service times out.

    Args:
        service_name (str): The name of the service that timed out (default is "external service").

    Returns:
        dict: A dictionary with an error message indicating the timeout.
    """
    return format_error(f"Request to {service_name} timed out", "TIMEOUT")

def dependency_failure(service_name: str = "external service") -> dict:
    """
    Handles errors when an external service fails to respond properly.

    Args:
        service_name (str): The name of the service that failed (default is "external service").

    Returns:
        dict: A dictionary with an error message indicating the dependency failure.
    """
    return format_error(f"{service_name} failed to respond properly", "DEPENDENCY_FAILURE")

# 5. Rate limiting / throttling

def rate_limit_exceeded(message: str = "Rate limit exceeded") -> dict:
    """
    Handles errors when a rate limit is exceeded for API requests.

    Args:
        message (str): A custom message indicating the rate limit issue (default is "Rate limit exceeded").

    Returns:
        dict: A dictionary with an error message indicating that the rate limit has been exceeded.
    """
    return format_error(message, "RATE_LIMIT")

# 6. Internal/unexpected errors

def unhandled_exception(e: Exception, context: str = "An unexpected error occurred") -> dict:
    """
    Handles unexpected/unhandled exceptions and provides a standardized error response.

    Args:
        e (Exception): The exception object that was raised.
        context (str): A custom context message explaining the source of the error (default is "An unexpected error occurred").

    Returns:
        dict: A dictionary with an error message for the unhandled exception.
    """
    traceback.print_exc()  # Optional: disable in production
    return format_error(f"{context}: {str(e)}", "UNHANDLED_EXCEPTION")

def internal_server_error(message: str = "Something went wrong") -> dict:
    """
    Handles errors related to server issues, typically when something goes wrong internally.

    Args:
        message (str): A custom message indicating the internal server issue (default is "Something went wrong").

    Returns:
        dict: A dictionary with an error message indicating an internal server error.
    """
    return format_error(message, "INTERNAL_SERVER_ERROR")
