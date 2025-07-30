from enum import Enum


class BasicCalculationRequestPaymentMethod(str, Enum):
    PAY_LATER = "PAY_LATER"

    def __str__(self) -> str:
        return str(self.value)
