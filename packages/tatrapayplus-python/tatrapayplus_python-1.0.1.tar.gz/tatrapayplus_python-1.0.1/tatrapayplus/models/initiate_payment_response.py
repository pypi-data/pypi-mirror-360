from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.available_payment_method import AvailablePaymentMethod


T = TypeVar("T", bound="InitiatePaymentResponse")


@_attrs_define
class InitiatePaymentResponse:
    """
    Attributes:
        payment_id (str): Payment intent identifier
        tatra_pay_plus_url (Union[Unset, str]): URL address for FE redirect to tatraPayPlus app
        available_payment_methods (Union[Unset, list['AvailablePaymentMethod']]): List of availibility of each possible
            methods.
    """

    payment_id: str
    tatra_pay_plus_url: Union[Unset, str] = UNSET
    available_payment_methods: Union[Unset, list["AvailablePaymentMethod"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payment_id = self.payment_id

        tatra_pay_plus_url = self.tatra_pay_plus_url

        available_payment_methods: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.available_payment_methods, Unset):
            available_payment_methods = []
            for available_payment_methods_item_data in self.available_payment_methods:
                available_payment_methods_item = available_payment_methods_item_data.to_dict()
                available_payment_methods.append(available_payment_methods_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "paymentId": payment_id,
            }
        )
        if tatra_pay_plus_url is not UNSET:
            field_dict["tatraPayPlusUrl"] = tatra_pay_plus_url
        if available_payment_methods is not UNSET:
            field_dict["availablePaymentMethods"] = available_payment_methods

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.available_payment_method import AvailablePaymentMethod

        d = dict(src_dict)
        payment_id = d.pop("paymentId")

        tatra_pay_plus_url = d.pop("tatraPayPlusUrl", UNSET)

        available_payment_methods = []
        _available_payment_methods = d.pop("availablePaymentMethods", UNSET)
        for available_payment_methods_item_data in _available_payment_methods or []:
            available_payment_methods_item = AvailablePaymentMethod.from_dict(available_payment_methods_item_data)

            available_payment_methods.append(available_payment_methods_item)

        initiate_payment_response = cls(
            payment_id=payment_id,
            tatra_pay_plus_url=tatra_pay_plus_url,
            available_payment_methods=available_payment_methods,
        )

        initiate_payment_response.additional_properties = d
        return initiate_payment_response

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
