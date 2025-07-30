from __future__ import annotations
from typing import TYPE_CHECKING, List

from .consts import SDK_LOGGER  # Use SDK logger

if TYPE_CHECKING:
    from .wiim_device import WiimDevice  # Changed from LinkPlayBridge


class WiimMultiroomGroup:  # Renamed from LinkPlayMultiroom
    """
    Represents a WiiM multiroom group, primarily for HTTP-based multiroom commands.
    The actual state (leader, followers) is now managed by WiimController based on
    HTTP API responses. This class could be a data structure or provide helper methods
    if multiroom commands are complex.
    """

    leader: WiimDevice
    followers: List[WiimDevice]

    def __init__(self, leader: WiimDevice):
        self.leader = leader
        self.followers = []
        self.logger = SDK_LOGGER

    def to_dict(self):
        """Return the state of the WiimMultiroomGroup."""
        return {
            "leader_udn": self.leader.udn,
            "follower_udns": [follower.udn for follower in self.followers],
        }


# This file is now mostly empty or could be removed.
SDK_LOGGER.info(
    "wiim/bridge.py is now minimal; functionality moved to WiimDevice and WiimController."
)
