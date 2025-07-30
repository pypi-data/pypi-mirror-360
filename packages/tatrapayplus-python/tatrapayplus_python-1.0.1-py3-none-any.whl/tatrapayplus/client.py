import time
import uuid
from base64 import b64encode
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Optional, Union

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from tatrapayplus.enums import Mode, Scope, Urls
from tatrapayplus.errors import TatrapayPlusApiException
from tatrapayplus.helpers import (
    TatrapayPlusLogger,
    get_saved_card_data,
    get_simple_status,
    remove_diacritics,
    remove_special_characters_from_strings,
    trim_and_remove_special_characters,
)
from tatrapayplus.models import (
    BasicCalculationRequest,
    BasicCalculationResponseItem,
    Field40XErrorBody,
    Field400ErrorBody,
    GetAccessTokenResponse400,
)
from tatrapayplus.models.appearance_logo_request import AppearanceLogoRequest
from tatrapayplus.models.appearance_request import AppearanceRequest
from tatrapayplus.models.card_pay_update_instruction import CardPayUpdateInstruction
from tatrapayplus.models.initiate_direct_transaction_request import (
    InitiateDirectTransactionRequest,
)
from tatrapayplus.models.initiate_direct_transaction_response import (
    InitiateDirectTransactionResponse,
)
from tatrapayplus.models.initiate_payment_request import InitiatePaymentRequest
from tatrapayplus.models.initiate_payment_response import InitiatePaymentResponse
from tatrapayplus.models.payment_intent_status_response import (
    PaymentIntentStatusResponse,
)
from tatrapayplus.models.payment_method_rules import PaymentMethodRules
from tatrapayplus.models.payment_methods_list_response import PaymentMethodsListResponse


class TatrapayPlusToken:
    def __init__(self, token: str, expires_in: int) -> None:
        self.token = token
        self.expires_in = expires_in + time.time()

    def is_expired(self) -> bool:
        return time.time() >= self.expires_in

    def __str__(self) -> str:
        return self.token


class TBPlusSDK:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: Scope = Scope.TATRAPAYPLUS,
        mode: Mode = Mode.SANDBOX,
        logger: Optional[TatrapayPlusLogger] = None,
    ) -> None:
        self.logger = logger
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        if mode == Mode.PRODUCTION:
            self.base_url = Urls.PRODUCTION
        else:
            self.base_url = Urls.SANDBOX
        self.token: Optional[TatrapayPlusToken] = None
        self.session = self.init_session()

    @staticmethod
    def init_session() -> requests.Session:
        session = requests.Session()

        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PATCH", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def handle_response(self, response: Response, loging: bool = True) -> Response:
        if loging:
            self.log(response)

        try:
            response.raise_for_status()
        except Exception as e:
            json_data = response.json()
            error_body: Union[None, Field400ErrorBody, GetAccessTokenResponse400, Field40XErrorBody] = None
            if Urls.AUTH_ENDPOINT in response.url:
                error_body = GetAccessTokenResponse400.from_dict(json_data)
            elif response.status_code == 400:
                error_body = Field400ErrorBody.from_dict(json_data)
            elif response.status_code < 500:
                error_body = Field40XErrorBody.from_dict(json_data)
            if error_body:
                raise TatrapayPlusApiException(error_body) from e

        return response

    def get_access_token(self) -> TatrapayPlusToken:
        token_url = f"{self.base_url}{Urls.AUTH_ENDPOINT}"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
        }
        response = self.handle_response(self.session.post(token_url, data=payload))
        data = response.json()

        return TatrapayPlusToken(
            token=data.get("access_token"),
            expires_in=data.get("expires_in", 0),
        )

    def get_default_headers(self) -> MutableMapping[str, Union[str, bytes]]:
        if not self.token or self.token.is_expired():
            self.token = self.get_access_token()

        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Request-ID": str(uuid.uuid4()),
        }

    def create_payment(
        self,
        request: InitiatePaymentRequest,
        redirect_uri: str,
        ip_address: str,
        language: str = "sk",
        preferred_method: Optional[str] = None,
    ) -> InitiatePaymentResponse:
        url = f"{self.base_url}{Urls.PAYMENTS}"
        self.session.headers = self.get_default_headers()
        self.session.headers["Redirect-URI"] = redirect_uri
        self.session.headers["Accept-Language"] = language.lower()
        self.session.headers["IP-Address"] = ip_address

        if preferred_method:
            self.session.headers["Preferred-Method"] = preferred_method

        cleaned_request = remove_special_characters_from_strings(request.to_dict())
        card_holder = cleaned_request.get("cardDetail", {}).get("cardHolder")
        if card_holder:
            cleaned_request["cardDetail"]["cardHolder"] = trim_and_remove_special_characters(
                remove_diacritics(card_holder)
            )

        response = self.handle_response(self.session.post(url, json=cleaned_request))
        return InitiatePaymentResponse.from_dict(response.json())

    def create_payment_direct(
        self,
        request: InitiateDirectTransactionRequest,
        redirect_uri: str,
        ip_address: str,
    ) -> InitiateDirectTransactionResponse:
        url = f"{self.base_url}{Urls.DIRECT_PAYMENT}"
        self.session.headers = self.get_default_headers()
        self.session.headers["Redirect-URI"] = redirect_uri
        self.session.headers["IP-Address"] = ip_address

        cleaned_request = remove_special_characters_from_strings(request.to_dict())
        card_holder = cleaned_request.get("tdsData", {}).get("cardHolder")
        if card_holder:
            cleaned_request["tdsData"]["cardHolder"] = trim_and_remove_special_characters(
                remove_diacritics(card_holder)
            )

        response = self.handle_response(self.session.post(url, json=cleaned_request))
        return InitiateDirectTransactionResponse.from_dict(response.json())

    def get_payment_methods(self) -> PaymentMethodsListResponse:
        self.session.headers = self.get_default_headers()
        url = f"{self.base_url}{Urls.PAYMENT_METHODS}"
        response = self.handle_response(self.session.get(url))
        return PaymentMethodsListResponse.from_dict(response.json())

    def get_payment_status(self, payment_id: str) -> dict[str, Any]:
        url = f"{self.base_url}{Urls.PAYMENTS}/{payment_id}{Urls.STATUS}"
        self.session.headers = self.get_default_headers()
        response = self.handle_response(self.session.get(url), loging=False)
        status = PaymentIntentStatusResponse.from_dict(response.json())
        helpers = {
            "simple_status": get_simple_status(status),
            "saved_card": get_saved_card_data(status),
        }
        self.log(response, helpers)
        return {"status": status, **helpers}

    def update_payment(self, payment_id: str, request: CardPayUpdateInstruction) -> Response:
        url = f"{self.base_url}{Urls.PAYMENTS}/{payment_id}"
        self.session.headers = self.get_default_headers()
        self.session.headers["Idempotency-Key"] = self.session.headers["X-Request-ID"]
        return self.handle_response(self.session.patch(url, json=request.to_dict()))

    def cancel_payment(self, payment_id: str) -> Response:
        url = f"{self.base_url}{Urls.PAYMENTS}/{payment_id}"
        self.session.headers = self.get_default_headers()
        return self.handle_response(self.session.delete(url))

    def get_available_payment_methods(
        self,
        currency_code: Optional[str] = None,
        country_code: Optional[str] = None,
        total_amount: Optional[float] = None,
    ) -> list[PaymentMethodRules]:
        response = self.get_payment_methods()
        available_methods: list[PaymentMethodRules] = []

        for method in response.payment_methods:
            if currency_code and method.supported_currency and currency_code not in list(method.supported_currency):
                continue

            if total_amount is not None and method.amount_range_rule:
                min_amount = method.amount_range_rule.min_amount or 0
                max_amount = method.amount_range_rule.max_amount or float("inf")
                if not (min_amount <= total_amount <= max_amount):
                    continue

            if country_code and method.supported_country and country_code not in list(method.supported_country):
                continue

            available_methods.append(method)

        return available_methods

    def set_appearance(self, request: AppearanceRequest) -> Response:
        url = f"{self.base_url}{Urls.APPEARANCES}"
        self.session.headers = self.get_default_headers()
        return self.handle_response(self.session.post(url, json=request.to_dict()))

    def set_appearance_logo(self, request: AppearanceLogoRequest) -> Response:
        url = f"{self.base_url}{Urls.APPEARANCE_LOGO}"
        self.session.headers = self.get_default_headers()
        return self.handle_response(self.session.post(url, json=request.to_dict()))

    def precalculate_loan(
        self, request: BasicCalculationRequest, ip_address: str
    ) -> list[BasicCalculationResponseItem]:
        loan_offers: list[BasicCalculationResponseItem] = []

        url = f"{self.base_url}{Urls.LOAN_PRECALCULATION}"
        self.session.headers = self.get_default_headers()
        self.session.headers["IP-Address"] = ip_address

        response = self.handle_response(self.session.put(url, json=request.to_dict()))
        for loan_item in response.json():
            loan_offers.append(BasicCalculationResponseItem.from_dict(loan_item))

        return loan_offers

    @staticmethod
    def generate_signed_card_id_from_cid(cid: str, public_key_content: Optional[str] = None) -> Optional[str]:
        if public_key_content is None:
            try:
                public_key_path = Path(__file__).parent / "../ECID_PUBLIC_KEY_2023.txt"
                public_key_content = public_key_path.read_text(encoding="utf-8")
            except Exception as e:
                print("Error reading public key file:", e)
                return None

        try:
            public_key = serialization.load_pem_public_key(
                public_key_content.encode("utf-8"),
                backend=default_backend(),
            )

            if not isinstance(public_key, RSAPublicKey):
                print("Public key is not an RSA public key.")
                return None

            encrypted = public_key.encrypt(
                cid.encode("utf-8"),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            base64_encoded = b64encode(encrypted).decode("utf-8")
            return "\n".join(base64_encoded[i : i + 64] for i in range(0, len(base64_encoded), 64))

        except Exception as e:
            print("Encryption error:", e)
            return None

    def log(
        self,
        response: Response,
        additional_response_data: Optional[dict[str, Any]] = None,
    ) -> None:
        if self.logger:
            self.logger.log(response, additional_response_data)
