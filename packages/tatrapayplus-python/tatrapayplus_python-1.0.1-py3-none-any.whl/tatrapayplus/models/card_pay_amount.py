from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CardPayAmount")


@_attrs_define
class CardPayAmount:
    """
    Attributes:
        amount (float): The amount given with fractional digits, where fractions must be compliant to the currency
            definition. Negative amounts are signed by minus.
            The decimal separator is a dot.

            **Example:**
            Valid representations for EUR with up to two decimals are:

              * 1056
              * 5768.2
              * -1.50
              * 5877.78
             Example: 120.
    """

    amount: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        amount = self.amount

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount": amount,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        amount = d.pop("amount")

        card_pay_amount = cls(
            amount=amount,
        )

        card_pay_amount.additional_properties = d
        return card_pay_amount

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
