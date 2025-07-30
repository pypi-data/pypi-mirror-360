from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.capacity_info import CapacityInfo
    from ..models.order import Order


T = TypeVar("T", bound="PayLater")


@_attrs_define
class PayLater:
    """
    Attributes:
        order (Order): Order detail informations
        capacity_info (Union[Unset, CapacityInfo]): Capacity posibilities of user. It is used to specify the calculation
            of the client's request. Based on this, the bank can make a more accurate calculation of the possibility of
            obtaining a loan
    """

    order: "Order"
    capacity_info: Union[Unset, "CapacityInfo"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        order = self.order.to_dict()

        capacity_info: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.capacity_info, Unset):
            capacity_info = self.capacity_info.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "order": order,
            }
        )
        if capacity_info is not UNSET:
            field_dict["capacityInfo"] = capacity_info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.capacity_info import CapacityInfo
        from ..models.order import Order

        d = dict(src_dict)
        order = Order.from_dict(d.pop("order"))

        _capacity_info = d.pop("capacityInfo", UNSET)
        capacity_info: Union[Unset, CapacityInfo]
        if isinstance(_capacity_info, Unset):
            capacity_info = UNSET
        else:
            capacity_info = CapacityInfo.from_dict(_capacity_info)

        pay_later = cls(
            order=order,
            capacity_info=capacity_info,
        )

        pay_later.additional_properties = d
        return pay_later

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
