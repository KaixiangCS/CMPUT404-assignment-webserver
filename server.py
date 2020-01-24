#  coding: utf-8
import socketserver
import os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# get the first part (method like GET) and the second part (the address) from the request
def handle_request(data):
    list_1 = data.split()[0:2]
    return list_1

# check if the method is indeeeed GET
def handle_method(method):
    if method == "GET":
        return False
    else:
        return True

# since we are trying to use www to find the file
def handle_path(list_1):
    # I dont know why sometimes if I keep refresh the page the request will be
    # nothing, the folllowing is for handling that problem
    if len(list_1) < 2:
        method = "None"
        path = "/"
    else:
        method = list_1[0]
        path = list_1[1]
        # handling the problem without the "/" at the beginning of the path
        if(path[0] != "/"):
            path = "/" + path
    # here since we serve files from the www directory so we need to add www before the path
    # however the problems is some of the path has the www someone are not
    # in order to form www/....... we have to
    if(path[0:4]=="/www"):
        final_path = path[1:]
    else:
        final_path = "www" + path
    return [method,final_path]

# this function is used to handle the response for each case
def handle_response(list_2):
    [method,final_path] = list_2
    # initialize 2 kind of redirct cases here
    # first one is for check if the directory have file if have then redirect
    # example: deep/ ==> deep/index.html
    redirect_1 = False
    # example: deep ==> deep/
    redirect_2 = False
    '''
    print(os.path.abspath(final_path))
    print(os.getcwd())
    print(final_path)
    print(os.path.isfile(os.path.abspath(final_path)))

    print(final_path)
    print(os.path.normpath(final_path))

    print(os.path.abspath(final_path))
    print(os.getcwd())
    print(final_path)
    print(os.path.isfile(os.path.abspath(final_path)))
    '''
    # check if the method is GET
    if(handle_method(method)):
        response = handle_return("405",final_path)
    # check if it is already file
    elif((os.path.isfile(final_path))and(os.getcwd() in os.path.abspath(final_path))):
        response = handle_return("200",final_path)
    # check if it is a path and with a good url
    elif((os.path.isdir(final_path))and(os.getcwd() in os.path.abspath(final_path))):
        # check if need redirect
        if(final_path[-1]!="/"):
            redirect_1 = True
            redirect_2 = True
        if not redirect_2:
            final_path = final_path +  "index.html"
            # check if there is a file in the end
            if(os.path.isfile(final_path)):
                response = handle_return("200",final_path)
        # 2nd case redirect
        # this time cant use isfile since + "/" may still not a file
        if(os.path.exists(final_path)):
            if(redirect_1):
                if (redirect_2):
                    final_path = final_path + "/"
                response = handle_return("301",final_path)
        else:
            response = handle_return("404",final_path)
    else:
        response = handle_return("404",final_path)
    return response

# form the return here
def handle_return(status,path):
    respond = "HTTP/1.1 "
    if status == '405':
        respond = respond + "405 Method Not Allowed \r\n"
    elif status == '301':
        respond = respond + "301 Moved Permanently \r\n" + "Location: " + path[3:] +"\r\n\r\n"
    elif status == '200':
        respond = respond + "200 OK \r\n"
        if(".css" in path):
            with open(path,'r', encoding="utf8") as f:
                file = f.read()
                leng = len(file)
                length = str(leng)
                '''
                length = len(file.read())
                string = str(length)
                 + "Content-length: "+length+"; \r\n\r\n"
                 '''
                 # here add content-type and content-length as the respone and end with \r\n\r\n
                respond = respond + "Content-Type: text/css \r\n" + "Content-length: " +length+ " \r\n\r\n" + file
                f.close()
        elif(".html" in path):
            with open(path,'r', encoding="utf8") as f:
                file = f.read()
                leng = len(file)
                length = str(leng)
                '''
                length = len(file.read())
                string = str(length)
                 + "Content-length: "+length+"; \r\n\r\n"
                 '''
                respond = respond + "Content-Type: text/html \r\n" + "Content-length: " +length+ " \r\n\r\n" + file
                f.close()
        else:
            with open(path,'r', encoding="utf8") as f:
                file = f.read()
                leng = len(file)
                length = str(leng)
                '''
                length = len(file.read())
                string = str(length)
                 + "Content-length: "+length+"; \r\n\r\n"
                 '''
                respond = respond + "Content-Type: text/plain \r\n" + "Content-length: " +length+ " \r\n\r\n" + file
                f.close()
    elif status == '404':
        respond = respond + "404 Not FOUND \r\n"
    return respond

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)
        self.data = self.data.decode('utf-8')
        #print(self.data)
        # call the user defined functions
        response = handle_response(handle_path(handle_request(self.data)))
        self.request.sendall(bytearray(response,'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
