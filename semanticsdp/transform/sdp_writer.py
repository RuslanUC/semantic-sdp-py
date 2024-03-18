from __future__ import annotations
from semanticsdp.transform import grammar

outerOrder = [
    'v', 'o', 's', 'i',
    'u', 'e', 'p', 'c',
    'b', 't', 'r', 'z', 'a'
]
innerOrder = ['i', 'c', 'b', 'a']


class SDPWriter:
    @staticmethod
    def makeLine(typ: str, obj: dict, location: dict) -> str:
        if "format" in obj:
            s = obj["format"] if isinstance(obj["format"], str) else \
                obj["format"](location if obj.get("push") else location[obj["name"]])
        else:
            s = "{%s}" % obj["name"]

        fmt = f"{typ}={s}"
        fmt_args = {}
        if obj.get("names"):
            for i in range(len(obj["names"])):
                n = obj["names"][i]
                if obj.get("name") in location:
                    fmt_args[n] = location[obj["name"]][n]
                elif obj["names"][i] in location:
                    fmt_args[obj["names"][i]] = location[obj["names"][i]]
        else:
            fmt_args[obj["name"]] = location[obj["name"]]

        return fmt.format(**fmt_args)

    @staticmethod
    def write(sdp_dict: dict) -> str:
        for media in sdp_dict["media"]:
            if not media.get("payloads"):
                media["payloads"] = ""

        sdp = []

        for ord_type in outerOrder:
            for obj in grammar[ord_type]:
                if sdp_dict.get(obj.get("name")):
                    sdp.append(SDPWriter.makeLine(ord_type, obj, sdp_dict))
                elif sdp_dict.get(obj.get("push")):
                    for el in sdp_dict[obj["push"]]:
                        sdp.append(SDPWriter.makeLine(ord_type, obj, el))

        for m_line in sdp_dict["media"]:
            sdp.append(SDPWriter.makeLine('m', grammar["m"][0], m_line))
            for ord_type in innerOrder:
                for obj in grammar[ord_type]:
                    if m_line.get(obj.get("name")):
                        sdp.append(SDPWriter.makeLine(ord_type, obj, m_line))
                    elif m_line.get(obj.get("push")):
                        for el in m_line[obj["push"]]:
                            sdp.append(SDPWriter.makeLine(ord_type, obj, el))

        return "\r\n".join(sdp)
