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
        print("Socket IN",IN)
        CON.sendstdat("The Time Is " + str(datetime.datetime.now()))