#
# Copyright nilswinter 2020-2025. License: AGPL
# _____________________________________________

import json
import logging
import os
import shutil

from urllib.parse import parse_qsl, urlparse

from remoshock.core.action import Action


class RestHandler:
    """handles requests for REST services"""

    def __init__(self, requesthandler):
        self.requesthandler = requesthandler


    def answer_json(self, status, data):
        """Sends a JSON response"""
        try:
            self.requesthandler.send_response(status)
            self.requesthandler.send_header("Content-type", "application/json")
            self.requesthandler.send_header("Cache-Control", "no-cache")
            self.requesthandler.send_header("Access-Control-Allow-Origin", "*")
            self.requesthandler.end_headers()
            self.requesthandler.wfile.write(json.dumps(data).encode('utf-8'))
        except BrokenPipeError:
            logging.warn("Browser disconnected")



    def verify_authentication_token(self, headers, params):
        """validates authentication token

        @param headers HTTP headers
        @param params  url parameters
        """
        expected_token = self.requesthandler.remoshock.config.get("global", "web_authentication_token")

        auth_header = headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2:
                if parts[0].lower() == "bearer":
                    if parts[1] == expected_token:
                        return True
            logging.warn("Invalid authentication header or invalid Bearer token.")

        if "token" in params:
            return params["token"] == expected_token

        return False


    def handle_command(self, params):
        """Sends the specified command to specified receiver"""

        action = Action[params["action"]]
        receiver = int(params["receiver"])
        power = int(params["power"])
        duration = int(params["duration"])
        source = params["source"] if "source" in params else "client"

        if action not in [Action.LIGHT, Action.BEEP, Action.VIBRATE, Action.SHOCK, Action.BEEPSHOCK]:
            raise Exception("Invalid action")

        self.requesthandler.remoshock.command(receiver, action, power, duration, "web-" + source)


    def read_parameters(self):
        """reads parameters from json body and url"""

        request = self.requesthandler
        params = {}

        command = request.command.upper()
        if command == "POST" or command == "PUT":
            length = int(request.headers.get('content-length'))
            if length > 0:
                params = json.loads(request.rfile.read(length))

        path = request.path
        params.update(dict(parse_qsl(urlparse(path).query)))
        return params


    def handle_log(self):
        """sends the logfile to the client"""

        self.requesthandler.send_response(200)
        self.requesthandler.send_header("Content-Type", "text/plain")
        self.requesthandler.send_header("Content-Security-Policy", "default-src 'self'")
        self.requesthandler.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.requesthandler.end_headers()
        with open(os.getenv("HOME") + "/remoshock.log", "rb") as content:
            shutil.copyfileobj(content, self.requesthandler.wfile)



    def handle_restart(self):
        """shuts the server down, assuming systemd will restart it"""

        if self.requesthandler.args.enable_feature is not None \
                and "restart" in self.requesthandler.args.enable_feature:
            logging.info("Restarting remoshock server")
            self.answer_json(200, {"status": "ok"})
            os._exit(3)
        else:
            logging.warn("Restarting remoshock server not allowed, feature not enabled")
            self.answer_json(200, {"status": "not enabled"})


    def serve_rest(self):
        """serves a rest request"""

        path = self.requesthandler.path
        method = self.requesthandler.command.upper()
        params = self.read_parameters()
        if not self.verify_authentication_token(self.requesthandler.headers, params):
            self.requesthandler.answer_html(403, "Missing or invalid authentication token")
            return

        if path.startswith("/remoshock/command"):
            self.handle_command(params)
            self.answer_json(200, {"status": "ok"})

        elif path.startswith("/remoshock/config"):
            if method == "POST":
                self.requesthandler.remoshock.config_manager.save_settings(params["settings"])
            self.answer_json(200, self.requesthandler.remoshock.get_config())

        elif path.startswith("/remoshock/randomizer"):
            if method == "POST":
                if "start" in path:
                    error = self.requesthandler.randomizer.start_in_server_mode(params)
                    if error != "":
                        self.answer_json(422, {"status": "error", "error": error})
                        return
                elif "stop" in path:
                    self.requesthandler.randomizer.stop_in_server_mode()
                else:
                    self.answer_json(404, {"status": "unknown service for randomizer"})
                    return
            self.answer_json(200, self.requesthandler.randomizer.get_status_and_config())

        elif path.startswith("/remoshock/log"):
            self.handle_log()

        elif path.startswith("/remoshock/admin/restart"):
            if method == "POST":
                self.handle_restart()

        else:
            self.answer_json(404, {"status": "unknown service"})
