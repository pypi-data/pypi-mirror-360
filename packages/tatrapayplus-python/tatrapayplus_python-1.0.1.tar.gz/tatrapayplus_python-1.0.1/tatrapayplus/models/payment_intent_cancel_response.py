from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.payment_method import PaymentMethod
from ..types import UNSET, Unset

T = TypeVar("T", bound="PaymentIntentCancelResponse")


@_attrs_define
class PaymentIntentCancelResponse:
    """
    **TatraPayPlus cancel response. **

        Attributes:
            selected_payment_method (Union[Unset, PaymentMethod]): TatraPayPlus enumaration
    """

    selected_payment_method: Union[Unset, PaymentMethod] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        selected_payment_method: Union[Unset, str] = UNSET
        if not isinstance(self.selected_payment_method, Unset):
            selected_payment_method = self.selected_payment_method.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if selected_payment_method is not UNSET:
            field_dict["selectedPaymentMethod"] = selected_payment_method

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _selected_payment_method = d.pop("selectedPaymentMethod", UNSET)
        selected_payment_method: Union[Unset, PaymentMethod]
        if isinstance(_selected_payment_method, Unset):
            selected_payment_method = UNSET
        else:
            selected_payment_method = PaymentMethod(_selected_payment_method)

        payment_intent_cancel_response = cls(
            selected_payment_method=selected_payment_method,
        )

        payment_intent_cancel_response.additional_properties = d
        return payment_intent_cancel_response

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
