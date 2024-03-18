from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class CryptoInfo(BaseSdp):
    tag: int
    suite: str
    key_params: str
    session_params: str
