from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.available_payment_method_reason_code_method_availability import (
    AvailablePaymentMethodReasonCodeMethodAvailability,
)
from ..models.payment_method import PaymentMethod
from ..types import UNSET, Unset

T = TypeVar("T", bound="AvailablePaymentMethod")


@_attrs_define
class AvailablePaymentMethod:
    """
    Attributes:
        payment_method (PaymentMethod): TatraPayPlus enumaration
        is_available (bool): if true, method will be shown to user. Otherwise reasonCode will be provided
        reason_code_method_availability (Union[Unset, AvailablePaymentMethodReasonCodeMethodAvailability]): reason code.
            List of enumaration will be provided in documentation
        reason_code_method_availability_description (Union[Unset, str]): reason code description
    """

    payment_method: PaymentMethod
    is_available: bool
    reason_code_method_availability: Union[Unset, AvailablePaymentMethodReasonCodeMethodAvailability] = UNSET
    reason_code_method_availability_description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payment_method = self.payment_method.value

        is_available = self.is_available

        reason_code_method_availability: Union[Unset, str] = UNSET
        if not isinstance(self.reason_code_method_availability, Unset):
            reason_code_method_availability = self.reason_code_method_availability.value

        reason_code_method_availability_description = self.reason_code_method_availability_description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "paymentMethod": payment_method,
                "isAvailable": is_available,
            }
        )
        if reason_code_method_availability is not UNSET:
            field_dict["reasonCodeMethodAvailability"] = reason_code_method_availability
        if reason_code_method_availability_description is not UNSET:
            field_dict["reasonCodeMethodAvailabilityDescription"] = reason_code_method_availability_description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        payment_method = PaymentMethod(d.pop("paymentMethod"))

        is_available = d.pop("isAvailable")

        _reason_code_method_availability = d.pop("reasonCodeMethodAvailability", UNSET)
        reason_code_method_availability: Union[Unset, AvailablePaymentMethodReasonCodeMethodAvailability]
        if isinstance(_reason_code_method_availability, Unset):
            reason_code_method_availability = UNSET
        else:
            reason_code_method_availability = AvailablePaymentMethodReasonCodeMethodAvailability(
                _reason_code_method_availability
            )

        reason_code_method_availability_description = d.pop("reasonCodeMethodAvailabilityDescription", UNSET)

        available_payment_method = cls(
            payment_method=payment_method,
            is_available=is_available,
            reason_code_method_availability=reason_code_method_availability,
            reason_code_method_availability_description=reason_code_method_availability_description,
        )

        available_payment_method.additional_properties = d
        return available_payment_method

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
