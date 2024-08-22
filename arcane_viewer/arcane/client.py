"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.

    Description:
        Client class that handles secure communication with a remote
        server using TLS. Supports password authentication through a
        challenge-based mechanism.

    Todo:
        * (0001) Add support for certificate-based authentication
        * (0002) Display dialog for unknown / first-time seen server
                 certificate
        * (0003) Support for server certificate verification
        * (0004) Implement custom exception for authentication failure,
                 display a message box
"""

import binascii
import hashlib
import json
import logging
import socket
import ssl

import arcane_viewer.arcane as arcane

logger = logging.getLogger(__name__)


class Client:
    """ Client class to handle secure communication with remote server
    Things to note:
        * It is possible to read and write to a socket at the same time, so one thread (for example the main thread) can
        write to the socket while a secondary thread reads from it (at the same time).
    """
    def __init__(self, server_address: str, server_port: int, password: str) -> None:
        self.id = -1

        self.info("Connecting to remote server: `{}:{}`...".format(
            server_address,
            server_port
        ))

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.debug("Creating and configure new SSL context...")
        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE

        self.conn = self.context.wrap_socket(
            self.client,
            server_hostname=server_address,
        )

        self.id = self.conn.fileno()

        self.debug("Establishing connection to remote server...")
        self.conn.settimeout(10)

        self.conn.connect((server_address, server_port))

        server_certificate = self.conn.getpeercert(binary_form=True)
        if server_certificate is None:
            raise arcane.ArcaneProtocolException(
                arcane.ArcaneProtocolError.MissingServerCertificate
            )

        self.server_fingerprint = hashlib.sha1(server_certificate).hexdigest().upper()
        self.debug(f"Server certificate fingerprint: `{self.server_fingerprint}`")

        self.conn.settimeout(None)

        self.info("Connected! Authenticating with remote server...")

        self.authenticate(password)

        self.info("Authentication successful")

    def __del__(self) -> None:
        self.close()

    def _log(self, level, message: str) -> None:
        """ Log a message with the client ID as prefix
        I prefer to use this method instead of directly configuring the logger which I find to be less straightforward.
        Of course if we would need to reflect the same principle across different classes, we would not use this
        method. having an id (uuid) prefix is really for debugging purposes and solely for the client class.
        (Client Tracking: ON; OFF) """
        logger.log(level, f"[{self.id}] {message}")

    def debug(self, message: str) -> None:
        self._log(logging.DEBUG, message)

    def info(self, message: str) -> None:
        self._log(logging.INFO, message)

    def read_line(self) -> str:
        data = b""

        while True:
            try:
                b = self.conn.recv(1)
            except (Exception, ):
                break

            if not b:
                break

            data += b
            if b == b'\n':
                break

        return data.decode('utf-8').strip()

    def write_line(self, line: str) -> None:
        try:
            self.conn.write(line.encode('utf-8') + b'\r\n')
        except (Exception, ):
            pass

    def read_json(self) -> dict:
        try:
            return json.loads(self.read_line())
        except json.JSONDecodeError:
            return {}

    def write_json(self, data: dict) -> None:
        self.write_line(json.dumps(data))

    def authenticate(self, password: str) -> None:
        self.debug("Request challenge...")

        challenge = self.read_line()

        self.debug(f"Received challenge: `{challenge}`, attempt to solve it with defined password...")

        challenge_solution_as_bytes = hashlib.pbkdf2_hmac(
            "sha512",
            password.encode("utf-8"),
            challenge.encode("utf-8"),
            1000
        )
        challenge_solution = binascii.hexlify(challenge_solution_as_bytes)\
            .decode("utf-8").upper()

        self.debug(f"Challenge solved: `{challenge_solution}`, sending solution to server...")

        self.write_line(challenge_solution)

        response = self.read_line()
        if response != arcane.ArcaneProtocolCommand.Success.name:
            raise arcane.ArcaneProtocolException(
                arcane.ArcaneProtocolError.AuthenticationFailed
            )

    def close(self) -> None:
        self.info("Closing connection...")
        if self.conn is not None:
            try:
                self.conn.shutdown(socket.SHUT_RDWR)
                self.conn.close()
            except OSError:
                pass

        if self.client is not None:
            try:
                self.client.close()
            except OSError:
                # Should not happen (very unlikely but not null)
                pass
