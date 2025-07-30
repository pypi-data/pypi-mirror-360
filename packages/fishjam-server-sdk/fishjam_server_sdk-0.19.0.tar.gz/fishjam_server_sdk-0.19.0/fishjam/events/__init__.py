"""
.. include:: ../../docs/server_notifications.md
"""

# Exported messages
from fishjam.events._protos.fishjam import (
    ServerMessagePeerAdded,
    ServerMessagePeerConnected,
    ServerMessagePeerCrashed,
    ServerMessagePeerDeleted,
    ServerMessagePeerDisconnected,
    ServerMessagePeerMetadataUpdated,
    ServerMessageRoomCrashed,
    ServerMessageRoomCreated,
    ServerMessageRoomDeleted,
    ServerMessageTrack,
    ServerMessageTrackAdded,
    ServerMessageTrackMetadataUpdated,
    ServerMessageTrackRemoved,
    ServerMessageTrackType,
)

__all__ = [
    "ServerMessageRoomCreated",
    "ServerMessageRoomDeleted",
    "ServerMessageRoomCrashed",
    "ServerMessagePeerAdded",
    "ServerMessagePeerConnected",
    "ServerMessagePeerDeleted",
    "ServerMessagePeerDisconnected",
    "ServerMessagePeerMetadataUpdated",
    "ServerMessagePeerCrashed",
    "ServerMessageTrack",
    "ServerMessageTrackType",
    "ServerMessageTrackAdded",
    "ServerMessageTrackMetadataUpdated",
    "ServerMessageTrackRemoved",
]
