from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.room_config_room_type import RoomConfigRoomType
from ..models.room_config_video_codec import RoomConfigVideoCodec
from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomConfig")


@_attrs_define
class RoomConfig:
    """Room configuration"""

    max_peers: Union[Unset, None, int] = UNSET
    """Maximum amount of peers allowed into the room"""
    public: Union[Unset, bool] = False
    """True if livestream viewers can omit specifying a token."""
    room_type: Union[Unset, RoomConfigRoomType] = RoomConfigRoomType.CONFERENCE
    """The use-case of the room. If not provided, this defaults to conference."""
    video_codec: Union[Unset, None, RoomConfigVideoCodec] = UNSET
    """Enforces video codec for each peer in the room"""
    webhook_url: Union[Unset, None, str] = UNSET
    """URL where Fishjam notifications will be sent"""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)
    """@private"""

    def to_dict(self) -> Dict[str, Any]:
        """@private"""
        max_peers = self.max_peers
        public = self.public
        room_type: Union[Unset, str] = UNSET
        if not isinstance(self.room_type, Unset):
            room_type = self.room_type.value

        video_codec: Union[Unset, None, str] = UNSET
        if not isinstance(self.video_codec, Unset):
            video_codec = self.video_codec.value if self.video_codec else None

        webhook_url = self.webhook_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if max_peers is not UNSET:
            field_dict["maxPeers"] = max_peers
        if public is not UNSET:
            field_dict["public"] = public
        if room_type is not UNSET:
            field_dict["roomType"] = room_type
        if video_codec is not UNSET:
            field_dict["videoCodec"] = video_codec
        if webhook_url is not UNSET:
            field_dict["webhookUrl"] = webhook_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """@private"""
        d = src_dict.copy()
        max_peers = d.pop("maxPeers", UNSET)

        public = d.pop("public", UNSET)

        _room_type = d.pop("roomType", UNSET)
        room_type: Union[Unset, RoomConfigRoomType]
        if isinstance(_room_type, Unset):
            room_type = UNSET
        else:
            room_type = RoomConfigRoomType(_room_type)

        _video_codec = d.pop("videoCodec", UNSET)
        video_codec: Union[Unset, None, RoomConfigVideoCodec]
        if _video_codec is None:
            video_codec = None
        elif isinstance(_video_codec, Unset):
            video_codec = UNSET
        else:
            video_codec = RoomConfigVideoCodec(_video_codec)

        webhook_url = d.pop("webhookUrl", UNSET)

        room_config = cls(
            max_peers=max_peers,
            public=public,
            room_type=room_type,
            video_codec=video_codec,
            webhook_url=webhook_url,
        )

        room_config.additional_properties = d
        return room_config

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
