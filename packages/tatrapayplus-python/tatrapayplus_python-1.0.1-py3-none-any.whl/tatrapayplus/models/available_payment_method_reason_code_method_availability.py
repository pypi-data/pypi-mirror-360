from enum import Enum


class AvailablePaymentMethodReasonCodeMethodAvailability(str, Enum):
    MANDATORY_STRUCTURE_NOT_PROVIDED = "MANDATORY_STRUCTURE_NOT_PROVIDED"
    NOT_FEASIBLE_CURRENCY = "NOT_FEASIBLE_CURRENCY"
    NO_CONTRACT = "NO_CONTRACT"
    OUT_OF_RANGE_AMOUNT = "OUT_OF_RANGE_AMOUNT"

    def __str__(self) -> str:
        return str(self.value)
