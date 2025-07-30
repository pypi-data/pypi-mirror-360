from typing import Optional

from modempay.resources.base import BaseResource
from modempay.types.transfer import (
    Transfer,
    TransferFeeCheckParams,
    TransferFeeCheckResponse,
    TransferParams,
)


class TransfersResource(BaseResource):
    """
    Resource class for managing transfers.
    """

    def __init__(self, api_key: str, max_retries: int, timeout: int):
        super().__init__(api_key, max_retries, timeout)

    def initiate(self, params: TransferParams) -> Transfer:
        """
        Initiates a transfer.

        Args:
            params (dict): Parameters for initiating the transfer.

        Returns:
            Transfer: The created transfer object.
        """
        return self.request(
            "post",
            "/v1/transfers",
            json=params,
        )

    def retrieve(self, id: str) -> Transfer:
        """
        Retrieves transfer data by ID.

        Args:
            id (str): The ID of the transfer.

        Returns:
            Transfer: The transfer object.
        """
        return self.request(
            "get",
            f"/v1/transfers/{id}",
        )

    def fee(self, params: TransferFeeCheckParams) -> TransferFeeCheckResponse:
        """
        Checks the transfer fee.

        Args:
            params (TransferFeeCheckParams): Parameters for checking the transfer fee.

        Returns:
            TransferFeeCheckResponse: The response containing the transfer fee details.
        """
        return self.request(
            "post",
            "/v1/transfers/fees",
            json=params,
        )
