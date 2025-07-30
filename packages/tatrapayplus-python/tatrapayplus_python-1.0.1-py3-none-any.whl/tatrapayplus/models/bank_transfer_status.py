from enum import Enum


class BankTransferStatus(str, Enum):
    ACCC = "ACCC"
    ACCP = "ACCP"
    ACFC = "ACFC"
    ACSC = "ACSC"
    ACSP = "ACSP"
    ACTC = "ACTC"
    ACWC = "ACWC"
    ACWP = "ACWP"
    CANC = "CANC"
    PART = "PART"
    PATC = "PATC"
    PDNG = "PDNG"
    RCVD = "RCVD"
    RJCT = "RJCT"

    def __str__(self) -> str:
        return str(self.value)
