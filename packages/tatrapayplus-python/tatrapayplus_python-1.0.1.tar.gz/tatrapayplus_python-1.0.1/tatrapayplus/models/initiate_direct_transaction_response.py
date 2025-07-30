from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InitiateDirectTransactionResponse")


@_attrs_define
class InitiateDirectTransactionResponse:
    """
    Attributes:
        payment_id (str): Payment intent identifier
        redirect_form_html (Union[Unset, str]): HTML form. Only for status TDS_AUTH_REQUIRED
    """

    payment_id: str
    redirect_form_html: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payment_id = self.payment_id

        redirect_form_html = self.redirect_form_html

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "paymentId": payment_id,
            }
        )
        if redirect_form_html is not UNSET:
            field_dict["redirectFormHtml"] = redirect_form_html

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        payment_id = d.pop("paymentId")

        redirect_form_html = d.pop("redirectFormHtml", UNSET)

        initiate_direct_transaction_response = cls(
            payment_id=payment_id,
            redirect_form_html=redirect_form_html,
        )

        initiate_direct_transaction_response.additional_properties = d
        return initiate_direct_transaction_response

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
