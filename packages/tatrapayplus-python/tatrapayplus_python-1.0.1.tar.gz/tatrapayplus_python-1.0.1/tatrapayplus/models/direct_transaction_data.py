from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DirectTransactionData")


@_attrs_define
class DirectTransactionData:
    """
    Attributes:
        reason_code (Union[Unset, str]):
        payment_authorization_code (Union[Unset, str]): Payment authorization code
    """

    reason_code: Union[Unset, str] = UNSET
    payment_authorization_code: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reason_code: Union[Unset, str]
        if isinstance(self.reason_code, Unset):
            reason_code = UNSET
        else:
            reason_code = self.reason_code

        payment_authorization_code = self.payment_authorization_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if reason_code is not UNSET:
            field_dict["reasonCode"] = reason_code
        if payment_authorization_code is not UNSET:
            field_dict["paymentAuthorizationCode"] = payment_authorization_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_reason_code(data: object) -> Union[Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, str], data)

        reason_code = _parse_reason_code(d.pop("reasonCode", UNSET))

        payment_authorization_code = d.pop("paymentAuthorizationCode", UNSET)

        direct_transaction_data = cls(
            reason_code=reason_code,
            payment_authorization_code=payment_authorization_code,
        )

        direct_transaction_data.additional_properties = d
        return direct_transaction_data

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
