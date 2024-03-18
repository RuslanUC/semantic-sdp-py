from __future__ import annotations

from dataclasses import dataclass, field

from semanticsdp import RTCPFeedbackInfo, BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


@dataclass(**DATACLASS_KWARGS)
class CodecInfo(BaseSdp):
    codec: str
    type: int
    rtx: int | None = None
    channels: int | None = None
    params: dict[str, str] = field(default_factory=dict)
    rtcpfbs: set[RTCPFeedbackInfo] = field(default_factory=set)

    def to_dict(self) -> dict:
        return {
            "codec": self.codec,
            "type": self.type,
            "rtx": self.rtx,
            "channels": self.channels,
            "params": self.params.copy(),
            "rtcpfbs": [rtcpfb.to_dict() for rtcpfb in self.rtcpfbs],
        }

    @classmethod
    def from_dict(cls, data: dict) -> CodecInfo:
        data = data.copy()
        data["params"] = data.pop("params", {}).copy()
        data["rtcpfbs"] = set([RTCPFeedbackInfo.from_dict(rtcpfb) for rtcpfb in data.pop("rtcpfbs", [])])
        return super(CodecInfo, cls).from_dict(data)

    @classmethod
    def map_from_names(cls, names: list[str], rtx: bool, rtcpfbs: list[RTCPFeedbackInfo]) -> dict[int, CodecInfo]:
        codecs = {}
        dyn = 96

        for element in names:
            params = element.split(";")
            name = params.pop(0)

            if name == "pmcu":
                pt = 0
            elif name == "pcma":
                pt = 8
            else:
                pt = dyn
                dyn += 1

            kw = {"codec": name, "type": pt}
            if name == "opus":
                kw["channels"] = 2
            elif name == "multiopus":
                kw["channels"] = 6

            if rtx and name not in {"ulpfec", "flexfec-03", "red"}:
                kw["rtx"] = dyn
                dyn += 1

            kw["rtcpfbs"] = set()
            for rtcpfb in rtcpfbs:
                kw["rtcpfbs"].add(RTCPFeedbackInfo(rtcpfb.id, rtcpfb.params))

            kw["params"] = {}
            for elem in params:
                param_name, param_value = elem.split("=", 1)
                kw["params"][param_name.strip()] = param_value.strip()

            codecs[pt] = CodecInfo(**kw)

        return codecs
