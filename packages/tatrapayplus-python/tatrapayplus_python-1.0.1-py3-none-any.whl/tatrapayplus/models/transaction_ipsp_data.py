from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TransactionIPSPData")


@_attrs_define
class TransactionIPSPData:
    """In case of payment facilitator mode - this structure is mandatory

    Attributes:
        sub_merchant_id (str):
        name (str):
        location (str):
        country (str): ISO 3166 ALPHA2 country code. Example: SE.
    """

    sub_merchant_id: str
    name: str
    location: str
    country: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sub_merchant_id = self.sub_merchant_id

        name = self.name

        location = self.location

        country = self.country

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "subMerchantId": sub_merchant_id,
                "name": name,
                "location": location,
                "country": country,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sub_merchant_id = d.pop("subMerchantId")

        name = d.pop("name")

        location = d.pop("location")

        country = d.pop("country")

        transaction_ipsp_data = cls(
            sub_merchant_id=sub_merchant_id,
            name=name,
            location=location,
            country=country,
        )

        transaction_ipsp_data.additional_properties = d
        return transaction_ipsp_data

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
