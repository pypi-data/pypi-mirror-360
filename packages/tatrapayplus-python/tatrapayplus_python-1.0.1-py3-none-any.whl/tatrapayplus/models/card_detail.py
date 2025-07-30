from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.card_detail_card_pay_lang_override import CardDetailCardPayLangOverride
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.address import Address
    from ..models.register_for_comfort_pay_obj import RegisterForComfortPayObj
    from ..models.signed_card_id_obj import SignedCardIdObj
    from ..models.transaction_ipsp_data import TransactionIPSPData


T = TypeVar("T", bound="CardDetail")


@_attrs_define
class CardDetail:
    """Card pay information

    Attributes:
        card_holder (str): The card holder name. In case of Direct API either cardHolder or email is mandatory
        card_pay_lang_override (Union[Unset, CardDetailCardPayLangOverride]): It is possible to override the accept-
            language header for the CardPay payment method. This override only affects CardPay itself, not the whole
            TatraPayPlus service.
            If it is empty , then accept-language is taken into account
        is_pre_authorization (Union[Unset, bool]): If true - pre-authorization transaction
        billing_address (Union[Unset, Address]):
        shipping_address (Union[Unset, Address]):
        comfort_pay (Union['RegisterForComfortPayObj', 'SignedCardIdObj', Unset]):
        ipsp_data (Union[Unset, TransactionIPSPData]): In case of payment facilitator mode - this structure is mandatory
    """

    card_holder: str
    card_pay_lang_override: Union[Unset, CardDetailCardPayLangOverride] = UNSET
    is_pre_authorization: Union[Unset, bool] = UNSET
    billing_address: Union[Unset, "Address"] = UNSET
    shipping_address: Union[Unset, "Address"] = UNSET
    comfort_pay: Union["RegisterForComfortPayObj", "SignedCardIdObj", Unset] = UNSET
    ipsp_data: Union[Unset, "TransactionIPSPData"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.register_for_comfort_pay_obj import RegisterForComfortPayObj

        card_holder = self.card_holder

        card_pay_lang_override: Union[Unset, str] = UNSET
        if not isinstance(self.card_pay_lang_override, Unset):
            card_pay_lang_override = self.card_pay_lang_override.value

        is_pre_authorization = self.is_pre_authorization

        billing_address: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.billing_address, Unset):
            billing_address = self.billing_address.to_dict()

        shipping_address: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.shipping_address, Unset):
            shipping_address = self.shipping_address.to_dict()

        comfort_pay: Union[Unset, dict[str, Any]]
        if isinstance(self.comfort_pay, Unset):
            comfort_pay = UNSET
        elif isinstance(self.comfort_pay, RegisterForComfortPayObj):
            comfort_pay = self.comfort_pay.to_dict()
        else:
            comfort_pay = self.comfort_pay.to_dict()

        ipsp_data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.ipsp_data, Unset):
            ipsp_data = self.ipsp_data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cardHolder": card_holder,
            }
        )
        if card_pay_lang_override is not UNSET:
            field_dict["cardPayLangOverride"] = card_pay_lang_override
        if is_pre_authorization is not UNSET:
            field_dict["isPreAuthorization"] = is_pre_authorization
        if billing_address is not UNSET:
            field_dict["billingAddress"] = billing_address
        if shipping_address is not UNSET:
            field_dict["shippingAddress"] = shipping_address
        if comfort_pay is not UNSET:
            field_dict["comfortPay"] = comfort_pay
        if ipsp_data is not UNSET:
            field_dict["ipspData"] = ipsp_data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.address import Address
        from ..models.register_for_comfort_pay_obj import RegisterForComfortPayObj
        from ..models.signed_card_id_obj import SignedCardIdObj
        from ..models.transaction_ipsp_data import TransactionIPSPData

        d = dict(src_dict)
        card_holder = d.pop("cardHolder")

        _card_pay_lang_override = d.pop("cardPayLangOverride", UNSET)
        card_pay_lang_override: Union[Unset, CardDetailCardPayLangOverride]
        if isinstance(_card_pay_lang_override, Unset):
            card_pay_lang_override = UNSET
        else:
            card_pay_lang_override = CardDetailCardPayLangOverride(_card_pay_lang_override)

        is_pre_authorization = d.pop("isPreAuthorization", UNSET)

        _billing_address = d.pop("billingAddress", UNSET)
        billing_address: Union[Unset, Address]
        if isinstance(_billing_address, Unset):
            billing_address = UNSET
        else:
            billing_address = Address.from_dict(_billing_address)

        _shipping_address = d.pop("shippingAddress", UNSET)
        shipping_address: Union[Unset, Address]
        if isinstance(_shipping_address, Unset):
            shipping_address = UNSET
        else:
            shipping_address = Address.from_dict(_shipping_address)

        def _parse_comfort_pay(data: object) -> Union["RegisterForComfortPayObj", "SignedCardIdObj", Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemascard_identifier_or_register_type_0 = RegisterForComfortPayObj.from_dict(data)

                return componentsschemascard_identifier_or_register_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemascard_identifier_or_register_type_1 = SignedCardIdObj.from_dict(data)

            return componentsschemascard_identifier_or_register_type_1

        comfort_pay = _parse_comfort_pay(d.pop("comfortPay", UNSET))

        _ipsp_data = d.pop("ipspData", UNSET)
        ipsp_data: Union[Unset, TransactionIPSPData]
        if isinstance(_ipsp_data, Unset):
            ipsp_data = UNSET
        else:
            ipsp_data = TransactionIPSPData.from_dict(_ipsp_data)

        card_detail = cls(
            card_holder=card_holder,
            card_pay_lang_override=card_pay_lang_override,
            is_pre_authorization=is_pre_authorization,
            billing_address=billing_address,
            shipping_address=shipping_address,
            comfort_pay=comfort_pay,
            ipsp_data=ipsp_data,
        )

        card_detail.additional_properties = d
        return card_detail

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
