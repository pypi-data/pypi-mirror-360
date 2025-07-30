"""
ExecutionLogger - Enterprise Python Logging Solution

Comprehensive logging with SharePoint uploads and Dataverse error tracking.
"""

__version__ = "1.1.1"
__author__ = "Shaik Rizwana"

# Import main class with dependency check
try:
    from .execution_logger import ExecutionLogger
except ImportError as e:
    raise ImportError(
        f"ExecutionLogger dependencies missing: {e}. "
        "Install with: pip install msal requests"
    )

# Public API
__all__ = ['ExecutionLogger']