from enum import Enum


class CardDetailCardPayLangOverride(str, Enum):
    CZ = "CZ"
    DE = "DE"
    EN = "EN"
    ES = "ES"
    FR = "FR"
    HU = "HU"
    IT = "IT"
    PL = "PL"
    SK = "SK"

    def __str__(self) -> str:
        return str(self.value)
