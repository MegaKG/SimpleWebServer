#!/usr/bin/env python3
#GNU General Public License v3.0
#Code by MegaKG
import Pages
import json
import requests

def _dictMerge(D1,D2):
        for key in D1:
            D2[key] = D1[key]
        return D2

#Refer to Pages
class page(Pages.webpage):
    def connect(self):
        #print(json.dumps(self.Options,indent=4))
        

        #GET Request
        rq = None
        if len(self.Options["POST"]) == 0:
            print("Is Get")
            rq = requests.get(self.Options["Resource"],data=self.Options["GET"])

        #POST Request
        else:
            print("Is Post")
            dat = _dictMerge(self.Options["POST"],self.Options["GET"])
            rq = requests.post(self.Options["Resource"],dat)

        if rq == None:
            print("Error In Request")
            self.sendCode(500)
            self.sendLength(42)
            self.sendType("text/html")
            self.print("<html><body><b>Error 500</b></body></html>")
        else:
            print(rq.headers)
            self.sendCode(rq.status_code)
            if 'Content-Length' in rq.headers:
                self.sendLength(rq.headers["Content-Length"])
            if 'Set-Cookie' in rq.headers:
                self.sendHeader("Set-Cookie",rq.headers["Set-Cookie"])
            self.sendType(rq.headers['Content-Type'])

            for chunk in rq.iter_content(1024):
                self.Connection.senddat(chunk)