from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

HTML_SNIPPET = """
<html>
    <body>
        <h1>Authentication successful!</h1>
        <p>
            You can now close this window.
        </p>
    </body>
</html>
"""


class AuthHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        # Suppress logging
        pass

    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        if "code" in params:
            self.server.last_auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_SNIPPET.encode("utf-8"))


class AuthWebServer:
    def __init__(self, port: int):
        self.port = port
        self.server = HTTPServer(
            ("localhost", self.port),
            AuthHandler,
        )

    def handle_request(self):
        self.server.handle_request()
        return self.server.last_auth_code
