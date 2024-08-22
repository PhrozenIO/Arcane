"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

import logging

from PyQt6.QtCore import QThread, pyqtSignal

import arcane_viewer.arcane as arcane

logger = logging.getLogger(__name__)


class ConnectThread(QThread):
    """ Thread to handle the first connection to the server, first-authentication and session token creation """

    thread_started = pyqtSignal()
    thread_finished = pyqtSignal(object)
    session_error = pyqtSignal(str)

    def __init__(self, server_address: str, server_port: int, password: str) -> None:
        super().__init__()

        self.server_address = server_address
        self.server_port = server_port
        self.__password = password

    def run(self) -> None:
        session = None

        self.thread_started.emit()
        try:
            session = arcane.Session(
                self.server_address,
                self.server_port,
                self.__password,
            )
        except Exception as e:
            logger.error(f"An error occurred while connecting to the server: {e}")

            if (isinstance(e, arcane.ArcaneProtocolException) and
                    e.reason == arcane.ArcaneProtocolError.AuthenticationFailed):
                error_message = "Authentication failed, check your credentials"
            elif (isinstance(e, arcane.ArcaneProtocolException) and
                    e.reason == arcane.ArcaneProtocolError.UnsupportedVersion):
                error_message = ("Protocol version mismatch, be sure to connect to a compatible server"
                                 f" (v{arcane.PROTOCOL_VERSION})")
            elif isinstance(e, TimeoutError):
                error_message = "The connection to the server timed out, check the server address and port"
            else:
                error_message = "An error occurred while connecting to the server, check the console output for more " \
                                "information."

            # Notify the main thread about the error
            self.session_error.emit(error_message)
        finally:
            self.thread_finished.emit(session)
