from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AppearanceLogoRequest")


@_attrs_define
class AppearanceLogoRequest:
    """The logo image.

    Attributes:
        logo_image (str): base64 Encoded image. MaxLength - 256px MaxHeight - 64px, Max size 1MB(base64 encoded string).
            Supported formats are SVG, JPEG, PNG
    """

    logo_image: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        logo_image = self.logo_image

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "logoImage": logo_image,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        logo_image = d.pop("logoImage")

        appearance_logo_request = cls(
            logo_image=logo_image,
        )

        appearance_logo_request.additional_properties = d
        return appearance_logo_request

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
