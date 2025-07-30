from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.order_item import OrderItem


T = TypeVar("T", bound="Order")


@_attrs_define
class Order:
    """Order detail informations

    Attributes:
        order_no (str): Order Number. Sending the same orderNo will affect that previously created application status
            will change to 'CANCELLED' and new application will be created. In case that application is in state that its
            not possible to cancel, the error state 422 will be returned
        order_items (list['OrderItem']):
        preferred_loan_duration (Union[Unset, int]): Preferred loan payment period
        down_payment (Union[Unset, float]): Downpayment for activation of service
    """

    order_no: str
    order_items: list["OrderItem"]
    preferred_loan_duration: Union[Unset, int] = UNSET
    down_payment: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        order_no = self.order_no

        order_items = []
        for componentsschemasorder_items_item_data in self.order_items:
            componentsschemasorder_items_item = componentsschemasorder_items_item_data.to_dict()
            order_items.append(componentsschemasorder_items_item)

        preferred_loan_duration = self.preferred_loan_duration

        down_payment = self.down_payment

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "orderNo": order_no,
                "orderItems": order_items,
            }
        )
        if preferred_loan_duration is not UNSET:
            field_dict["preferredLoanDuration"] = preferred_loan_duration
        if down_payment is not UNSET:
            field_dict["downPayment"] = down_payment

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.order_item import OrderItem

        d = dict(src_dict)
        order_no = d.pop("orderNo")

        order_items = []
        _order_items = d.pop("orderItems")
        for componentsschemasorder_items_item_data in _order_items:
            componentsschemasorder_items_item = OrderItem.from_dict(componentsschemasorder_items_item_data)

            order_items.append(componentsschemasorder_items_item)

        preferred_loan_duration = d.pop("preferredLoanDuration", UNSET)

        down_payment = d.pop("downPayment", UNSET)

        order = cls(
            order_no=order_no,
            order_items=order_items,
            preferred_loan_duration=preferred_loan_duration,
            down_payment=down_payment,
        )

        order.additional_properties = d
        return order

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
