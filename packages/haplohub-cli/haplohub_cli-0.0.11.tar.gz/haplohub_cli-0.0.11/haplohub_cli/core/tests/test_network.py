import socket
from unittest import TestCase

from haplohub_cli.core.network import check_port_available


class NetworkTestCase(TestCase):
    def test_check_port_available_should_return_true_when_port_is_available(self):
        with socket.socket() as sock:
            sock.bind(("localhost", 0))
            port = sock.getsockname()[1]

        self.assertTrue(check_port_available(port))

    def test_check_port_available_should_return_false_when_port_is_not_available(self):
        with socket.socket() as sock:
            sock.bind(("localhost", 0))
            port = sock.getsockname()[1]
            sock.listen()
            self.assertFalse(check_port_available(port))
