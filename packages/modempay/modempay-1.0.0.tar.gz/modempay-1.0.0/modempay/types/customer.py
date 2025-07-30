from typing import TypedDict, Optional


class Customer(TypedDict):
    """
    Representation of a customer.

    Attributes:
        id (str): Unique identifier for the customer.
        name (str): Customer's name.
        email (str): Customer's email address.
        phone (Optional[str]): Customer's phone number. Optional field.
        balance (Optional[float]): Current balance associated with the customer. Optional field.
    """

    id: str
    name: str
    email: str
    phone: Optional[str]
    balance: Optional[float]


class CustomerParams(TypedDict, total=False):
    """
    Parameters used to define or update a customer.

    Attributes:
        name (str, optional): Customer's name.
        email (str, optional): Customer's email address.
        phone (str, optional): Customer's phone number.
        balance (float, optional): Initial balance assigned to the customer.
    """

    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    balance: Optional[float]


class CustomerCreateOption(TypedDict):
    """
    Options for creating a customer.

    Attributes:
        distinct (bool): Determines whether the customer should be created uniquely.
            If true, ensures no duplicate customers are created based on unique constraints.
    """

    distinct: bool


class CustomerListOption(TypedDict, total=False):
    """
    Options for listing customers.

    Attributes:
        limit (int, optional): Maximum number of customers to retrieve in a single request.
        search (str, optional): Search term for filtering customers. Can be used to filter by name, email, or other customer attributes.
    """

    limit: int
    search: str
