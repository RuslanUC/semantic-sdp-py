from __future__ import annotations

from dataclasses import dataclass, field

from semanticsdp import BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class RTCPFeedbackInfo(BaseSdp):
    id: str
    params: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "params": self.params.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        data["params"] = data.pop("params", []).copy()
        return super(RTCPFeedbackInfo, cls).from_dict(data)

    def __hash__(self):
        return hash(self.id)
