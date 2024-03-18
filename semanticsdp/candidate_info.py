from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class CandidateInfo(BaseSdp):
    foundation: str
    component_id: int
    transport: str
    priority: int
    address: str
    port: int
    type: str
    rel_addr: str | None = None
    rel_port: int | None = None
