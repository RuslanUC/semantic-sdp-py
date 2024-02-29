from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import BaseSdp


@dataclass(slots=True, eq=True)
class CryptoInfo(BaseSdp):
    tag: int
    suite: str
    key_params: str
    session_params: str
