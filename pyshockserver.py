#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import json
import sys

import config
from pyshocklib import Pyshock, Action


pyshock = Pyshock()
pyshock.boot()

class PyshockRequestHandler(BaseHTTPRequestHandler):

    def answer(self, status, message):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(('{"status": ' + json.dumps(message) + '}').encode('utf-8'))


    def handle_command(self, params):
        if (params["token"][0] != config.web_authentication_token):
            raise Exception("Invalid authentication token")

        action = Action[params["action"][0]]
        device = int(params["device"][0])
        power = int(params["power"][0])
        duration = int(params["duration"][0])

        if not action in [Action.LED, Action.BEEP, Action.VIB, Action.ZAP]:
            raise Exception("Invalid action")

        pyshock.command(action, device, power, duration)


    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        try:
            if self.path.startswith("/pyshock"):
                self.handle_command(params)
                self.answer(200, "ok")
            else:
                self.answer(404, "unknown path: " + self.path)
        except Exception:
            self.answer(500, str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]))


server = ThreadingHTTPServer(('localhost', 7777), PyshockRequestHandler)
server.serve_forever()

