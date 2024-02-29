from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import SimulcastStreamInfo, BaseSdp


@dataclass(slots=True, eq=True)
class SimulcastInfo(BaseSdp):
    send: list[SimulcastStreamInfo]
    recv: list[SimulcastStreamInfo]

    @classmethod
    def from_dict(cls, data: dict) -> SimulcastInfo:
        data["send"] = [SimulcastStreamInfo.from_dict(stream) for stream in data["send"]]
        data["recv"] = [SimulcastStreamInfo.from_dict(stream) for stream in data["recv"]]
        return super(SimulcastInfo, cls).from_dict(data)
