"""
    .. include:: ../README.md
"""

# pylint: disable=locally-disabled, no-name-in-module, import-error

# Exceptions and Server Messages

# API
# pylint: disable=locally-disabled, no-name-in-module, import-error

# Exceptions and Server Messages
from fishjam import errors, events, peer, room

# API
from fishjam._webhook_notifier import receive_binary
from fishjam._ws_notifier import FishjamNotifier
from fishjam.api._fishjam_client import (
    FishjamClient,
    Peer,
    PeerOptions,
    Room,
    RoomOptions,
)

__all__ = [
    "FishjamClient",
    "FishjamNotifier",
    "receive_binary",
    "PeerOptions",
    "RoomOptions",
    "Room",
    "Peer",
    "events",
    "errors",
    "room",
    "peer",
]

__docformat__ = "restructuredtext"
