"""Retry utilities for network requests"""

import random
import time
from functools import wraps
from typing import Any, Callable, Tuple, Type

from ..exceptions import MTAConnectionError, MTATimeoutError, RateLimitError


def exponential_backoff_with_jitter(
    attempt: int, base_delay: float = 1.0, max_delay: float = 60.0
) -> float:
    """
    Calculate exponential backoff delay with jitter

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds

    Returns:
        Delay in seconds
    """
    delay = base_delay * (2**attempt)
    delay = min(delay, max_delay)
    # Add jitter (±25% of delay)
    jitter = delay * 0.25 * (2 * random.random() - 1)
    return float(max(0.0, delay + jitter))


def retry_on_failure(
    max_attempts: int = 3,
    backoff_strategy: Callable[[int], float] = exponential_backoff_with_jitter,
    retry_exceptions: Tuple[Type[Exception], ...] = (
        MTAConnectionError,
        MTATimeoutError,
    ),
    rate_limit_max_wait: int = 300,  # 5 minutes max wait for rate limiting
) -> Callable:
    """
    Decorator to retry function calls on specific exceptions

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        backoff_strategy: Function to calculate delay between attempts
        retry_exceptions: Tuple of exceptions that should trigger a retry
        rate_limit_max_wait: Maximum time to wait for rate limit recovery

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except RateLimitError as e:
                    # Special handling for rate limiting
                    if e.retry_after and e.retry_after <= rate_limit_max_wait:
                        time.sleep(e.retry_after)
                        continue
                    else:
                        # Rate limit wait too long, give up
                        raise e

                except Exception as e:
                    if not isinstance(e, retry_exceptions):
                        # Don't retry on unexpected exceptions
                        raise e

                    last_exception = e

                    # Don't wait after the last attempt
                    if attempt == max_attempts - 1:
                        break

                    # Calculate and apply backoff delay
                    delay = backoff_strategy(attempt)
                    time.sleep(delay)

            # All attempts failed, raise the last exception
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def linear_backoff(
    attempt: int, base_delay: float = 1.0, increment: float = 1.0
) -> float:
    """
    Calculate linear backoff delay

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        increment: Delay increment per attempt

    Returns:
        Delay in seconds
    """
    return base_delay + (attempt * increment)


def fixed_delay(delay: float = 1.0) -> Callable[[int], float]:
    """
    Create a fixed delay backoff strategy

    Args:
        delay: Fixed delay in seconds

    Returns:
        Backoff function
    """

    def backoff_func(attempt: int) -> float:
        return delay

    return backoff_func
