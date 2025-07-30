from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.bank_transfer_status import BankTransferStatus
from ..models.pay_later_status import PayLaterStatus
from ..models.payment_intent_status_response_authorization_status import PaymentIntentStatusResponseAuthorizationStatus
from ..models.payment_method import PaymentMethod
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.card_pay_status_structure import CardPayStatusStructure


T = TypeVar("T", bound="PaymentIntentStatusResponse")


@_attrs_define
class PaymentIntentStatusResponse:
    """
    **TatraPayPlus status response. For each payment method will be sent specific status structure**

    | selectedPaymentMethod      | status structure | description|
    | ---------------- | ------------| ------------|
    | BANK_TRANSFER              | bankTransferStatus     ||
    | QR_PAY                   | bankTransferStatus     | Only ACCC is provided. Status will be provided as soon as
    amount is in target account |
    | CARD_PAY              | cardPayStatusStructure ||
    | PAY_LATER               | payLaterStatus ||
    | DIRECT_API               | cardPayStatusStructure ||

        Attributes:
            authorization_status (PaymentIntentStatusResponseAuthorizationStatus): Status of payment intent authorization
                progress. Be aware, It doesnt indicate payment status! To get payment status see attribute status.
            selected_payment_method (Union[Unset, PaymentMethod]): TatraPayPlus enumaration
            status (Union['CardPayStatusStructure', BankTransferStatus, PayLaterStatus, Unset]):
    """

    authorization_status: PaymentIntentStatusResponseAuthorizationStatus
    selected_payment_method: Union[Unset, PaymentMethod] = UNSET
    status: Union["CardPayStatusStructure", BankTransferStatus, PayLaterStatus, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.card_pay_status_structure import CardPayStatusStructure

        authorization_status = self.authorization_status.value

        selected_payment_method: Union[Unset, str] = UNSET
        if not isinstance(self.selected_payment_method, Unset):
            selected_payment_method = self.selected_payment_method.value

        status: Union[Unset, dict[str, Any], str]
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, CardPayStatusStructure):
            status = self.status.to_dict()
        elif isinstance(self.status, BankTransferStatus):
            status = self.status.value
        else:
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authorizationStatus": authorization_status,
            }
        )
        if selected_payment_method is not UNSET:
            field_dict["selectedPaymentMethod"] = selected_payment_method
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.card_pay_status_structure import CardPayStatusStructure

        d = dict(src_dict)
        authorization_status = PaymentIntentStatusResponseAuthorizationStatus(d.pop("authorizationStatus"))

        _selected_payment_method = d.pop("selectedPaymentMethod", UNSET)
        selected_payment_method: Union[Unset, PaymentMethod]
        if isinstance(_selected_payment_method, Unset):
            selected_payment_method = UNSET
        else:
            selected_payment_method = PaymentMethod(_selected_payment_method)

        def _parse_status(data: object) -> Union["CardPayStatusStructure", BankTransferStatus, PayLaterStatus, Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                status_type_0 = CardPayStatusStructure.from_dict(data)

                return status_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_1 = BankTransferStatus(data)

                return status_type_1
            except:  # noqa: E722
                pass
            if not isinstance(data, str):
                raise TypeError()
            status_type_2 = PayLaterStatus(data)

            return status_type_2

        status = _parse_status(d.pop("status", UNSET))

        payment_intent_status_response = cls(
            authorization_status=authorization_status,
            selected_payment_method=selected_payment_method,
            status=status,
        )

        payment_intent_status_response.additional_properties = d
        return payment_intent_status_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
