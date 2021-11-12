#!/usr/bin/env python3
#GNU General Public License v3.0
#Code by MegaKG

#Import some of the custom support libraries
import TCPstreams3 #This handles TCP sockets nicely
import TLSwrapper #This converts TCP sockets from the above library to SSL, providing the same interface
import ConfigUtils #Loads configuration from files
import Logger #Logs to files with date and time
import WebsocketUtils #Handler for Websocket magic 

#Import standard library things
import sys #Used to get commandline arguments
import threading #Used to start handlers for clients after they have connected
import time #Used to get Current Epoch time in seconds
import importlib #Used to dynamically load python files 
import json #Processes JSON text


#This is a normal response header by the server for HTTP requests
#200 = the HTTP code for success
#Content-Type is the mimetype, text/html is the most common
#In this case, the [EXTRA] area is replaced with extra tags from the python page
NORMAL_HEADER = """HTTP/1.1 200 OK
Server: KPython V3
Vary: Accept-Encoding
Content-Length: [LENGTH]
Content-Type: [TYPE]
[EXTRA]

"""

#This is an error response (Header and Body) for if the requested resource isn't found
#404 = HTTP code for not found
E404 = """HTTP/1.1 404 Not Found
Server: KPython V3
Vary: Accept-Encoding
Content-Type: text/html


<html><p>404 Not Found</p></html>
"""

#This is an error response (Header and Body) for if something breaks in the webpage during runtime
#505 = HTTP code for internal server error
E500 = """HTTP/1.1 500 Internal Server Error
Server: KPython V3
Vary: Accept-Encoding
Content-Type: text/html


<html><p>500 Internal Server Error</p></html>
"""

#The main class, initialised as follows:
#Server = webServer(Dict)
#Where Dict is a Dictionary containing required configuration values
#PassIn is an optional argument that can be used to pass objects to webpage workers (Intended for use if this server is run as a library)
class webServer:
    #Redefine the Print Command to enable logging
    #Here we take any amount of arguments, converting them all to strings with spaces in between
    def print(self,*Input):
        StringOut = ''
        for i in Input:
            StringOut += str(i) + ' '
        StringOut = StringOut[:-1]
        self.logObj.log(StringOut)


    #The Initialisation code of the class / webserver object
    def __init__(self,Config,PassIn=None):
        #The first thing to do is initialise the logger so error messages have somewhere to go
        self.logObj = Logger.logger(Config['LogFile'])
        self.print("Initiate Server")

        #Save the Config internally
        self.config = Config

        #Open the TCP server socket on specified Address and Port
        self.server = TCPstreams3.newServer(Config['HostAddress'],int(Config['HostPort']))

        #These keep track of connnected clients (and their threads)
        self.connections = []
        self.connectionCount = 0

        #Dynamically import all of the Page Python files
        self.modules = {}
        for location in self.config['Pages']:
            self.print("Import",location,self.config['Pages'][location])
            self.modules[location] = importlib.import_module(self.config['Pages'][location].split('.py')[0])

        #Create a fast lookup array for all available locations
        self.loadedModules = set(self.modules.keys())

        #If a Catch-all page is defined, load it as well
        if self.config['CatchAll'].lower() == 'true':
            self.catch = importlib.import_module(self.config['CatchPage'].split('.py')[0])
        else:
            self.catch = None

        #Keep track of this as well
        self.PassIn = PassIn

    #This processes GET requests
    def procGet(self,GETR):
        RET = {}
        for pair in GETR.split('&'):
                    SP = pair.split('=')
                    RET[SP[0]] = SP[1].replace('+',' ')
        return RET

    #Merges two dictionaries, internal method
    def _dictMerge(self,D1,D2):
        for key in D1:
            D2[key] = D1[key]
        return D2

    #This parses HTTP request headers from the client
    def parseRequest(self,Req):
        #First Get the Request type and resource
        SP = Req.decode().replace('\r','\n').split('\n')
        Resource = SP[0]

        #Process HTTP Attributes in the request
        OUT = {}
        for i in SP[1:]:
            if (len(i) > 3) and (':' in i):
                REQ_SP = i.split(': ')
                OUT[REQ_SP[0]] = REQ_SP[1]
            elif '=' in i:
                OUT = self._dictMerge(OUT,self.procGet(i))


        #Process GET values
        Resource = Resource.split(' ')[1]
        if '?' in Resource:
            Resource,GET = Resource.split('?')
            OUT = self._dictMerge(OUT,self.procGet(GET))
                    

        return OUT,Resource


    def client(self,CON,ID):
        try:
            #Upgrade to TLS if required
            if self.config['TlsEnable'].lower() == 'true':
                CON = TLSwrapper.wrappedServer(CON,self.config['TlsKey'],self.config['TlsCert'])

            #Read our Request
            Request = CON.getdat(1024)
            self.print(ID,"Got Request")

            try:
                #Parse the raw request and get both the resource and the variable values
                ParsedOptions,Resource = self.parseRequest(Request)

                #Keep a record of this transaction
                self.print(ID,"has requested",Resource,"By",CON.report()['Address'])

                #Determine type of Response
                #First check if the resource exists
                if Resource in self.loadedModules:
                    #Handle Websocket
                    if 'Upgrade' in ParsedOptions.keys():
                        #If a websocket is wanted
                        if ParsedOptions['Upgrade'] == 'websocket':
                            if self.config['AllowWebsocket'].lower() == 'true':
                                self.print(ID,"Upgrading to Websocket")
                                #Do the special magic that prevents Caching
                                HEADER = WebsocketUtils.responseHeader(ParsedOptions)
                                CON.sendstdat(HEADER)

                                #Convert CON to something usable
                                CON = WebsocketUtils.wrappedConnection(CON)

                                #Now we begin websocket
                                try:
                                    self.modules[Resource].websocket(ParsedOptions,CON,self.PassIn)
                                except OSError:
                                    self.print(ID,"Websocket Died")

                    #Handle HTTP
                    else:
                        #Respond with the requested resource
                        #First get the content type from the python file
                        ContentType = self.modules[Resource].typeHeader(ParsedOptions,self.PassIn)
                        #Then the body content
                        Body = self.modules[Resource].body(ParsedOptions,CON,self.PassIn)
                        #Calculate length of the response
                        ContentLength = str(len(Body))
                        #Get any extra attributes that need to be in the response header
                        Extra = self.modules[Resource].headerExtra(ParsedOptions,self.PassIn)

                        #Finally send it
                        CON.senddat(
                            NORMAL_HEADER.replace('[LENGTH]',ContentLength).replace('[TYPE]',ContentType).replace('[EXTRA]',Extra).encode() + Body
                            )
                            

                #Otherwise, handle it
                else:
                    if self.config['CatchAll'].lower() == 'true':
                        #Server Catchall page
                        #First get the content type from the python file
                        ContentType = self.catch.typeHeader(ParsedOptions,self.PassIn)
                        #Then the body content
                        Body = self.catch.body(ParsedOptions,CON,self.PassIn)
                        #Calculate length of the response
                        ContentLength = str(len(Body))
                        #Get any extra attributes that need to be in the response header
                        Extra = self.catch.headerExtra(ParsedOptions,self.PassIn)

                        #Here we modify the websocket to allow it to persist longer than a HTTP Connection
                        #This requires modifying the connection (class) attributes. It is a hack and is poor practice, but works!
                        #To enable this, the initialisation time is pushed into the future
                        CON.info['InitTime'] = time.time() + int(self.config['WebsocketMaxTime'])

                        #Finally send it
                        CON.senddat(
                            NORMAL_HEADER.replace('[LENGTH]',ContentLength).replace('[TYPE]',ContentType).replace('[EXTRA]',Extra).encode() + Body
                        )

                    else:
                        #Server 404 response
                        CON.sendstdat(E404)

            except Exception as E:
                self.print("ERR",E)
                #raise #For Debug
                CON.sendstdat(E500)

        except TLSwrapper.ssl.SSLError:
            self.print("CertError")


    #This is the main loop of the webserver
    def run(self):

        #For logging, each client has an ID per connection
        IDcounter = 0
        while True:
            #First wait for an available position (If the server is full)
            while self.connectionCount > int(self.config['MaxConnections']):
                #Iterate over all threads, killing those that should be gone
                for count in range(len(self.connections)):
                    con = self.connections[len(self.connections)-1-count]
                    Report = con['con'].report()
                    #Here we check how long the connection is on and if the system reports it as alive, thus preventing DoS attacks
                    if (not con['thread']) or (not Report['Alive']) or ((time.time() - Report['InitTime']) > int(self.config['MaxConnectionTime']) ):
                        self.print("Connection Terminate",str(con['ID']))
                        del self.connections[len(self.connections)-1-count]
                        self.connectionCount -= 1

                time.sleep(0.1)

            #Accept a Client
            Connection = TCPstreams3.serverCon(self.server)
            
            #Create a record
            self.connections.append(
                {
                    'con':Connection,
                    'thread':threading.Thread(target=self.client,args=(Connection,IDcounter),name='Worker'+str(IDcounter)),
                    'ID':IDcounter
                }
            )

            #Start the handler
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
