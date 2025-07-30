from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.card_pay_update_instruction_operation_type import CardPayUpdateInstructionOperationType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CardPayUpdateInstruction")


@_attrs_define
class CardPayUpdateInstruction:
    """CardPay update instruction. For CONFIRM_PRE_AUTHORIZATION, CHARGEBACK is amount mandatory.

    Attributes:
        operation_type (CardPayUpdateInstructionOperationType):
        amount (Union[Unset, float]): The amount given with fractional digits, where fractions must be compliant to the
            currency definition. Negative amounts are signed by minus.
            The decimal separator is a dot.

            **Example:**
            Valid representations for EUR with up to two decimals are:

              * 1056
              * 5768.2
              * -1.50
              * 5877.78
             Example: 120.
    """

    operation_type: CardPayUpdateInstructionOperationType
    amount: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        operation_type = self.operation_type.value

        amount = self.amount

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "operationType": operation_type,
            }
        )
        if amount is not UNSET:
            field_dict["amount"] = amount

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        operation_type = CardPayUpdateInstructionOperationType(d.pop("operationType"))

        amount = d.pop("amount", UNSET)

        card_pay_update_instruction = cls(
            operation_type=operation_type,
            amount=amount,
        )

        card_pay_update_instruction.additional_properties = d
        return card_pay_update_instruction

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
