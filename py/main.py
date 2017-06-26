#!/usr/bin/python
import sys
import os
import server as handler
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer


PORT_NUMBER = 8080

if __name__ == "__main__":
	arguments = sys.argv

try:
	#Create a web server and define the handler to manage the
	#incoming request

	server = HTTPServer(('', PORT_NUMBER), handler.MyHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
