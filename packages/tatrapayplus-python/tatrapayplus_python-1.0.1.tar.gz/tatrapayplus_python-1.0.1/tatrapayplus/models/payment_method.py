from enum import Enum


class PaymentMethod(str, Enum):
    BANK_TRANSFER = "BANK_TRANSFER"
    CARD_PAY = "CARD_PAY"
    DIRECT_API = "DIRECT_API"
    PAY_LATER = "PAY_LATER"
    QR_PAY = "QR_PAY"

    def __str__(self) -> str:
        return str(self.value)
