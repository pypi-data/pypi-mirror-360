import httpx
import threading
import time
import random

from typing import Any, Dict
from ..central_data import Client as CentralDataClient
from ..series_state import Client as SeriesStateClient


class RateLimitMixin:
    """
    Mixin class that allows us to access the original response and apply rate limiting.

    We override the get_data method to access the original HTTP response.
    """

    def __init__(self, *args, **kwargs):
        self.rate_limit_headers = set(
            ["x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset"]
        )
        self.buffer_ratio = 0.1
        self.default_wait = 1.0
        self.lock = threading.Lock()

        super().__init__(*args, **kwargs)

    def get_data(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Override the get_data method in the generated clients to apply a rate limit.

        Args:
            response: The HTTP response from the GraphQL request
        """
        data = super().get_data(response)

        headers = response.headers

        with self.lock:
            if not set(headers).issuperset(self.rate_limit_headers):
                time.sleep(self.default_wait)
            else:
                limit = int(headers["x-ratelimit-limit"])
                remaining = int(headers["x-ratelimit-remaining"])
                reset_seconds = int(headers["x-ratelimit-reset"])

                buffer_threshold = max(1, int(limit * self.buffer_ratio))

                if remaining <= buffer_threshold:
                    # Sleep until reset plus a small random delay
                    sleep_time = reset_seconds + random.uniform(0.1, 1.0)
                    time.sleep(sleep_time)
                else:
                    usage_ratio = (limit - remaining) / limit
                    sleep_time = (reset_seconds / remaining) * (1 + usage_ratio)
                    # Cap sleep time to avoid excessive waits
                    sleep_time = min(sleep_time, reset_seconds / 2)
                    time.sleep(sleep_time)

        return data


# Extended Base Clients
class ExtendedCentralDataClient(RateLimitMixin, CentralDataClient):
    pass


class ExtendedSeriesStateClient(RateLimitMixin, SeriesStateClient):
    pass
