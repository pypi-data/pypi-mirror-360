from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RegisterForComfortPayObj")


@_attrs_define
class RegisterForComfortPayObj:
    """
    Attributes:
        register_for_comfort_pay (Union[Unset, bool]): Flag to register the card for ComfortPay
    """

    register_for_comfort_pay: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        register_for_comfort_pay = self.register_for_comfort_pay

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if register_for_comfort_pay is not UNSET:
            field_dict["registerForComfortPay"] = register_for_comfort_pay

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        register_for_comfort_pay = d.pop("registerForComfortPay", UNSET)

        register_for_comfort_pay_obj = cls(
            register_for_comfort_pay=register_for_comfort_pay,
        )

        register_for_comfort_pay_obj.additional_properties = d
        return register_for_comfort_pay_obj

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
