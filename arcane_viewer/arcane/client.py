"""
    Arcane - A secure remote desktop application for Windows with the
    particularity of having a server entirely written in PowerShell and
    a cross-platform client (Python/QT6).

    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    https://github.com/PhrozenIO
    https://github.com/DarkCoderSc
    https://twitter.com/DarkCoderSc
    www.phrozen.io

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
    """ Client class to handle secure communication with remote server """
    def __init__(self, server_address: str, server_port: int, password: str):
        logger.info("Connecting to remote server: `{}:{}`...".format(
            server_address,
            server_port
        ))

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logger.debug("Creating and configure new SSL context...")
        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE

        self.conn = self.context.wrap_socket(
            self.client,
            server_hostname=server_address,
        )

        logger.debug("Establishing connection to remote server...")
        self.conn.settimeout(10)

        self.conn.connect((server_address, server_port))

        server_certificate = self.conn.getpeercert(binary_form=True)
        if server_certificate is None:
            raise arcane.ArcaneProtocolException(
                arcane.ArcaneProtocolError.MissingServerCertificate
            )

        self.server_fingerprint = hashlib.sha1(server_certificate).hexdigest().upper()
        logger.debug(f"Server certificate fingerprint: `{self.server_fingerprint}`")

        self.conn.settimeout(None)

        logger.info(f"[{self.conn.fileno()}] Connected! Authenticating with remote server...")

        self.authenticate(password)

        logger.info("Authentication successful")

    def __del__(self):
        self.close()

    def read_line(self):
        data = b""

        while True:
            try:
                b = self.conn.recv(1)
            except ssl.SSLError:
                break

            if not b:
                break

            data += b
            if b == b'\n':
                break

        return data.decode('utf-8').strip()

    def write_line(self, line: str):
        self.conn.write(line.encode('utf-8') + b'\r\n')

    def read_json(self):
        try:
            return json.loads(self.read_line())
        except json.JSONDecodeError:
            return None

    def write_json(self, data: dict):
        self.write_line(json.dumps(data))

    def authenticate(self, password: str):
        logger.debug("Request challenge...")

        challenge = self.read_line()

        logger.debug(f"Received challenge: `{challenge}`, attempt to solve it with defined password...")

        challenge_solution = hashlib.pbkdf2_hmac(
            "sha512",
            password.encode("utf-8"),
            challenge.encode("utf-8"),
            1000
        )
        challenge_solution = binascii.hexlify(challenge_solution)\
            .decode("utf-8").upper()

        logger.debug(f"Challenge solved: `{challenge_solution}`, sending solution to server...")

        self.write_line(challenge_solution)

        response = self.read_line()
        if response != arcane.ArcaneProtocolCommand.Success.name:
            raise arcane.ArcaneProtocolException(
                arcane.ArcaneProtocolError.AuthenticationFailed
            )

    def close(self):
        if self.client is not None:
            logger.info(f"[{self.conn.fileno()}] Closing connection...")
            try:
                if self.conn is not None:
                    self.conn.shutdown(socket.SHUT_RDWR)
                    self.conn.close()
            except OSError:
                self.client.close()

                pass
            finally:
                self.conn = None
                self.client = None
