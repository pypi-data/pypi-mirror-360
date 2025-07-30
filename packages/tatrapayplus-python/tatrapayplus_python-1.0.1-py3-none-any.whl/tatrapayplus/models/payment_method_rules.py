from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.payment_method import PaymentMethod
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.amount_range_rule import AmountRangeRule
    from ..models.provider import Provider


T = TypeVar("T", bound="PaymentMethodRules")


@_attrs_define
class PaymentMethodRules:
    """
    Attributes:
        payment_method (PaymentMethod): TatraPayPlus enumaration
        amount_range_rule (Union[Unset, AmountRangeRule]): Range of amounts allowed for a given payment method
        supported_currency (Union[Unset, list[str]]):
        supported_country (Union[Unset, list[str]]): Payment method is applicable for payment to listed countries
        allowed_bank_providers (Union[Unset, list['Provider']]): Allowed bank providers for BANK_TRNASFER method
            selected by TatraPayPlus client
        is_precalculation_allowed (Union[Unset, bool]):  Default: False.
    """

    payment_method: PaymentMethod
    amount_range_rule: Union[Unset, "AmountRangeRule"] = UNSET
    supported_currency: Union[Unset, list[str]] = UNSET
    supported_country: Union[Unset, list[str]] = UNSET
    allowed_bank_providers: Union[Unset, list["Provider"]] = UNSET
    is_precalculation_allowed: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payment_method = self.payment_method.value

        amount_range_rule: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.amount_range_rule, Unset):
            amount_range_rule = self.amount_range_rule.to_dict()

        supported_currency: Union[Unset, list[str]] = UNSET
        if not isinstance(self.supported_currency, Unset):
            supported_currency = self.supported_currency

        supported_country: Union[Unset, list[str]] = UNSET
        if not isinstance(self.supported_country, Unset):
            supported_country = self.supported_country

        allowed_bank_providers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.allowed_bank_providers, Unset):
            allowed_bank_providers = []
            for (
                componentsschemasallowed_bank_providers_item_data
            ) in self.allowed_bank_providers:
                componentsschemasallowed_bank_providers_item = (
                    componentsschemasallowed_bank_providers_item_data.to_dict()
                )
                allowed_bank_providers.append(
                    componentsschemasallowed_bank_providers_item
                )

        is_precalculation_allowed = self.is_precalculation_allowed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "paymentMethod": payment_method,
            }
        )
        if amount_range_rule is not UNSET:
            field_dict["amountRangeRule"] = amount_range_rule
        if supported_currency is not UNSET:
            field_dict["supportedCurrency"] = supported_currency
        if supported_country is not UNSET:
            field_dict["supportedCountry"] = supported_country
        if allowed_bank_providers is not UNSET:
            field_dict["allowedBankProviders"] = allowed_bank_providers
        if is_precalculation_allowed is not UNSET:
            field_dict["isPrecalculationAllowed"] = is_precalculation_allowed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.amount_range_rule import AmountRangeRule
        from ..models.provider import Provider

        d = dict(src_dict)
        payment_method = PaymentMethod(d.pop("paymentMethod"))

        _amount_range_rule = d.pop("amountRangeRule", UNSET)
        amount_range_rule: Union[Unset, AmountRangeRule]
        if isinstance(_amount_range_rule, Unset):
            amount_range_rule = UNSET
        else:
            amount_range_rule = AmountRangeRule.from_dict(_amount_range_rule)

        supported_currency = cast(list[str], d.pop("supportedCurrency", UNSET))

        supported_country = cast(list[str], d.pop("supportedCountry", UNSET))

        allowed_bank_providers = []
        _allowed_bank_providers = d.pop("allowedBankProviders", UNSET)
        for componentsschemasallowed_bank_providers_item_data in (
            _allowed_bank_providers or []
        ):
            componentsschemasallowed_bank_providers_item = Provider.from_dict(
                componentsschemasallowed_bank_providers_item_data
            )

            allowed_bank_providers.append(componentsschemasallowed_bank_providers_item)

        is_precalculation_allowed = d.pop("isPrecalculationAllowed", UNSET)

        payment_method_rules = cls(
            payment_method=payment_method,
            amount_range_rule=amount_range_rule,
            supported_currency=supported_currency,
            supported_country=supported_country,
            allowed_bank_providers=allowed_bank_providers,
            is_precalculation_allowed=is_precalculation_allowed,
        )

        payment_method_rules.additional_properties = d
        return payment_method_rules

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
