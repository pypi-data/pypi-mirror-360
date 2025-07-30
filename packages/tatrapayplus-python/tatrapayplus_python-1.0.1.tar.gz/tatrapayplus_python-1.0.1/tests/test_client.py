import os
import time
from unittest.mock import MagicMock, patch

import pytest
import responses

from tatrapayplus.client import TatrapayPlusToken, TBPlusSDK
from tatrapayplus.enums import Mode, SimpleStatus
from tatrapayplus.helpers import TatrapayPlusLogger
from tatrapayplus.models import (
    Address,
    AppearanceLogoRequest,
    AppearanceRequest,
    AppearanceRequestTheme,
    ApplePayToken,
    ApplePayTokenToken,
    ApplePayTokenTokenHeader,
    BasicCalculationRequest,
    BasicCalculationRequestPaymentMethod,
    CapacityInfo,
    CardDetail,
    CardDetailCardPayLangOverride,
    CardPayUpdateInstruction,
    CardPayUpdateInstructionOperationType,
    ColorAttribute,
    DirectTransactionTDSData,
    InitiateDirectTransactionRequest,
    ItemDetail,
    ItemDetailLangUnit,
    Order,
    OrderItem,
    PayLater,
    PaymentMethod,
    PaymentSymbols,
    RegisterForComfortPayObj,
    TransactionIPSPData,
    UserData,
)
from tatrapayplus.models.amount import Amount
from tatrapayplus.models.bank_transfer import BankTransfer
from tatrapayplus.models.base_payment import BasePayment
from tatrapayplus.models.initiate_payment_request import InitiatePaymentRequest


class TestLogger(TatrapayPlusLogger):
    def write_line(self, line):
        print(line)


@pytest.fixture
def tatrapay_client():
    return TBPlusSDK(
        client_id=os.environ["TATRAPAY_CLIENT_ID"],
        client_secret=os.environ["TATRAPAY_CLIENT_SECRET"],
        mode=Mode.SANDBOX,
        logger=TestLogger(),
    )


def get_minimal_payment_data():
    return InitiatePaymentRequest(
        base_payment=BasePayment(
            instructed_amount=Amount(
                amount_value=120,
                currency="EUR",
            ),
            end_to_end="ORDER123456",
        ),
        bank_transfer=BankTransfer(),
    )


def test_create_minimal_payment(tatrapay_client):
    payment_response = tatrapay_client.create_payment(
        request=get_minimal_payment_data(),
        redirect_uri="https://tatrabanka.sk/",
        ip_address="127.0.0.1",
    )
    assert payment_response.payment_id is not None


def test_create_full_payment(tatrapay_client):
    payment_data = InitiatePaymentRequest(
        base_payment=BasePayment(
            instructed_amount=Amount(
                amount_value=10.0,
                currency="EUR",
            ),
            end_to_end="ORDER123456",
        ),
        bank_transfer=BankTransfer(),
        pay_later=PayLater(
            order=Order(
                order_no="ORDER123456",
                order_items=[
                    OrderItem(
                        quantity=1,
                        total_item_price=10.0,
                        item_detail=ItemDetail(
                            item_detail_sk=ItemDetailLangUnit(
                                item_name="Testovací produkt",
                                item_description="Popis produktu",
                            ),
                            item_detail_en=ItemDetailLangUnit(
                                item_name="Test Product",
                                item_description="Product description",
                            ),
                        ),
                        item_info_url="https://tatrabanka.sk",
                    )
                ],
                preferred_loan_duration=12,
                down_payment=1.0,
            ),
            capacity_info=CapacityInfo(
                monthly_income=2000.0,
                monthly_expenses=800.0,
                number_of_children=1,
            ),
        ),
        card_detail=CardDetail(
            card_pay_lang_override=CardDetailCardPayLangOverride.SK,
            is_pre_authorization=True,
            card_holder="Janko Hruška",
            billing_address=Address(
                street_name="Hlavná Ulica",
                building_number="123",
                town_name="Bratislava",
                post_code="81101",
                country="SK",
            ),
            shipping_address=Address(
                street_name="Hlavna Ulica",
                building_number="123",
                town_name="Bratislava",
                post_code="81101",
                country="SK",
            ),
            comfort_pay=RegisterForComfortPayObj(register_for_comfort_pay=True),
        ),
        user_data=UserData(
            first_name="Janko",
            last_name="Hruska",
            email="janko.hruska@example.com",
        ),
    )

    payment_response = tatrapay_client.create_payment(
        request=payment_data,
        redirect_uri="https://tatrabanka.sk/",
        ip_address="127.0.0.1",
    )

    assert payment_response.payment_id is not None


def test_create_direct_payment(tatrapay_client):
    payment_data = InitiateDirectTransactionRequest(
        amount=Amount(
            amount_value=30.0,
            currency="EUR",
        ),
        end_to_end=PaymentSymbols(
            variable_symbol="123456",
            specific_symbol="0244763",
            constant_symbol="389",
        ),
        is_pre_authorization=True,
        tds_data=DirectTransactionTDSData(
            card_holder="Janko Hruška",
            email="janko.hruska@example.com",
            phone="+421900000000",
            billing_address=Address(
                street_name="Ulica",
                building_number="35",
                town_name="Bratislava",
                post_code="81101",
                country="SK",
            ),
            shipping_address=Address(
                street_name="Ulica",
                building_number="35",
                town_name="Bratislava",
                post_code="81101",
                country="SK",
            ),
        ),
        ipsp_data=TransactionIPSPData(
            sub_merchant_id="5846864684",
            name="Test Predajca",
            location="Bratislava",
            country="SK",
        ),
        token=ApplePayToken(
            token=ApplePayTokenToken(
                header=ApplePayTokenTokenHeader(
                    ephemeral_public_key="MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAELAfD...",
                    public_key_hash="LjAAyv6vb6jOEkjfG7L1a5OR2uCTHIkB61DaYdEWD",
                    transaction_id="0c4352c073ad460044517596dbbf8fe503a837138c8c2de18fddb37ca3ec5295",
                ),
                data="M8i9PNK4yXtKO3xmOn6uyYOWmQ+iX9...",
                signature="bNEa18hOrgG/oFk/o0CtYR01vhm+34RbStas1T+tkFLpP0eG5A+...",
                version="EC_v1",
            )
        ),
    )

    payment_response = tatrapay_client.create_payment_direct(
        request=payment_data,
        redirect_uri="https://tatrabanka.sk/",
        ip_address="127.0.0.1",
    )

    assert payment_response.payment_id is not None


def test_get_payment_methods(tatrapay_client):
    response = tatrapay_client.get_payment_methods()
    assert response.payment_methods is not None


def test_get_available_payment_methods(tatrapay_client):
    expected_methods = {
        PaymentMethod.BANK_TRANSFER,
        PaymentMethod.CARD_PAY,
        PaymentMethod.QR_PAY,
        PaymentMethod.DIRECT_API,
    }
    response = tatrapay_client.get_available_payment_methods("EUR", "SK", 10)

    assert expected_methods.issubset([p.payment_method for p in response])


def test_cancel_payment(tatrapay_client):
    cancel_payment_response = tatrapay_client.cancel_payment(
        tatrapay_client.create_payment(
            request=get_minimal_payment_data(),
            redirect_uri="https://tatrabanka.sk/",
            ip_address="127.0.0.1",
        ).payment_id
    )
    assert cancel_payment_response.ok


@patch("tatrapayplus.client.requests.Session.patch")
def test_update_payment_mocked(mock_request, tatrapay_client):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.ok = True
    mock_request.return_value = mock_response

    update_data = CardPayUpdateInstruction(
        operation_type=CardPayUpdateInstructionOperationType.CHARGEBACK,
        amount=120,
    )
    payment_update_response = tatrapay_client.update_payment("123", update_data)
    assert payment_update_response.ok


def test_get_payment_status(tatrapay_client):
    payment_status = tatrapay_client.get_payment_status(
        tatrapay_client.create_payment(
            request=get_minimal_payment_data(),
            redirect_uri="https://tatrabanka.sk/",
            ip_address="127.0.0.1",
        ).payment_id
    )
    assert payment_status is not None


def test_set_appearance(tatrapay_client):
    appearance_data = AppearanceRequest(
        theme=AppearanceRequestTheme.SYSTEM,
        surface_accent=ColorAttribute(color_dark_mode="#fff", color_light_mode="#fff"),
        tint_accent=ColorAttribute(color_dark_mode="#fff", color_light_mode="#fff"),
        tint_on_accent=ColorAttribute(color_dark_mode="#fff", color_light_mode="#fff"),
    )
    response = tatrapay_client.set_appearance(appearance_data)
    assert response.ok


@patch("tatrapayplus.client.requests.Session.post")
def test_set_appearance_logo_mocked(mock_request, tatrapay_client):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.ok = True
    mock_request.return_value = mock_response

    tatrapay_client.token = TatrapayPlusToken("123", expires_in=int(time.time() + 3600))

    logo_data = AppearanceLogoRequest(
        logo_image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII",
    )

    response = tatrapay_client.set_appearance_logo(logo_data)

    assert response.ok


@patch("tatrapayplus.client.requests.Session.get")
def test_saved_card_and_simple_status_data_mocked(mock_request, tatrapay_client):
    mocked_status_response = {
        "selectedPaymentMethod": "CARD_PAY",
        "authorizationStatus": "AUTH_DONE",
        "status": {
            "status": "OK",
            "currency": "EUR",
            "maskedCardNumber": "440577******5558",
            "comfortPay": {"cid": "123", "status": "OK"},
        },
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.ok = True
    mock_response.json.return_value = mocked_status_response

    mock_request.return_value = mock_response

    response = tatrapay_client.get_payment_status("123")

    assert response["simple_status"] == SimpleStatus.CAPTURE
    assert response["saved_card"]["credit_card"] == "Visa"
    assert response["saved_card"]["cid"] == "123"


@responses.activate
def test_retry_policy(tatrapay_client):
    url = "https://example.com/test"
    retry_count = 3

    for _ in range(retry_count):
        responses.add(responses.GET, url, status=500)
    responses.add(responses.GET, url, status=200, json={"success": True})

    response = tatrapay_client.session.get(url)

    assert response.status_code == 200
    assert len(responses.calls) == retry_count + 1


def test_precalculate_loan():
    tatrapay_client = TBPlusSDK(
        client_id=os.environ["TATRAPAY_CLIENT_ID"],
        client_secret=os.environ["TATRAPAY_CLIENT_SECRET"],
        mode=Mode.PRODUCTION,
        logger=TestLogger(),
    )

    loan_data = BasicCalculationRequest(
        loan_amount=250.45,
        payment_method=BasicCalculationRequestPaymentMethod.PAY_LATER,
        capacity_info=CapacityInfo(
            monthly_income=2000.0,
            monthly_expenses=800.0,
            number_of_children=1,
        ),
    )
    loan_offers = tatrapay_client.precalculate_loan(
        request=loan_data,
        ip_address="127.0.0.1",
    )

    for loan_offer in loan_offers:
        assert loan_offer.loan_duration is not None
        assert loan_offer.loan_interest_rate is not None
        assert loan_offer.total_amount is not None
        assert loan_offer.preference is not None
        assert loan_offer.installment_amount is not None
        assert loan_offer.main_preference is not None
        assert loan_offer.rpmn is not None
        assert loan_offer.loan_fee is not None
