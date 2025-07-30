from threading import Timer
from unittest import TestCase

import requests

from haplohub_cli.auth.auth_web_server import AuthWebServer


class AuthWebServerTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 60000
        cls.auth_code = "qwerty123456"
        cls.instance = AuthWebServer(cls.port)

    def test_auth_web_server_should_return_auth_code_from_redirect_uri(self):
        Timer(0.01, self._send_request).start()
        auth_code = self.instance.handle_request()
        self.assertEqual(auth_code, self.auth_code)

    def _send_request(self):
        requests.get(f"http://localhost:{self.port}/?code={self.auth_code}")
