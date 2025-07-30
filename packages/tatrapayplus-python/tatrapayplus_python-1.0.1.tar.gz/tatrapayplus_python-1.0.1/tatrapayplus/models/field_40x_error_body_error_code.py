from enum import Enum


class Field40XErrorBodyErrorCode(str, Enum):
    NOT_ALLOWED_OPER = "NOT_ALLOWED_OPER"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    TOKEN_UNKNOWN = "TOKEN_UNKNOWN"

    def __str__(self) -> str:
        return str(self.value)
