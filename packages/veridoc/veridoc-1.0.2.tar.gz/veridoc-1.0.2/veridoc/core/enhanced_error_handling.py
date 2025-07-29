"""
Enhanced Error Handling for VeriDoc
Comprehensive error management and user-friendly responses
"""

import logging
import traceback
import functools
from typing import Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification."""
    VALIDATION = "validation"
    PERMISSION = "permission"
    NOT_FOUND = "not_found"
    INTERNAL = "internal"
    SECURITY = "security"
    NETWORK = "network"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"


class VeriDocError(Exception):
    """Base exception class for VeriDoc errors."""
    
    def __init__(self, 
                 message: str,
                 category: ErrorCategory = ErrorCategory.INTERNAL,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 details: Optional[Dict[str, Any]] = None,
                 user_message: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.user_message = user_message or self._generate_user_message()
        self.timestamp = datetime.utcnow()
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly error message."""
        if self.category == ErrorCategory.VALIDATION:
            return "The request contains invalid data. Please check your input and try again."
        elif self.category == ErrorCategory.PERMISSION:
            return "You don't have permission to access this resource."
        elif self.category == ErrorCategory.NOT_FOUND:
            return "The requested resource was not found."
        elif self.category == ErrorCategory.SECURITY:
            return "Security policy violation detected."
        elif self.category == ErrorCategory.NETWORK:
            return "Network connectivity issue. Please try again later."
        elif self.category == ErrorCategory.TIMEOUT:
            return "The operation timed out. Please try again."
        elif self.category == ErrorCategory.RATE_LIMIT:
            return "Rate limit exceeded. Please wait before trying again."
        else:
            return "An unexpected error occurred. Please try again later."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        return {
            "error": True,
            "message": self.user_message,
            "details": {
                "category": self.category.value,
                "severity": self.severity.value,
                "timestamp": self.timestamp.isoformat(),
                "internal_message": self.message
            }
        }


class ValidationError(VeriDocError):
    """Error for validation failures."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            message, 
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )
        if field:
            self.details["field"] = field


class PermissionError(VeriDocError):
    """Error for permission/access issues."""
    
    def __init__(self, message: str, resource: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.PERMISSION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )
        if resource:
            self.details["resource"] = resource


class NotFoundError(VeriDocError):
    """Error for resource not found."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NOT_FOUND,
            severity=ErrorSeverity.LOW,
            **kwargs
        )
        if resource_type:
            self.details["resource_type"] = resource_type


class SecurityError(VeriDocError):
    """Error for security violations."""
    
    def __init__(self, message: str, violation_type: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        if violation_type:
            self.details["violation_type"] = violation_type


class ErrorHandler:
    """Centralized error handling for VeriDoc."""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or "logs/error.log"
        self.error_counts = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup error logging."""
        # Ensure log directory exists
        log_dir = Path(self.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure error logger
        error_logger = logging.getLogger('veridoc_errors')
        error_logger.setLevel(logging.ERROR)
        
        # File handler for error logs
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - Category: %(category)s - Severity: %(severity)s - %(message)s'
        )
        handler.setFormatter(formatter)
        error_logger.addHandler(handler)
        
        self.error_logger = error_logger
    
    def handle_exception(self, 
                        exc: Exception, 
                        context: Optional[Dict[str, Any]] = None) -> VeriDocError:
        """Convert generic exception to VeriDocError."""
        context = context or {}
        
        # Convert known exception types
        if isinstance(exc, FileNotFoundError):
            return NotFoundError(
                f"File not found: {str(exc)}",
                resource_type="file",
                details=context
            )
        elif isinstance(exc, PermissionError):
            return PermissionError(
                f"Permission denied: {str(exc)}",
                resource=context.get("resource"),
                details=context
            )
        elif isinstance(exc, ValueError):
            return ValidationError(
                f"Invalid value: {str(exc)}",
                field=context.get("field"),
                details=context
            )
        elif isinstance(exc, TimeoutError):
            return VeriDocError(
                f"Operation timed out: {str(exc)}",
                category=ErrorCategory.TIMEOUT,
                severity=ErrorSeverity.MEDIUM,
                details=context
            )
        elif isinstance(exc, ConnectionError):
            return VeriDocError(
                f"Connection error: {str(exc)}",
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.MEDIUM,
                details=context
            )
        else:
            # Generic internal error
            return VeriDocError(
                f"Internal error: {str(exc)}",
                category=ErrorCategory.INTERNAL,
                severity=ErrorSeverity.HIGH,
                details={
                    **context,
                    "exception_type": type(exc).__name__,
                    "traceback": traceback.format_exc()
                }
            )
    
    def log_error(self, error: Union[VeriDocError, Exception], context: Optional[Dict[str, Any]] = None):
        """Log error with appropriate detail level."""
        if isinstance(error, VeriDocError):
            veridoc_error = error
        else:
            veridoc_error = self.handle_exception(error, context)
        
        # Count error occurrences
        error_key = f"{veridoc_error.category.value}:{veridoc_error.message[:50]}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log with context
        self.error_logger.error(
            veridoc_error.message,
            extra={
                "category": veridoc_error.category.value,
                "severity": veridoc_error.severity.value,
                "details": veridoc_error.details,
                "count": self.error_counts[error_key]
            }
        )
        
        # Log stack trace for critical errors
        if veridoc_error.severity == ErrorSeverity.CRITICAL:
            self.error_logger.critical(
                f"Critical error details: {veridoc_error.details.get('traceback', 'No traceback available')}"
            )
    
    def get_error_response(self, 
                          error: Union[VeriDocError, Exception],
                          context: Optional[Dict[str, Any]] = None,
                          include_debug: bool = False) -> Dict[str, Any]:
        """Get error response for API."""
        if isinstance(error, VeriDocError):
            veridoc_error = error
        else:
            veridoc_error = self.handle_exception(error, context)
        
        # Log the error
        self.log_error(veridoc_error, context)
        
        # Prepare response
        response = veridoc_error.to_dict()
        
        # Add debug information if requested
        if include_debug and veridoc_error.details:
            response["debug"] = veridoc_error.details
        
        return response
    
    def get_http_status_code(self, error: VeriDocError) -> int:
        """Get appropriate HTTP status code for error."""
        status_map = {
            ErrorCategory.VALIDATION: 400,  # Bad Request
            ErrorCategory.PERMISSION: 403,  # Forbidden
            ErrorCategory.NOT_FOUND: 404,   # Not Found
            ErrorCategory.SECURITY: 403,    # Forbidden
            ErrorCategory.TIMEOUT: 408,     # Request Timeout
            ErrorCategory.RATE_LIMIT: 429,  # Too Many Requests
            ErrorCategory.NETWORK: 503,     # Service Unavailable
            ErrorCategory.INTERNAL: 500     # Internal Server Error
        }
        return status_map.get(error.category, 500)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        total_errors = sum(self.error_counts.values())
        return {
            "total_errors": total_errors,
            "error_counts": dict(self.error_counts),
            "top_errors": sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def reset_statistics(self):
        """Reset error statistics."""
        self.error_counts.clear()


# Global error handler instance
error_handler = ErrorHandler()


def handle_api_error(func):
    """Decorator for API endpoint error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except VeriDocError as e:
            status_code = error_handler.get_http_status_code(e)
            response = error_handler.get_error_response(e)
            from fastapi import HTTPException
            raise HTTPException(status_code=status_code, detail=response)
        except Exception as e:
            veridoc_error = error_handler.handle_exception(e, {
                "function": func.__name__,
                "args": str(args)[:100],
                "kwargs": str(kwargs)[:100]
            })
            status_code = error_handler.get_http_status_code(veridoc_error)
            response = error_handler.get_error_response(veridoc_error)
            from fastapi import HTTPException
            raise HTTPException(status_code=status_code, detail=response)
    
    return wrapper


def handle_async_api_error(func):
    """Decorator for async API endpoint error handling."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except VeriDocError as e:
            status_code = error_handler.get_http_status_code(e)
            response = error_handler.get_error_response(e)
            from fastapi import HTTPException
            raise HTTPException(status_code=status_code, detail=response)
        except Exception as e:
            veridoc_error = error_handler.handle_exception(e, {
                "function": func.__name__,
                "args": str(args)[:100],
                "kwargs": str(kwargs)[:100]
            })
            status_code = error_handler.get_http_status_code(veridoc_error)
            response = error_handler.get_error_response(veridoc_error)
            from fastapi import HTTPException
            raise HTTPException(status_code=status_code, detail=response)
    
    return wrapper