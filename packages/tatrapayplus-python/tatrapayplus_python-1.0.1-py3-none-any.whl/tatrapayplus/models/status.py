from enum import Enum


class Status(str, Enum):
    NO_OFFER = "NO_OFFER"
    OFFER = "OFFER"
    OPEN = "OPEN"
    PROCESSING = "PROCESSING"

    def __str__(self) -> str:
        return str(self.value)
