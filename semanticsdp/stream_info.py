from __future__ import annotations

from dataclasses import dataclass, field

from semanticsdp import TrackInfo, BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class StreamInfo(BaseSdp):
    id: str
    tracks: dict[str, TrackInfo] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tracks": {key: track.to_dict() for key, track in self.tracks.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> StreamInfo:
        data = data.copy()
        data["tracks"] = {key: TrackInfo.from_dict(track) for key, track in data.pop("tracks", {}).items()}
        return super(StreamInfo, cls).from_dict(data)
