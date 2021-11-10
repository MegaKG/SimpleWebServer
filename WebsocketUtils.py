#!/usr/bin/env python3
#GNU General Public License v3.0
#Code by MegaKG
import hashlib
import base64

CONSTANT = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'


def genaccept(REQUEST):
    return base64.b64encode(hashlib.sha1(REQUEST['Sec-WebSocket-Key'].encode() + CONSTANT).digest())


RESP = """HTTP/1.1 101 Switching Protocols
Server: KPython V3
Upgrade: WebSocket
Sec-WebSocket-Accept: [ACCEPT]
Sec-WebSocket-Protocol: chat
"""


def responseHeader(REQUEST):
    return RESP.replace('[ACCEPT]',genaccept(REQUEST))
