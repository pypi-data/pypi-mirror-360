from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.direct_transaction_status import DirectTransactionStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.direct_transaction_data import DirectTransactionData


T = TypeVar("T", bound="DirectTransactionTaskStatusResponse")


@_attrs_define
class DirectTransactionTaskStatusResponse:
    """
    Attributes:
        transaction_id (Union[Unset, str]): This identification of the transaction, available only in state OK and FAIL
            Example: 5e8bda08-5521-11ed-bdc3-0242ac120002.
        status (Union[Unset, DirectTransactionStatus]):
        transaction_data (Union[Unset, DirectTransactionData]):
    """

    transaction_id: Union[Unset, str] = UNSET
    status: Union[Unset, DirectTransactionStatus] = UNSET
    transaction_data: Union[Unset, "DirectTransactionData"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        transaction_id = self.transaction_id

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        transaction_data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.transaction_data, Unset):
            transaction_data = self.transaction_data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if transaction_id is not UNSET:
            field_dict["transactionId"] = transaction_id
        if status is not UNSET:
            field_dict["status"] = status
        if transaction_data is not UNSET:
            field_dict["transactionData"] = transaction_data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.direct_transaction_data import DirectTransactionData

        d = dict(src_dict)
        transaction_id = d.pop("transactionId", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, DirectTransactionStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = DirectTransactionStatus(_status)

        _transaction_data = d.pop("transactionData", UNSET)
        transaction_data: Union[Unset, DirectTransactionData]
        if isinstance(_transaction_data, Unset):
            transaction_data = UNSET
        else:
            transaction_data = DirectTransactionData.from_dict(_transaction_data)

        direct_transaction_task_status_response = cls(
            transaction_id=transaction_id,
            status=status,
            transaction_data=transaction_data,
        )

        direct_transaction_task_status_response.additional_properties = d
        return direct_transaction_task_status_response

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
