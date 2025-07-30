from typing import Optional

from modempay.resources.base import BaseResource
from modempay.types.customer import (
    Customer,
    CustomerParams,
    CustomerCreateOption,
    CustomerListOption,
)
from modempay.types.type import List, ListOption


class CustomersResource(BaseResource):
    """
    Resource class for managing customers.
    """

    def __init__(self, api_key: str, max_retries: int, timeout: int):
        super().__init__(api_key, max_retries, timeout)

    def create(
        self,
        params: CustomerParams,
        options: Optional[CustomerCreateOption] = None,
    ) -> Customer:
        """
        Creates a new customer.

        Args:
            params (CustomerParams): Parameters for the new customer.
            options (CustomerCreateOption, optional): Options for customer creation.

        Returns:
            Customer: The created customer object.
        """
        if options is None:
            options = {"distinct": False}
        data = {**params, "config": {**options}}
        return self.request(
            "post",
            "/v1/customers",
            headers=self.get_headers(),
            json=data,
        )

    def retrieve(self, id: str) -> Customer:
        """
        Retrieves a customer's data.

        Args:
            id (str): The customer ID.

        Returns:
            Customer: The customer object.
        """
        return self.request(
            "get",
            f"/v1/customers/{id}",
            headers=self.get_headers(),
        )

    def list(
        self,
        options: Optional[CustomerListOption] = None,
    ) -> List[Customer]:
        """
        Returns a list of customers.

        Args:
            options (CustomerListOption, optional): Options for listing customers.

        Returns:
            Dict[str, Any]: A dictionary containing a list of customers and metadata.
        """
        if options is None:
            options = {"limit": 10}
        search_term = options.get("search", "")
        params = {"offset": 0, **options}
        return self.request(
            "get",
            f"/v1/customers?term={search_term}",
            headers=self.get_headers(),
            params=params,
        )

    def update(self, id: str, params: CustomerParams) -> Customer:
        """
        Updates the specified customer.

        Args:
            id (str): The customer ID.
            params (CustomerParams): Parameters to update.

        Returns:
            Customer: The updated customer object.
        """
        return self.request(
            "put",
            f"/v1/customers/{id}",
            headers=self.get_headers(),
            json={"data": {**params}},
        )

    def delete(self, id: str) -> None:
        """
        Permanently deletes a customer.

        Args:
            id (str): The customer ID.

        Returns:
            None
        """
        self.request(
            "delete",
            f"/v1/customers/{id}",
            headers=self.get_headers(),
        )
