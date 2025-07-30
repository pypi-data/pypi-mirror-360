"""StockAlert Python SDK Client."""
import time
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests

from .__version__ import __version__
from .exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    StockAlertError,
    ValidationError,
)
from .resources.alerts import AlertsResource
from .resources.webhooks import WebhooksResource


class StockAlert:
    """StockAlert API client."""

    DEFAULT_BASE_URL = "https://stockalert.pro/api/public/v1"
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        debug: bool = False,
    ):
        """Initialize the StockAlert client."""
        if not api_key:
            raise ValidationError("API key is required")

        if not api_key.startswith("sk_") or len(api_key) < 10:
            raise ValidationError("Invalid API key format")

        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retries = max_retries or self.DEFAULT_MAX_RETRIES
        self.debug = debug

        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "User-Agent": f"stockalert-python/{__version__}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

        # Initialize resources
        self.alerts = AlertsResource(self)

        # Create config dict for WebhooksResource
        config = {
            "api_key": api_key,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries
        }
        self.webhooks = WebhooksResource(config)

        # Rate limit tracking
        self._rate_limit_reset: Dict[str, float] = {}

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        """Make an HTTP request to the API."""
        url = urljoin(self.base_url, path)
        timeout = timeout or self.timeout

        # Check rate limit
        if url in self._rate_limit_reset:
            reset_time = self._rate_limit_reset[url]
            current_time = time.time()
            if current_time < reset_time:
                wait_time = reset_time - current_time
                raise RateLimitError(
                    f"Rate limit exceeded. Please wait {wait_time:.0f} seconds.",
                    retry_after=int(wait_time)
                )

        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                if self.debug and attempt > 0:
                    print(f"[StockAlert SDK] Retry attempt {attempt}/{self.max_retries}")

                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    timeout=timeout
                )

                # Handle rate limits
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    self._rate_limit_reset[url] = time.time() + retry_after

                    data = response.json()
                    raise RateLimitError(
                        data.get("error", "Rate limit exceeded"),
                        retry_after=retry_after
                    )

                # Parse response
                try:
                    data = response.json()
                except ValueError as e:
                    raise APIError(f"Invalid JSON response: {response.text}", response.status_code) from e

                # Handle errors
                if response.status_code == 401:
                    raise AuthenticationError(data.get("error", "Authentication failed"))

                if not response.ok:
                    raise APIError(
                        data.get("error", f"HTTP {response.status_code}"),
                        response.status_code,
                        data
                    )

                if not data.get("success", True):
                    raise APIError(
                        data.get("error", "Request failed"),
                        response.status_code,
                        data
                    )

                # Return data directly for single objects, or full response for lists
                if "data" in data and "meta" not in data:
                    return data["data"]
                return data

            except requests.exceptions.Timeout:
                last_error = NetworkError("Request timeout")
            except requests.exceptions.ConnectionError as e:
                last_error = NetworkError(f"Connection error: {e}")
            except (APIError, RateLimitError, AuthenticationError):
                raise  # Don't retry client errors
            except Exception as e:
                last_error = e

            # Retry with exponential backoff
            if attempt < self.max_retries:
                delay = (2 ** attempt) + (0.1 * (attempt + 1))
                if isinstance(last_error, RateLimitError) and last_error.retry_after:
                    delay = last_error.retry_after

                time.sleep(delay)

        raise last_error or StockAlertError("Request failed after retries")

    def __enter__(self) -> "StockAlert":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.session.close()
