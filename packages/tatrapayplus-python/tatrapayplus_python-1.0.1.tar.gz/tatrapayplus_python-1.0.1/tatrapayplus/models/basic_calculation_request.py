from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.basic_calculation_request_payment_method import (
    BasicCalculationRequestPaymentMethod,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.capacity_info import CapacityInfo


T = TypeVar("T", bound="BasicCalculationRequest")


@_attrs_define
class BasicCalculationRequest:
    """
    Attributes:
        loan_amount (float): Loan amount in EUR Example: 156.95.
        payment_method (Union[Unset, BasicCalculationRequestPaymentMethod]): Only if isPrecalculationAllowed = true
        capacity_info (Union[Unset, CapacityInfo]): Capacity posibilities of user. It is used to specify the calculation
            of the client's request. Based on this, the bank can make a more accurate calculation of the possibility of
            obtaining a loan
    """

    loan_amount: float
    payment_method: Union[Unset, BasicCalculationRequestPaymentMethod] = UNSET
    capacity_info: Union[Unset, "CapacityInfo"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        loan_amount = self.loan_amount

        payment_method: Union[Unset, str] = UNSET
        if not isinstance(self.payment_method, Unset):
            payment_method = self.payment_method.value

        capacity_info: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.capacity_info, Unset):
            capacity_info = self.capacity_info.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "loanAmount": loan_amount,
            }
        )
        if payment_method is not UNSET:
            field_dict["paymentMethod"] = payment_method
        if capacity_info is not UNSET:
            field_dict["capacityInfo"] = capacity_info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.capacity_info import CapacityInfo

        d = dict(src_dict)
        loan_amount = d.pop("loanAmount")

        _payment_method = d.pop("paymentMethod", UNSET)
        payment_method: Union[Unset, BasicCalculationRequestPaymentMethod]
        if isinstance(_payment_method, Unset):
            payment_method = UNSET
        else:
            payment_method = BasicCalculationRequestPaymentMethod(_payment_method)

        _capacity_info = d.pop("capacityInfo", UNSET)
        capacity_info: Union[Unset, CapacityInfo]
        if isinstance(_capacity_info, Unset):
            capacity_info = UNSET
        else:
            capacity_info = CapacityInfo.from_dict(_capacity_info)

        basic_calculation_request = cls(
            loan_amount=loan_amount,
            payment_method=payment_method,
            capacity_info=capacity_info,
        )

        basic_calculation_request.additional_properties = d
        return basic_calculation_request

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
