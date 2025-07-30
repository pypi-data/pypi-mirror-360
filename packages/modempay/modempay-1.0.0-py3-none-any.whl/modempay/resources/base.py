import os
import random
import time

from modempay.error import ModemPayError

import requests


class BaseResource:
    _apiURL = "https://api.modempay.com"
    _MAX_DELAY = 30000  # ms

    def __init__(
        self, api_key: str, max_retries: int, timeout: int, retry_delay: int = 1000
    ):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max(0, max_retries)
        self.retry_delay = max(100, retry_delay)
        self.enable_retry_logging = (
            os.environ.get("RETRY_LOGGING", "true").lower() != "false"
        )

    def get_headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def request(self, method: str, url: str, **kwargs):
        retries = kwargs.pop("retries", self.max_retries)
        attempt = self.max_retries - retries + 1
        try:
            timeout_seconds = self.timeout if self.timeout is not None else 60
            clamped_timeout = min(timeout_seconds, 180)
            headers = {
                **self.get_headers(),
                "User-Agent": "modem-pay-python/v1",
                **kwargs.pop("headers", {}),
            }
            response = requests.request(
                method,
                f"{self._apiURL}{url}",
                headers=headers,
                timeout=clamped_timeout,
                **kwargs,
            )
            try:
                response.raise_for_status()
            except requests.HTTPError as http_err:
                try:
                    resp_json = response.json() if response.content else {}
                except Exception:
                    resp_json = {}
                http_err.response = {
                    **resp_json,
                    "status_code": response.status_code,
                }
                raise http_err
            if response.content:
                return response.json()
            return None
        except Exception as error:
            if retries > 0 and self._is_retryable_error(error):
                delay = self._calculate_backoff(attempt)
                if self.enable_retry_logging:
                    print(
                        f"Retry attempt {attempt} of {self.max_retries} after {delay}ms delay"
                    )
                self._delay(delay)
                return self.request(method, url, retries=retries - 1, **kwargs)
            err = self._get_error_message(error)
            raise ModemPayError(
                err.get("message", "An error occurred."),
                err.get("status_code", 500),
            )

    def _calculate_backoff(self, attempt: int) -> int:
        exponential_delay = self.retry_delay * (2**attempt)
        jitter = random.random() * min(100, exponential_delay * 0.1)
        return int(min(exponential_delay + jitter, self._MAX_DELAY))

    def _is_retryable_error(self, error) -> bool:
        # Retry on requests.ConnectionError, requests.Timeout, or HTTP 5xx
        from requests.exceptions import ConnectionError, Timeout, HTTPError

        if isinstance(error, (ConnectionError, Timeout)):
            return True
        if isinstance(error, HTTPError):
            response = getattr(error, "response", None)
            if response is not None and response["status_code"] >= 500:
                return True
        response = getattr(error, "response", None)
        if response is not None and getattr(response, "status_code", 0) >= 500:
            return True
        return False

    def _delay(self, ms: int):
        time.sleep(ms / 1000.0)

    def _get_error_message(self, error):
        response = getattr(error, "response", None)
        status_code = getattr(error, "status_code", None)
        if response is not None:
            message_val = response.get("message", "An error occurred.")
            status = response.get("status_code", 500)
            return {
                "status_code": status_code if status_code is not None else status,
                "message": message_val,
            }
        message = getattr(error, "message", None)
        return {
            "status_code": status_code if status_code is not None else 500,
            "message": message if message is not None else "An error occurred.",
        }
