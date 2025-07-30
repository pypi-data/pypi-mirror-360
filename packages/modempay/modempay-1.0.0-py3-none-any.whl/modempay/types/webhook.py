from typing import TypedDict, Literal, Dict, Any

EventType = Literal[
    "customer.created",
    "customer.updated",
    "customer.deleted",
    "payment_intent.created",
    "payment_intent.cancelled",
    "charge.cancelled",
    "charge.succeeded",
    "charge.created",
    "charge.updated",
    "charge.failed",
    "transfer.failed",
    "transfer.succeeded",
    "transfer.reversed",
]


class Event(TypedDict):
    """
    Represents an event in the payment system, triggered by specific actions or state changes.

    Attributes:
        event (EventType): The type of event (e.g., "customer.created", "payment_intent.created").
        payload (Dict[str, Any]): The payload data associated with the event.
    """

    event: EventType
    payload: Dict[str, Any]
