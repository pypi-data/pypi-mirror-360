from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.apple_pay_token_token import ApplePayTokenToken


T = TypeVar("T", bound="ApplePayToken")


@_attrs_define
class ApplePayToken:
    """
    Attributes:
        token (Union[Unset, ApplePayTokenToken]):
    """

    token: Union[Unset, "ApplePayTokenToken"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        token: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.token, Unset):
            token = self.token.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if token is not UNSET:
            field_dict["token"] = token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.apple_pay_token_token import ApplePayTokenToken

        d = dict(src_dict)
        _token = d.pop("token", UNSET)
        token: Union[Unset, ApplePayTokenToken]
        if isinstance(_token, Unset):
            token = UNSET
        else:
            token = ApplePayTokenToken.from_dict(_token)

        apple_pay_token = cls(
            token=token,
        )

        apple_pay_token.additional_properties = d
        return apple_pay_token

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
