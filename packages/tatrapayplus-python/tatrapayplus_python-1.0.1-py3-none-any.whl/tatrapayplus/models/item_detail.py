from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.item_detail_lang_unit import ItemDetailLangUnit


T = TypeVar("T", bound="ItemDetail")


@_attrs_define
class ItemDetail:
    """
    Attributes:
        item_detail_sk (ItemDetailLangUnit):
        item_detail_en (Union[Unset, ItemDetailLangUnit]):
    """

    item_detail_sk: "ItemDetailLangUnit"
    item_detail_en: Union[Unset, "ItemDetailLangUnit"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        item_detail_sk = self.item_detail_sk.to_dict()

        item_detail_en: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.item_detail_en, Unset):
            item_detail_en = self.item_detail_en.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "itemDetailSK": item_detail_sk,
            }
        )
        if item_detail_en is not UNSET:
            field_dict["itemDetailEN"] = item_detail_en

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.item_detail_lang_unit import ItemDetailLangUnit

        d = dict(src_dict)
        item_detail_sk = ItemDetailLangUnit.from_dict(d.pop("itemDetailSK"))

        _item_detail_en = d.pop("itemDetailEN", UNSET)
        item_detail_en: Union[Unset, ItemDetailLangUnit]
        if isinstance(_item_detail_en, Unset):
            item_detail_en = UNSET
        else:
            item_detail_en = ItemDetailLangUnit.from_dict(_item_detail_en)

        item_detail = cls(
            item_detail_sk=item_detail_sk,
            item_detail_en=item_detail_en,
        )

        item_detail.additional_properties = d
        return item_detail

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
