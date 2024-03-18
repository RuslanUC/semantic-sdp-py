from __future__ import annotations

from dataclasses import dataclass, field

from semanticsdp import DirectionWay, BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class RIDInfo(BaseSdp):
    id: str
    direction: DirectionWay
    formats: list[int] = field(default_factory=list)
    params: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "direction": self.direction.value,
            "formats": self.formats.copy(),
            "params": self.params.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> RIDInfo:
        data = data.copy()
        data["formats"] = data.pop("formats", []).copy()
        data["params"] = data.pop("params", {}).copy()
        data["direction"] = DirectionWay(data.pop("direction"))
        return super(RIDInfo, cls).from_dict(data)
