from enum import Enum


class PaymentIntentStatusResponseAuthorizationStatus(str, Enum):
    AUTH_DONE = "AUTH_DONE"
    AUTH_FAILED = "AUTH_FAILED"
    CANCELLED_BY_TPP = "CANCELLED_BY_TPP"
    CANCELLED_BY_USER = "CANCELLED_BY_USER"
    EXPIRED = "EXPIRED"
    NEW = "NEW"
    PAY_METHOD_SELECTED = "PAY_METHOD_SELECTED"

    def __str__(self) -> str:
        return str(self.value)
