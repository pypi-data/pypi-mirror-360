from typing import TypedDict, Optional, Literal, Dict, Any


class TransferParams(TypedDict, total=False):
    """
    Parameters for initiating a transfer.
    """

    amount: int
    currency: str
    narration: Optional[str]
    network: str
    beneficiary_name: str
    metadata: Optional[Dict[str, Any]]
    account_number: str


class Transfer(TypedDict, total=False):
    """
    Representation of a transfer transaction.
    """

    id: str
    business_id: str
    account_id: str
    merchant_id: Optional[str]
    recipient_business_id: Optional[str]
    amount: int
    fee: int
    currency: str
    type: Literal["self", "modem-pay", "mobile-money", "bank"]
    status: Literal["pending", "completed", "failed", "cancelled"]
    balance_before: int
    balance_after: int
    account_name: Optional[str]
    network: Optional[str]
    bank: Optional[str]
    amount_received: Optional[int]
    mobile_number: Optional[str]
    account_number: Optional[str]
    transfer_reference: str
    test_mode: bool
    events: Dict[str, Any]
    note: Optional[str]
    otp: Optional[str]
    metadata: Dict[str, Any]


class TransferFeeCheckParams(TypedDict):
    """
    Parameters for checking transfer fee.
    """

    amount: int
    currency: str
    network: str


class TransferFeeCheckResponse(TypedDict):
    """
    Response for transfer fee check.
    """

    fee: int
    currency: str
    network: str
    amount: int
