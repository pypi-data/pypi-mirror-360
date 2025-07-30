from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.card_pay_status import CardPayStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.card_pay_amount import CardPayAmount
    from ..models.card_pay_status_structure_comfort_pay import CardPayStatusStructureComfortPay


T = TypeVar("T", bound="CardPayStatusStructure")


@_attrs_define
class CardPayStatusStructure:
    """card pay status structure

    Attributes:
        status (CardPayStatus):
            **CardPay status**

            | Enum      | description |
            | ---------------- | ------------|
            | INIT              | initialized transaction     |
            | OK              | processed successfully transaction     |
            | FAIL              | failed transaction |
            | PA              | pre-authorization |
            | CPA              | completed pre-authorization |
            | SPA               | canceled preauthorization |
            | XPA               | expired pre-authorization |
            | CB               | returned payment |
            | AUTH_REQUIRED               | 3D secure authorization required |
            | AUTH_EXPIRED               | authorization expired |
            | AUTH_CANCELED               | authorization canceled |
             Example: OK.
        currency (str): ISO 4217 Alpha 3 currency code.
             Example: EUR.
        amount (Union[Unset, float]): The amount given with fractional digits, where fractions must be compliant to the
            currency definition. Negative amounts are signed by minus.
            The decimal separator is a dot.

            **Example:**
            Valid representations for EUR with up to two decimals are:

              * 1056
              * 5768.2
              * -1.50
              * 5877.78
             Example: 120.
        pre_authorization (Union[Unset, CardPayAmount]):
        charge_back (Union[Unset, CardPayAmount]):
        comfort_pay (Union[Unset, CardPayStatusStructureComfortPay]):
        masked_card_number (Union[Unset, str]): Masked card number.
        reason_code (Union[Unset, str]):
        payment_authorization_code (Union[Unset, str]): Payment authorization code
    """

    status: CardPayStatus
    currency: str
    amount: Union[Unset, float] = UNSET
    pre_authorization: Union[Unset, "CardPayAmount"] = UNSET
    charge_back: Union[Unset, "CardPayAmount"] = UNSET
    comfort_pay: Union[Unset, "CardPayStatusStructureComfortPay"] = UNSET
    masked_card_number: Union[Unset, str] = UNSET
    reason_code: Union[Unset, str] = UNSET
    payment_authorization_code: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        currency = self.currency

        amount = self.amount

        pre_authorization: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.pre_authorization, Unset):
            pre_authorization = self.pre_authorization.to_dict()

        charge_back: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.charge_back, Unset):
            charge_back = self.charge_back.to_dict()

        comfort_pay: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.comfort_pay, Unset):
            comfort_pay = self.comfort_pay.to_dict()

        masked_card_number = self.masked_card_number

        reason_code: Union[Unset, str]
        if isinstance(self.reason_code, Unset):
            reason_code = UNSET
        else:
            reason_code = self.reason_code

        payment_authorization_code = self.payment_authorization_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "currency": currency,
            }
        )
        if amount is not UNSET:
            field_dict["amount"] = amount
        if pre_authorization is not UNSET:
            field_dict["preAuthorization"] = pre_authorization
        if charge_back is not UNSET:
            field_dict["chargeBack"] = charge_back
        if comfort_pay is not UNSET:
            field_dict["comfortPay"] = comfort_pay
        if masked_card_number is not UNSET:
            field_dict["maskedCardNumber"] = masked_card_number
        if reason_code is not UNSET:
            field_dict["reasonCode"] = reason_code
        if payment_authorization_code is not UNSET:
            field_dict["paymentAuthorizationCode"] = payment_authorization_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.card_pay_amount import CardPayAmount
        from ..models.card_pay_status_structure_comfort_pay import CardPayStatusStructureComfortPay

        d = dict(src_dict)
        status = CardPayStatus(d.pop("status"))

        currency = d.pop("currency")

        amount = d.pop("amount", UNSET)

        _pre_authorization = d.pop("preAuthorization", UNSET)
        pre_authorization: Union[Unset, CardPayAmount]
        if isinstance(_pre_authorization, Unset):
            pre_authorization = UNSET
        else:
            pre_authorization = CardPayAmount.from_dict(_pre_authorization)

        _charge_back = d.pop("chargeBack", UNSET)
        charge_back: Union[Unset, CardPayAmount]
        if isinstance(_charge_back, Unset):
            charge_back = UNSET
        else:
            charge_back = CardPayAmount.from_dict(_charge_back)

        _comfort_pay = d.pop("comfortPay", UNSET)
        comfort_pay: Union[Unset, CardPayStatusStructureComfortPay]
        if isinstance(_comfort_pay, Unset):
            comfort_pay = UNSET
        else:
            comfort_pay = CardPayStatusStructureComfortPay.from_dict(_comfort_pay)

        masked_card_number = d.pop("maskedCardNumber", UNSET)

        def _parse_reason_code(data: object) -> Union[Unset, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, str], data)

        reason_code = _parse_reason_code(d.pop("reasonCode", UNSET))

        payment_authorization_code = d.pop("paymentAuthorizationCode", UNSET)

        card_pay_status_structure = cls(
            status=status,
            currency=currency,
            amount=amount,
            pre_authorization=pre_authorization,
            charge_back=charge_back,
            comfort_pay=comfort_pay,
            masked_card_number=masked_card_number,
            reason_code=reason_code,
            payment_authorization_code=payment_authorization_code,
        )

        card_pay_status_structure.additional_properties = d
        return card_pay_status_structure

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
