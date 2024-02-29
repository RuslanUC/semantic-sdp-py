def candidatesFormat(o):
    s = 'candidate:%s %d %s %d %s %d typ %s'
    s += ' raddr %s rport %d' if o.get("raddr") is not None else '%v%v'
    s += ' tcptype %s' if o.get("tcptype") is not None else '%v'
    s += ' generation %d' if o.get("generation") is not None else ''
    s += ' network-id %d' if o.get('network-id') is not None else '%v'
    s += ' network-cost %d' if o.get('network-cost') is not None else '%v'

    return s


def ssrcsFormat(o):
    s = 'ssrc:%d'
    if o.get("attribute") is not None:
        s += ' %s'
        if o.get("value") is not None:
            s += ':%s'

    return s


def mediaClkFormat(o):
    s = 'mediaclk:'
    s += 'id=%s %s' if o.get("id") is not None else '%v%s'
    s += '=%s' if o.get("mediaClockValue") is not None else ''
    s += ' rate=%s' if o.get("rateNumerator") is not None else ''
    s += '/%s' if o.get("rateDenominator") is not None else ''

    return s


grammar = {
    "v": [{
        "name": 'version',
    }],
    "o": [{
        "name": 'origin',
        "names": ['username', 'sessionId', 'sessionVersion', 'netType', 'ipVer', 'address'],
        "format": '%s %s %d %s IP%d %s'
    }],
    "s": [{"name": 'name'}],
    "i": [{"name": 'description'}],
    "u": [{"name": 'uri'}],
    "e": [{"name": 'email'}],
    "p": [{"name": 'phone'}],
    "c": [{
        "name": 'connection',
        "names": ['version', 'ip'],
        "format": 'IN IP%d %s'
    }],
    "b": [{
        "push": 'bandwidth',
        "names": ['type', 'limit'],
        "format": '%s:%s'
    }],
    "t": [{
        "name": 'timing',
        "names": ['start', 'stop'],
        "format": '%d %d'
    }],
    "r": [{"name": 'repeats'}],
    "z": [{"name": 'timezones'}],
    "a": [
        {
            "push": 'rtp',
            "names": ['payload', 'codec', 'rate', 'encoding'],
            "format": lambda o: 'rtpmap:%d %s/%s/%s' if o.get("encoding") else \
                ('rtpmap:%d %s/%s' if o.get("rate") else 'rtpmap:%d %s')
        },
        {
            "push": 'fmtp',
            "names": ['payload', 'config'],
            "format": 'fmtp:%d %s'
        },
        {
            "name": 'control',
            "format": 'control:%s'
        },
        {
            "name": 'rtcp',
            "names": ['port', 'netType', 'ipVer', 'address'],
            "format": lambda o: 'rtcp:%d %s IP%d %s' if o.get("address") is not None else 'rtcp:%d'
        },
        {
            "push": 'rtcpFbTrrInt',
            "names": ['payload', 'value'],
            "format": 'rtcp-fb:%s trr-int %d'
        },
        {
            "push": 'rtcpFb',
            "names": ['payload', 'type', 'subtype'],
            "format": lambda o: 'rtcp-fb:%s %s %s' if o.get("subtype") is not None else 'rtcp-fb:%s %s'
        },
        {
            "push": 'ext',
            "names": ['value', 'direction', 'encrypt-uri', 'uri', 'config'],
            "format": lambda o: 'extmap:%d' + ('/%s' if o.get("direction") else '%v') + (
                ' %s' if o.get('encrypt-uri') else '%v') + ' %s' + (' %s' if o.get("config") else '')
        },
        {
            "name": 'extmapAllowMixed',
        },
        {
            "push": 'crypto',
            "names": ['id', 'suite', 'config', 'sessionConfig'],
            "format": lambda o: ('crypto:%d %s %s %s' if o.get("sessionConfig") is not None else 'crypto:%d %s %s')
        },
        {
            "name": 'setup',
            "format": 'setup:%s'
        },
        {
            "name": 'connectionType',
            "format": 'connection:%s'
        },
        {
            "name": 'mid',
            "format": 'mid:%s'
        },
        {
            "name": 'msid',
            "format": 'msid:%s'
        },
        {
            "name": 'ptime',
            "format": 'ptime:%d'
        },
        {
            "name": 'maxptime',
            "format": 'maxptime:%d'
        },
        {
            "name": 'direction',
        },
        {
            "name": 'icelite',
        },
        {
            "name": 'iceUfrag',
            "format": 'ice-ufrag:%s'
        },
        {
            "name": 'icePwd',
            "format": 'ice-pwd:%s'
        },
        {
            "name": 'fingerprint',
            "names": ['type', 'hash'],
            "format": 'fingerprint:%s %s'
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
            "format": 'remote-candidates:%s'
        },
        {
            "name": 'iceOptions',
            "format": 'ice-options:%s'
        },
        {
            "push": 'ssrcs',
            "names": ['id', 'attribute', 'value'],
            "format": ssrcsFormat
        },
        {
            "push": 'ssrcGroups',
            "names": ['semantics', 'ssrcs'],
            "format": 'ssrc-group:%s %s'
        },
        {
            "name": 'msidSemantic',
            "names": ['semantic', 'token'],
            "format": 'msid-semantic: %s %s'},
        {
            "push": 'groups',
            "names": ['type', 'mids'],
            "format": 'group:%s %s'
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
            "format": lambda o: 'sctpmap:%s %s %s' if o.get("maxMessageSize") is not None else 'sctpmap:%s %s'
        },
        {
            "name": 'xGoogleFlag',
            "format": 'x-google-flag:%s'
        },
        {
            "push": 'rids',
            "names": ['id', 'direction', 'params'],
            "format": lambda o: 'rid:%s %s %s' if o.get("params") else 'rid:%s %s'
        },
        {
            "push": 'imageattrs',
            "names": ['pt', 'dir1', 'attrs1', 'dir2', 'attrs2'],
            "format": lambda o: 'imageattr:%s %s %s' + (' %s %s' if o.get("dir2") else '')
        },
        {
            "name": 'simulcast',
            "names": ['dir1', 'list1', 'dir2', 'list2'],
            "format": lambda o: 'simulcast:%s %s' + (' %s %s' if o.get("dir2") else '')
        },
        {
            "name": 'simulcast_03',
            "names": ['value'],
            "format": 'simulcast: %s'
        },
        {
            "name": 'framerate',
            "format": 'framerate:%s'
        },
        {
            "name": 'sourceFilter',
            "names": ['filterMode', 'netType', 'addressTypes', 'destAddress', 'srcList'],
            "format": 'source-filter: %s %s %s %s %s'
        },
        {
            "name": 'bundleOnly',
        },
        {
            "name": 'label',
            "format": 'label:%s'
        },
        {
            "name": 'sctpPort',
            "format": 'sctp-port:%s'
        },
        {
            "name": 'maxMessageSize',
            "format": 'max-message-size:%s'
        },
        {
            "push": 'tsRefClocks',
            "names": ['clksrc', 'clksrcExt'],
            "format": lambda o: 'ts-refclk:%s' + ('=%s' if o.get("clksrcExt") is not None else '')
        },
        {
            "name": 'mediaClk',
            "names": ['id', 'mediaClockName', 'mediaClockValue', 'rateNumerator', 'rateDenominator'],
            "format": mediaClkFormat
        },
        {
            "name": 'keywords',
            "format": 'keywds:%s'
        },
        {
            "name": 'content',
            "format": 'content:%s'
        },
        {
            "name": 'bfcpFloorCtrl',
            "format": 'floorctrl:%s'
        },
        {
            "name": 'bfcpConfId',
            "format": 'confid:%s'
        },
        {
            "name": 'bfcpUserId',
            "format": 'userid:%s'
        },
        {
            "name": 'bfcpFloorId',
            "names": ['id', 'mStream'],
            "format": 'floorid:%s mstrm:%s'
        },
        {
            "push": 'invalid',
            "names": ['value']
        }
    ],
    "m": [{
        "names": ['type', 'port', 'protocol', 'payloads'],
        "format": '%s %d %s %s'
    }],
}

"""

// customized util.format - discards excess arguments and can void middle ones
var formatRegExp = /%[sdv%]/g;
var format = function (formatStr) {
  var i = 1;
  var args = arguments;
  var len = args.length;
  return formatStr.replace(formatRegExp, function (x) {
    if (i >= len) {
      return x;
    }
    var arg = args[i];
    i += 1;
    switch (x) {
    case '%%':
      return '%';
    case '%s':
      return String(arg);
    case '%d':
      return Number(arg);
    case '%v':
      return '';
    }
  });
};

"""

outerOrder = [
    'v', 'o', 's', 'i',
    'u', 'e', 'p', 'c',
    'b', 't', 'r', 'z', 'a'
]
innerOrder = ['i', 'c', 'b', 'a']


class SDPWriter:
    @staticmethod
    def makeLine(typ: str, obj: dict, location: dict) -> str:
        if "format" not in obj:
            print(f"Format not defined for {typ} ({obj}, {location[obj['name']]}, {location}).")
            return
        s = obj["format"] if isinstance(obj["format"], str) else \
            obj["format"](location if obj.get("push") else location[obj["name"]])
        args = [f"{typ}={s}"]
        if obj.get("names"):
            for i in range(len(obj["names"])):
                n = obj["names"][i]
                if obj.get("name"):
                    args.append(location[obj["name"]][n])
                else:
                    args.append(location[obj["names"][i]])
        else:
            args.append(location[obj["name"]])

        print(args)

        # return format.apply(null, args);
        return ""

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
