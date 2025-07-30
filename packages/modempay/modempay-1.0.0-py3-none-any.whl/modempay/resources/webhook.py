from typing import Any, Dict, Union

from modempay.resources.base import BaseResource
from modempay.types.webhook import Event

import hmac
import hashlib


class WebhooksResource(BaseResource):
    """
    Resource class for handling webhook event signature validation and event composition.
    """

    def __init__(self, api_key: str, max_retries: int, timeout: int):
        super().__init__(api_key, max_retries, timeout)

    def compose_event_details(
        self,
        payload: Union[str, Dict[str, Any]],
        signature: str,
        secret: str,
    ) -> Event:
        """
        Builds and validates an Event signature based on the provided details.

        Args:
            payload (str | dict): The webhook payload, as a JSON string or dict.
            signature (str): The signature to validate against.
            secret (str): The secret key used to compute the HMAC.

        Returns:
            Event: The parsed and validated event object.

        Raises:
            ValueError: If the signature is invalid or the payload is malformed.
        """
        if isinstance(payload, str):
            payload_string = payload
        else:
            payload_string = self._json_stringify(payload)

        # Generate HMAC-SHA512 hash for comparison
        computed_signature = hmac.new(
            secret.encode("utf-8"),
            payload_string.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()

        # Check signature length for a quick validation step
        if len(computed_signature) != len(signature):
            raise ValueError("Invalid signature length")

        # Perform timing-safe comparison for added security
        if not hmac.compare_digest(computed_signature, signature):
            raise ValueError("Invalid signature!")

        # Parse the payload if it's a JSON string
        if isinstance(payload, str):
            try:
                import json

                parsed_payload = json.loads(payload)
            except Exception:
                raise ValueError("Invalid Payload!")
        else:
            parsed_payload = payload

        # Return the event object with event type and payload
        return {
            "event": parsed_payload["event"],
            "payload": parsed_payload["payload"],
        }

    def _json_stringify(self, obj: Dict[str, Any]) -> str:
        """
        Helper method to convert a dict to a JSON string with consistent formatting.
        """
        import json

        return json.dumps(obj, separators=(",", ":"), sort_keys=True)
