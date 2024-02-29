from __future__ import annotations

from dataclasses import dataclass, field

from semanticsdp import DirectionWay, BaseSdp


@dataclass(slots=True, eq=True)
class RIDInfo(BaseSdp):
    id: str
    direction: DirectionWay
    formats: list[int] = field(default_factory=list)
    params: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return super().to_dict() | {"direction": self.direction.value}

    @classmethod
    def from_dict(cls, data: dict) -> RIDInfo:
        data["direction"] = DirectionWay(data.pop("direction"))
        return super(RIDInfo, cls).from_dict(data)
