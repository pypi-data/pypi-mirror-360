from enum import Enum


class CardPayUpdateInstructionOperationType(str, Enum):
    CANCEL_PRE_AUTHORIZATION = "CANCEL_PRE_AUTHORIZATION"
    CHARGEBACK = "CHARGEBACK"
    CONFIRM_PRE_AUTHORIZATION = "CONFIRM_PRE_AUTHORIZATION"

    def __str__(self) -> str:
        return str(self.value)
