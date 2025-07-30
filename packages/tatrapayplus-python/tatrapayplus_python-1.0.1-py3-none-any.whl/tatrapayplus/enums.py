from enum import Enum


class Scope(str, Enum):
    TATRAPAYPLUS = "TATRAPAYPLUS"


class Urls:
    SANDBOX = "https://api.tatrabanka.sk/tatrapayplus/sandbox"
    PRODUCTION = "https://api.tatrabanka.sk/tatrapayplus/production"
    AUTH_ENDPOINT = "/auth/oauth/v2/token"
    PAYMENTS = "/v1/payments"
    DIRECT_PAYMENT = "/v1/payments-direct"
    PAYMENT_METHODS = PAYMENTS + "/methods"
    STATUS = "/status"
    APPEARANCES = "/v1/appearances"
    APPEARANCE_LOGO = APPEARANCES + "/logo"
    LOAN_PRECALCULATION = "/v1/payments/loans/precalculation"


class SimpleStatus(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    PENDING = "PENDING"
    CAPTURE = "CAPTURE"
    REJECTED = "REJECTED"


class Mode(str, Enum):
    PRODUCTION = "PRODUCTION"
    SANDBOX = "SANDBOX"
