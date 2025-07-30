# Modem Pay Python SDK

The official Python SDK for integrating Modem Pay's payment services.

## Installation

Install the SDK using npm:

```bash
pip install modempay
```

## Quickstart

Initialize the SDK and authenticate with your API key:

```python
from modempay import ModemPay

modem_pay = ModemPay(
    api_key="your_api_key"
)

# Example: Create a payment intent
payment_intent = modem_pay.payment_intents.create(
    params={"amount": 1000, "currency": "GMD", "customer": "customer_id"}
)

print(payment_intent)
```

## Documentation

For detailed usage, visit the [Modem Pay Docs](https://docs.modempay.com).
