from __future__ import annotations

from enum import Enum


class Direction(Enum):
    SENDRECV = "sendrecv"
    SENDONLY = "sendonly"
    RECVONLY = "recvonly"
    INACTIVE = "inactive"

    @classmethod
    def reverse(cls, direction: Direction) -> Direction:
        return _reverse[direction]


_reverse = {
    Direction.SENDRECV: Direction.SENDRECV,
    Direction.SENDONLY: Direction.RECVONLY,
    Direction.RECVONLY: Direction.SENDONLY,
    Direction.INACTIVE: Direction.INACTIVE,
}
