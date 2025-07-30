from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CapacityInfo")


@_attrs_define
class CapacityInfo:
    """Capacity posibilities of user. It is used to specify the calculation of the client's request. Based on this, the
    bank can make a more accurate calculation of the possibility of obtaining a loan

        Attributes:
            monthly_income (float): Declared monthly income by user
            monthly_expenses (float): Declared monthly expenses by user
            number_of_children (int): Declared number of children of user
    """

    monthly_income: float
    monthly_expenses: float
    number_of_children: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        monthly_income = self.monthly_income

        monthly_expenses = self.monthly_expenses

        number_of_children = self.number_of_children

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "monthlyIncome": monthly_income,
                "monthlyExpenses": monthly_expenses,
                "numberOfChildren": number_of_children,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        monthly_income = d.pop("monthlyIncome")

        monthly_expenses = d.pop("monthlyExpenses")

        number_of_children = d.pop("numberOfChildren")

        capacity_info = cls(
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            number_of_children=number_of_children,
        )

        capacity_info.additional_properties = d
        return capacity_info

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
