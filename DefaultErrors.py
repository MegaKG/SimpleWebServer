#!/usr/bin/env python3
#GNU General Public License v3.0
#Code by MegaKG

import Pages

class e404(Pages.webpage):
    def connect(self):
        self.sendCode(404)
        self.sendLength(54)
        self.sendType('text/html')

        self.print("<html><body><h3>404, Page Not Found</h3></body></html>")

class e500(Pages.webpage):
    def connect(self):
        self.sendCode(500)
        self.sendType('text/html')

        self.print("<html><body><h3>500, Internal Server Error</h3></body></html>")