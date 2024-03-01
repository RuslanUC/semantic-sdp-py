import re

from semanticsdp.transform import grammar

re_valid_line = re.compile(r'^([a-z])=(.*)')


class SDPParser:
    @staticmethod
    def parse(sdp: str) -> dict:
        sdp_dict = {"media": []}
        location = sdp_dict

        for line in sdp.split("\n"):
            line = line.strip("\r")
            if not (match := re_valid_line.match(line)):
                continue
            typ, content = match.groups()
            if typ == "m":
                location = {"rtp": [], "fmtp": []}
                sdp_dict["media"].append(location)

            for obj in grammar[typ]:
                if "reg" not in obj:
                    continue
                if obj["reg"].match(content):
                    SDPParser.parseReg(obj, location, content)
                    break

        return sdp_dict

    @staticmethod
    def parseReg(obj: dict, location: dict, content: str) -> None:
        needsBlank = "name" in obj and "names" in obj
        if "push" in obj and obj["push"] not in location:
            location[obj["push"]] = []
        elif needsBlank and obj["name"] not in location:
            location[obj["name"]] = {}

        keyLocation = {} if "push" in obj else (location[obj["name"]] if needsBlank else location)
        SDPParser.attachProperties(obj["reg"].match(content).groups(), keyLocation, obj.get("names"), obj.get("name"))

        if "push" in obj:
            location[obj["push"]].append(keyLocation)

    @staticmethod
    def attachProperties(match: tuple[str], location: dict, names: list[str] | None, name: str | None):
        if name is not None and names is None:
            location[name] = int(match[0]) if match[0].isdigit() else match[0]
            return
        for idx, m_name in enumerate(names):
            if match[idx] is not None:
                location[m_name] = int(match[idx]) if match[idx].isdigit() else match[idx]

    @staticmethod
    def parseParams(params_str: str) -> dict:
        acc = {}
        for param in params_str.split(";"):
            param = param.strip()
            kv = param.split("=", 1)
            if len(kv) == 2:
                acc[kv[0]] = int(kv[1]) if kv[1].isdigit() else kv[1]
            else:
                acc[kv[0]] = None

        return acc

    @staticmethod
    def parseSimulcastStreamList(sl: str) -> list[list[dict]]:
        streams = []
        for stream in sl.split(";"):
            alts = []
            for fmt in stream.split(","):
                paused = False
                if fmt[0] == "~":
                    scid = int(fmt[1:]) if fmt[1:].isdigit() else fmt[1:]
                    paused = True
                else:
                    scid = int(fmt) if fmt.isdigit() else fmt

                alts.append({"scid": scid, "paused": paused})

            streams.append(alts)

        return streams
