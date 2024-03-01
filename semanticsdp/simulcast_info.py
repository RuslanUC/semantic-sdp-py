from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import SimulcastStreamInfo, BaseSdp


@dataclass(slots=True, eq=True)
class SimulcastInfo(BaseSdp):
    send: list[list[SimulcastStreamInfo]]
    recv: list[list[SimulcastStreamInfo]]

    @classmethod
    def from_dict(cls, data: dict) -> SimulcastInfo:
        for streams in data["send"]:
            for idx, stream in enumerate(streams):
                streams[idx] = SimulcastStreamInfo.from_dict(stream)
        for streams in data["recv"]:
            for idx, stream in enumerate(streams):
                streams[idx] = SimulcastStreamInfo.from_dict(stream)
        return super(SimulcastInfo, cls).from_dict(data)
