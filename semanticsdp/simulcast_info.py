from __future__ import annotations

from dataclasses import dataclass

from semanticsdp import SimulcastStreamInfo, BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class SimulcastInfo(BaseSdp):
    send: list[list[SimulcastStreamInfo]]
    recv: list[list[SimulcastStreamInfo]]

    def to_dict(self) -> dict:
        return {
            "send": [[stream.to_dict() for stream in streams] for streams in self.send],
            "recv": [[stream.to_dict() for stream in streams] for streams in self.recv],
        }

    @classmethod
    def from_dict(cls, data: dict) -> SimulcastInfo:
        new_data = {"send": [], "recv": []}

        for streams in data["send"]:
            new_data["send"].append([])
            for stream in streams:
                new_data["send"][-1].append(SimulcastStreamInfo.from_dict(stream))

        for streams in data["recv"]:
            new_data["recv"].append([])
            for stream in streams:
                new_data["recv"][-1].append(SimulcastStreamInfo.from_dict(stream))

        return super(SimulcastInfo, cls).from_dict(new_data)
