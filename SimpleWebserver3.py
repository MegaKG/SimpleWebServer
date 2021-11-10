#!/usr/bin/env python3 
import TCPstreams3
import TLSwrapper
import ConfigUtils
import Logger
import WebsocketUtils

import sys
import threading
import time
import importlib
import json


NORMAL_HEADER = """HTTP/1.1 200 OK
Server: KPython V3
Vary: Accept-Encoding
Content-Length: [LENGTH]
Content-Type: [TYPE]
[EXTRA]

"""

E404 = """HTTP/1.1 404 Not Found
Server: KPython V3
Vary: Accept-Encoding
Content-Type: text/html


<html><p>404 Not Found</p></html>
"""
E500 = """HTTP/1.1 500 Internal Server Error
Server: KPython V3
Vary: Accept-Encoding
Content-Type: text/html


<html><p>500 Internal Server Error</p></html>
"""

#The main class
class webServer:
    #Redefine the Print Command
    def print(self,*Input):
        ST = ''
        for i in Input:
            ST += str(i) + ' '
        ST = ST[:-1]

        self.logObj.log(ST)


    
    def __init__(self,Config,PassIn=None):
        self.logObj = Logger.logger(Config['LogFile'])
        self.print("Initiate Server")

        self.config = Config

        #Open the server
        self.server = TCPstreams3.newServer(Config['HostAddress'],int(Config['HostPort']))

        #Initialise some values
        self.connections = []
        self.connectionCount = 0

        #Initialise the Module Library
        self.modules = {}
        for i in self.config['Pages']:
            self.modules[i] = importlib.import_module(self.config['Pages'][i].split('.py')[0])
        self.loadedModules = set(self.modules.keys())

        #If Catchall
        if self.config['CatchAll'].lower() == 'true':
            self.catch = importlib.import_module(self.config['CatchPage'].split('.py')[0])
        else:
            self.catch = None

        self.PassIn = PassIn

    def procGet(self,GETR):
        RET = {}
        for pair in GETR.split('&'):
                    SP = pair.split('=')
                    RET[SP[0]] = SP[1].replace('+',' ')
        return RET

    def dictMerge(self,D1,D2):
        for key in D1:
            D2[key] = D1[key]
        return D2

    def parseRequest(self,Req):
        SP = Req.decode().replace('\r','\n').split('\n')
        Resource = SP[0]

        #Process HTTP Attributes
        OUT = {}
        for i in SP[1:]:
            if (len(i) > 3) and (':' in i):
                REQ_SP = i.split(': ')
                OUT[REQ_SP[0]] = REQ_SP[1]
            elif '=' in i:
                OUT = self.dictMerge(OUT,self.procGet(i))


        #Process GET Info
        Resource = Resource.split(' ')[1]
        if '?' in Resource:
            Resource,GET = Resource.split('?')
            OUT = self.dictMerge(OUT,self.procGet(GET))
                    

        return OUT,Resource


    def client(self,CON,ID):
        try:
            #Upgrade to TLS if required
            if self.config['TlsEnable'].lower() == 'true':
                CON = TLSwrapper.wrappedServer(CON,self.config['TlsKey'],self.config['TlsCert'])


            Request = CON.getdat(1024)
            self.print(ID,"Got Request")

            try:
                ParsedOptions,Resource = self.parseRequest(Request)

                self.print(ID,"has requested",Resource,"By",CON.report()['Address'])

                #self.print(json.dumps(ParsedOptions,indent=4))

                #Determine Response
                if Resource in self.loadedModules:
                    #Handle Websocket
                    if 'Upgrade' in ParsedOptions.keys():
                        if ParsedOptions['Upgrade'] == 'websocket':
                            self.print(ID,"Upgrading to Websocket")
                            HEADER = WebsocketUtils.responseHeader(ParsedOptions)
                            CON.sendstdat(HEADER)

                            #Now we begin websocket
                            self.modules[Resource].websocket(ParsedOptions,CON,self.PassIn)

                    #Handle HTTP
                    else:
                        ContentType = self.modules[Resource].typeHeader(ParsedOptions,self.PassIn)
                        Body = self.modules[Resource].body(ParsedOptions,CON,self.PassIn)
                        ContentLength = str(len(Body))
                        Extra = self.modules[Resource].headerExtra(ParsedOptions,self.PassIn)

                        CON.senddat(
                            NORMAL_HEADER.replace('[LENGTH]',ContentLength).replace('[TYPE]',ContentType).replace('[EXTRA]',Extra).encode() + Body
                            )
                            


                else:
                    if self.config['CatchAll'].lower() == 'true':
                        ContentType = self.catch.typeHeader(ParsedOptions,self.PassIn)
                        Body = self.catch.body(ParsedOptions,CON,self.PassIn)
                        ContentLength = str(len(Body))
                        Extra = self.catch.headerExtra(ParsedOptions,self.PassIn)

                        CON.senddat(
                            NORMAL_HEADER.replace('[LENGTH]',ContentLength).replace('[TYPE]',ContentType).replace('[EXTRA]',Extra).encode() + Body
                        )

                    else:
                        CON.sendstdat(E404)
            except Exception as E:
                self.print("ERR",E)
                CON.sendstdat(E500)

        except TLSwrapper.ssl.SSLError:
            self.print("CertError")







    def run(self):
        #This is the main connection accepter
        IDcounter = 0
        while True:

            while self.connectionCount > int(self.config['MaxConnections']):
                for count in range(len(self.connections)):
                    con = self.connections[len(self.connections)-1-count]
                    Report = con['con'].report()
                    if (not con['thread']) or (not Report['Alive']) or ((time.time() - Report['InitTime']) > int(self.config['MaxConnectionTime']) ):
                        self.print("Connection Terminate",str(con['ID']))
                        del self.connections[len(self.connections)-1-count]
                        self.connectionCount -= 1

                time.sleep(0.1)

            #Accept a Client
            Connection = TCPstreams3.serverCon(self.server)
            

            self.connections.append(
                {
                    'con':Connection,
                    'thread':threading.Thread(target=self.client,args=(Connection,IDcounter),name='Worker'+str(IDcounter)),
                    'ID':IDcounter
                }
            )

            self.connections[-1]['thread'].start()

            self.print("Started Connection",IDcounter)

            IDcounter += 1

            





if __name__ == '__main__':
    try:
        Config = ConfigUtils.complexParseConfig(sys.argv[1])
    except:
        print("Config Error, Loading Default")
        Config = ConfigUtils.complexParseConfig('webConfig.conf')
    serv = webServer(Config)
    serv.run()
