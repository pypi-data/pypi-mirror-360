from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Provider")


@_attrs_define
class Provider:
    """Data provider

    Attributes:
        country_code (str): ISO 3166 ALPHA2 country code. Example: SE.
        provider_name (str):  Example: Dummie bank.
        provider_code (str):
        swift_code (str): BICFI
             Example: AAAADEBBXXX.
    """

    country_code: str
    provider_name: str
    provider_code: str
    swift_code: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        country_code = self.country_code

        provider_name = self.provider_name

        provider_code = self.provider_code

        swift_code = self.swift_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "countryCode": country_code,
                "providerName": provider_name,
                "providerCode": provider_code,
                "swiftCode": swift_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        country_code = d.pop("countryCode")

        provider_name = d.pop("providerName")

        provider_code = d.pop("providerCode")

        swift_code = d.pop("swiftCode")

        provider = cls(
            country_code=country_code,
            provider_name=provider_name,
            provider_code=provider_code,
            swift_code=swift_code,
        )

        provider.additional_properties = d
        return provider

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
