from __future__ import annotations

from dataclasses import dataclass, field
from time import time

from semanticsdp import BaseSdp, MediaInfo, StreamInfo, \
    CandidateInfo, IceInfo, DTLSInfo, CryptoInfo
from semanticsdp.sdp_writer import SDPWriter


@dataclass(slots=True, eq=True)
class SDPInfo(BaseSdp):
    version: int = 1
    streams: dict[str, StreamInfo] = field(default_factory=dict)
    medias: list[MediaInfo] = field(default_factory=list)
    candidates: list[CandidateInfo] = field(default_factory=list)
    ice: IceInfo | None = None
    dtls: DTLSInfo | None = None
    crypto: CryptoInfo | None = None
    extmap_allow_mixed: bool = True

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["streams"] = list(data["streams"].values())
        return data

    @classmethod
    def from_dict(cls, data: dict) -> SDPInfo:
        data["streams"] = {stream["id"]: StreamInfo.from_dict(stream) for stream in data.pop("streams", [])}
        data["medias"] = [MediaInfo.from_dict(media) for media in data.pop("medias", [])]
        data["candidates"] = {key: CandidateInfo.from_dict(candidate) for key, candidate in data.pop("candidates", [])}
        return super(SDPInfo, cls).from_dict(data)

    def answer(self, ice: IceInfo | None = None, dtls: DTLSInfo | None = None, crypto: CryptoInfo | None = None,
               capabilities: dict | None = None) -> SDPInfo:
        return SDPInfo(
            medias=[media.answer(capabilities[media.type] if capabilities else {}) for media in self.medias],
            candidates=[candidate.clone() for candidate in self.candidates],
            ice=ice.clone() if ice else None,
            dtls=dtls.clone() if dtls else None,
            crypto=crypto.clone() if crypto else None,
            extmap_allow_mixed=self.extmap_allow_mixed,
        )

    def __str__(self) -> str:
        sdp = {
            "version": 0,
            "media": [],
            "origin": {
                "username": "-",
                "sessionId": int(time() * 1000),
                "sessionVersion": self.version,
                "netType": "IN",
                "ipVer": 4,
                "address": "127.0.0.1",
            },
            "name": "semantic-sdp-py",
            "connection": {
                "version": 4,
                "ip": "0.0.0.0",
            },
            "timing": {
                "start": 0,
                "stop": 0,
            },
            "msidSemantic": {
                "semantic": "WMS",
                "token": "*",
            },
            "groups": [],
        }

        if self.ice and self.ice.lite:
            sdp["icelite"] = "ice-lite"

        if self.extmap_allow_mixed:
            sdp["extmapAllowMixed"] = "extmap-allow-mixed"

        mids = []
        for media in self.medias:
            mids.append(media.id)

            md = {
                "type": media.type,
                "port": 9,
                "protocol": "",
                "fmtp": [],
                "rtp": [],
                "rtcpFb": [],
                "ext": [],
                "bandwidth": [{"type": "AS", "limit": media.bitrate},
                              {"type": "TIAS", "limit": media.bitrate * 1000}] if media.bitrate > 0 else [],
                "candidates": [{
                    "foundation": candidate.foundation,
                    "component": candidate.component_id,
                    "transport": candidate.transport,
                    "priority": candidate.priority,
                    "ip": candidate.address,
                    "port": candidate.port,
                    "type": candidate.type,
                    "raddr": candidate.rel_addr,
                    "rport": candidate.rel_port,
                } for candidate in self.candidates],
                "ssrcGroups": [],
                "ssrcs": [],
                "rids": [],
                "direction": media.direction.value,
                "mid": media.id,
                "control": media.control,
            }

            if self.extmap_allow_mixed:
                md["extmapAllowMixed"] = "extmap-allow-mixed"

            if self.ice:
                md["iceUfrag"] = self.ice.ufrag
                md["icePwd"] = self.ice.pwd

            if media.type.lower() in {"video", "audio"}:
                md["rtcpMux"] = "rtcp-mux"
                md["rtcpRsize"] = "rtcp-rsize"

                if self.dtls:
                    md["protocol"] = "UDP/TLS/RTP/SAVPF"
                    md["fingerprint"] = {
                        "type": self.dtls.hash,
                        "hash": self.dtls.fingerprint,
                    }
                    md["setup"] = self.dtls.setup.value
                elif self.crypto:
                    md["protocol"] = "RTP/SAVPF"
                    md["crypto"] = [{
                        "id": self.crypto.tag,
                        "suite": self.crypto.suite,
                        "config": self.crypto.key_params,
                    }]
                else:
                    md["protocol"] = "RTP/AVP"

                for codec in media.codecs.values():
                    if media.type.lower() == "video":
                        md["rtp"].append({
                            "payload": codec.type,
                            "codec": codec.codec.upper(),
                            "rate": 90000,
                        })
                    else:
                        if codec.codec.lower() == "opus":
                            md["rtp"].append({
                                "payload": codec.type,
                                "codec": codec.codec,
                                "rate": 48000,
                                "encoding": codec.channels,
                            })
                        elif codec.codec.lower() == "multiopus":
                            md["rtp"].append({
                                "payload": codec.type,
                                "codec": codec.codec,
                                "rate": 48000,
                                "encoding": codec.channels,
                            })
                        else:
                            md["rtp"].append({
                                "payload": codec.type,
                                "codec": codec.codec,
                                "rate": 8000,
                            })

                    for rtcpfb in codec.rtcpfbs:
                        md["rtcpFb"].append({
                            "payload": codec.type,
                            "type": rtcpfb.id,
                            "subtype": " ".join(rtcpfb.params),
                        })

                    if codec.rtx is not None:
                        md["rtp"].append({
                            "payload": codec.rtx,
                            "codec": "rtx",
                            "rate": 90000,
                        })
                        md["fmtp"].append({
                            "payload": codec.rtx,
                            "config": f"apt={codec.type}",
                        })

                    if codec.params:
                        fmtp = {
                            "payload": codec.type,
                            "config": "",
                        }
                        for k in codec.params:
                            if fmtp["config"]:
                                fmtp["config"] += ";"
                            fmtp["config"] += f"{k}={codec.params[k]}" if codec.params[k] else k

                        md["fmtp"].append(fmtp)

                md["payloads"] = " ".join([str(rtp["payload"]) for rtp in md["rtp"]])

                for ext_id, ext_uri in media.extensions.items():
                    md["ext"].append({"value": ext_id, "uri": ext_uri})

                for rid in media.rids.values():
                    ridInfo = {
                        "id": rid.id,
                        "direction": rid.direction.value,
                        "params": "" if not rid.formats else f"pt={','.join(map(str, rid.formats))}"
                    }

                    for key, value in rid.params.items():
                        if ridInfo["params"]:
                            ridInfo["params"] += ";"
                        ridInfo["params"] += f"{key}={value}"

                    md["rids"].append(ridInfo)

                if media.simulcast:
                    idx = 1
                    md["simulcast"] = {}

                    if media.simulcast.send:
                        lst = ""
                        for stream in media.simulcast.send:
                            if lst:
                                lst += ";"
                            lst += ("~" if stream.paused else "") + stream.id
                        md["simulcast"][f"dir{idx}"] = "send"
                        md["simulcast"][f"list{idx}"] = "lst"
                        idx += 1

                    if media.simulcast.recv:
                        lst = ""
                        for stream in media.simulcast.recv:
                            if lst:
                                lst += ";"
                            lst += ("~" if stream.paused else "") + stream.id
                        md["simulcast"][f"dir{idx}"] = "recv"
                        md["simulcast"][f"list{idx}"] = "lst"
                        idx += 1
            elif media.datachannel:
                md["protocol"] = "UDP/DTLS/SCTP"
                md["payloads"] = "webrtc-datachannel"

                md["sctpPort"] = media.datachannel.port
                md["maxMessageSize"] = media.datachannel.max_message_size

            sdp["media"].append(md)

        for stream in self.streams.values():
            for track in stream.tracks.values():
                for media in sdp["media"]:
                    if track.media_id:
                        if track.media_id == media["mid"]:
                            for group in track.groups:
                                media["ssrcGroups"].append({
                                    "semantics": group.semantics,
                                    "ssrcs": " ".join(map(str, group.ssrcs)),
                                })

                            for ssrc in track.ssrcs:
                                media["ssrcs"].append({
                                    "id": ssrc,
                                    "attribute": "cname",
                                    "value": stream.id,
                                })
                                media["ssrcs"].append({
                                    "id": ssrc,
                                    "attribute": "msid",
                                    "value": f"{stream.id} {track.id}",
                                })

                            media["msid"] = f"{stream.id} {track.id}"
                            break
                    elif media["type"] == track.media:
                        for group in track.groups:
                            media["ssrcGroups"].append({
                                "semantics": group.semantics,
                                "ssrcs": " ".join(map(str, group.ssrcs)),
                            })

                        for ssrc in track.ssrcs:
                            media["ssrcs"].append({
                                "id": ssrc,
                                "attribute": "cname",
                                "value": stream.id,
                            })
                            media["ssrcs"].append({
                                "id": ssrc,
                                "attribute": "msid",
                                "value": f"{stream.id} {track.id}",
                            })

                        break

        sdp["groups"].append({"type": "BUNDLE", "mids": " ".join(mids)})

        return SDPWriter.write(sdp)  # ???
