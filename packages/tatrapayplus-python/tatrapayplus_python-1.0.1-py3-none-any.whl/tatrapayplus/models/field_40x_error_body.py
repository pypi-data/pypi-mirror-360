from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.field_40x_error_body_error_code import Field40XErrorBodyErrorCode
from ..types import UNSET, Unset

T = TypeVar("T", bound="Field40XErrorBody")


@_attrs_define
class Field40XErrorBody:
    """
    Attributes:
        error_code (Field40XErrorBodyErrorCode):
        error_description (Union[Unset, str]):
    """

    error_code: Field40XErrorBodyErrorCode
    error_description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error_code = self.error_code.value

        error_description = self.error_description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "errorCode": error_code,
            }
        )
        if error_description is not UNSET:
            field_dict["errorDescription"] = error_description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        error_code = Field40XErrorBodyErrorCode(d.pop("errorCode"))

        error_description = d.pop("errorDescription", UNSET)

        field_40x_error_body = cls(
            error_code=error_code,
            error_description=error_description,
        )

        field_40x_error_body.additional_properties = d
        return field_40x_error_body

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
