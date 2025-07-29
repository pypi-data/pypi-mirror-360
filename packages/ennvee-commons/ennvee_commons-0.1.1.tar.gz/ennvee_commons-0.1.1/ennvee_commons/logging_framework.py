"""
log_utils.py

This module provides a utility to configure and dispatch logs
using the loguru logging framework in a standardized way.

Key functionality:
- Creates log files with rotation and retention settings
- Logs to both file and console
- Supports basic log types (info, error, debug, etc.)

Dependencies:
- loguru>=0.7.0
- Python 3.8+

Author: Paavan Boddeda
Organization: ennVee TechnoGroup
"""

# import os
# import sys
# from loguru import logger


# def get_logger(
#     *,
#     log_file: str,
# ):
#     """
#     Initialize and dispatch log messages using loguru.

#     Args:
#         log_file (str): Full path to the log file.
#         log_type (str): Type of log message (e.g., info, error, debug).
#         msg (str): Log message to write.

#     Returns:
#         loguru.logger: Configured logger instance.

#     Supported log types:
#         - "debug", "info", "success", "warning", "error", "critical", "exception", "trace"
    
#     Example:
#         >>> get_logger(
#         ...     log_file="logs/app.log",
#         ...     log_type="error",
#         ...     msg="Something went wrong"
#         ... )
#     """
#     os.makedirs(os.path.dirname(log_file), exist_ok=True)

#     # Clear default handlers
#     logger.remove()

#     # Add console and file handlers
#     logger.add(sys.stdout, level="DEBUG", enqueue=True)
#     logger.add(log_file, rotation="1 MB", retention="7 days", level="DEBUG", enqueue=True)

#     # Safe dispatching of known log types
#     log_type = log_type.lower()
#     log_dispatch = {
#         "debug": logger.debug,
#         "info": logger.info,
#         "success": logger.success,
#         "warning": logger.warning,
#         "error": logger.error,
#         "critical": logger.critical,
#         "exception": logger.exception,
#         "trace": logger.trace,
#         "add": logger.add,
#         "bind": logger.bind,
#         "catch": logger.catch,
#         "complete": logger.complete,
#         "configure": logger.configure,
#         "disable": logger.disable,
#         "enable": logger.enable,
#         "level": logger.level,
#         "log": logger.log,
#         "opt": logger.opt,
#         "parse": logger.parse,
#         "patch": logger.patch,
#         "remove": logger.remove,
#         "start": logger.start,
#         "stop": logger.stop,
#     }

#     if log_type in log_dispatch:
#         log_dispatch[log_type](msg)
#     else:
#         logger.info(f"[Invalid log type: '{log_type}'] {msg}")

#     return logger



from loguru import logger
import os
import sys

def get_logger(*, log_file: str):
    """
    Configure and return a reusable loguru logger instance.

    Args:
        log_file (str): Full path to the log file to write logs.

    Returns:
        loguru.logger: Configured logger instance ready for use.
    
    Example:
        >>> loggerinfo = get_logger("logs/system.log")
        >>> loggerinfo.success("OTP sent successfully!")
        >>> loggerinfo.error("Something went wrong")
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Remove default handlers
    logger.remove()

    # Add handlers
    logger.add(sys.stdout, level="DEBUG", enqueue=True)
    logger.add(log_file, rotation="1 MB", retention="7 days", level="DEBUG", enqueue=True)

    return logger

