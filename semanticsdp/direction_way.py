from __future__ import annotations

from enum import Enum


class DirectionWay(Enum):
    SEND = "send"
    RECV = "recv"

    @classmethod
    def reverse(cls, direction: DirectionWay) -> DirectionWay:
        return _reverse[direction]


_reverse = {
    DirectionWay.SEND: DirectionWay.RECV,
    DirectionWay.RECV: DirectionWay.SEND,
}
