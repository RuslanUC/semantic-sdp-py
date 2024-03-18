from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import Setup, BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class DTLSInfo(BaseSdp):
    setup: Setup
    hash: str
    fingerprint: str

    def to_dict(self) -> dict:
        return super().to_dict() | {"setup": self.setup.value}

    @classmethod
    def from_dict(cls, data: dict) -> DTLSInfo:
        data = data.copy()
        data["setup"] = Setup(data.pop("setup"))
        return super(DTLSInfo, cls).from_dict(data)
