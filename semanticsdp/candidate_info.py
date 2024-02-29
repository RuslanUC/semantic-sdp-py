from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import BaseSdp


@dataclass(slots=True, eq=True)
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
