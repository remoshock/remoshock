#
# Copyright nilswinter 2020-2025. License: AGPL
# _____________________________________________

import html
import logging
import sys
import traceback
from http.server import BaseHTTPRequestHandler

from remoshock.httpserver.filehandler import FileHandler
from remoshock.httpserver.resthandler import RestHandler


class RequestHandler(BaseHTTPRequestHandler):
    """handles requests from web browsers"""


    def answer_html(self, status, text):
        """Sends a message as HTML-response"""
        try:
            self.send_response(status)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Content-Security-Policy", "default-src 'self'")
            self.end_headers()
            self.wfile.write(html.escape(text).encode('utf-8'))
        except BrokenPipeError:
            logging.warn("Browser disconnected")


    def do_GET(self):
        """handles a browser request.

        path starting with /remoshock are interpreted as commands.
        everything else is seen as a reference to the web-folder"""

        try:
            if self.path.startswith("/remoshock/"):
                resthandler = RestHandler(self)
                resthandler.serve_rest()
            else:
                filehandler = FileHandler(self)
                filehandler.serve_file()
        except BrokenPipeError:
            logging.debug("Browser disconnected")
        except Exception as ex:
            logging.error("".join(traceback.TracebackException.from_exception(ex).format()))
            self.answer_html(500, str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]))


    def do_POST(self):
        """handles a browser request.

        path starting with /remoshock are REST services.
        everything else is rejected"""

        try:
            if self.path.startswith("/remoshock/"):
                resthandler = RestHandler(self)
                resthandler.serve_rest()
            else:
                self.answer_html(500, "POST is only valid for REST services")()
        except BrokenPipeError:
            logging.debug("Browser disconnected")
        except Exception as ex:
            logging.error("".join(traceback.TracebackException.from_exception(ex).format()))
            self.answer_html(500, str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]))


    def log_message(self, *arguments):
        """log requests, if verbose logging is active"""

        if RequestHandler.args.verbose:
            super().log_message(*arguments)
