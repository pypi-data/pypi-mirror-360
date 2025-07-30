from typing import Optional

from typing import Optional

from modempay.types.type import ModemPayConfig


class ModemPay:

    def __init__(self, api_key: str, config: Optional[ModemPayConfig] = None):
        if config is None:
            config = {"maxRetries": 3, "timeout": 60}
        self.api_key = api_key
        self.max_retries = config.get("maxRetries", 3)
        self.timeout = config.get("timeout", 60)

    @property
    def customers(self):
        if not hasattr(self, "_customers") or self._customers is None:
            from modempay.resources.customer import CustomersResource

            self._customers = CustomersResource(
                self.api_key, self.max_retries, self.timeout
            )
        return self._customers

    @property
    def payment_intents(self):
        if not hasattr(self, "_payment_intents") or self._payment_intents is None:
            from modempay.resources.payment_intent import PaymentIntentsResource

            self._payment_intents = PaymentIntentsResource(
                self.api_key, self.max_retries, self.timeout
            )
        return self._payment_intents

    @property
    def transfers(self):
        if not hasattr(self, "_transfers") or self._transfers is None:
            from modempay.resources.transfer import TransfersResource

            self._transfers = TransfersResource(
                self.api_key, self.max_retries, self.timeout
            )
        return self._transfers

    @property
    def transactions(self):
        if not hasattr(self, "_transactions") or self._transactions is None:
            from modempay.resources.transaction import TransactionsResource

            self._transactions = TransactionsResource(
                self.api_key, self.max_retries, self.timeout
            )
        return self._transactions

    @property
    def webhooks(self):
        if not hasattr(self, "_webhooks") or self._webhooks is None:
            from modempay.resources.webhook import WebhooksResource

            self._webhooks = WebhooksResource(
                self.api_key, self.max_retries, self.timeout
            )
        return self._webhooks
