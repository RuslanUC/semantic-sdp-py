from __future__ import annotations

from dataclasses import dataclass, field

from semanticsdp import TrackInfo, BaseSdp


@dataclass(slots=True, eq=True)
class StreamInfo(BaseSdp):
    id: str
    tracks: dict[str, TrackInfo] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> StreamInfo:
        data["tracks"] = {key: TrackInfo.from_dict(track) for key, track in data.pop("tracks", {}).items()}
        return super(StreamInfo, cls).from_dict(data)
