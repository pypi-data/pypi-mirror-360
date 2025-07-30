from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApplePayTokenTokenHeader")


@_attrs_define
class ApplePayTokenTokenHeader:
    """
    Attributes:
        ephemeral_public_key (Union[Unset, str]):
        public_key_hash (Union[Unset, str]):
        transaction_id (Union[Unset, str]):
    """

    ephemeral_public_key: Union[Unset, str] = UNSET
    public_key_hash: Union[Unset, str] = UNSET
    transaction_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ephemeral_public_key = self.ephemeral_public_key

        public_key_hash = self.public_key_hash

        transaction_id = self.transaction_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ephemeral_public_key is not UNSET:
            field_dict["ephemeralPublicKey"] = ephemeral_public_key
        if public_key_hash is not UNSET:
            field_dict["publicKeyHash"] = public_key_hash
        if transaction_id is not UNSET:
            field_dict["transactionId"] = transaction_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ephemeral_public_key = d.pop("ephemeralPublicKey", UNSET)

        public_key_hash = d.pop("publicKeyHash", UNSET)

        transaction_id = d.pop("transactionId", UNSET)

        apple_pay_token_token_header = cls(
            ephemeral_public_key=ephemeral_public_key,
            public_key_hash=public_key_hash,
            transaction_id=transaction_id,
        )

        apple_pay_token_token_header.additional_properties = d
        return apple_pay_token_token_header

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
