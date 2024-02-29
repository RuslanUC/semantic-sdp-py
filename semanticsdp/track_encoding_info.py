from __future__ import annotations

from dataclasses import dataclass, field

from semanticsdp import BaseSdp, CodecInfo


@dataclass(slots=True, eq=True)
class TrackEncodingInfo(BaseSdp):
    id: str
    paused: bool = False
    codecs: dict[int, CodecInfo] = field(default_factory=dict)
    params: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> TrackEncodingInfo:
        data["codecs"] = {key: CodecInfo.from_dict(codec) for key, codec in data.pop("codecs", {}).items()}
        return super(TrackEncodingInfo, cls).from_dict(data)
