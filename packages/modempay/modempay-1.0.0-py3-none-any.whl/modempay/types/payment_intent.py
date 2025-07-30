from typing import Literal, TypedDict, Optional, List, Dict, Any

from modempay.types.customer import Customer

PaymentMethodType = Literal["card", "bank", "wallet"]


class PaymentGateway(TypedDict):
    """
    Represents a payment gateway that can be used in a payment transaction.

    Attributes:
        tag (str): A unique tag identifying the payment gateway.
        group (str): The group to which this payment gateway belongs (e.g., "bank", "wallet", etc.).
        logo (str): The logo of the payment gateway, typically in URL form.
        id (str): Unique identifier for the payment gateway.
    """

    tag: str
    group: str
    logo: str
    id: str


class PaymentIntentParams(TypedDict, total=False):
    """
    Parameters for creating a payment intent.

    Attributes:
        amount (int): The amount to be charged for the payment intent.
        currency (Optional[str]): The currency in which the payment will be processed (e.g., "XOF", "GMD").
        payment_methods (Optional[List[PaymentMethodType]]): An array of payment method types to be used for processing the payment (e.g., "card", "bank", "wallet").
        title (Optional[str]): Title or name of the payment intent. It provides a label or description for the payment.
        description (Optional[str]): Detailed description of the payment intent.
        customer (Optional[str]): The customer associated with the payment intent. Can be a customer ID.
        customer_name (Optional[str]): The name of the customer associated with the payment intent.
        customer_email (Optional[str]): The email address of the customer associated with the payment intent.
        customer_phone (Optional[str]): The phone number of the customer associated with the payment intent.
        metadata (Optional[Dict[str, Any]]): Custom metadata associated with the payment intent.
        return_url (Optional[str]): URL to redirect the customer after successful payment.
        cancel_url (Optional[str]): URL to redirect the customer if the payment is cancelled.
        payment_method (Optional[str]): The payment method ID selected for processing the payment.
        coupon (Optional[str]): The ID of the coupon code to be applied to the payment intent for discounts or special offers.
        callback_url (Optional[str]): The URL to which Modem Pay will send a callback or webhook notification after payment processing.
    """

    amount: int
    currency: Optional[str]
    payment_methods: Optional[List[PaymentMethodType]]
    title: Optional[str]
    description: Optional[str]
    customer: Optional[str]
    customer_name: Optional[str]
    customer_email: Optional[str]
    customer_phone: Optional[str]
    metadata: Optional[Dict[str, Any]]
    return_url: Optional[str]
    cancel_url: Optional[str]
    payment_method: Optional[str]
    coupon: Optional[str]
    callback_url: Optional[str]


class PaymentIntent(TypedDict, total=False):
    """
    Representation of a payment intent.
    """

    # Inherits all fields from PaymentIntentParams
    id: str
    amount: int
    currency: Optional[str]
    payment_methods: Optional[List[PaymentMethodType]]
    title: Optional[str]
    description: Optional[str]
    customer: Optional[str]
    customer_name: Optional[str]
    customer_email: Optional[str]
    customer_phone: Optional[str]
    metadata: Optional[Dict[str, Any]]
    return_url: Optional[str]
    cancel_url: Optional[str]
    payment_method: Optional[str]
    coupon: Optional[str]
    callback_url: Optional[str]
    payment_method_options: List[PaymentGateway]
    Customer: Optional[Customer]
    intent_secret: str
    status: Literal[
        "initialized",
        "processing",
        "requires_payment_method",
        "successful",
        "failed",
        "cancelled",
    ]
    link: str
    custom_fields_values: Dict[str, Any]
    is_session: bool


class PaymentIntentResponseData(TypedDict):
    """
    The data associated with the created payment intent.
    """

    intent_secret: str
    payment_link: str
    amount: int
    currency: str
    expires_at: str
    status: str


class PaymentIntentResponse(TypedDict):
    """
    Represents the structure of the response returned after creating a payment intent.
    """

    status: bool
    message: str
    data: PaymentIntentResponseData
