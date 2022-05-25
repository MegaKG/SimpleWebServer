#!/usr/bin/env python3
#GNU General Public License v3.0
#Code by MegaKG
import mimetypes

#This file contains the base class for all webpages to be based off

class webpage:
    #This shouldn't ever be overwritten by the child
    def __init__(self,Options,PassIN,CON):
        self.Options = Options
        self.PassIN = PassIN
        self.Connection = CON

    #Me First
    def sendCode(self, Code):
        self.Connection.sendstdat("HTTP/1.1 " + str(Code) + " \nServer: KPython V4\nVary: Accept-Encoding\n")

    #Me Last
    def sendType(self,Mime):
        self.Connection.sendstdat("Content-Type: " + Mime + "\n\n")

    #Required for continual connections
    def sendLength(self,Length):
        self.Connection.sendstdat("Content-Length: " + str(Length) + "\n")

    #Makes life easy for page generation
    def print(self,*IN):
        OUTST = ''
        for i in IN:
            OUTST += str(i) + ' '
        OUTST = OUTST[:-1].encode('utf-8')
        self.Connection.senddat(OUTST)

    def mimeFromFileExtension(self,Path):
        return mimetypes.guess_type(Path)

    def close(self):
        self.Connection.close()

    #Deconstructor
    #def __del__(self):
        #self.Connection.close()
    


    



    #These are User replacable functions in the child classes
    def connect(self):
        pass

    def webSocket(self,WebCon):
        WebCon.close()

    