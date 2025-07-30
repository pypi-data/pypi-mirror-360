from enum import Enum


class ComfortPayStatus(str, Enum):
    FAIL = "FAIL"
    OK = "OK"

    def __str__(self) -> str:
        return str(self.value)
