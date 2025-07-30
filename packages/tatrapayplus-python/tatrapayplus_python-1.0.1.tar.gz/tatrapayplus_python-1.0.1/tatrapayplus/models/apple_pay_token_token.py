from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.apple_pay_token_token_header import ApplePayTokenTokenHeader


T = TypeVar("T", bound="ApplePayTokenToken")


@_attrs_define
class ApplePayTokenToken:
    """
    Attributes:
        header (Union[Unset, ApplePayTokenTokenHeader]):
        data (Union[Unset, str]):
        signature (Union[Unset, str]):
        version (Union[Unset, str]):
    """

    header: Union[Unset, "ApplePayTokenTokenHeader"] = UNSET
    data: Union[Unset, str] = UNSET
    signature: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        header: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.header, Unset):
            header = self.header.to_dict()

        data = self.data

        signature = self.signature

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if header is not UNSET:
            field_dict["header"] = header
        if data is not UNSET:
            field_dict["data"] = data
        if signature is not UNSET:
            field_dict["signature"] = signature
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.apple_pay_token_token_header import ApplePayTokenTokenHeader

        d = dict(src_dict)
        _header = d.pop("header", UNSET)
        header: Union[Unset, ApplePayTokenTokenHeader]
        if isinstance(_header, Unset):
            header = UNSET
        else:
            header = ApplePayTokenTokenHeader.from_dict(_header)

        data = d.pop("data", UNSET)

        signature = d.pop("signature", UNSET)

        version = d.pop("version", UNSET)

        apple_pay_token_token = cls(
            header=header,
            data=data,
            signature=signature,
            version=version,
        )

        apple_pay_token_token.additional_properties = d
        return apple_pay_token_token

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
