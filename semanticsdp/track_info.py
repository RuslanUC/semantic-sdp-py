from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from semanticsdp import TrackEncodingInfo, SourceGroupInfo, BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class TrackInfo(BaseSdp):
    media: Literal["audio", "video", "application"]
    id: str
    media_id: str | None = None
    ssrcs: list[int] = field(default_factory=list)
    groups: list[SourceGroupInfo] = field(default_factory=list)
    encodings: list[list[TrackEncodingInfo]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "media": self.media,
            "id": self.id,
            "media_id": self.media_id,
            "ssrcs": self.ssrcs.copy(),
            "groups": [group.to_dict() for group in self.groups],
            "encodings": [[encoding.to_dict() for encoding in encodings] for encodings in self.encodings],
        }

    @classmethod
    def from_dict(cls, data: dict) -> TrackInfo:
        new_data = data.copy()
        new_data["ssrcs"] = new_data.pop("ssrcs", []).copy()
        new_data["groups"] = [SourceGroupInfo.from_dict(group) for group in new_data["groups"]]
        new_data["encodings"] = []

        for encodings in data["encodings"]:
            new_data["encodings"].append([])
            for encoding in encodings:
                new_data["encodings"][-1].append(TrackEncodingInfo.from_dict(encoding))

        return super(TrackInfo, cls).from_dict(new_data)
