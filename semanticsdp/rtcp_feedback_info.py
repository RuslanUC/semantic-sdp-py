from __future__ import annotations

from dataclasses import dataclass, field

from semanticsdp import BaseSdp


@dataclass(slots=True, eq=True)
class RTCPFeedbackInfo(BaseSdp):
    id: str
    params: list[str] = field(default_factory=list)

    def __hash__(self):
        return hash(self.id)
