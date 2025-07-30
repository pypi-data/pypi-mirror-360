from typing import Generic, TypeVar, TypedDict, List as PyList


class ListOption(TypedDict, total=False):
    """
    Options for listing resources, such as customers or transactions.

    Attributes:
        limit (int, optional): Maximum number of items to retrieve in a single request.
    """

    limit: int


class ModemPayConfig(TypedDict, total=False):
    """
    Configuration options for ModemPay.

    Attributes:
        maxRetries (Optional[int]): Maximum number of retry attempts for API requests in case of failure.
            If not specified, a default value may be used.
        timeout (Optional[int]): Request timeout in seconds. Defaults to 60 seconds (1 minute).
    """

    maxRetries: int
    timeout: int


T = TypeVar("T")


class ListMeta(TypedDict):
    total: int


class List(TypedDict, Generic[T]):
    data: PyList[T]
    meta: ListMeta
