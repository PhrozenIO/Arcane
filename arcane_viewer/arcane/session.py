"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

import json
import logging
from typing import Optional

from PyQt6.QtCore import QSettings

import arcane_viewer.arcane as arcane

logger = logging.getLogger(__name__)


class Session:
    """ Session class to handle remote session """
    def __init__(self, server_address: str, server_port: int, password: str) -> None:
        self.server_address = server_address
        self.server_port = server_port
        self.__password = password

        self.presentation = False

        self.session_id: Optional[str] = None
        self.display_name: Optional[str] = None
        self.server_fingerprint: Optional[str] = None

        # Load settings (options)
        settings = QSettings(arcane.APP_ORGANIZATION_NAME, arcane.APP_NAME)

        # Remote Desktop Options
        self.clipboard_mode = settings.value(arcane.SETTINGS_KEY_CLIPBOARD_MODE, arcane.ClipboardMode.Both)

        # Remote Desktop Capture Options
        self.option_image_quality = settings.value(arcane.SETTINGS_KEY_IMAGE_QUALITY, 80)
        self.option_packet_size = settings.value(arcane.SETTINGS_KEY_PACKET_SIZE, arcane.PacketSize.Size4096)
        self.option_block_size = settings.value(arcane.SETTINGS_KEY_BLOCK_SIZE, arcane.BlockSize.Size64)

        self.request_session()

    def claim_client(self, worker_kind: Optional[arcane.WorkerKind] = None) -> arcane.Client:
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

    def request_session(self) -> None:
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
                    "Version",
                    "ViewOnly",
                    "Clipboard",
                    "Username",
                    "MachineName",
                    "WindowsVersion",
            )):
                raise arcane.ArcaneProtocolException(arcane.ArcaneProtocolError.InvalidStructureData)

            # Protocol Version Check
            if session_information["Version"] != arcane.PROTOCOL_VERSION:
                logger.error(f"Incompatible server version, client version: `{arcane.PROTOCOL_VERSION}` != "
                             f"server version: `{session_information['Version']}`")

                raise arcane.ArcaneProtocolException(
                    arcane.ArcaneProtocolError.UnsupportedVersion
                )

            # Assign session information
            self.session_id = session_information["SessionId"]

            self.display_name = "{}@{}".format(
                session_information["Username"],
                session_information["MachineName"],
            )

            # Handle Server-Clipboard Mode and solve possible clash with client-clipboard mode
            # By default, if for any reason, server clipboard mode is not recognized, we consider it as disabled
            server_clipboard_mode = arcane.ClipboardMode.Disabled
            try:
                server_clipboard_mode = arcane.ClipboardMode(session_information["Clipboard"])
            except ValueError:
                pass

            logger.info("Server clipboard mode: `{}`".format(server_clipboard_mode.name))

            if session_information["ViewOnly"]:
                logger.warning("Presentation mode enforced by remote server, no input / output "
                               "(Mouse, Keyboard, Clipboard) will be accepted")

                # In view only (presentation) mode, whatever the client clipboard mode is, we disable it
                self.clipboard_mode = arcane.ClipboardMode.Disabled
                self.presentation = True
            else:
                # If server clipboard mode is disabled, whatever the client clipboard mode is, we disable it
                if (server_clipboard_mode == arcane.ClipboardMode.Disabled and
                        self.clipboard_mode != arcane.ClipboardMode.Disabled):
                    self.clipboard_mode = arcane.ClipboardMode.Disabled
                    logger.warning("Server clipboard mode is disabled, reflecting to client clipboard mode")
                # If server clipboard mode is send-only, we set client clipboard mode to receive-only only if client
                # clipboard mode is set to both.
                elif (server_clipboard_mode == arcane.ClipboardMode.Send and
                      self.clipboard_mode == arcane.ClipboardMode.Both):
                    self.clipboard_mode = arcane.ClipboardMode.Receive
                    logger.warning("Server clipboard mode is send-only, client clipboard mode set to receive-only")
                # If server clipboard mode is receive-only, we set client clipboard mode to send-only only if client
                # clipboard mode is set to both.
                elif (server_clipboard_mode == arcane.ClipboardMode.Receive and
                      self.clipboard_mode == arcane.ClipboardMode.Both):
                    self.clipboard_mode = arcane.ClipboardMode.Send
                    logger.warning("Server clipboard mode is receive-only, client clipboard mode set to send-only")
                # If there is a clash between server and client clipboard mode, we disable it
                elif (
                        (server_clipboard_mode == arcane.ClipboardMode.Send and
                         self.clipboard_mode == arcane.ClipboardMode.Send) or
                        (server_clipboard_mode == arcane.ClipboardMode.Receive and
                         self.clipboard_mode == arcane.ClipboardMode.Receive)
                ):
                    self.clipboard_mode = arcane.ClipboardMode.Disabled
                    logger.warning("Server clipboard mode and client clash, clipboard is then disabled")

            # Finally
            logger.info("Session established with `{}` on `{}`".format(
                self.display_name,
                session_information["WindowsVersion"],
            ))
        finally:
            if client is not None:
                client.close()
