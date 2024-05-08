from __future__ import annotations

from dataclasses import dataclass, field
from time import time

from semanticsdp import BaseSdp, MediaInfo, StreamInfo, \
    CandidateInfo, IceInfo, DTLSInfo, CryptoInfo, Setup, Direction, CodecInfo, RTCPFeedbackInfo, DirectionWay, RIDInfo, \
    SimulcastInfo, SimulcastStreamInfo, TrackEncodingInfo, SourceInfo, TrackInfo, SourceGroupInfo, DatachannelInfo
from semanticsdp._dataclass_fix import DATACLASS_KWARGS
from semanticsdp.transform import SDPWriter, SDPParser


@dataclass(**DATACLASS_KWARGS)
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
        return {
            "version": self.version,
            "streams": [stream.to_dict() for stream in self.streams.values()],
            "medias": [media.to_dict() for media in self.medias],
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "ice": self.ice.to_dict() if self.ice else None,
            "dtls": self.dtls.to_dict() if self.dtls else None,
            "crypto": self.crypto.to_dict() if self.crypto else None,
            "extmap_allow_mixed": self.extmap_allow_mixed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SDPInfo:
        data = data.copy()
        data["streams"] = {stream["id"]: StreamInfo.from_dict(stream) for stream in data.pop("streams", [])}
        data["medias"] = [MediaInfo.from_dict(media) for media in data.pop("medias", [])]
        data["candidates"] = [CandidateInfo.from_dict(candidate) for candidate in data.pop("candidates", [])]
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
                            alts = ""
                            for alt in stream:
                                if alts:
                                    alts += ","
                                alts += ("~" if alt.paused else "") + alt.id
                            if lst:
                                lst += ";" + alts
                        md["simulcast"][f"dir{idx}"] = "send"
                        md["simulcast"][f"list{idx}"] = lst
                        idx += 1

                    if media.simulcast.recv:
                        lst = ""
                        for stream in media.simulcast.recv:
                            alts = ""
                            for alt in stream:
                                if alts:
                                    alts += ","
                                alts += ("~" if alt.paused else "") + alt.id
                            if lst:
                                lst += ";" + alts
                        md["simulcast"][f"dir{idx}"] = "recv"
                        md["simulcast"][f"list{idx}"] = lst
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

        sdp["groups"].append({"type": "BUNDLE", "mids": " ".join(map(str, mids))})

        return SDPWriter.write(sdp)

    @classmethod
    def parse(cls, sdp: str) -> SDPInfo:
        sdp = SDPParser.parse(sdp)
        sdpInfo = SDPInfo(sdp.get("origin", {}).get("sessionVersion", 1))

        if "iceUfrag" in sdp and "icePwd" in sdp:
            sdpInfo.ice = IceInfo(sdp["iceUfrag"], sdp["icePwd"], sdp.get("icelite") == "ice-lite",
                                  sdp.get("endOfCandidates") == "end-of-candidates")

        for media in sdp["media"]:
            md = MediaInfo(str(media.get("mid", 0)), media.get("type", "audio"))
            if "iceUfrag" in media and "icePwd" in media:
                sdpInfo.ice = IceInfo(media["iceUfrag"], media["icePwd"], media.get("icelite") == "ice-lite",
                                      media.get("endOfCandidates") == "end-of-candidates")

            for candidate in media.get("candidates", []):
                sdpInfo.candidates.append(CandidateInfo(
                    candidate["foundation"],
                    candidate["component"],
                    candidate["transport"],
                    candidate["priority"],
                    candidate["ip"],
                    candidate["port"],
                    candidate["type"],
                    candidate.get("raddr", None),
                    candidate.get("rport", None),
                ))

            fp = media.get("fingerprint") or sdp.get("fingerprint")
            if fp:
                sdpInfo.dtls = DTLSInfo(Setup(fp.get("setup", "actpass")), fp["type"], fp["hash"])

            if media.get("crypto"):
                crypto = media["crypto"][0]
                sdpInfo.crypto = CryptoInfo(crypto["id"], crypto["suite"], crypto["config"], crypto["sessionConfig"])

            if media.get("direction"):
                md.direction = Direction(media.get("direction", "sendrecv"))

            if media.get("control"):
                md.control = media["control"]

            sdpInfo.extmap_allow_mixed = "extmap-allow-mixed" in (media.get("extmapAllowMixed"),
                                                                  sdp.get("extmapAllowMixed"))

            apts = {}
            for fmt in media["rtp"]:
                if fmt["codec"].upper() in ("RED", "ULPFEC"):
                    continue

                params = {}
                for fmtp in media["fmtp"]:
                    if fmtp["payload"] != fmt["payload"]:
                        continue
                    for k in fmtp["config"].split(";"):
                        key, value = k.split("=", 1)
                        params[key.strip()] = value.strip()

                if fmt["codec"].upper() == "RTX":
                    apts[int(params.get("apt", 97))] = fmt["payload"]
                else:
                    md.codecs[fmt["payload"]] = CodecInfo(fmt["codec"], fmt["payload"], params=params)
                    if fmt.get("encoding", 0) > 1:
                        md.codecs[fmt["payload"]].channels = fmt["encoding"]

            for apt, rtx in apts.items():
                if codecInfo := md.codecs.get(apt):
                    codecInfo.rtx = rtx

            for rtcpFb in media.get("rtcpFb", []):
                if codecInfo := md.codecs.get(rtcpFb["payload"]):
                    codecInfo.rtcpfbs.add(RTCPFeedbackInfo(
                        rtcpFb["type"],
                        rtcpFb["subtype"].split(" ") if rtcpFb.get("subtype") else []
                    ))

            for extmap in media["ext"]:
                md.extensions[extmap["value"]] = extmap["uri"]

            for rid in media.get("rids", []):
                ridInfo = RIDInfo(rid["id"], DirectionWay(rid["direction"]))

                if "params" not in rid:
                    continue

                for key, param in SDPParser.parseParams(rid["params"]):
                    if key == 'pt':
                        ridInfo.formats = param.split(',')
                    else:
                        ridInfo.params[key] = param

                md.rids[ridInfo.id] = rid

            encodings = []

            if media.get("simulcast"):
                simulcast = SimulcastInfo([], [])

                if media["simulcast"].get("dir1"):
                    direction = DirectionWay(media["simulcast"]["dir1"])
                    for stream in SDPParser.parseSimulcastStreamList(media["simulcast"]["list1"]):
                        alternatives = [SimulcastStreamInfo(alt["scid"], alt["paused"]) for alt in stream]
                        (simulcast.recv if direction == DirectionWay.RECV else simulcast.send).append(alternatives)

                if media["simulcast"].get("dir2"):
                    direction = DirectionWay(media["simulcast"]["dir2"])
                    for stream in SDPParser.parseSimulcastStreamList(media["simulcast"]["list2"]):
                        alternatives = [SimulcastStreamInfo(alt["scid"], alt["paused"]) for alt in stream]
                        (simulcast.recv if direction == DirectionWay.RECV else simulcast.send).append(alternatives)

                for streams in simulcast.send:
                    alts = []
                    for stream in streams:
                        enc = TrackEncodingInfo(stream.id, stream.paused)
                        if not (rid := md.rids[enc.id]):
                            continue
                        for format_ in rid.formats:
                            if codec := md.codecs[format_]:
                                enc.codecs[codec.type] = codec

                        enc.params = rid.params
                        alts.append(enc)

                    if alts:
                        encodings.append(alts)

                md.simulcast = simulcast

            sources = {}

            for ssrc in media.get("ssrcs", {}):
                if not (source := sources.get(ssrc["id"])):
                    sources[ssrc["id"]] = (source := SourceInfo(ssrc["id"]))

                if ssrc["attribute"].lower() == "cname":
                    source.cname = ssrc["value"]
                if ssrc["attribute"].lower() != "msid":
                    continue

                source.stream_id, source.track_id = ssrc["value"].split(" ")
                if not (stream := sdpInfo.streams.get(source.stream_id)):
                    stream = StreamInfo(source.stream_id)
                    sdpInfo.streams[source.stream_id] = stream

                if not (track := stream.tracks.get(source.track_id)):
                    track = TrackInfo(media["type"], source.track_id, media["mid"], encodings=encodings)
                    stream.tracks[track.id] = track

                track.ssrcs.append(ssrc["id"])

            if media.get("msid"):
                stream_id, track_id = media["msid"].split(" ")
                if not (stream := sdpInfo.streams.get(stream_id)):
                    stream = StreamInfo(stream_id)
                    sdpInfo.streams[stream_id] = stream

                if not (track := stream.tracks.get(track_id)):
                    track = TrackInfo(media["type"], track_id, media["mid"], encodings=encodings)
                    stream.tracks[track.id] = track

                for ssrc, source in sources.items():
                    if source.stream_id:
                        continue
                    source.stream_id = stream_id
                    source.track_id = track_id
                    track.ssrcs.append(ssrc)

            for ssrc, source in sources.items():
                if source.stream_id:
                    continue
                source.stream_id = source.cname
                source.track_id = media["mid"]
                if not (stream := sdpInfo.streams.get(source.stream_id)):
                    stream = StreamInfo(source.stream_id)
                    sdpInfo.streams[source.stream_id] = stream

                if not (track := stream.tracks.get(source.track_id)):
                    track = TrackInfo(media["type"], source.track_id, media["mid"], encodings=encodings)
                    stream.tracks[track.id] = track

                track.ssrcs.append(ssrc)

            for ssrcGroup in media.get("ssrcGroups", []):
                ssrcs = ssrcGroup["ssrcs"].split(" ")
                group = SourceGroupInfo(ssrcGroup["semantics"], ssrcs)
                if not (source := sources.get(int(ssrcs[0]))):
                    continue

                sdpInfo.streams[source.stream_id].tracks[source.track_id].groups.append(group)

            if media.get("type") == "application" and media.get("payloads") == "webrtc-datachannel":
                md.datachannel = DatachannelInfo(media["sctpPort"], media["maxMessageSize"])

            sdpInfo.medias.append(md)

        return sdpInfo
