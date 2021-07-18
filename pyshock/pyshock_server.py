#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import json
import sys
import shutil
import traceback

import config

from pyshock.pyshocklib import Pyshock, PyshockMock
from pyshock.pyshocklibdevices import Action

__pyshock = None

class PyshockRequestHandler(BaseHTTPRequestHandler):

    def answer(self, status, data):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write((json.dumps(data)).encode('utf-8'))


    def handle_command(self, params):
        if (params["token"][0] != config.web_authentication_token):
            raise Exception("Invalid authentication token")

        action = Action[params["action"][0]]
        device = int(params["device"][0])
        power = int(params["power"][0])
        duration = int(params["duration"][0])

        if not action in [Action.LED, Action.BEEP, Action.VIB, Action.ZAP, Action.BEEPZAP]:
            raise Exception("Invalid action")

        __pyshock.command(action, device, power, duration)


    def do_GET(self):
        files = ["/index.html", "/remote.css", "/remote.js", "/favicon.png", "/manifest.json"]
        types = ["text/html; charset=utf-8", "text/css", "application/javascript", "image/png", "application/json"]

        if self.path == "/":
            self.path = "/index.html"

        params = parse_qs(urlparse(self.path).query)
        try:
            if self.path.startswith("/pyshock/command"):
                self.handle_command(params)
                self.answer(200, { "status": "ok"})
            elif self.path.startswith("/pyshock/config"):
                self.answer(200, __pyshock.get_config())
            elif self.path in files:
                self.send_response(200)
                self.send_header("Content-Type", types[files.index(self.path)])
                self.end_headers()
                with open("web/" + self.path, "rb") as content:
                    shutil.copyfileobj(content, self.wfile)
            else:
                self.answer(404, "unknown path: " + self.path)
        except Exception as ex:
            print("".join(traceback.TracebackException.from_exception(ex).format()))
            self.answer(500, { "error": str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1])})

class PyshockServer:
    
    def __boot_pyshock(self):
        global __pyshock
        if len(sys.argv) > 1 and sys.argv[1] == "mock":
            pyshock = PyshockMock()
        else:
            pyshock = Pyshock()
        pyshock.boot()
        __pyshock = pyshock

    def __start_web_server(self):
        port = int(config.web_port)
        print()
        print("Open http://127.0.0.1:" + str(port) + "/#token=" + config.web_authentication_token)
        print()

        server = ThreadingHTTPServer(('0.0.0.0', port), PyshockRequestHandler)
        server.serve_forever()


    def start(self):
        self.__boot_pyshock()
        self.__start_server()
