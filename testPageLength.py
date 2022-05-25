#!/usr/bin/env python3
#GNU General Public License v3.0
#Code by MegaKG
import Pages

#Refer to Pages
class page(Pages.webpage):
    def connect(self):
        self.sendCode(200)
        self.sendLength(24) # This is important if the connection isn't closed
        self.sendType("text/html")

        self.print("<html>Hello World</html>")