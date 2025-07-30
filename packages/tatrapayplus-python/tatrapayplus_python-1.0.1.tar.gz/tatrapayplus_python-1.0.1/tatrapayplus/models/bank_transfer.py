from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BankTransfer")


@_attrs_define
class BankTransfer:
    """Bank transder attributes

    Attributes:
        remittance_information_unstructured (Union[Unset, str]): Unstructured transfer information. Currently,
            Tatrabanka bank transfer does not display the transfer information. The entire SEPA
            remittanceInformationUnstructured contains 140 characters. The structure of the string consists of 3 parts:

                - A. paymentId - fixed 40 characters are reserved for paymentId
                - B. Merchant Name value length - provided in the contract, up to 50 characters
                - C. Custom value length - free characters are calculated as C = 140-A-(B+1). Depends on the length of the
            merchant name.

                E.g. Merchant name = MerchantABCD,s.r.o. (19 characters + 1 separator space). 80 characters are available.

                The result of the UnstructuredTransferInformation will look like this

                07b940d2-8b82-4c7a-a0dd-5ebeabcf1f3d MerchantABCD,s.r.o. Your text in remittance

                If the value of RemittanceInformationUnstructured in this attribute is longer than the calculated C, your
            custom value will be truncated.


             Example: Ref Number Merchant.
    """

    remittance_information_unstructured: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        remittance_information_unstructured = self.remittance_information_unstructured

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if remittance_information_unstructured is not UNSET:
            field_dict["remittanceInformationUnstructured"] = remittance_information_unstructured

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        remittance_information_unstructured = d.pop("remittanceInformationUnstructured", UNSET)

        bank_transfer = cls(
            remittance_information_unstructured=remittance_information_unstructured,
        )

        bank_transfer.additional_properties = d
        return bank_transfer

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
