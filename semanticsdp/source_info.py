from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class SourceInfo(BaseSdp):
    ssrc: int
    cname: str | None = None
    stream_id: str | None = None
    track_id: str | None = None
