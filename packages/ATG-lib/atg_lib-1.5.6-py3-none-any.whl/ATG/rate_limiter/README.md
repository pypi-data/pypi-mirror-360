# Riot API Rate Limiter

A lightweight, decorator-based rate limiter for Riot API requests that respects the rate limit headers provided by Riot's API.

## Features

- Dynamic rate limiting based on Riot API response headers
- Per-endpoint and per-region rate limiting
- Automatic retry on 429 responses
- Shared rate limiter instance across function calls
- Thread-safe implementation
- Progressive wait times based on current usage ratios

## Usage

```python
from ATG.rate_limiter import riot_api_limiter

@riot_api_limiter(endpoint_key="my_endpoint")
def my_riot_api_function(region: str, api_key: str):
    # Your API call here
    # The decorator will handle rate limiting
    pass
```

## How It Works

1. The rate limiter parses Riot API headers to understand current limits
2. It tracks usage across multiple time windows (short and long-term limits)
3. Before making a request, it checks if we should wait based on current usage
4. It progressively slows down requests as we approach rate limits
5. If a 429 response is received, it automatically retries after waiting

## Core Components

- **RiotRateLimiter**: Tracks rate limits and calculates wait times
- **riot_api_limiter**: Decorator that applies rate limiting to API functions

## Benefits

- More efficient use of rate limits (uses headers rather than fixed delays)
- Prevents 429 errors by proactively waiting when approaching limits
- Respects both application-wide and method-specific limits
- Maintains backward compatibility with existing code