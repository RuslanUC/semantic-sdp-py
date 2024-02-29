from __future__ import annotations

from enum import Enum


class Setup(Enum):
    ACTIVE = "active"
    PASSIVE = "passive"
    ACTPASS = "actpass"
    INACTIVE = "inactive"

    @classmethod
    def reverse(cls, setup: Setup, preferActive: bool = False) -> Setup:
        if setup == Setup.ACTPASS:
            return Setup.ACTIVE if preferActive else Setup.PASSIVE
        return _reverse[setup]


_reverse = {
    Setup.ACTIVE: Setup.PASSIVE,
    Setup.PASSIVE: Setup.ACTIVE,
    Setup.ACTPASS: Setup.ACTPASS,
    Setup.INACTIVE: Setup.INACTIVE,
}
