from typing import Optional

from modempay.resources.base import BaseResource
from modempay.types.transaction import Transaction, TransactionListOption
from modempay.types.type import List


class TransactionsResource(BaseResource):
    """
    Resource class for managing transactions.
    """

    def __init__(self, api_key: str, max_retries: int, timeout: int):
        super().__init__(api_key, max_retries, timeout)

    def retrieve(self, id: str) -> Transaction:
        """
        Retrieves a single transaction by its ID.

        Args:
            id (str): The ID of the transaction.

        Returns:
            Transaction: The transaction object.
        """
        return self.request(
            "get",
            f"/v1/transactions/{id}",
        )

    def reverse(self, reference: str) -> Transaction:
        """
        Reverses (refunds) a single transaction by its reference.

        Args:
            reference (str): The reference of the transaction to reverse.

        Returns:
            Transaction: The reversed transaction object.
        """
        return self.request(
            "post",
            "/v1/transactions/refund",
            json={"reference": reference},
        )

    def list(
        self, options: Optional[TransactionListOption] = None
    ) -> List[Transaction]:
        """
        Returns a list of transactions.

        Args:
            options (Optional[TransactionListOption]): Options for listing transactions.

        Returns:
            List[Transaction]: A list of transaction objects.
        """
        if options is None:
            options = {"limit": 10}
        params = {"offset": 0, **options, "term": options.get("search", "")}
        return self.request(
            "get",
            "/v1/transactions",
            params=params,
        )
