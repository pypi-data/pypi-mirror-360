from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.address import Address


T = TypeVar("T", bound="DirectTransactionTDSData")


@_attrs_define
class DirectTransactionTDSData:
    """In case of Direct API either cardHolder or email is mandatory

    Attributes:
        card_holder (Union[Unset, str]): The card holder name. In case of Direct API either cardHolder or email is
            mandatory
        email (Union[Unset, str]): Conditionally mandatory. In case of TatraPayPlus payment initiation - It is mandatory
            only if the phone attribute is not provided. If the email is not provided, the user will not receive the cardPay
            notification and payLater will ask for the email in the app.
            In case of Direct API either cardHolder or email is mandatory
        phone (Union[Unset, str]): Conditionally mandatory.  In case of TatraPayPlus payment initiation - It is
            mandatory only if the email attribute is not provided.
        billing_address (Union[Unset, Address]):
        shipping_address (Union[Unset, Address]):
    """

    card_holder: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    phone: Union[Unset, str] = UNSET
    billing_address: Union[Unset, "Address"] = UNSET
    shipping_address: Union[Unset, "Address"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        card_holder = self.card_holder

        email = self.email

        phone = self.phone

        billing_address: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.billing_address, Unset):
            billing_address = self.billing_address.to_dict()

        shipping_address: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.shipping_address, Unset):
            shipping_address = self.shipping_address.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if card_holder is not UNSET:
            field_dict["cardHolder"] = card_holder
        if email is not UNSET:
            field_dict["email"] = email
        if phone is not UNSET:
            field_dict["phone"] = phone
        if billing_address is not UNSET:
            field_dict["billingAddress"] = billing_address
        if shipping_address is not UNSET:
            field_dict["shippingAddress"] = shipping_address

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.address import Address

        d = dict(src_dict)
        card_holder = d.pop("cardHolder", UNSET)

        email = d.pop("email", UNSET)

        phone = d.pop("phone", UNSET)

        _billing_address = d.pop("billingAddress", UNSET)
        billing_address: Union[Unset, Address]
        if isinstance(_billing_address, Unset):
            billing_address = UNSET
        else:
            billing_address = Address.from_dict(_billing_address)

        _shipping_address = d.pop("shippingAddress", UNSET)
        shipping_address: Union[Unset, Address]
        if isinstance(_shipping_address, Unset):
            shipping_address = UNSET
        else:
            shipping_address = Address.from_dict(_shipping_address)

        direct_transaction_tds_data = cls(
            card_holder=card_holder,
            email=email,
            phone=phone,
            billing_address=billing_address,
            shipping_address=shipping_address,
        )

        direct_transaction_tds_data.additional_properties = d
        return direct_transaction_tds_data

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
