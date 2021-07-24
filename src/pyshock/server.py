#!/usr/bin/python3
#
# Copyright nilswinter 2020-2021. License: AGPL
#_______________________________________________


from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import argparse
import html
import json
import os
import ssl
import sys
import shutil
import traceback


from pyshock.core.pyshock import Pyshock, PyshockMock
from pyshock.core.action import Action
from pyshock.core.version import VERSION

pyshock = None

mimetypes = {
    ".css": "text/css",
    ".html": "text/html; charset=utf-8",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".js": "application/javascript",
    ".json": "application/json",
    ".png": "image/png"
}

class PyshockRequestHandler(BaseHTTPRequestHandler):
    """handles requests from web browsers"""
    
    def answer_json(self, status, data):
        """Sends a JSON response"""
        try:
            self.send_response(status)
            self.send_header("Content-type", "application/json")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        except BrokenPipeError:
            print("Browser disconnected")
            pass

    def answer_html(self, status, text):
        """Sends a message as HTML-response"""
        try:
            self.send_response(status)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(html.escape(text).encode('utf-8'))
        except BrokenPipeError:
            print("Browser disconnected")
            pass


    def verify_authentication_token(self, params):
        """validates authentication token"""
        if not "token" in params:
            return False

        return params["token"][0] == pyshock.config.get("global", "web_authentication_token")


    def handle_command(self, params):
        """Sends the specified command to specified receiver"""
        action = Action[params["action"][0]]
        receiver = int(params["receiver"][0])
        power = int(params["power"][0])
        duration = int(params["duration"][0])

        if not action in [Action.LIGHT, Action.BEEP, Action.VIBRATE, Action.SHOCK, Action.BEEPSHOCK]:
            raise Exception("Invalid action")

        pyshock.command(receiver, action, power, duration)


    def serve_file(self):
        """serves a file from the web-folder
        
        this methods takes care of preventing directory traversing
        and automatically expands directory references to index.html.
        Furthermore it sends the correct MIME Content-Type header."""

        if ".." in self.path:
            self.answer_html(404, "Invalid file name.")
            return

        filename = "web/" + self.path
        if os.path.isdir(filename):
            filename = filename + "/index.html"

        if not os.path.isfile(filename):
            self.answer_html(404, "Not found.")
            return

        ext = os.path.splitext(filename)[1]
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.get(ext.lower(), "application/octet-stream"))
        self.end_headers()
        with open(filename, "rb") as content:
            shutil.copyfileobj(content, self.wfile)


    def do_GET(self):
        """handles a browser request.
        
        path starting with /pyshock are interpreted as commands.
        everything else is seen as a reference to the web-folder"""

        params = parse_qs(urlparse(self.path).query)
        try:
            if self.path.startswith("/pyshock/"):
                if not self.verify_authentication_token(params):
                    self.answer_html(403, "Missing or invalid authentication token")
                    return

                if self.path.startswith("/pyshock/command"):
                    self.handle_command(params)
                    self.answer_json(200, { "status": "ok"})
                elif self.path.startswith("/pyshock/config"):
                    self.answer_json(200, pyshock.get_config())

            else:
                self.serve_file()
        except Exception as ex:
            print("".join(traceback.TracebackException.from_exception(ex).format()))
            self.answer_html(500, str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]))



class PyshockServer:
    """pyshockserver is a web server that provides the remote-control user-interface """

    def __parse_args(self):
        """parses command line arguments"""
        parser = argparse.ArgumentParser(description="Shock collar remote control",
                                         epilog="Please see https://github.com/pyshock/pyshock for documentation.")
        parser.add_argument("--mock",
                            action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument("--sdr",
                            help=argparse.SUPPRESS)
        parser.add_argument("-v", "--verbose",
                            action="store_true",
                            help="prints debug messages")
        parser.add_argument("--version",
                            action="version",
                            version=VERSION)
    
        self.args = parser.parse_args()


    def __boot_pyshock(self):
        """starts up the pyshock infrastructure"""
        global pyshock
        if self.args.mock:
            pyshock = PyshockMock(self.args)
        else:
            pyshock = Pyshock(self.args)
        pyshock.boot()


    def __start_web_server(self):
        """starts the webserver on tcp-port configured in pyshock.ini"""
        port = pyshock.config.getint("global", "web_port", fallback=7777)
        print()
        print("Open http://127.0.0.1:" + str(port) + "/#token=" + pyshock.config.get("global", "web_authentication_token"))
        print()

        server = ThreadingHTTPServer(('0.0.0.0', port), PyshockRequestHandler)
        certfile = pyshock.config.get("global", "web_server_certfile", fallback=None) 
        if certfile:
            server.socket = ssl.wrap_socket(server.socket, certfile=certfile, server_side=True)
        server.serve_forever()


    def start(self):
        """starts up pyshockserver"""
        self.__parse_args()
        self.__boot_pyshock()
        self.__start_web_server()
