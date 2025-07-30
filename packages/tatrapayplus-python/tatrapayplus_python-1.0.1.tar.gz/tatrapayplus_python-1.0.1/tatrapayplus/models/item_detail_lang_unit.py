from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ItemDetailLangUnit")


@_attrs_define
class ItemDetailLangUnit:
    """
    Attributes:
        item_name (str):
        item_description (Union[Unset, str]):
    """

    item_name: str
    item_description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        item_name = self.item_name

        item_description = self.item_description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "itemName": item_name,
            }
        )
        if item_description is not UNSET:
            field_dict["itemDescription"] = item_description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        item_name = d.pop("itemName")

        item_description = d.pop("itemDescription", UNSET)

        item_detail_lang_unit = cls(
            item_name=item_name,
            item_description=item_description,
        )

        item_detail_lang_unit.additional_properties = d
        return item_detail_lang_unit

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
