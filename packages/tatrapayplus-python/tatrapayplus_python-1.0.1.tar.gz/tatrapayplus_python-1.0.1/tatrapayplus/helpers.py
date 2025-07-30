import json
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any, Optional, Union
from urllib.parse import parse_qsl

from requests import Response

from tatrapayplus.enums import SimpleStatus
from tatrapayplus.models.bank_transfer_status import BankTransferStatus
from tatrapayplus.models.card_pay_status import CardPayStatus
from tatrapayplus.models.card_pay_status_structure import CardPayStatusStructure
from tatrapayplus.models.comfort_pay_status import ComfortPayStatus
from tatrapayplus.models.pay_later_status import PayLaterStatus
from tatrapayplus.models.payment_intent_status_response import (
    PaymentIntentStatusResponse,
)
from tatrapayplus.models.payment_method import PaymentMethod

AMEX = "AMEX"
DISCOVER = "Discover"
MASTERCARD = "MasterCard"
VISA = "Visa"
UNKNOWN = "Unknown"

# Card number constants
AMEX_2 = ("34", "37")
MASTERCARD_2 = ("51", "52", "53", "54", "55")
DISCOVER_2 = ("65",)
DISCOVER_4 = ("6011",)
VISA_1 = ("4",)


def identify_card_type(card_num: Union[str, int]) -> str:
    card_type = UNKNOWN
    card_num = str(card_num)

    if len(card_num) == 15 and card_num[:2] in AMEX_2:
        card_type = AMEX
    elif len(card_num) == 16:
        if card_num[:2] in MASTERCARD_2:
            card_type = MASTERCARD
        elif card_num[:2] in DISCOVER_2 or card_num[:4] in DISCOVER_4:
            card_type = DISCOVER
        elif card_num[:1] in VISA_1:
            card_type = VISA
    elif len(card_num) == 13 and card_num[:1] in VISA_1:
        card_type = VISA

    return card_type


payment_method_statuses: dict[PaymentMethod, dict[str, list[Any]]] = {
    PaymentMethod.QR_PAY: {
        "capture": [BankTransferStatus.ACCC],
        "rejected": [BankTransferStatus.CANC, BankTransferStatus.RJCT],
        "authorized": [],
    },
    PaymentMethod.BANK_TRANSFER: {
        "capture": [BankTransferStatus.ACSC, BankTransferStatus.ACCC],
        "rejected": [BankTransferStatus.CANC, BankTransferStatus.RJCT],
        "authorized": [],
    },
    PaymentMethod.PAY_LATER: {
        "capture": [
            PayLaterStatus.LOAN_APPLICATION_FINISHED,
            PayLaterStatus.LOAN_DISBURSED,
        ],
        "rejected": [PayLaterStatus.CANCELED, PayLaterStatus.EXPIRED],
        "authorized": [],
    },
    PaymentMethod.CARD_PAY: {
        "capture": [CardPayStatus.OK, CardPayStatus.CB],
        "rejected": [CardPayStatus.FAIL],
        "authorized": [CardPayStatus.PA],
    },
    PaymentMethod.DIRECT_API: {
        "capture": [CardPayStatus.OK, CardPayStatus.CB],
        "rejected": [CardPayStatus.FAIL],
        "authorized": [],
    },
}


def get_simple_status(payment_status: PaymentIntentStatusResponse) -> SimpleStatus:
    if not payment_status or not payment_status.status:
        return SimpleStatus.PENDING

    status = payment_status.status
    plain_status: Any

    if isinstance(status, CardPayStatusStructure):
        plain_status = status.status
    elif isinstance(status, (BankTransferStatus, PayLaterStatus)):
        plain_status = status
    else:
        return SimpleStatus.PENDING

    method = payment_status.selected_payment_method
    if isinstance(method, PaymentMethod) and method in payment_method_statuses:
        if plain_status in payment_method_statuses[method]["authorized"]:
            return SimpleStatus.AUTHORIZED
        if plain_status in payment_method_statuses[method]["capture"]:
            return SimpleStatus.CAPTURE
        if plain_status in payment_method_statuses[method]["rejected"]:
            return SimpleStatus.REJECTED

    return SimpleStatus.PENDING


def get_saved_card_data(payment_status: PaymentIntentStatusResponse) -> dict[str, Any]:
    if payment_status.selected_payment_method != PaymentMethod.CARD_PAY or not isinstance(
        payment_status.status, CardPayStatusStructure
    ):
        return {}

    comfort_pay = payment_status.status.comfort_pay
    masked = payment_status.status.masked_card_number or None
    card_type = identify_card_type(masked) if masked else None

    saved_card_data: dict[str, Any] = {
        "masked_card_number": masked,
        "credit_card": card_type,
    }

    if comfort_pay and comfort_pay.status == ComfortPayStatus.OK and comfort_pay.cid:
        saved_card_data["cid"] = comfort_pay.cid

    return saved_card_data


def remove_diacritics(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = re.sub(r"[\u0300-\u036f]", "", s)
    s = re.sub(r"[^0-9a-zA-Z.@_ \-]", "", s)
    return s


def trim_and_remove_special_characters(s: str) -> str:
    return re.sub(r"[<>|`\\]", " ", s).strip()


def remove_special_characters_from_strings(obj: Any) -> Any:
    if isinstance(obj, str):
        return trim_and_remove_special_characters(obj)
    elif isinstance(obj, list):
        return [remove_special_characters_from_strings(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: remove_special_characters_from_strings(value) for key, value in obj.items()}
    return obj


class TatrapayPlusLogger:
    def __init__(self, mask_sensitive_data: bool = True) -> None:
        self.mask_sensitive_data = mask_sensitive_data
        self.mask_body_fields = ["client_id", "client_secret", "access_token"]
        self.mask_header_fields = ["Authorization"]

    @staticmethod
    def _mask_value(value: str, keep: int = 5) -> str:
        if not isinstance(value, str) or len(value) <= keep * 2:
            return "*" * len(value)
        return value[:keep] + "*" * (len(value) - (keep * 2)) + value[-keep:]

    def _mask_body(self, body: Any) -> str:
        if isinstance(body, bytes):
            body = json.loads(body.decode("utf-8"))

        if isinstance(body, str):
            try:
                pairs = parse_qsl(body)
                masked_pairs = [
                    f"{key}={self._mask_value(value) if key in self.mask_body_fields else value}"
                    for key, value in pairs
                ]
                return "&".join(masked_pairs)
            except Exception:
                return body

        if isinstance(body, dict):
            for key in self.mask_body_fields:
                if key in body:
                    body[key] = self._mask_value(str(body[key]))
            return json.dumps(body, indent=2, ensure_ascii=False)

        return str(body)

    def _mask_header(self, header: dict[str, Any]) -> dict[str, Any]:
        return {
            key: (self._mask_value(str(value)) if key in self.mask_header_fields else value)
            for key, value in header.items()
        }

    def log(
        self,
        response: Response,
        additional_response_data: Optional[dict[str, Any]] = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        readable_time = now.strftime("%Y-%m-%d %H:%M:%S")

        request = response.request
        request_data = self._mask_body(request.body) if self.mask_sensitive_data and request.body else request.body

        headers = (
            self._mask_header(dict(request.headers))
            if self.mask_sensitive_data and request.headers
            else request.headers
        )

        self.write_line(f"INFO [{readable_time}] [INFO] Request:")
        self.write_line(f"Method: {request.method}")
        self.write_line(f"URL: {request.url}")
        self.write_line("Headers:")
        self.write_line(json.dumps(headers, indent=2, ensure_ascii=False))
        if request_data:
            self.write_line("Body:")
            self.write_line(str(request_data))
        self.write_line("")

        status = response.status_code
        outcome = "success" if response.ok else "error"
        self.write_line(f"INFO [{readable_time}] [INFO] Response {outcome}(status: {status}):")

        try:
            response_body = response.json()
            if isinstance(response_body, dict) and additional_response_data:
                response_body.update(additional_response_data)

            response_body_masked = (
                self._mask_body(response_body) if response_body and self.mask_body_fields else response_body
            )
            self.write_line(response_body_masked)
        except Exception:
            self.write_line(response.text)

    def write_line(self, line: str) -> None:
        raise NotImplementedError("TatrapayPlusLogger subclass must implement write_line()")
