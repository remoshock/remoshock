#
# Copyright nilswinter 2020-2022. License: AGPL
# _____________________________________________

import os
import shutil
from http.cookies import SimpleCookie
from urllib.parse import unquote

MIME_CONTENT_TYPES = {
    ".css": "text/css",
    ".html": "text/html; charset=utf-8",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".js": "application/javascript",
    ".json": "application/json",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".woff2": "font/woff2"
}


class FileHandler():
    """handles requests from web browsers for static files"""


    def __init__(self, requesthandler):
        self.requesthandler = requesthandler


    def verify_authentication_cookie(self):
        """verifies the authentication cookie"""

        cookies = SimpleCookie(self.requesthandler.headers.get("Cookie"))
        if "authentication_token" not in cookies:
            return False

        expected_token = self.requesthandler.remoshock.config.get("global", "web_authentication_token")
        return cookies["authentication_token"].value == expected_token


    def serve_file(self):
        """serves a file from the web-folder

        this methods takes care of preventing directory traversing
        and automatically expands directory references to index.html.
        Furthermore it sends the correct headers."""

        web_folder = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + "/../web")
        filename = os.path.normpath(web_folder + unquote(self.requesthandler.path))
        if not filename.startswith(web_folder):
            self.requesthandler.answer_html(404, "Invalid file name.")
            return

        if not self.requesthandler.path.startswith("/auth") and not self.verify_authentication_cookie():
            filename = os.path.normpath(web_folder + "/auth/index.html")
            self.send_file(filename, 403, False, False)
            return


        if os.path.isdir(filename):
            filename = filename + "/index.html"

        compressed = False
        if not os.path.isfile(filename):
            if os.path.isfile(filename + ".gz"):
                compressed = True
            else:
                self.requesthandler.answer_html(404, "Not found.")
                return

        self.send_file(filename, 200, True, compressed)


    def send_file(self, filename, status, cache, compressed):
        """answers a browser request with the content of a file

        @param filename filename on disk
        @paran status http status code
        @param cache False to prevent caching
        @param compressed True, if the file gzip-compressed
        """

        ext = os.path.splitext(filename)[1]
        self.requesthandler.send_response(status)
        self.requesthandler.send_header("Content-Type", MIME_CONTENT_TYPES.get(ext.lower(), "application/octet-stream"))
        self.requesthandler.send_header("Content-Security-Policy", "default-src 'self'")
        if not cache:
            self.requesthandler.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        if compressed:
            self.requesthandler.send_header("Content-Encoding", "gzip")
        self.requesthandler.end_headers()

        if compressed:
            filename = filename + ".gz"

        with open(filename, "rb") as content:
            shutil.copyfileobj(content, self.requesthandler.wfile)
