from typing import Optional, Dict, Any, Literal, TypedDict
from modempay.types.payment_intent import PaymentGateway
from modempay.types.customer import Customer


class Transaction(TypedDict):
    """
    Represents a transaction in the payment system.
    """

    id: str
    payment_intent_id: str
    amount: float
    currency: str
    status: Literal["pending", "completed", "failed", "refunded", "cancelled"]
    type: Literal["payment", "subscription", "invoice"]
    transaction_reference: str
    payment_account: str
    payment_method: str
    customer_name: str
    customer_phone: str
    customer_email: str
    account_id: str
    business_id: str
    createdAt: str
    updatedAt: str
    custom_fields_values: Dict[str, Any]
    metadata: Dict[str, Any]
    PaymentGateway: PaymentGateway
    Customer: Optional[Customer]


class TransactionListOption(TypedDict, total=False):
    """
    Options for listing transactions.

    Attributes:
        limit (Optional[int]): Maximum number of transactions to retrieve in a single request.
        search (Optional[str]): Search term for filtering transactions. Can be used to filter by currency, reference, payment method, or customer.
        timeframe (Optional[int]): Duration in minutes to filter transactions within a specific timeframe.
    """

    limit: Optional[int]
    search: Optional[str]
    timeframe: Optional[int]
