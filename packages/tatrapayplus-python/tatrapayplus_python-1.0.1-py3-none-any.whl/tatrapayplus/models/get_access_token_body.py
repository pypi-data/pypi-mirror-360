from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetAccessTokenBody")


@_attrs_define
class GetAccessTokenBody:
    """
    Attributes:
        grant_type (str):  Example: client_credentials.
        client_id (str):  Example: dd.
        client_secret (str):  Example: dd.
        scope (str):  Example: TATRAPAYPLUS.
    """

    grant_type: str
    client_id: str
    client_secret: str
    scope: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        grant_type = self.grant_type

        client_id = self.client_id

        client_secret = self.client_secret

        scope = self.scope

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "grant_type": grant_type,
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": scope,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        grant_type = d.pop("grant_type")

        client_id = d.pop("client_id")

        client_secret = d.pop("client_secret")

        scope = d.pop("scope")

        get_access_token_body = cls(
            grant_type=grant_type,
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
        )

        get_access_token_body.additional_properties = d
        return get_access_token_body

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
