# SimpleWebServer
A Simple Python Webserver

This is a very basic HTTP, HTTPS, Websocket (WS) and Secure Websocket (WSS) Server.
It is intended to be educational and definitely isn't secure. - Don't use it in any production environments unless you understand the risks.



Usage:
- The main file is 'SimpleWebServer3.py'
- This can be executed directly with one command line argument pointing to the config file
- Alternatively, the file can be imported and the class initialised with a dictionary of configuration values.


To Do: (Coming Soon)
- Bug fix - Close Connections
- Reuse of Existing Connections (Keepalive)
- Class based page files and responses
- Allow returning of HTTP Status Codes from page files
- Attach resource http request to page file input
- Basic (htaccess like) 401 Challenge Authentication
- Security Hardening
