from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.payment_method_rules import PaymentMethodRules


T = TypeVar("T", bound="PaymentMethodsListResponse")


@_attrs_define
class PaymentMethodsListResponse:
    """TatraPayPlus methods list, in case BANK_TRANSFER method is allowed for client,allowedBankProviders will be also
    provided

        Attributes:
            payment_methods (list['PaymentMethodRules']): TatraPayPlus methods list
    """

    payment_methods: list["PaymentMethodRules"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payment_methods = []
        for componentsschemaspayment_methods_item_data in self.payment_methods:
            componentsschemaspayment_methods_item = componentsschemaspayment_methods_item_data.to_dict()
            payment_methods.append(componentsschemaspayment_methods_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "paymentMethods": payment_methods,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.payment_method_rules import PaymentMethodRules

        d = dict(src_dict)
        payment_methods = []
        _payment_methods = d.pop("paymentMethods")
        for componentsschemaspayment_methods_item_data in _payment_methods:
            componentsschemaspayment_methods_item = PaymentMethodRules.from_dict(
                componentsschemaspayment_methods_item_data
            )

            payment_methods.append(componentsschemaspayment_methods_item)

        payment_methods_list_response = cls(
            payment_methods=payment_methods,
        )

        payment_methods_list_response.additional_properties = d
        return payment_methods_list_response

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
