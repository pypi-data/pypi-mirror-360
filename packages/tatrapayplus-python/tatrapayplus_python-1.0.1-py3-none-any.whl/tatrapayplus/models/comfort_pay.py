from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.register_for_comfort_pay_obj import RegisterForComfortPayObj
    from ..models.signed_card_id_obj import SignedCardIdObj


T = TypeVar("T", bound="ComfortPay")


@_attrs_define
class ComfortPay:
    """ComfortPay attributes

    Attributes:
        card_identifier (Union['RegisterForComfortPayObj', 'SignedCardIdObj', Unset]):
    """

    card_identifier: Union["RegisterForComfortPayObj", "SignedCardIdObj", Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.register_for_comfort_pay_obj import RegisterForComfortPayObj

        card_identifier: Union[Unset, dict[str, Any]]
        if isinstance(self.card_identifier, Unset):
            card_identifier = UNSET
        elif isinstance(self.card_identifier, RegisterForComfortPayObj):
            card_identifier = self.card_identifier.to_dict()
        else:
            card_identifier = self.card_identifier.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if card_identifier is not UNSET:
            field_dict["cardIdentifier"] = card_identifier

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.register_for_comfort_pay_obj import RegisterForComfortPayObj
        from ..models.signed_card_id_obj import SignedCardIdObj

        d = dict(src_dict)

        def _parse_card_identifier(data: object) -> Union["RegisterForComfortPayObj", "SignedCardIdObj", Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemascard_identifier_or_register_type_0 = RegisterForComfortPayObj.from_dict(data)

                return componentsschemascard_identifier_or_register_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemascard_identifier_or_register_type_1 = SignedCardIdObj.from_dict(data)

            return componentsschemascard_identifier_or_register_type_1

        card_identifier = _parse_card_identifier(d.pop("cardIdentifier", UNSET))

        comfort_pay = cls(
            card_identifier=card_identifier,
        )

        comfort_pay.additional_properties = d
        return comfort_pay

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
