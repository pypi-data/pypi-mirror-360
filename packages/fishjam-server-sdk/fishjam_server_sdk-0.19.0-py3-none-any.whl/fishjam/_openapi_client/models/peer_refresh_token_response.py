from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.peer_refresh_token_response_data import PeerRefreshTokenResponseData


T = TypeVar("T", bound="PeerRefreshTokenResponse")


@_attrs_define
class PeerRefreshTokenResponse:
    """Response containing new peer token"""

    data: "PeerRefreshTokenResponseData"
    """"""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)
    """@private"""

    def to_dict(self) -> Dict[str, Any]:
        """@private"""
        data = self.data.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """@private"""
        from ..models.peer_refresh_token_response_data import (
            PeerRefreshTokenResponseData,
        )

        d = src_dict.copy()
        data = PeerRefreshTokenResponseData.from_dict(d.pop("data"))

        peer_refresh_token_response = cls(
            data=data,
        )

        peer_refresh_token_response.additional_properties = d
        return peer_refresh_token_response

    @property
    def additional_keys(self) -> List[str]:
        """@private"""
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
