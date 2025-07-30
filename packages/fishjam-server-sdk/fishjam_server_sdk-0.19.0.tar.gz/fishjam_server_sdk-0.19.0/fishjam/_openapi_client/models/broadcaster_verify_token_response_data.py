from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BroadcasterVerifyTokenResponseData")


@_attrs_define
class BroadcasterVerifyTokenResponseData:
    """ """

    authenticated: bool
    """None"""
    stream_id: Union[Unset, str] = UNSET
    """None"""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)
    """@private"""

    def to_dict(self) -> Dict[str, Any]:
        """@private"""
        authenticated = self.authenticated
        stream_id = self.stream_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authenticated": authenticated,
            }
        )
        if stream_id is not UNSET:
            field_dict["streamId"] = stream_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """@private"""
        d = src_dict.copy()
        authenticated = d.pop("authenticated")

        stream_id = d.pop("streamId", UNSET)

        broadcaster_verify_token_response_data = cls(
            authenticated=authenticated,
            stream_id=stream_id,
        )

        broadcaster_verify_token_response_data.additional_properties = d
        return broadcaster_verify_token_response_data

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
