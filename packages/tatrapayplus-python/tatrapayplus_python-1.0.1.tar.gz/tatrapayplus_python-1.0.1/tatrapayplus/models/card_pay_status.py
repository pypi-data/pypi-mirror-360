from enum import Enum


class CardPayStatus(str, Enum):
    AUTH_CANCELED = "AUTH_CANCELED"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    CB = "CB"
    CPA = "CPA"
    FAIL = "FAIL"
    INIT = "INIT"
    OK = "OK"
    PA = "PA"
    SPA = "SPA"
    XPA = "XPA"

    def __str__(self) -> str:
        return str(self.value)
