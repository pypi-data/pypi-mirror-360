from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SignedCardIdObj")


@_attrs_define
class SignedCardIdObj:
    """
    Attributes:
        signed_card_id (Union[Unset, str]): Signed registered card identifier by client signing certificate for direct
            ComfortPay in base64 encoded string
    """

    signed_card_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        signed_card_id = self.signed_card_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if signed_card_id is not UNSET:
            field_dict["signedCardId"] = signed_card_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        signed_card_id = d.pop("signedCardId", UNSET)

        signed_card_id_obj = cls(
            signed_card_id=signed_card_id,
        )

        signed_card_id_obj.additional_properties = d
        return signed_card_id_obj

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
