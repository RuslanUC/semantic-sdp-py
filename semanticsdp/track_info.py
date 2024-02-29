from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from semanticsdp import TrackEncodingInfo, SourceGroupInfo, BaseSdp


@dataclass(slots=True, eq=True)
class TrackInfo(BaseSdp):
    media: Literal["audio", "video", "application"]
    id: str
    media_id: str | None = None
    ssrcs: list[int] = field(default_factory=list)
    groups: list[SourceGroupInfo] = field(default_factory=list)
    encodings: list[TrackEncodingInfo] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> TrackInfo:
        data["groups"] = [SourceGroupInfo.from_dict(group) for group in data["groups"]]
        data["encodings"] = [TrackEncodingInfo.from_dict(encoding) for encoding in data["encodings"]]
        return super(TrackInfo, cls).from_dict(data)
