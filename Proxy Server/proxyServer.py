from socket import *
import urllib
import os.path
import sys
import time

basedir = os.path.dirname(os.path.abspath(__file__))    # Current directory of proxy server
os.chdir(basedir)                                       # Change the current working directory to proxy server directory

SERVERPORT = 8888
SERVERSOCKET = socket(AF_INET, SOCK_STREAM)
SERVERSOCKET.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)    # Reuse the port
SERVERSOCKET.bind(('localhost', SERVERPORT))
SERVERSOCKET.listen(100)							    # Number of requests to listen for

while True:
    print "Server is ready to receive"
    clientSocket, clientaddr = SERVERSOCKET.accept()        # Accept client connection
    try:
        request = clientSocket.recv(1024).decode()	        # Recive HTTP Request
        print clientaddr , " connected!"
        #print request

        rtrype = request.split(' ')[0]                      # Check request type
        if rtrype != 'GET':                                 # Ignore request if it is not GET
            continue

        url = request.split(' ') [1]                        # Get url
        requestedFilename = os.path.basename(url)           # Get filename from url
        hostname = url.split("/") [2]                       # Get hostname

        requestedFile = open(requestedFilename)
        print "Cache Hit..."
        clientSocket.send(requestedFile.read())             # Send file back
        clientSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())# HTTP Response
        requestedFile.close()

    except IOError:                             
        try:
            c = socket(AF_INET, SOCK_STREAM)            
            c.connect((hostname, 80))
            print "Connected to host..."
            fileobj = c.makefile('r', 0)
            fileobj.write("GET " + url + " HTTP/1.0\n\n")
            buff = fileobj.readlines()

            print "File downloaded!"
            tmpFile = open(requestedFilename, 'wb')
            for line in buff:
                tmpFile.write(line)
                clientSocket.send(line) # send file back

            clientSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())
            tmpFile.close()
        except IOError:
            print "Error 404: File not found"
            clientSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())

clientSocket.close()