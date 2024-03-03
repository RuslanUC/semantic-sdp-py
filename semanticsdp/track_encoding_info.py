from __future__ import annotations

from dataclasses import dataclass, field

from semanticsdp import BaseSdp, CodecInfo


@dataclass(slots=True, eq=True)
class TrackEncodingInfo(BaseSdp):
    id: str
    paused: bool = False
    codecs: dict[int, CodecInfo] = field(default_factory=dict)
    params: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "paused": self.paused,
            "codecs": {key: codec.to_dict() for key, codec in self.codecs.items()},
            "params": self.params.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> TrackEncodingInfo:
        data = data.copy()
        data["params"] = data.pop("params", {}).copy()
        data["codecs"] = {key: CodecInfo.from_dict(codec) for key, codec in data.pop("codecs", {}).items()}
        return super(TrackEncodingInfo, cls).from_dict(data)
