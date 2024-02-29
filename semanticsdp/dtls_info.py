from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import Setup, BaseSdp


@dataclass(slots=True, eq=True)
class DTLSInfo(BaseSdp):
    setup: Setup
    hash: str
    fingerprint: str

    def to_dict(self) -> dict:
        return super().to_dict() | {"setup": self.setup.value}

    @classmethod
    def from_dict(cls, data: dict) -> DTLSInfo:
        data["setup"] = Setup(data.pop("setup"))
        return super(DTLSInfo, cls).from_dict(data)
