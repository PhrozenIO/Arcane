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
    option_image_quality = 80
    option_packet_size = arcane.PacketSize.Size9216
    option_block_size = arcane.BlockSize.Size64

    """ Session class to handle remote session """
    def __init__(self, server_address: str, server_port: int, password: str):
        self.server_address = server_address
        self.server_port = server_port
        self.__password = password

        self.session_id = None
        self.display_name = None
        self.presentation = False

        self.request_session()

    def claim_client(self):
        return arcane.Client(self.server_address, self.server_port, self.__password)

    def request_session(self):
        client = self.claim_client()
        try:
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
