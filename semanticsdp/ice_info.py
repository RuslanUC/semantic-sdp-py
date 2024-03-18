from __future__ import annotations

from dataclasses import dataclass
from os import urandom

from semanticsdp import BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class IceInfo(BaseSdp):
    ufrag: str
    pwd: str
    lite: bool = False
    end_of_candidates: bool = False

    @classmethod
    def generate(cls, lite: bool = False) -> IceInfo:
        return cls(urandom(8).hex(), urandom(24).hex(), lite)
