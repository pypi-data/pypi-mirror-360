from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bank_transfer import BankTransfer
    from ..models.base_payment import BasePayment
    from ..models.card_detail import CardDetail
    from ..models.pay_later import PayLater
    from ..models.user_data import UserData


T = TypeVar("T", bound="InitiatePaymentRequest")


@_attrs_define
class InitiatePaymentRequest:
    """Body for payment initiation

    Attributes:
        base_payment (BasePayment): Common instruction detail
        user_data (Union[Unset, UserData]):
        bank_transfer (Union[Unset, BankTransfer]): Bank transder attributes
        card_detail (Union[Unset, CardDetail]): Card pay information
        pay_later (Union[Unset, PayLater]):
    """

    base_payment: "BasePayment"
    user_data: Union[Unset, "UserData"] = UNSET
    bank_transfer: Union[Unset, "BankTransfer"] = UNSET
    card_detail: Union[Unset, "CardDetail"] = UNSET
    pay_later: Union[Unset, "PayLater"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base_payment = self.base_payment.to_dict()

        user_data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.user_data, Unset):
            user_data = self.user_data.to_dict()

        bank_transfer: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.bank_transfer, Unset):
            bank_transfer = self.bank_transfer.to_dict()

        card_detail: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.card_detail, Unset):
            card_detail = self.card_detail.to_dict()

        pay_later: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.pay_later, Unset):
            pay_later = self.pay_later.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "basePayment": base_payment,
            }
        )
        if user_data is not UNSET:
            field_dict["userData"] = user_data
        if bank_transfer is not UNSET:
            field_dict["bankTransfer"] = bank_transfer
        if card_detail is not UNSET:
            field_dict["cardDetail"] = card_detail
        if pay_later is not UNSET:
            field_dict["payLater"] = pay_later

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bank_transfer import BankTransfer
        from ..models.base_payment import BasePayment
        from ..models.card_detail import CardDetail
        from ..models.pay_later import PayLater
        from ..models.user_data import UserData

        d = dict(src_dict)
        base_payment = BasePayment.from_dict(d.pop("basePayment"))

        _user_data = d.pop("userData", UNSET)
        user_data: Union[Unset, UserData]
        if isinstance(_user_data, Unset):
            user_data = UNSET
        else:
            user_data = UserData.from_dict(_user_data)

        _bank_transfer = d.pop("bankTransfer", UNSET)
        bank_transfer: Union[Unset, BankTransfer]
        if isinstance(_bank_transfer, Unset):
            bank_transfer = UNSET
        else:
            bank_transfer = BankTransfer.from_dict(_bank_transfer)

        _card_detail = d.pop("cardDetail", UNSET)
        card_detail: Union[Unset, CardDetail]
        if isinstance(_card_detail, Unset):
            card_detail = UNSET
        else:
            card_detail = CardDetail.from_dict(_card_detail)

        _pay_later = d.pop("payLater", UNSET)
        pay_later: Union[Unset, PayLater]
        if isinstance(_pay_later, Unset):
            pay_later = UNSET
        else:
            pay_later = PayLater.from_dict(_pay_later)

        initiate_payment_request = cls(
            base_payment=base_payment,
            user_data=user_data,
            bank_transfer=bank_transfer,
            card_detail=card_detail,
            pay_later=pay_later,
        )

        initiate_payment_request.additional_properties = d
        return initiate_payment_request

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
