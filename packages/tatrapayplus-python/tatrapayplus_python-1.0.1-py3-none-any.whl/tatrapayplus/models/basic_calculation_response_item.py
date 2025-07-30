from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="BasicCalculationResponseItem")


@_attrs_define
class BasicCalculationResponseItem:
    """
    Attributes:
        loan_interest_rate (float): Loan interest rate
        installment_amount (float): Installment amount
        loan_duration (int): Loan duration
        preference (bool): Preferred maturity of loan offer (max 3)
        main_preference (bool): Main preferred maturity of loan offer (max 1)
        capacity_validity (bool): Loan offer is valid with respect to entered capacity
        rpmn (float): Calculated RPMN
        total_amount (float): Total amount of the order including all fees, insurance, shipping,... Example: 156.95.
        loan_fee (float):
    """

    loan_interest_rate: float
    installment_amount: float
    loan_duration: int
    preference: bool
    main_preference: bool
    capacity_validity: bool
    rpmn: float
    total_amount: float
    loan_fee: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        loan_interest_rate = self.loan_interest_rate

        installment_amount = self.installment_amount

        loan_duration = self.loan_duration

        preference = self.preference

        main_preference = self.main_preference

        capacity_validity = self.capacity_validity

        rpmn = self.rpmn

        total_amount = self.total_amount

        loan_fee = self.loan_fee

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "loanInterestRate": loan_interest_rate,
                "installmentAmount": installment_amount,
                "loanDuration": loan_duration,
                "preference": preference,
                "mainPreference": main_preference,
                "capacityValidity": capacity_validity,
                "rpmn": rpmn,
                "totalAmount": total_amount,
                "loanFee": loan_fee,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        loan_interest_rate = d.pop("loanInterestRate")

        installment_amount = d.pop("installmentAmount")

        loan_duration = d.pop("loanDuration")

        preference = d.pop("preference")

        main_preference = d.pop("mainPreference")

        capacity_validity = d.pop("capacityValidity")

        rpmn = d.pop("rpmn")

        total_amount = d.pop("totalAmount")

        loan_fee = d.pop("loanFee")

        basic_calculation_response_item = cls(
            loan_interest_rate=loan_interest_rate,
            installment_amount=installment_amount,
            loan_duration=loan_duration,
            preference=preference,
            main_preference=main_preference,
            capacity_validity=capacity_validity,
            rpmn=rpmn,
            total_amount=total_amount,
            loan_fee=loan_fee,
        )

        basic_calculation_response_item.additional_properties = d
        return basic_calculation_response_item

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
