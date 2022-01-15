#
# Copyright nilswinter 2020-2022. License: AGPL
# _____________________________________________

import json
from urllib.parse import parse_qs, urlparse

from remoshock.core.action import Action

remoshock = None
args = None


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
            print("Browser disconnected")



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
            print("Invalid authentication header or invalid Bearer token.")

        if "token" in params:
            return params["token"][0] == expected_token

        return False


    def handle_command(self, params):
        """Sends the specified command to specified receiver"""

        action = Action[params["action"][0]]
        receiver = int(params["receiver"][0])
        power = int(params["power"][0])
        duration = int(params["duration"][0])

        if action not in [Action.LIGHT, Action.BEEP, Action.VIBRATE, Action.SHOCK, Action.BEEPSHOCK]:
            raise Exception("Invalid action")

        self.requesthandler.remoshock.command(receiver, action, power, duration)


    def serve_rest(self):
        """serves a rest request"""

        path = self.requesthandler.path
        params = parse_qs(urlparse(path).query)
        if not self.verify_authentication_token(self.requesthandler.headers, params):
            self.answer_html(403, "Missing or invalid authentication token")
            return

        if path.startswith("/remoshock/command"):
            self.handle_command(params)
            self.answer_json(200, {"status": "ok"})
        elif path.startswith("/remoshock/config"):
            self.answer_json(200, self.requesthandler.remoshock.get_config())
        else:
            self.answer_json(400, {"status": "unknown service"})
