"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

from enum import Enum, auto


class ArcaneProtocolError(Enum):
    AuthenticationFailed = auto()
    ResourceNotFound = auto()
    InvalidStructureData = auto()
    UnsupportedVersion = auto()
    MissingServerCertificate = auto()
    MissingSession = auto()
    ServerFingerprintTampered = auto()


class ArcaneProtocolException(Exception):
    def __init__(self, reason: ArcaneProtocolError) -> None:
        self.reason = reason

        error_messages = {
            ArcaneProtocolError.AuthenticationFailed: "Authentication failed",
            ArcaneProtocolError.ResourceNotFound: "A resource was not found",
            ArcaneProtocolError.InvalidStructureData: "Invalid structure data, whether corrupted or missing properties",
            ArcaneProtocolError.UnsupportedVersion: "Unsupported protocol version: protocol versions between client and"
                                                    "server do not match",
            ArcaneProtocolError.MissingServerCertificate: "Server certificate is missing",
            ArcaneProtocolError.MissingSession: "Session is missing, you must request a session first",
            ArcaneProtocolError.ServerFingerprintTampered: "Server fingerprint has changed, confidentiality is possibly"
                                                           " compromised",
        }

        super().__init__(error_messages.get(reason, "Unknown error"))
