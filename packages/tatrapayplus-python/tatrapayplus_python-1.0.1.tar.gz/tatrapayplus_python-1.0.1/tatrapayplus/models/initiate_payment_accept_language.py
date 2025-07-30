from enum import Enum


class InitiatePaymentAcceptLanguage(str, Enum):
    CZ = "cz"
    DE = "de"
    EN = "en"
    ES = "es"
    HU = "hu"
    PL = "pl"
    SK = "sk"

    def __str__(self) -> str:
        return str(self.value)
