"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

from enum import Enum, auto

PROTOCOL_VERSION = '5.0.2'


class WorkerKind(Enum):
    Desktop = 0x1
    Events = 0x2


class ClipboardMode(Enum):
    Disabled = 0x1
    Receive = 0x2
    Send = 0x3
    Both = 0x4


class ArcaneProtocolCommand(Enum):
    Success = 0x1
    Fail = 0x2
    RequestSession = 0x3
    AttachToSession = 0x4
    BadRequest = 0x5
    ResourceFound = 0x6
    ResourceNotFound = 0x7


class OutputEvent(Enum):
    Keyboard = 0x1
    MouseClickMove = 0x2
    MouseWheel = 0x3
    KeepAlive = 0x4  # Not used but actually defined by the protocol
    ClipboardUpdated = 0x5


class InputEvent(Enum):
    KeepAlive = 0x1
    MouseCursorUpdated = 0x2
    ClipboardUpdated = 0x3
    DesktopActive = 0x4
    DesktopInactive = 0x5


class MouseState(Enum):
    Up = 0x1
    Down = 0x2
    Move = 0x3


class MouseButton(Enum):
    Left = 0x1
    Right = 0x2
    Middle = 0x3
    Void = 0x4


class MouseCursorKind(Enum):
    IDC_APPSTARTING = auto()
    IDC_ARROW = auto()
    IDC_CROSS = auto()
    IDC_HAND = auto()
    IDC_HELP = auto()
    IDC_IBEAM = auto()
    IDC_ICON = auto()
    IDC_NO = auto()
    IDC_SIZE = auto()
    IDC_SIZEALL = auto()
    IDC_SIZENESW = auto()
    IDC_SIZENS = auto()
    IDC_SIZENWSE = auto()
    IDC_SIZEWE = auto()
    IDC_UPARROW = auto()
    IDC_WAIT = auto()


class PacketSize(Enum):
    Size1024 = 1024
    Size2048 = 2048
    Size4096 = 4096
    Size8192 = 8192
    Size9216 = 9216
    Size12288 = 12288
    Size16384 = 16384

    @property
    def display_name(self) -> str:
        return f"{self.value} bytes"


class BlockSize(Enum):
    Size32 = 32
    Size64 = 64
    Size96 = 96
    Size128 = 128
    Size256 = 256
    Size512 = 512

    @property
    def display_name(self) -> str:
        return f"{self.value}x{self.value}"
