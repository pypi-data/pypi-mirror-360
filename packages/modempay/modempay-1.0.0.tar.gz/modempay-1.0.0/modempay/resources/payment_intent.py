from typing import Optional, Dict, Any

from modempay.resources.base import BaseResource
from modempay.types.payment_intent import (
    PaymentIntent,
    PaymentIntentParams,
    PaymentIntentResponse,
)
from modempay.types.type import List, ListOption


class PaymentIntentsResource(BaseResource):
    """
    Resource class for managing payment intents.
    """

    def __init__(self, api_key: str, max_retries: int, timeout: int):
        super().__init__(api_key, max_retries, timeout)

    def create(self, params: PaymentIntentParams) -> PaymentIntentResponse:
        """
        Creates a payment intent.

        Args:
            params (PaymentIntentParams): Parameters for creating the payment intent.

        Returns:
            PaymentIntentResponse: The response containing the created payment intent details.
        """
        data = {"data": {**params, "from_sdk": False}}
        return self.request(
            "post",
            "/v1/payments",
            json=data,
        )

    def retrieve(self, intent_secret: str) -> PaymentIntent:
        """
        Retrieves a payment intent by its intent secret.

        Args:
            intent_secret (str): The secret of the payment intent.

        Returns:
            PaymentIntent: The payment intent object.
        """
        return self.request(
            "get",
            f"/v1/payments/verify?intent_secret={intent_secret}",
        )

    def cancel(self, id: str) -> PaymentIntent:
        """
        Cancels the payment intent.

        Args:
            id (str): The ID of the payment intent to cancel.

        Returns:
            PaymentIntent: The cancelled payment intent object.
        """
        return self.request(
            "patch",
            f"/v1/payments/{id}",
        )

    def list(self, options: Optional[ListOption] = None) -> List[PaymentIntent]:
        """
        Returns a list of payment intents.

        Args:
            options (Optional[ListOption]): Options for listing payment intents (e.g., limit, offset).

        Returns:
            List[PaymentIntent]: A list of payment intents.
        """
        if options is None:
            options = {"limit": 10}
        params = {"offset": 0, **options}
        return self.request(
            "get",
            "/v1/payments",
            params=params,
        )
