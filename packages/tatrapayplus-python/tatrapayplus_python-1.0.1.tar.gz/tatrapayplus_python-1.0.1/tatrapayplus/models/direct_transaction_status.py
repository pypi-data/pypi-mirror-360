from enum import Enum


class DirectTransactionStatus(str, Enum):
    FAIL = "FAIL"
    OK = "OK"
    TDS_AUTH_REQUIRED = "TDS_AUTH_REQUIRED"

    def __str__(self) -> str:
        return str(self.value)
