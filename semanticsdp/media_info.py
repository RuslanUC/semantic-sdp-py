from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypedDict

from semanticsdp import DirectionWay, Direction, CodecInfo, RIDInfo, SimulcastInfo, DatachannelInfo, RTCPFeedbackInfo, \
    BaseSdp
from semanticsdp._dataclass_fix import DATACLASS_KWARGS


class SupportedMedia(TypedDict):
    codecs: dict[int, CodecInfo] | list[str]
    extensions: list[str] | None
    simulcast: bool | None
    rtcpfbs: list[RTCPFeedbackInfo]
    rtx: bool | None
    datachannel: DatachannelInfo | None


@dataclass(**DATACLASS_KWARGS)
class MediaInfo(BaseSdp):
    id: str
    type: Literal["audio", "video", "application"]
    direction: Direction = Direction.SENDRECV
    extensions: dict[int, str] = field(default_factory=dict)
    codecs: dict[int, CodecInfo] = field(default_factory=dict)
    rids: dict[str, RIDInfo] = field(default_factory=dict)
    simulcast: SimulcastInfo | None = None
    bitrate: int = 0
    control: str | None = None
    datachannel: DatachannelInfo | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "direction": self.direction.value,
            "extensions": self.extensions.copy(),
            "codecs": [codec.to_dict() for codec in self.codecs.values()],
            "rids": [rid.to_dict() for rid in self.rids.values()],
            "simulcast": self.simulcast.to_dict() if self.simulcast else None,
            "bitrate": self.bitrate,
            "control": self.control,
            "datachannel": self.datachannel.to_dict() if self.datachannel else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MediaInfo:
        data = data.copy()
        data["extensions"] = data.pop("extensions", {}).copy()
        data["codecs"] = {codec["type"]: CodecInfo.from_dict(codec) for codec in data.pop("codecs", [])}
        data["rids"] = {rid["id"]: RIDInfo.from_dict(rid) for rid in data.pop("rids", [])}
        data["simulcast"] = SimulcastInfo.from_dict(data["simulcast"]) if data.get("simulcast") else None
        data["datachannel"] = DatachannelInfo.from_dict(data["datachannel"]) if data.get("datachannel") else None
        data["direction"] = Direction(data["direction"])
        return super(MediaInfo, cls).from_dict(data)

    def answer(self, supported: SupportedMedia):
        answer = MediaInfo(self.id, self.type)
        if not supported:
            answer.direction = Direction.INACTIVE
            return answer

        answer.direction = Direction.reverse(self.direction)
        if codecs := supported["codecs"]:
            sup_codecs = codecs
            if isinstance(codecs, list):
                sup_codecs = CodecInfo.map_from_names(codecs, supported.get("rtx"), supported.get("rtcpfbs") or [])

            for codec in self.codecs.values():
                for sup in sup_codecs.values():
                    if sup.codec != codec.codec:
                        continue
                    if sup.codec == "h264" and \
                            sup.params.get("packetization-mode") != codec.params.get("packetization-mode", "0"):
                        continue
                    if sup.codec == "h264" and "profile-level-id" in sup.params and \
                            sup.params.get("profile-level-id") != codec.params.get("profile-level-id"):
                        continue
                    if sup.codec == "multiopus" and "num_streams" in sup.params and \
                            sup.params.get("num_streams") != codec.params.get("num_streams"):
                        continue

                    cl = sup.clone()
                    cl.type = codec.type
                    cl.rtx = codec.rtx
                    cl.channels = codec.channels
                    cl.params = codec.params.copy()
                    answer.codecs[cl.type] = cl

        extensions = set(supported.get("extensions", []))
        for ext_id, ext_uri in self.extensions:
            if ext_uri in extensions:
                answer.extensions[ext_id] = ext_uri

        if supported.get("simulcast") and self.simulcast:
            send = []
            recv = []

            for streams in self.simulcast.send:
                recv.append([stream.clone() for stream in streams])

            for streams in self.simulcast.recv:
                send.append([stream.clone() for stream in streams])

            answer.simulcast = SimulcastInfo(send, recv)

            for rid in self.rids.values():
                rev = rid.clone()
                rev.direction = DirectionWay.reverse(rev.direction)
                answer.rids[rev.id] = rid

        if (datachannel := supported.get("datachannel")) and self.datachannel:
            answer.datachannel = DatachannelInfo(
                self.datachannel.port, datachannel.max_message_size or self.datachannel.max_message_size
            )

        return answer

    @classmethod
    def create(cls, typ: Literal["audio", "video", "application"], supported: SupportedMedia) -> MediaInfo:
        info = MediaInfo(typ, typ)

        if supported:
            if codecs := supported["codecs"]:
                if isinstance(codecs, list):
                    info.codecs = CodecInfo.map_from_names(codecs, supported.get("rtx"), supported.get("rtcpfbs") or [])
                else:
                    info.codecs = codecs
        else:
            info.direction = Direction.INACTIVE

        return info
