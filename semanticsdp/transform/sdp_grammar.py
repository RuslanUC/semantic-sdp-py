import re


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
        "reg": re.compile(r'^(\d*)$'),
    }],
    "o": [{
        "name": 'origin',
        "reg": re.compile(r'^(\S*) (\d*) (\d*) (\S*) IP(\d) (\S*)'),
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
        "reg": re.compile(r'^IN IP(\d) (\S*)'),
        "names": ['version', 'ip'],
        "format": 'IN IP{version} {ip}'
    }],
    "b": [{
        "push": 'bandwidth',
        "reg": re.compile(r'^(TIAS|AS|CT|RR|RS):(\d*)'),
        "names": ['type', 'limit'],
        "format": '{type}:{limit}'
    }],
    "t": [{
        "name": 'timing',
        "reg": re.compile(r'^(\d*) (\d*)'),
        "names": ['start', 'stop'],
        "format": '{start} {stop}'
    }],
    "r": [{"name": 'repeats'}],
    "z": [{"name": 'timezones'}],
    "a": [
        {
            "push": 'rtp',
            "reg": re.compile(r'^rtpmap:(\d*) ([\w\-.]*)(?:\s*/(\d*)(?:\s*/(\S*))?)?'),
            "names": ['payload', 'codec', 'rate', 'encoding'],
            "format": lambda o: 'rtpmap:{payload} {codec}/{rate}/{encoding}' if o.get("encoding")
            else ('rtpmap:{payload} {codec}/{rate}' if o.get("rate") else 'rtpmap:{payload} {codec}')
        },
        {
            "push": 'fmtp',
            "reg": re.compile(r'^fmtp:(\d*) ([\S| ]*)'),
            "names": ['payload', 'config'],
            "format": 'fmtp:{payload} {config}'
        },
        {
            "name": 'control',
            "reg": re.compile(r'^control:(.*)'),
            "format": 'control:{control}'
        },
        {
            "name": 'rtcp',
            "reg": re.compile(r'^rtcp:(\d*)(?: (\S*) IP(\d) (\S*))?'),
            "names": ['port', 'netType', 'ipVer', 'address'],
            "format": lambda o: 'rtcp:{port} {netType} IP{ipVer} {address}' if o.get("address") is not None
            else 'rtcp:{port}'
        },
        {
            "push": 'rtcpFbTrrInt',
            "reg": re.compile(r'^rtcp-fb:(\*|\d*) trr-int (\d*)'),
            "names": ['payload', 'value'],
            "format": 'rtcp-fb:{payload} trr-int {value}'
        },
        {
            "push": 'rtcpFb',
            "reg": re.compile(r'^rtcp-fb:(\*|\d*) ([\w_-]*)(?: ([\w_-]*))?'),
            "names": ['payload', 'type', 'subtype'],
            "format": lambda o: 'rtcp-fb:{payload} {type} {subtype}' if o.get("subtype") is not None
            else 'rtcp-fb:{payload} {type}'
        },
        {
            "push": 'ext',
            "reg": re.compile(r'^extmap:(\d+)(?:/(\w+))?(?: (urn:ietf:params:rtp-hdrext:encrypt))? (\S*)(?: (\S*))?'),
            "names": ['value', 'direction', 'encrypt-uri', 'uri', 'config'],
            "format": lambda o: 'extmap:{value}' + ('/{direction}' if o.get("direction") else '') + (
                ' {encrypt-uri}' if o.get('encrypt-uri') else '') + ' {uri}' + (' {config}' if o.get("config") else '')
        },
        {
            "name": 'extmapAllowMixed',
            "reg": re.compile(r'^(extmap-allow-mixed)')
        },
        {
            "push": 'crypto',
            "reg": re.compile(r'^crypto:(\d*) ([\w_]*) (\S*)(?: (\S*))?'),
            "names": ['id', 'suite', 'config', 'sessionConfig'],
            "format": lambda o: ('crypto:{id} {suite} {config} {sessionConfig}' if o.get("sessionConfig") is not None
                                 else 'crypto:{id} {suite} {config}')
        },
        {
            "name": 'setup',
            "reg": re.compile(r'^setup:(\w*)'),
            "format": 'setup:{setup}'
        },
        {
            "name": 'connectionType',
            "reg": re.compile(r'^connection:(new|existing)'),
            "format": 'connection:{connectionType}'
        },
        {
            "name": 'mid',
            "reg": re.compile(r'^mid:([^\s]*)'),
            "format": 'mid:{mid}'
        },
        {
            "name": 'msid',
            "reg": re.compile(r'^msid:(.*)'),
            "format": 'msid:{msid}'
        },
        {
            "name": 'ptime',
            "reg": re.compile(r'^ptime:(\d*(?:\.\d*)*)'),
            "format": 'ptime:{ptime}'
        },
        {
            "name": 'maxptime',
            "reg": re.compile(r'^maxptime:(\d*(?:\.\d*)*)'),
            "format": 'maxptime:{maxptime}'
        },
        {
            "name": 'direction',
            "reg": re.compile(r'^(sendrecv|recvonly|sendonly|inactive)'),
        },
        {
            "name": 'icelite',
            "reg": re.compile(r'^(ice-lite)'),
        },
        {
            "name": 'iceUfrag',
            "reg": re.compile(r'^ice-ufrag:(\S*)'),
            "format": 'ice-ufrag:{iceUfrag}'
        },
        {
            "name": 'icePwd',
            "reg": re.compile(r'^ice-pwd:(\S*)'),
            "format": 'ice-pwd:{icePwd}'
        },
        {
            "name": 'fingerprint',
            "reg": re.compile(r'^fingerprint:(\S*) (\S*)'),
            "names": ['type', 'hash'],
            "format": 'fingerprint:{type} {hash}'
        },
        {
            "push": 'candidates',
            "reg": re.compile(r'^candidate:(\S*) (\d*) (\S*) (\d*) (\S*) (\d*) typ (\S*)(?: raddr (\S*) rport (\d*))?'
                              r'(?: tcptype (\S*))?(?: generation (\d*))?(?: network-id (\d*))?'
                              r'(?: network-cost (\d*))?'),
            "names": ['foundation', 'component', 'transport', 'priority', 'ip', 'port', 'type', 'raddr', 'rport',
                      'tcptype', 'generation', 'network-id', 'network-cost'],
            "format": candidatesFormat
        },
        {
            "name": 'endOfCandidates',
            "reg": re.compile(r'^(end-of-candidates)'),
        },
        {
            "name": 'remoteCandidates',
            "reg": re.compile(r'^remote-candidates:(.*)'),
            "format": 'remote-candidates:{remoteCandidates}'
        },
        {
            "name": 'iceOptions',
            "reg": re.compile(r'^ice-options:(\S*)'),
            "format": 'ice-options:{iceOptions}'
        },
        {
            "push": 'ssrcs',
            "reg": re.compile(r'^ssrc:(\d*) ([\w_-]*)(?::(.*))?'),
            "names": ['id', 'attribute', 'value'],
            "format": ssrcsFormat
        },
        {
            "push": 'ssrcGroups',
            "reg": re.compile(r'^ssrc-group:([\x21\x23\x24\x25\x26\x27\x2A\x2B\x2D\x2E\w]*) (.*)'),
            "names": ['semantics', 'ssrcs'],
            "format": 'ssrc-group:{semantics} {ssrcs}'
        },
        {
            "name": 'msidSemantic',
            "reg": re.compile(r'^msid-semantic:\s?(\w*) (\S*)'),
            "names": ['semantic', 'token'],
            "format": 'msid-semantic: {semantic} {token}'},
        {
            "push": 'groups',
            "reg": re.compile(r'^group:(\w*) (.*)'),
            "names": ['type', 'mids'],
            "format": 'group:{type} {mids}'
        },
        {
            "name": 'rtcpMux',
            "reg": re.compile(r'^(rtcp-mux)'),
        },
        {
            "name": 'rtcpRsize',
            "reg": re.compile(r'^(rtcp-rsize)'),
        },
        {
            "name": 'sctpmap',
            "reg": re.compile(r'^sctpmap:([\w_/]*) (\S*)(?: (\S*))?'),
            "names": ['sctpmapNumber', 'app', 'maxMessageSize'],
            "format": lambda o: 'sctpmap:{sctpmapNumber} {app} {maxMessageSize}' if o.get("maxMessageSize") is not None
            else 'sctpmap:{sctpmapNumber} {app}'
        },
        {
            "name": 'xGoogleFlag',
            "reg": re.compile(r'^x-google-flag:(\S*)'),
            "format": 'x-google-flag:{xGoogleFlag}'
        },
        {
            "push": 'rids',
            "reg": re.compile(r'^rid:(\w+) (\w+)(?: ([\S| ]*))?'),
            "names": ['id', 'direction', 'params'],
            "format": lambda o: 'rid:{id} {direction} {params}' if o.get("params") else 'rid:{id} {direction}'
        },
        {
            "push": 'imageattrs',
            "reg": re.compile(r'^imageattr:(\\d+|\\*)'
                              r'[\\s\\t]+(send|recv)[\\s\\t]+(\\*|\\[\\S+\\](?:[\\s\\t]+\\[\\S+\\])*)'
                              r'(?:[\\s\\t]+(recv|send)[\\s\\t]+(\\*|\\[\\S+\\](?:[\\s\\t]+\\[\\S+\\])*))?'),
            "names": ['pt', 'dir1', 'attrs1', 'dir2', 'attrs2'],
            "format": lambda o: 'imageattr:{pt} {dir1} {attrs1}' + (' {dir2} {attrs2}' if o.get("dir2") else '')
        },
        {
            "name": 'simulcast',
            "reg": re.compile(r'^simulcast:'
                              r'(send|recv) ([a-zA-Z0-9\\-_~;,]+)'
                              r'(?:\\s?(send|recv) ([a-zA-Z0-9\\-_~;,]+))?$'),
            "names": ['dir1', 'list1', 'dir2', 'list2'],
            "format": lambda o: 'simulcast:{dir1} {list1}' + (' {dir2} {list2}' if o.get("dir2") else '')
        },
        {
            "name": 'simulcast_03',
            "reg": re.compile(r'^simulcast:[\s\t]+([\S+\s\t]+)$'),
            "names": ['value'],
            "format": 'simulcast: {value}'
        },
        {
            "name": 'framerate',
            "reg": re.compile(r'^framerate:(\d+(?:$|\.\d+))'),
            "format": 'framerate:{framerate}'
        },
        {
            "name": 'sourceFilter',
            "reg": re.compile(r'^source-filter: *(excl|incl) (\S*) (IP4|IP6|\*) (\S*) (.*)'),
            "names": ['filterMode', 'netType', 'addressTypes', 'destAddress', 'srcList'],
            "format": 'source-filter: {filterMode} {netType} {addressTypes} {destAddress} {srcList}'
        },
        {
            "name": 'bundleOnly',
            "reg": re.compile(r'^(bundle-only)'),
        },
        {
            "name": 'label',
            "reg": re.compile(r'^label:(.+)'),
            "format": 'label:{label}'
        },
        {
            "name": 'sctpPort',
            "reg": re.compile(r'^sctp-port:(\d+)$'),
            "format": 'sctp-port:{sctpPort}'
        },
        {
            "name": 'maxMessageSize',
            "reg": re.compile(r'^max-message-size:(\d+)$'),
            "format": 'max-message-size:{maxMessageSize}'
        },
        {
            "push": 'tsRefClocks',
            "reg": re.compile(r'^ts-refclk:([^\s=]*)(?:=(\S*))?'),
            "names": ['clksrc', 'clksrcExt'],
            "format": lambda o: 'ts-refclk:{clksrc}' + ('={clksrcExt}' if o.get("clksrcExt") is not None else '')
        },
        {
            "name": 'mediaClk',
            "reg": re.compile(r'^mediaclk:(?:id=(\S*))? *([^\s=]*)(?:=(\S*))?(?: *rate=(\d+)\/(\d+))?'),
            "names": ['id', 'mediaClockName', 'mediaClockValue', 'rateNumerator', 'rateDenominator'],
            "format": mediaClkFormat
        },
        {
            "name": 'keywords',
            "reg": re.compile(r'^keywds:(.+)$'),
            "format": 'keywds:{keywords}'
        },
        {
            "name": 'content',
            "reg": re.compile(r'^content:(.+)'),
            "format": 'content:{content}'
        },
        {
            "name": 'bfcpFloorCtrl',
            "reg": re.compile(r'^floorctrl:(c-only|s-only|c-s)'),
            "format": 'floorctrl:{bfcpFloorCtrl}'
        },
        {
            "name": 'bfcpConfId',
            "reg": re.compile(r'^confid:(\d+)'),
            "format": 'confid:{bfcpConfId}'
        },
        {
            "name": 'bfcpUserId',
            "reg": re.compile(r'^userid:(\d+)'),
            "format": 'userid:{bfcpUserId}'
        },
        {
            "name": 'bfcpFloorId',
            "reg": re.compile(r'^floorid:(.+) (?:m-stream|mstrm):(.+)'),
            "names": ['id', 'mStream'],
            "format": 'floorid:{id} mstrm:{mStream}'
        },
        {
            "push": 'invalid',
            "names": ['value']
        }
    ],
    "m": [{
        "reg": re.compile(r'^(\w*) (\d*) ([\w/]*)(?: (.*))?'),
        "names": ['type', 'port', 'protocol', 'payloads'],
        "format": '{type} {port} {protocol} {payloads}'
    }],
}
