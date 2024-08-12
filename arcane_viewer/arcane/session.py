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
"""

import json
import logging

import arcane_viewer.arcane as arcane

logger = logging.getLogger(__name__)


class Session:
    """ Session class to handle remote session """
    def __init__(self, server_address: str, server_port: int, password: str):
        self.server_address = server_address
        self.server_port = server_port
        self.__password = password

        self.session_id = None
        self.display_name = None
        self.presentation = False
        self.server_fingerprint = None

        self.option_image_quality = 80
        self.option_packet_size = arcane.PacketSize.Size9216
        self.option_block_size = arcane.BlockSize.Size64

        self.request_session()

    def claim_client(self, worker_kind: arcane.WorkerKind = None):
        """ Establish a new TLS connection to the remote server and authenticate. Optionally we can specify a worker
        to be attached to the current session """
        client = arcane.Client(self.server_address, self.server_port, self.__password)

        # If a session is already established and a worker kind is provided, we attach to current session a new worker
        if worker_kind is not None:
            if self.session_id is None:
                raise arcane.ArcaneProtocolException(arcane.ArcaneProtocolError.MissingSession)

            # If the server fingerprint has changed after session creation, we may be facing a MITM attack,
            # Abort connection
            if self.server_fingerprint != client.server_fingerprint:
                raise arcane.ArcaneProtocolException(arcane.ArcaneProtocolError.ServerFingerprintTampered)

            client.write_line("AttachToSession")

            client.write_line(self.session_id)

            response = client.read_line()
            if response != "ResourceFound":
                raise arcane.ArcaneProtocolException(arcane.ArcaneProtocolError.ResourceNotFound)

            client.write_line(worker_kind.name)

        return client

    def request_session(self):
        """ Request a new session to the remote server """
        client = self.claim_client()
        try:
            self.server_fingerprint = client.server_fingerprint

            client.write_line("RequestSession")

            session_information = client.read_json()
            if session_information is None:
                raise arcane.ArcaneProtocolException(arcane.ArcaneProtocolError.InvalidStructureData)

            logger.debug("@Session information:")
            logger.debug(json.dumps(session_information, indent=4))

            if not all(k in session_information for k in (
                    "SessionId",
                    "Username",
                    "MachineName",
                    "ViewOnly",
                    "Version"
            )):
                raise arcane.ArcaneProtocolException(arcane.ArcaneProtocolError.InvalidStructureData)

            if session_information["Version"] != arcane.PROTOCOL_VERSION:
                logger.error(f"Incompatible server version, client version: `{arcane.PROTOCOL_VERSION}` != "
                             f"server version: `{session_information['Version']}`")

                raise arcane.ArcaneProtocolException(
                    arcane.ArcaneProtocolError.UnsupportedVersion
                )

            self.session_id = session_information["SessionId"]

            self.display_name = "{}@{}".format(
                session_information["Username"],
                session_information["MachineName"],
            )

            if session_information["ViewOnly"]:
                logger.info("Presentation mode enforced by remote server")
                self.presentation = True

            logger.info("Session established with remote peer")
        finally:
            if client is not None:
                client.close()
