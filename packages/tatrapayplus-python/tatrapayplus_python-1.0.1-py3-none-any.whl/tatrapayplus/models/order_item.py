from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.item_detail import ItemDetail


T = TypeVar("T", bound="OrderItem")


@_attrs_define
class OrderItem:
    """
    Attributes:
        quantity (int): Quantity of the item Example: 1.
        total_item_price (float): Total item price (including quantity e.g.:(item price*quantity)) Example: 120.
        item_detail (ItemDetail):
        item_info_url (Union[Unset, str]):  Example: https://developer.tatrabanka.sk.
        item_image (Union[Unset, str]): base64 encoded image h:48px w:48px Example: VGhpcyBpcyB0ZXN0.
    """

    quantity: int
    total_item_price: float
    item_detail: "ItemDetail"
    item_info_url: Union[Unset, str] = UNSET
    item_image: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        quantity = self.quantity

        total_item_price = self.total_item_price

        item_detail = self.item_detail.to_dict()

        item_info_url = self.item_info_url

        item_image = self.item_image

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "quantity": quantity,
                "totalItemPrice": total_item_price,
                "itemDetail": item_detail,
            }
        )
        if item_info_url is not UNSET:
            field_dict["itemInfoURL"] = item_info_url
        if item_image is not UNSET:
            field_dict["itemImage"] = item_image

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.item_detail import ItemDetail

        d = dict(src_dict)
        quantity = d.pop("quantity")

        total_item_price = d.pop("totalItemPrice")

        item_detail = ItemDetail.from_dict(d.pop("itemDetail"))

        item_info_url = d.pop("itemInfoURL", UNSET)

        item_image = d.pop("itemImage", UNSET)

        order_item = cls(
            quantity=quantity,
            total_item_price=total_item_price,
            item_detail=item_detail,
            item_info_url=item_info_url,
            item_image=item_image,
        )

        order_item.additional_properties = d
        return order_item

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
