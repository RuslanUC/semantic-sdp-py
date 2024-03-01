def candidatesFormat(o):
    s = 'candidate:{foundation} {component} {transport} {priority} {ip} {port} typ {type}'
    s += ' raddr {raddr} rport {rport}' if o.get("raddr") is not None else ''
    s += ' tcptype {tcptype}' if o.get("tcptype") is not None else ''
    s += ' generation {generation}' if o.get("generation") is not None else ''
    s += ' network-id {network-id}' if o.get('network-id') is not None else ''
    s += ' network-cost {network-cost}' if o.get('network-cost') is not None else ''

    return s


def ssrcsFormat(o):
    s = 'ssrc:{id}'
    if o.get("attribute") is not None:
        s += ' {attribute}'
        if o.get("value") is not None:
            s += ':{value}'

    return s


def mediaClkFormat(o):
    s = 'mediaclk:'
    s += 'id={id} {mediaClockName}' if o.get("id") is not None else '{mediaClockName}'
    s += '={mediaClockValue}' if o.get("mediaClockValue") is not None else ''
    s += ' rate={rateNumerator}' if o.get("rateNumerator") is not None else ''
    s += '/{rateDenominator}' if o.get("rateDenominator") is not None else ''

    return s


grammar = {
    "v": [{
        "name": 'version',
    }],
    "o": [{
        "name": 'origin',
        "names": ['username', 'sessionId', 'sessionVersion', 'netType', 'ipVer', 'address'],
        "format": '{username} {sessionId} {sessionVersion} {netType} IP{ipVer} {address}'
    }],
    "s": [{"name": 'name'}],
    "i": [{"name": 'description'}],
    "u": [{"name": 'uri'}],
    "e": [{"name": 'email'}],
    "p": [{"name": 'phone'}],
    "c": [{
        "name": 'connection',
        "names": ['version', 'ip'],
        "format": 'IN IP{version} {ip}'
    }],
    "b": [{
        "push": 'bandwidth',
        "names": ['type', 'limit'],
        "format": '{type}:{limit}'
    }],
    "t": [{
        "name": 'timing',
        "names": ['start', 'stop'],
        "format": '{start} {stop}'
    }],
    "r": [{"name": 'repeats'}],
    "z": [{"name": 'timezones'}],
    "a": [
        {
            "push": 'rtp',
            "names": ['payload', 'codec', 'rate', 'encoding'],
            "format": lambda o: 'rtpmap:{payload} {codec}/{rate}/{encoding}' if o.get("encoding") else \
                ('rtpmap:{payload} {codec}/{rate}' if o.get("rate") else 'rtpmap:{payload} {codec}')
        },
        {
            "push": 'fmtp',
            "names": ['payload', 'config'],
            "format": 'fmtp:{payload} {config}'
        },
        {
            "name": 'control',
            "format": 'control:{control}'
        },
        {
            "name": 'rtcp',
            "names": ['port', 'netType', 'ipVer', 'address'],
            "format": lambda o: 'rtcp:{port} {netType} IP{ipVer} {address}' if o.get("address") is not None \
                else 'rtcp:{port}'
        },
        {
            "push": 'rtcpFbTrrInt',
            "names": ['payload', 'value'],
            "format": 'rtcp-fb:{payload} trr-int {value}'
        },
        {
            "push": 'rtcpFb',
            "names": ['payload', 'type', 'subtype'],
            "format": lambda o: 'rtcp-fb:{payload} {type} {subtype}' if o.get("subtype") is not None \
                else 'rtcp-fb:{payload} {type}'
        },
        {
            "push": 'ext',
            "names": ['value', 'direction', 'encrypt-uri', 'uri', 'config'],
            "format": lambda o: 'extmap:{value}' + ('/{direction}' if o.get("direction") else '') + (
                ' {encrypt-uri}' if o.get('encrypt-uri') else '') + ' {uri}' + (' {config}' if o.get("config") else '')
        },
        {
            "name": 'extmapAllowMixed',
        },
        {
            "push": 'crypto',
            "names": ['id', 'suite', 'config', 'sessionConfig'],
            "format": lambda o: ('crypto:{id} {suite} {config} {sessionConfig}' if o.get("sessionConfig") is not None \
                                     else 'crypto:{id} {suite} {config}')
        },
        {
            "name": 'setup',
            "format": 'setup:{setup}'
        },
        {
            "name": 'connectionType',
            "format": 'connection:{connectionType}'
        },
        {
            "name": 'mid',
            "format": 'mid:{mid}'
        },
        {
            "name": 'msid',
            "format": 'msid:{msid}'
        },
        {
            "name": 'ptime',
            "format": 'ptime:{ptime}'
        },
        {
            "name": 'maxptime',
            "format": 'maxptime:{maxptime}'
        },
        {
            "name": 'direction',
        },
        {
            "name": 'icelite',
        },
        {
            "name": 'iceUfrag',
            "format": 'ice-ufrag:{iceUfrag}'
        },
        {
            "name": 'icePwd',
            "format": 'ice-pwd:{icePwd}'
        },
        {
            "name": 'fingerprint',
            "names": ['type', 'hash'],
            "format": 'fingerprint:{type} {hash}'
        },
        {
            "push": 'candidates',
            "names": ['foundation', 'component', 'transport', 'priority', 'ip', 'port', 'type', 'raddr', 'rport',
                      'tcptype', 'generation', 'network-id', 'network-cost'],
            "format": candidatesFormat
        },
        {
            "name": 'endOfCandidates',
        },
        {
            "name": 'remoteCandidates',
            "format": 'remote-candidates:{remoteCandidates}'
        },
        {
            "name": 'iceOptions',
            "format": 'ice-options:{iceOptions}'
        },
        {
            "push": 'ssrcs',
            "names": ['id', 'attribute', 'value'],
            "format": ssrcsFormat
        },
        {
            "push": 'ssrcGroups',
            "names": ['semantics', 'ssrcs'],
            "format": 'ssrc-group:{semantics} {ssrcs}'
        },
        {
            "name": 'msidSemantic',
            "names": ['semantic', 'token'],
            "format": 'msid-semantic: {semantic} {token}'},
        {
            "push": 'groups',
            "names": ['type', 'mids'],
            "format": 'group:{type} {mids}'
        },
        {
            "name": 'rtcpMux',
        },
        {
            "name": 'rtcpRsize',
        },
        {
            "name": 'sctpmap',
            "names": ['sctpmapNumber', 'app', 'maxMessageSize'],
            "format": lambda o: 'sctpmap:{sctpmapNumber} {app} {maxMessageSize}' if o.get("maxMessageSize") is not None\
                else 'sctpmap:{sctpmapNumber} {app}'
        },
        {
            "name": 'xGoogleFlag',
            "format": 'x-google-flag:{xGoogleFlag}'
        },
        {
            "push": 'rids',
            "names": ['id', 'direction', 'params'],
            "format": lambda o: 'rid:{id} {direction} {params}' if o.get("params") else 'rid:{id} {direction}'
        },
        {
            "push": 'imageattrs',
            "names": ['pt', 'dir1', 'attrs1', 'dir2', 'attrs2'],
            "format": lambda o: 'imageattr:{pt} {dir1} {attrs1}' + (' {dir2} {attrs2}' if o.get("dir2") else '')
        },
        {
            "name": 'simulcast',
            "names": ['dir1', 'list1', 'dir2', 'list2'],
            "format": lambda o: 'simulcast:{dir1} {list1}' + (' {dir2} {list2}' if o.get("dir2") else '')
        },
        {
            "name": 'simulcast_03',
            "names": ['value'],
            "format": 'simulcast: {value}'
        },
        {
            "name": 'framerate',
            "format": 'framerate:{framerate}'
        },
        {
            "name": 'sourceFilter',
            "names": ['filterMode', 'netType', 'addressTypes', 'destAddress', 'srcList'],
            "format": 'source-filter: {filterMode} {netType} {addressTypes} {destAddress} {srcList}'
        },
        {
            "name": 'bundleOnly',
        },
        {
            "name": 'label',
            "format": 'label:{label}'
        },
        {
            "name": 'sctpPort',
            "format": 'sctp-port:{sctpPort}'
        },
        {
            "name": 'maxMessageSize',
            "format": 'max-message-size:{maxMessageSize}'
        },
        {
            "push": 'tsRefClocks',
            "names": ['clksrc', 'clksrcExt'],
            "format": lambda o: 'ts-refclk:{clksrc}' + ('={clksrcExt}' if o.get("clksrcExt") is not None else '')
        },
        {
            "name": 'mediaClk',
            "names": ['id', 'mediaClockName', 'mediaClockValue', 'rateNumerator', 'rateDenominator'],
            "format": mediaClkFormat
        },
        {
            "name": 'keywords',
            "format": 'keywds:{keywords}'
        },
        {
            "name": 'content',
            "format": 'content:{content}'
        },
        {
            "name": 'bfcpFloorCtrl',
            "format": 'floorctrl:{bfcpFloorCtrl}'
        },
        {
            "name": 'bfcpConfId',
            "format": 'confid:{bfcpConfId}'
        },
        {
            "name": 'bfcpUserId',
            "format": 'userid:{bfcpUserId}'
        },
        {
            "name": 'bfcpFloorId',
            "names": ['id', 'mStream'],
            "format": 'floorid:{id} mstrm:{mStream}'
        },
        {
            "push": 'invalid',
            "names": ['value']
        }
    ],
    "m": [{
        "names": ['type', 'port', 'protocol', 'payloads'],
        "format": '{type} {port} {protocol} {payloads}'
    }],
}

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
