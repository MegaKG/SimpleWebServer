#!/usr/bin/env python3
#GNU General Public License v3.0
#Code by MegaKG
import datetime

def typeHeader(Options,PassIN):
    return 'text/html; charset=UTF-8'

def headerExtra(Options,PassIN):
    return ''

def body(Options,CON,PassIN):
    return b"""
<html>
<body>

<div id='timediv'></div>

<script>
var socket = new WebSocket("ws://127.0.0.1:8080/testSocket/socket");
function gettime(){
    socket.send('Hello');
}

socket.onmessage = function(event){
    document.getElementById('timediv').innerHTML = event.data;
}
</script>

<button onclick='gettime()'>Get Time!</button>

</body>
</html>
    """


def websocket(Options,CON,PassIN):
    print("Socket Listener Running")
    while True:
        #Get the Response
        IN = CON.getdat()
        #Something Has to happen here to decode the packet header and content, not implemented yet
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

        print("I Got",IN)
        CON.sendstdat("The Time Is " + str(datetime.datetime.now()))