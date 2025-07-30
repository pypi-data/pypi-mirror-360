from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.card_pay_status_structure import CardPayStatusStructure


T = TypeVar("T", bound="PaymentIntentUpdateResponse")


@_attrs_define
class PaymentIntentUpdateResponse:
    """
    **TatraPayPlus payment update response. **

    | selectedPaymentMethod      | attribute supported |
    | ---------------- | ------------|
    | BANK_TRANSFER              | N/A     |
    | CARD_PAY              | cardPayStatusStructure |
    | PAY_LATER               | N/A |

        Attributes:
            status (Union[Unset, CardPayStatusStructure]): card pay status structure
    """

    status: Union[Unset, "CardPayStatusStructure"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.card_pay_status_structure import CardPayStatusStructure

        d = dict(src_dict)
        _status = d.pop("status", UNSET)
        status: Union[Unset, CardPayStatusStructure]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = CardPayStatusStructure.from_dict(_status)

        payment_intent_update_response = cls(
            status=status,
        )

        payment_intent_update_response.additional_properties = d
        return payment_intent_update_response

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
