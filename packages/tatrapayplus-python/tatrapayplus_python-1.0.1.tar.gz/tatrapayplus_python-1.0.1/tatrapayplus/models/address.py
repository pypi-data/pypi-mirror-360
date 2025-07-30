from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Address")


@_attrs_define
class Address:
    """
    Attributes:
        country (str): ISO 3166 ALPHA2 country code. Example: SE.
        street_name (Union[Unset, str]):
        building_number (Union[Unset, str]):
        town_name (Union[Unset, str]):
        post_code (Union[Unset, str]):
    """

    country: str
    street_name: Union[Unset, str] = UNSET
    building_number: Union[Unset, str] = UNSET
    town_name: Union[Unset, str] = UNSET
    post_code: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        country = self.country

        street_name = self.street_name

        building_number = self.building_number

        town_name = self.town_name

        post_code = self.post_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "country": country,
            }
        )
        if street_name is not UNSET:
            field_dict["streetName"] = street_name
        if building_number is not UNSET:
            field_dict["buildingNumber"] = building_number
        if town_name is not UNSET:
            field_dict["townName"] = town_name
        if post_code is not UNSET:
            field_dict["postCode"] = post_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        country = d.pop("country")

        street_name = d.pop("streetName", UNSET)

        building_number = d.pop("buildingNumber", UNSET)

        town_name = d.pop("townName", UNSET)

        post_code = d.pop("postCode", UNSET)

        address = cls(
            country=country,
            street_name=street_name,
            building_number=building_number,
            town_name=town_name,
            post_code=post_code,
        )

        address.additional_properties = d
        return address

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
