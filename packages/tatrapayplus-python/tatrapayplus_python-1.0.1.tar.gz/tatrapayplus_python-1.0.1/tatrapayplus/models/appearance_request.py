from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.appearance_request_theme import AppearanceRequestTheme
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.color_attribute import ColorAttribute


T = TypeVar("T", bound="AppearanceRequest")


@_attrs_define
class AppearanceRequest:
    """Attributes that can be customised

    Attributes:
        theme (Union[Unset, AppearanceRequestTheme]):  Default: AppearanceRequestTheme.SYSTEM.
        tint_on_accent (Union[Unset, ColorAttribute]): Color attributes for specific theme. Choose colour with
            sufficient contrast for the specific theme
        tint_accent (Union[Unset, ColorAttribute]): Color attributes for specific theme. Choose colour with sufficient
            contrast for the specific theme
        surface_accent (Union[Unset, ColorAttribute]): Color attributes for specific theme. Choose colour with
            sufficient contrast for the specific theme
    """

    theme: Union[Unset, AppearanceRequestTheme] = AppearanceRequestTheme.SYSTEM
    tint_on_accent: Union[Unset, "ColorAttribute"] = UNSET
    tint_accent: Union[Unset, "ColorAttribute"] = UNSET
    surface_accent: Union[Unset, "ColorAttribute"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        theme: Union[Unset, str] = UNSET
        if not isinstance(self.theme, Unset):
            theme = self.theme.value

        tint_on_accent: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tint_on_accent, Unset):
            tint_on_accent = self.tint_on_accent.to_dict()

        tint_accent: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tint_accent, Unset):
            tint_accent = self.tint_accent.to_dict()

        surface_accent: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.surface_accent, Unset):
            surface_accent = self.surface_accent.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if theme is not UNSET:
            field_dict["theme"] = theme
        if tint_on_accent is not UNSET:
            field_dict["tintOnAccent"] = tint_on_accent
        if tint_accent is not UNSET:
            field_dict["tintAccent"] = tint_accent
        if surface_accent is not UNSET:
            field_dict["surfaceAccent"] = surface_accent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.color_attribute import ColorAttribute

        d = dict(src_dict)
        _theme = d.pop("theme", UNSET)
        theme: Union[Unset, AppearanceRequestTheme]
        if isinstance(_theme, Unset):
            theme = UNSET
        else:
            theme = AppearanceRequestTheme(_theme)

        _tint_on_accent = d.pop("tintOnAccent", UNSET)
        tint_on_accent: Union[Unset, ColorAttribute]
        if isinstance(_tint_on_accent, Unset):
            tint_on_accent = UNSET
        else:
            tint_on_accent = ColorAttribute.from_dict(_tint_on_accent)

        _tint_accent = d.pop("tintAccent", UNSET)
        tint_accent: Union[Unset, ColorAttribute]
        if isinstance(_tint_accent, Unset):
            tint_accent = UNSET
        else:
            tint_accent = ColorAttribute.from_dict(_tint_accent)

        _surface_accent = d.pop("surfaceAccent", UNSET)
        surface_accent: Union[Unset, ColorAttribute]
        if isinstance(_surface_accent, Unset):
            surface_accent = UNSET
        else:
            surface_accent = ColorAttribute.from_dict(_surface_accent)

        appearance_request = cls(
            theme=theme,
            tint_on_accent=tint_on_accent,
            tint_accent=tint_accent,
            surface_accent=surface_accent,
        )

        appearance_request.additional_properties = d
        return appearance_request

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
