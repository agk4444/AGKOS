"""
API Error Handler for AGK Language Compiler
Comprehensive error handling for external API calls and service integrations
"""

import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import traceback


class APIErrorType(Enum):
    """Types of API errors"""
    NETWORK_ERROR = "network"
    TIMEOUT_ERROR = "timeout"
    AUTHENTICATION_ERROR = "auth"
    AUTHORIZATION_ERROR = "authorization"
    RATE_LIMIT_ERROR = "rate_limit"
    QUOTA_EXCEEDED_ERROR = "quota"
    SERVER_ERROR = "server"
    CLIENT_ERROR = "client"
    PARSING_ERROR = "parsing"
    VALIDATION_ERROR = "validation"
    SERVICE_UNAVAILABLE = "unavailable"
    UNKNOWN_ERROR = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for API errors"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class APIError:
    """Represents an API error with comprehensive information"""
    error_type: APIErrorType
    severity: ErrorSeverity
    message: str
    service_name: str
    endpoint: str
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    request_data: Optional[Any] = None
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: float = 1.0
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            'error_type': self.error_type.value,
            'severity': self.severity.value,
            'message': self.message,
            'service_name': self.service_name,
            'endpoint': self.endpoint,
            'status_code': self.status_code,
            'response_body': self.response_body,
            'headers': dict(self.headers) if self.headers else None,
            'timestamp': self.timestamp,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'context': dict(self.context)
        }

    def __str__(self) -> str:
        return f"APIError({self.service_name}:{self.endpoint} - {self.error_type.value}): {self.message}"


@dataclass
class RetryPolicy:
    """Retry policy for API calls"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    retry_on_status: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])


class APIErrorHandler:
    """Handles API errors with retry logic and recovery strategies"""

    def __init__(self):
        self.error_history: List[APIError] = []
        self.service_configs: Dict[str, Dict[str, Any]] = {}
        self.retry_policies: Dict[str, RetryPolicy] = {}
        self.error_callbacks: Dict[str, List[Callable]] = {}
        self.recovery_strategies: Dict[str, Callable] = {}

        # Default retry policies for common services
        self._setup_default_policies()

    def _setup_default_policies(self):
        """Setup default retry policies for common services"""
        # OpenAI API policy
        self.retry_policies['openai'] = RetryPolicy(
            max_retries=5,
            base_delay=1.0,
            max_delay=30.0,
            retry_on_status=[429, 500, 502, 503, 504]
        )

        # Anthropic API policy
        self.retry_policies['anthropic'] = RetryPolicy(
            max_retries=5,
            base_delay=1.0,
            max_delay=30.0,
            retry_on_status=[429, 500, 502, 503, 504]
        )

        # Generic API policy
        self.retry_policies['default'] = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            max_delay=10.0,
            retry_on_status=[429, 500, 502, 503, 504]
        )

    def classify_error(self, service_name: str, status_code: Optional[int],
                      response_body: Optional[str], exception: Optional[Exception] = None) -> APIError:
        """Classify an API error based on response"""

        # Handle exceptions
        if exception:
            if "timeout" in str(exception).lower():
                return APIError(
                    error_type=APIErrorType.TIMEOUT_ERROR,
                    severity=ErrorSeverity.MEDIUM,
                    message=f"Request timeout: {str(exception)}",
                    service_name=service_name,
                    endpoint="unknown"
                )
            elif "connection" in str(exception).lower():
                return APIError(
                    error_type=APIErrorType.NETWORK_ERROR,
                    severity=ErrorSeverity.HIGH,
                    message=f"Network connection error: {str(exception)}",
                    service_name=service_name,
                    endpoint="unknown"
                )
            else:
                return APIError(
                    error_type=APIErrorType.UNKNOWN_ERROR,
                    severity=ErrorSeverity.HIGH,
                    message=f"Unknown error: {str(exception)}",
                    service_name=service_name,
                    endpoint="unknown"
                )

        # Handle status codes
        if status_code:
            if status_code == 401:
                return APIError(
                    error_type=APIErrorType.AUTHENTICATION_ERROR,
                    severity=ErrorSeverity.CRITICAL,
                    message="Authentication failed - invalid API key",
                    service_name=service_name,
                    endpoint="unknown",
                    status_code=status_code
                )
            elif status_code == 403:
                return APIError(
                    error_type=APIErrorType.AUTHORIZATION_ERROR,
                    severity=ErrorSeverity.HIGH,
                    message="Access forbidden - insufficient permissions",
                    service_name=service_name,
                    endpoint="unknown",
                    status_code=status_code
                )
            elif status_code == 429:
                return APIError(
                    error_type=APIErrorType.RATE_LIMIT_ERROR,
                    severity=ErrorSeverity.MEDIUM,
                    message="Rate limit exceeded",
                    service_name=service_name,
                    endpoint="unknown",
                    status_code=status_code
                )
            elif status_code == 413:
                return APIError(
                    error_type=APIErrorType.QUOTA_EXCEEDED_ERROR,
                    severity=ErrorSeverity.HIGH,
                    message="Request too large or quota exceeded",
                    service_name=service_name,
                    endpoint="unknown",
                    status_code=status_code
                )
            elif status_code >= 500:
                return APIError(
                    error_type=APIErrorType.SERVER_ERROR,
                    severity=ErrorSeverity.HIGH,
                    message=f"Server error: {status_code}",
                    service_name=service_name,
                    endpoint="unknown",
                    status_code=status_code
                )
            elif status_code >= 400:
                return APIError(
                    error_type=APIErrorType.CLIENT_ERROR,
                    severity=ErrorSeverity.MEDIUM,
                    message=f"Client error: {status_code}",
                    service_name=service_name,
                    endpoint="unknown",
                    status_code=status_code
                )
            elif status_code == 503 or status_code == 502:
                return APIError(
                    error_type=APIErrorType.SERVICE_UNAVAILABLE,
                    severity=ErrorSeverity.HIGH,
                    message=f"Service temporarily unavailable: {status_code}",
                    service_name=service_name,
                    endpoint="unknown",
                    status_code=status_code
                )

        # Try to parse error from response body
        if response_body:
            try:
                # Try JSON parsing
                if response_body.strip().startswith('{'):
                    error_data = json.loads(response_body)
                    error_msg = error_data.get('error', {}).get('message', response_body)
                    return APIError(
                        error_type=APIErrorType.SERVER_ERROR,
                        severity=ErrorSeverity.HIGH,
                        message=f"API Error: {error_msg}",
                        service_name=service_name,
                        endpoint="unknown",
                        response_body=response_body
                    )
            except json.JSONDecodeError:
                pass

        # Default error
        return APIError(
            error_type=APIErrorType.UNKNOWN_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message=f"Unknown API error: {status_code or 'no status'}",
            service_name=service_name,
            endpoint="unknown",
            status_code=status_code,
            response_body=response_body
        )

    def should_retry(self, error: APIError) -> bool:
        """Determine if an error should be retried"""
        if error.retry_count >= error.max_retries:
            return False

        # Don't retry authentication or authorization errors
        if error.error_type in [APIErrorType.AUTHENTICATION_ERROR, APIErrorType.AUTHORIZATION_ERROR]:
            return False

        # Don't retry client errors (4xx except specific ones)
        if error.status_code and 400 <= error.status_code < 500:
            return error.status_code in [429]  # Only retry rate limits

        # Retry network, timeout, server errors
        return error.error_type in [
            APIErrorType.NETWORK_ERROR,
            APIErrorType.TIMEOUT_ERROR,
            APIErrorType.SERVER_ERROR,
            APIErrorType.SERVICE_UNAVAILABLE,
            APIErrorType.RATE_LIMIT_ERROR
        ]

    def calculate_retry_delay(self, error: APIError) -> float:
        """Calculate delay before retry"""
        policy = self.retry_policies.get(error.service_name, self.retry_policies['default'])

        # Exponential backoff
        delay = policy.base_delay * (policy.backoff_factor ** error.retry_count)

        # Cap at max delay
        delay = min(delay, policy.max_delay)

        # Add jitter if enabled
        if policy.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)

        return delay

    async def execute_with_retry(self, service_name: str, operation: Callable,
                               *args, **kwargs) -> Any:
        """Execute an API operation with retry logic"""
        policy = self.retry_policies.get(service_name, self.retry_policies['default'])
        error = None

        for attempt in range(policy.max_retries + 1):
            try:
                result = await operation(*args, **kwargs)
                return result

            except Exception as e:
                error = self.classify_error(
                    service_name=service_name,
                    status_code=getattr(e, 'status', None),
                    response_body=getattr(e, 'response_body', None),
                    exception=e
                )

                error.retry_count = attempt
                error.max_retries = policy.max_retries

                # Log the error
                self.error_history.append(error)
                self._trigger_error_callbacks(service_name, error)

                # Check if we should retry
                if attempt < policy.max_retries and self.should_retry(error):
                    delay = self.calculate_retry_delay(error)
                    print(f"Retrying {service_name} after {delay:.2f}s (attempt {attempt + 1}/{policy.max_retries + 1})")
                    await asyncio.sleep(delay)
                else:
                    break

        # If we get here, all retries failed
        raise error

    def add_error_callback(self, service_name: str, callback: Callable[[APIError], None]):
        """Add error callback for a service"""
        if service_name not in self.error_callbacks:
            self.error_callbacks[service_name] = []
        self.error_callbacks[service_name].append(callback)

    def _trigger_error_callbacks(self, service_name: str, error: APIError):
        """Trigger error callbacks for a service"""
        if service_name in self.error_callbacks:
            for callback in self.error_callbacks[service_name]:
                try:
                    callback(error)
                except Exception as e:
                    print(f"Error in callback: {e}")

    def add_recovery_strategy(self, error_type: APIErrorType, strategy: Callable[[APIError], Any]):
        """Add recovery strategy for specific error types"""
        self.recovery_strategies[error_type.value] = strategy

    def get_error_statistics(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get error statistics"""
        if service_name:
            errors = [e for e in self.error_history if e.service_name == service_name]
        else:
            errors = self.error_history

        stats = {
            'total_errors': len(errors),
            'error_types': {},
            'severities': {},
            'services': set()
        }

        for error in errors:
            # Count error types
            error_type = error.error_type.value
            stats['error_types'][error_type] = stats['error_types'].get(error_type, 0) + 1

            # Count severities
            severity = error.severity.value
            stats['severities'][severity] = stats['severities'].get(severity, 0) + 1

            # Track services
            stats['services'].add(error.service_name)

        stats['services'] = list(stats['services'])
        return stats

    def clear_error_history(self, service_name: Optional[str] = None):
        """Clear error history"""
        if service_name:
            self.error_history = [e for e in self.error_history if e.service_name != service_name]
        else:
            self.error_history.clear()

    def get_recent_errors(self, service_name: Optional[str] = None, limit: int = 10) -> List[APIError]:
        """Get recent errors"""
        if service_name:
            errors = [e for e in self.error_history if e.service_name == service_name]
        else:
            errors = self.error_history

        return sorted(errors, key=lambda x: x.timestamp, reverse=True)[:limit]

    def set_retry_policy(self, service_name: str, policy: RetryPolicy):
        """Set custom retry policy for a service"""
        self.retry_policies[service_name] = policy

    def get_retry_policy(self, service_name: str) -> RetryPolicy:
        """Get retry policy for a service"""
        return self.retry_policies.get(service_name, self.retry_policies['default'])


# Global error handler instance
error_handler = APIErrorHandler()

# Convenience functions for use in generated code
def classify_api_error(service_name: str, status_code: Optional[int], response_body: Optional[str], exception: Optional[Exception] = None) -> APIError:
    """Classify an API error (for use in generated Python code)"""
    return error_handler.classify_error(service_name, status_code, response_body, exception)

def should_retry_error(error: APIError) -> bool:
    """Check if an error should be retried (for use in generated Python code)"""
    return error_handler.should_retry(error)

def get_error_statistics(service_name: Optional[str] = None) -> Dict[str, Any]:
    """Get error statistics (for use in generated Python code)"""
    return error_handler.get_error_statistics(service_name)

def clear_error_history(service_name: Optional[str] = None):
    """Clear error history (for use in generated Python code)"""
    error_handler.clear_error_history(service_name)

# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def test_error_handler():
        """Test the API error handler"""

        # Test error classification
        error = error_handler.classify_error(
            service_name="openai",
            status_code=429,
            response_body='{"error": {"message": "Rate limit exceeded"}}'
        )
        print(f"Classified error: {error}")

        # Test retry logic
        should_retry = error_handler.should_retry(error)
        print(f"Should retry: {should_retry}")

        if should_retry:
            delay = error_handler.calculate_retry_delay(error)
            print(f"Retry delay: {delay:.2f} seconds")

        # Test error statistics
        stats = error_handler.get_error_statistics()
        print(f"Error statistics: {stats}")

        print("API Error Handler test completed!")

    # Run the test
    asyncio.run(test_error_handler())