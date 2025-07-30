from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PaymentSymbols")


@_attrs_define
class PaymentSymbols:
    """
    Attributes:
        variable_symbol (str):  Example: 123456.
        specific_symbol (Union[Unset, str]):
        constant_symbol (Union[Unset, str]): In case of payment method CardPay will be automatically rewrite to value
            0608
    """

    variable_symbol: str
    specific_symbol: Union[Unset, str] = UNSET
    constant_symbol: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        variable_symbol = self.variable_symbol

        specific_symbol = self.specific_symbol

        constant_symbol = self.constant_symbol

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "variableSymbol": variable_symbol,
            }
        )
        if specific_symbol is not UNSET:
            field_dict["specificSymbol"] = specific_symbol
        if constant_symbol is not UNSET:
            field_dict["constantSymbol"] = constant_symbol

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        variable_symbol = d.pop("variableSymbol")

        specific_symbol = d.pop("specificSymbol", UNSET)

        constant_symbol = d.pop("constantSymbol", UNSET)

        payment_symbols = cls(
            variable_symbol=variable_symbol,
            specific_symbol=specific_symbol,
            constant_symbol=constant_symbol,
        )

        payment_symbols.additional_properties = d
        return payment_symbols

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
