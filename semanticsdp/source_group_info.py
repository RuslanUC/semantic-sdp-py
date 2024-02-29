from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import BaseSdp


@dataclass(slots=True, eq=True)
class SourceGroupInfo(BaseSdp):
    semantics: str
    ssrcs: list[int]
