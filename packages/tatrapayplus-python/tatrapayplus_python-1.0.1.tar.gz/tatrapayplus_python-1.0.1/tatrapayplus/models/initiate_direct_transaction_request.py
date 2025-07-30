from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.amount import Amount
    from ..models.apple_pay_token import ApplePayToken
    from ..models.direct_transaction_tds_data import DirectTransactionTDSData
    from ..models.payment_symbols import PaymentSymbols
    from ..models.transaction_ipsp_data import TransactionIPSPData


T = TypeVar("T", bound="InitiateDirectTransactionRequest")


@_attrs_define
class InitiateDirectTransactionRequest:
    """Body for direct transaction initiation

    Attributes:
        amount (Amount):
        end_to_end (Union['PaymentSymbols', str]): EndToEndId or paymentSymbols
        tds_data (DirectTransactionTDSData): In case of Direct API either cardHolder or email is mandatory
        token (Union['ApplePayToken', str]):
        is_pre_authorization (Union[Unset, bool]): If true - pre-authorization transaction
        ipsp_data (Union[Unset, TransactionIPSPData]): In case of payment facilitator mode - this structure is mandatory
    """

    amount: "Amount"
    end_to_end: Union["PaymentSymbols", str]
    tds_data: "DirectTransactionTDSData"
    token: Union["ApplePayToken", str]
    is_pre_authorization: Union[Unset, bool] = UNSET
    ipsp_data: Union[Unset, "TransactionIPSPData"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.apple_pay_token import ApplePayToken
        from ..models.payment_symbols import PaymentSymbols

        amount = self.amount.to_dict()

        end_to_end: Union[dict[str, Any], str]
        if isinstance(self.end_to_end, PaymentSymbols):
            end_to_end = self.end_to_end.to_dict()
        else:
            end_to_end = self.end_to_end

        tds_data = self.tds_data.to_dict()

        token: Union[dict[str, Any], str]
        if isinstance(self.token, ApplePayToken):
            token = self.token.to_dict()
        else:
            token = self.token

        is_pre_authorization = self.is_pre_authorization

        ipsp_data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.ipsp_data, Unset):
            ipsp_data = self.ipsp_data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount": amount,
                "endToEnd": end_to_end,
                "tdsData": tds_data,
                "token": token,
            }
        )
        if is_pre_authorization is not UNSET:
            field_dict["isPreAuthorization"] = is_pre_authorization
        if ipsp_data is not UNSET:
            field_dict["ipspData"] = ipsp_data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.amount import Amount
        from ..models.apple_pay_token import ApplePayToken
        from ..models.direct_transaction_tds_data import DirectTransactionTDSData
        from ..models.payment_symbols import PaymentSymbols
        from ..models.transaction_ipsp_data import TransactionIPSPData

        d = dict(src_dict)
        amount = Amount.from_dict(d.pop("amount"))

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

        tds_data = DirectTransactionTDSData.from_dict(d.pop("tdsData"))

        def _parse_token(data: object) -> Union["ApplePayToken", str]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemastoken_type_0 = ApplePayToken.from_dict(data)

                return componentsschemastoken_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ApplePayToken", str], data)

        token = _parse_token(d.pop("token"))

        is_pre_authorization = d.pop("isPreAuthorization", UNSET)

        _ipsp_data = d.pop("ipspData", UNSET)
        ipsp_data: Union[Unset, TransactionIPSPData]
        if isinstance(_ipsp_data, Unset):
            ipsp_data = UNSET
        else:
            ipsp_data = TransactionIPSPData.from_dict(_ipsp_data)

        initiate_direct_transaction_request = cls(
            amount=amount,
            end_to_end=end_to_end,
            tds_data=tds_data,
            token=token,
            is_pre_authorization=is_pre_authorization,
            ipsp_data=ipsp_data,
        )

        initiate_direct_transaction_request.additional_properties = d
        return initiate_direct_transaction_request

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
