#!/usr/bin/env python3
#GNU General Public License v3.0
#Code by MegaKG
import datetime
import Pages

MSG = """
<html>
<body>

<div id='timediv'></div>

<script>
var socket = new WebSocket("ws://127.0.0.1:8080/socket");
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

class page(Pages.webpage):
    def connect(self):
        self.sendCode(200)
        self.sendLength(len(MSG))
        self.sendType("text/html")

        self.print(MSG)




    def websocket(self,CON):
        print("Socket Listener Running")
        while True:
            #Get the Response
            IN = CON.getdat()
            print("Socket IN",IN)
            CON.sendstdat("The Time Is " + str(datetime.datetime.now()))
