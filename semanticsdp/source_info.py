from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import BaseSdp


@dataclass(slots=True, eq=True)
class SourceInfo(BaseSdp):
    ssrc: int
    cname: str | None = None
    stream_id: str | None = None
    track_id: str | None = None
