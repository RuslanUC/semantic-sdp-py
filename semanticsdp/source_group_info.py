from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class SourceGroupInfo(BaseSdp):
    semantics: str
    ssrcs: list[int]

    def to_dict(self) -> dict:
        return {
            "semantics": self.semantics,
            "ssrcs": self.ssrcs.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()
        data["ssrcs"] = data.pop("ssrcs", []).copy()
        return super(SourceGroupInfo, cls).from_dict(data)
