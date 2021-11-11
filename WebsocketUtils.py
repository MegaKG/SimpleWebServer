#!/usr/bin/env python3
#GNU General Public License v3.0
#Code by MegaKG
import hashlib
import base64



#The Websocket Specification requires this UUID as a value
CONSTANT = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'


#We get a key encoded in base64. We respond with the base64 concatenated with the Constant UUID and return the SHA1 digest
def genaccept(REQUEST):
    return base64.b64encode(hashlib.sha1(REQUEST['Sec-WebSocket-Key'].encode() + CONSTANT).digest()).decode()


#The Response header for Websocket
RESP = """HTTP/1.1 101 Switching Protocols
Upgrade: WebSocket
Connection: Upgrade
Sec-WebSocket-Accept: [ACCEPT]

"""

#Takes the decoded request options and generates a response header
def responseHeader(REQUEST):
    return RESP.replace('[ACCEPT]',genaccept(REQUEST))

#To be Implemented
def parsePacket(Data):
    pass