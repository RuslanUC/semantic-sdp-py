from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import BaseSdp


@dataclass(slots=True, eq=True)
class SimulcastStreamInfo(BaseSdp):
    id: str
    paused: bool
