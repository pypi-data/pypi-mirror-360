from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.amount import Amount
    from ..models.payment_symbols import PaymentSymbols


T = TypeVar("T", bound="BasePayment")


@_attrs_define
class BasePayment:
    """Common instruction detail

    Attributes:
        instructed_amount (Amount):
        end_to_end (Union['PaymentSymbols', str]): EndToEndId or paymentSymbols
    """

    instructed_amount: "Amount"
    end_to_end: Union["PaymentSymbols", str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.payment_symbols import PaymentSymbols

        instructed_amount = self.instructed_amount.to_dict()

        end_to_end: Union[dict[str, Any], str]
        if isinstance(self.end_to_end, PaymentSymbols):
            end_to_end = self.end_to_end.to_dict()
        else:
            end_to_end = self.end_to_end

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "instructedAmount": instructed_amount,
                "endToEnd": end_to_end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.amount import Amount
        from ..models.payment_symbols import PaymentSymbols

        d = dict(src_dict)
        instructed_amount = Amount.from_dict(d.pop("instructedAmount"))

        def _parse_end_to_end(data: object) -> Union["PaymentSymbols", str]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemase2e_type_0 = PaymentSymbols.from_dict(data)

                return componentsschemase2e_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PaymentSymbols", str], data)

        end_to_end = _parse_end_to_end(d.pop("endToEnd"))

        base_payment = cls(
            instructed_amount=instructed_amount,
            end_to_end=end_to_end,
        )

        base_payment.additional_properties = d
        return base_payment

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
