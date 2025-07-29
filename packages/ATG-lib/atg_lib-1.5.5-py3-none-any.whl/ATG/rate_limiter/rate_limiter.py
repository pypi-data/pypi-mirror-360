"""
A lightweight, decorator-based approach to Riot API rate limiting.
Created with Claude 3.7
"""

import time
import functools
from typing import Dict, Callable, Any, Optional
import threading


class RiotRateLimiter:
    """Simple rate limiter for Riot API based on response headers."""

    def __init__(self):
        # Store rate limit info by endpoint key (method+region)
        self.limits = {}
        # Add thread lock for thread safety
        self.lock = threading.Lock()

    def update_limits(self, endpoint_key: str, headers: Dict[str, str]) -> None:
        """Update rate limit information from response headers."""
        with self.lock:
            # Track when we should retry if rate limited
            retry_after = headers.get("Retry-After")
            if retry_after:
                self.limits[endpoint_key] = {
                    "retry_after": int(retry_after) + time.time()
                }
                return

            # Parse app rate limit headers
            app_limit = headers.get("X-App-Rate-Limit")
            app_count = headers.get("X-App-Rate-Limit-Count")

            # Parse method rate limit headers
            method_limit = headers.get("X-Method-Rate-Limit")
            method_count = headers.get("X-Method-Rate-Limit-Count")

            # Only update if we have both values
            if not (app_limit and app_count and method_limit and method_count):
                return

            # Parse all time windows from app rate limit
            app_limits = {}
            app_counts = {}

            for limit_part, count_part in zip(
                app_limit.split(","), app_count.split(",")
            ):
                limit_val, window = limit_part.split(":")
                count_val, _ = count_part.split(":")
                window = int(window)
                app_limits[window] = int(limit_val)
                app_counts[window] = int(count_val)

            # Parse all time windows from method rate limit
            method_limits = {}
            method_counts = {}

            for limit_part, count_part in zip(
                method_limit.split(","), method_count.split(",")
            ):
                limit_val, window = limit_part.split(":")
                count_val, _ = count_part.split(":")
                window = int(window)
                method_limits[window] = int(limit_val)
                method_counts[window] = int(count_val)

            # Store the limit data with expiry time
            current_time = time.time()
            limit_data = {
                "app_limits": app_limits,
                "app_counts": app_counts,
                "app_reset": current_time + max(app_limits.keys()),
                "method_limits": method_limits,
                "method_counts": method_counts,
                "method_reset": current_time + max(method_limits.keys()),
                "last_updated": current_time,
            }

            # Update or set the limits for this endpoint
            self.limits[endpoint_key] = limit_data

    def should_wait(self, endpoint_key: str) -> float:
        """Determine if/how long we should wait before making another request."""
        with self.lock:
            if endpoint_key not in self.limits:
                return 0

            limit_data = self.limits[endpoint_key]
            current_time = time.time()

            # Handle explicit retry-after
            if "retry_after" in limit_data:
                wait_time = limit_data["retry_after"] - current_time
                if wait_time <= 0:
                    # Clear the retry after
                    del self.limits[endpoint_key]["retry_after"]
                    return 0
                return wait_time

            # If we don't have limit data yet, don't wait
            if not ("app_limits" in limit_data and "method_limits" in limit_data):
                return 0

            # Check all app limit windows
            app_wait = 0
            for window, limit in limit_data["app_limits"].items():
                count = limit_data["app_counts"].get(window, 0)
                usage_ratio = count / limit

                # If we're at more than 80% of capacity, calculate wait time
                if usage_ratio > 0.8:
                    # Estimate time until reset based on window size
                    time_elapsed = current_time - limit_data["last_updated"]
                    time_remaining = max(0, window - time_elapsed)
                    wait = time_remaining * (usage_ratio - 0.7)  # Progressive wait
                    app_wait = max(app_wait, wait)

            # Check all method limit windows
            method_wait = 0
            for window, limit in limit_data["method_limits"].items():
                count = limit_data["method_counts"].get(window, 0)
                usage_ratio = count / limit

                # If we're at more than 80% of capacity, calculate wait time
                if usage_ratio > 0.8:
                    # Estimate time until reset based on window size
                    time_elapsed = current_time - limit_data["last_updated"]
                    time_remaining = max(0, window - time_elapsed)
                    wait = time_remaining * (usage_ratio - 0.7)  # Progressive wait
                    method_wait = max(method_wait, wait)

            # Take the larger of the two wait times
            return max(app_wait, method_wait)


# Create a single shared rate limiter
_rate_limiter = RiotRateLimiter()


def riot_api_limiter(endpoint_key: Optional[str] = None):
    """
    Decorator that handles Riot API rate limiting based on response headers.

    Args:
        endpoint_key: Optional key to identify this endpoint. If not provided,
                     the function name will be used.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the endpoint key
            key = endpoint_key or func.__name__

            # Check region if it's in the kwargs
            if "region" in kwargs:
                key = f"{key}_{kwargs['region']}"

            # Wait if needed
            wait_time = _rate_limiter.should_wait(key)
            if wait_time > 0:
                time.sleep(wait_time)

            # Call the original function
            response = func(*args, **kwargs)

            # Update rate limits from the response
            if hasattr(response, "headers"):
                _rate_limiter.update_limits(key, response.headers)

            # Handle rate limiting response (429)
            if hasattr(response, "status_code") and response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                time.sleep(retry_after)
                # Retry the request
                return func(*args, **kwargs)

            return response

        return wrapper

    return decorator


def print_rate_limit_headers(response):
    """Helper function to print rate limit headers from a response."""
    print("\nRate Limit Headers:")
    for key, value in response.headers.items():
        if "rate" in key.lower() or "retry" in key.lower():
            print(f"{key}: {value}")
