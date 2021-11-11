#!/usr/bin/env python3
#GNU General Public License v3.0
#Code by MegaKG
import hashlib
import base64
import TCPstreams3 as tcp
import struct


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




#According to the specification:
"""
   0                   1                   2                   3
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
  +-+-+-+-+-------+-+-------------+-------------------------------+
  |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
  |I|S|S|S|  (4)  |A|     (7)     |             (16/63)           |
  |N|V|V|V|       |S|             |   (if payload len==126/127)   |
  | |1|2|3|       |K|             |                               |
  +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
  |     Extended payload length continued, if payload len == 127  |
  + - - - - - - - - - - - - - - - +-------------------------------+
  |                               |Masking-key, if MASK set to 1  |
  +-------------------------------+-------------------------------+
  | Masking-key (continued)       |          Payload Data         |
  +-------------------------------- - - - - - - - - - - - - - - - +
  :                     Payload Data continued ...                :
  + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
  |                     Payload Data continued ...                |
  +---------------------------------------------------------------+

"""



#This wraps Websocket Connections with a similar interface to those of TCPstreams3 and TLSwrapper
class wrappedConnection(tcp.serverCon):
    def __init__(self,CON,key):
        self.conn = CON
        self.info = CON.info

    #Parses the content of a websocket frame
    def _parsePacket(self,RawData):
        #Decode the first byte, containing the FIN and Opcode info
        B1 = RawData[0]

        #Get the Finish Flag Bit
        #128 = 10000000
        Fin = (B1 & 128) != 0 #Get the MSB (First Bit) and determine if it isn't zero

        #Get the Opcode
        #15 = 00001111
        OP = B1 & 15 #Get the Last 4 bits of the byte

        #Now get the Second significant Byte containing the Mask and Payload variable
        B2 = RawData[1]
        
        #Get the Mask Flag bit
        #128 = 10000000
        Mask = (B2 & 128) != 0 #Get the MSB (First Bit) and determine if it isn't zero

        #Get the Unsigned (char) 1 byte containing the length out of 127
        #127 = 01111111
        FirstLength = B2 & 127

        #This Length can have special meanings
        if FirstLength == 127:
            #64 Bit Length, need 8 Bytes
            #Format 'Q' is unsigned long integer (8 bytes)
            ActualLength = struct.unpack('Q',RawData[2:10])[0]
            ContentStart = 10

        elif FirstLength == 126:
            #16 Bit Length, Need 2 Bytes
            ActualLength = struct.unpack('H',RawData[2:4])[0]
            ContentStart = 4
        else:
            #7 Bit Length, do nothing as out of 127 anyway
            ActualLength = FirstLength
            ContentStart = 2

        #Get the masking key
        MaskingKey = RawData[10:14]

        #Return
        if not Mask:
            return {
                'IsEnd':Fin,
                'Content':RawData[ContentStart:],
                'Length':ActualLength,
                'OP':OP
            }
        else:
            return {
                'IsEnd':Fin,
                'Content':RawData[ContentStart:],
                'Length':ActualLength,
                'OP':OP
            }

    

    #Buffer is made irrelevant
    def getdat(self,BUFFER=None):
        pass

    def senddat(self,Data):
        pass

    