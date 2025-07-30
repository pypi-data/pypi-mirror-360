from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.comfort_pay_status import ComfortPayStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="CardPayStatusStructureComfortPay")


@_attrs_define
class CardPayStatusStructureComfortPay:
    """
    Attributes:
        status (ComfortPayStatus):
        cid (Union[Unset, str]): Card identifier for ComfortPay
    """

    status: ComfortPayStatus
    cid: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        cid = self.cid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if cid is not UNSET:
            field_dict["cid"] = cid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = ComfortPayStatus(d.pop("status"))

        cid = d.pop("cid", UNSET)

        card_pay_status_structure_comfort_pay = cls(
            status=status,
            cid=cid,
        )

        card_pay_status_structure_comfort_pay.additional_properties = d
        return card_pay_status_structure_comfort_pay

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
