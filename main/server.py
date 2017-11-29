from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import version as python_version
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
import json
from helper import process

# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Send message back to client
        message = "Hello world!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

    def parse_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        print('content-type', ctype, pdict)
        length = int(self.headers['content-length'])
        print('content-length', length)
        data = self.rfile.read(length)
        data = data.decode(encoding='UTF-8')
        # if ctype == 'multipart/form-data':
        #     postvars = parse_multipart(self.rfile, pdict)
        # elif ctype == 'application/x-www-form-urlencoded':
        #     length = int(self.headers['content-length'])
        #     postvars = parse_qs(
        #         self.rfile.read(length),
        #         keep_blank_values=1)
        # else:
        #     postvars = {}
        return data

    def do_POST(self):
        data = self.parse_POST()
        # print(data)
        js = json.loads(data)
        # print(js)
        message = process(js)

        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Send message back to client
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))


def run():
    print('starting server...')
    HOST = '127.0.0.1'
    PORT = 8081
    print('{}:{}'.format(HOST, PORT))
    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()


run()