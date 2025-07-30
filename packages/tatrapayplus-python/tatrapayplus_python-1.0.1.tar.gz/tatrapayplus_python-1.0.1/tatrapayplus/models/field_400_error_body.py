from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.field_400_error_body_error_code import Field400ErrorBodyErrorCode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.available_payment_method import AvailablePaymentMethod


T = TypeVar("T", bound="Field400ErrorBody")


@_attrs_define
class Field400ErrorBody:
    """
    Attributes:
        error_code (Union[Unset, Field400ErrorBodyErrorCode]):
        error_description (Union[Unset, str]):
        available_payment_methods (Union[Unset, list['AvailablePaymentMethod']]): Reason codes of declined methods
    """

    error_code: Union[Unset, Field400ErrorBodyErrorCode] = UNSET
    error_description: Union[Unset, str] = UNSET
    available_payment_methods: Union[Unset, list["AvailablePaymentMethod"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error_code: Union[Unset, str] = UNSET
        if not isinstance(self.error_code, Unset):
            error_code = self.error_code.value

        error_description = self.error_description

        available_payment_methods: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.available_payment_methods, Unset):
            available_payment_methods = []
            for available_payment_methods_item_data in self.available_payment_methods:
                available_payment_methods_item = available_payment_methods_item_data.to_dict()
                available_payment_methods.append(available_payment_methods_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if error_code is not UNSET:
            field_dict["errorCode"] = error_code
        if error_description is not UNSET:
            field_dict["errorDescription"] = error_description
        if available_payment_methods is not UNSET:
            field_dict["availablePaymentMethods"] = available_payment_methods

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.available_payment_method import AvailablePaymentMethod

        d = dict(src_dict)
        _error_code = d.pop("errorCode", UNSET)
        error_code: Union[Unset, Field400ErrorBodyErrorCode]
        if isinstance(_error_code, Unset):
            error_code = UNSET
        else:
            error_code = Field400ErrorBodyErrorCode(_error_code)

        error_description = d.pop("errorDescription", UNSET)

        available_payment_methods = []
        _available_payment_methods = d.pop("availablePaymentMethods", UNSET)
        for available_payment_methods_item_data in _available_payment_methods or []:
            available_payment_methods_item = AvailablePaymentMethod.from_dict(available_payment_methods_item_data)

            available_payment_methods.append(available_payment_methods_item)

        field_400_error_body = cls(
            error_code=error_code,
            error_description=error_description,
            available_payment_methods=available_payment_methods,
        )

        field_400_error_body.additional_properties = d
        return field_400_error_body

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
