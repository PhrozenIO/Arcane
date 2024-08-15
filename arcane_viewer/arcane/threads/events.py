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

import logging
from json.decoder import JSONDecodeError

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

import arcane_viewer.arcane as arcane

from .client_base import ClientBaseThread

logger = logging.getLogger(__name__)


class EventsThread(ClientBaseThread):
    update_mouse_cursor = pyqtSignal(Qt.CursorShape)
    update_clipboard = pyqtSignal(str)

    def __init__(self, session: arcane.Session):
        super().__init__(session, arcane.WorkerKind.Events)

    def client_execute(self):
        """ Execute the client thread """
        while self._running:
            try:
                event = self.client.read_json()
            except JSONDecodeError:
                continue

            if event is None or "Id" not in event:
                continue

            event_id = event["Id"]

            # Handle Cursor Icon Updates and Reflect it on the Virtual Desktop (Native Cursor)
            if event_id == arcane.InputEvent.MouseCursorUpdated.value and "Cursor" in event:
                cursor_name = event["Cursor"]

                # Default
                cursor = Qt.CursorShape.ArrowCursor

                if cursor_name in (arcane.MouseCursorKind.IDC_SIZEALL.name,
                                   cursor_name == arcane.MouseCursorKind.IDC_SIZE.name):
                    cursor = Qt.CursorShape.SizeAllCursor
                elif cursor_name == arcane.MouseCursorKind.IDC_SIZENESW.name:
                    cursor = Qt.CursorShape.SizeBDiagCursor
                elif cursor_name == arcane.MouseCursorKind.IDC_SIZENS.name:
                    cursor = Qt.CursorShape.SizeVerCursor
                elif cursor_name == arcane.MouseCursorKind.IDC_SIZENWSE.name:
                    cursor = Qt.CursorShape.SizeFDiagCursor
                elif cursor_name == arcane.MouseCursorKind.IDC_SIZEWE.name:
                    cursor = Qt.CursorShape.SizeHorCursor
                elif cursor_name == arcane.MouseCursorKind.IDC_UPARROW.name:
                    cursor = Qt.CursorShape.UpArrowCursor
                elif cursor_name == arcane.MouseCursorKind.IDC_WAIT.name:
                    cursor = Qt.CursorShape.WaitCursor
                elif cursor_name == arcane.MouseCursorKind.IDC_APPSTARTING.name:
                    cursor = Qt.CursorShape.BusyCursor
                elif cursor_name == arcane.MouseCursorKind.IDC_CROSS.name:
                    cursor = Qt.CursorShape.CrossCursor
                elif cursor_name == arcane.MouseCursorKind.IDC_HAND.name:
                    cursor = Qt.CursorShape.PointingHandCursor
                elif cursor_name == arcane.MouseCursorKind.IDC_HELP.name:
                    cursor = Qt.CursorShape.WhatsThisCursor
                elif cursor_name == arcane.MouseCursorKind.IDC_IBEAM.name:
                    cursor = Qt.CursorShape.IBeamCursor
                elif cursor_name == arcane.MouseCursorKind.IDC_ICON.name:
                    pass  # Obsolete
                elif cursor_name == arcane.MouseCursorKind.IDC_NO.name:
                    cursor = Qt.CursorShape.ForbiddenCursor

                self.update_mouse_cursor.emit(cursor)
            # Handle Clipboard Updates
            elif event_id == arcane.InputEvent.ClipboardUpdated.value and "Text" in event:
                if self.session.clipboard_mode in {
                    arcane.ClipboardMode.Disabled, arcane.ClipboardMode.Send
                }:
                    continue

                self.update_clipboard.emit(event["Text"])

    @pyqtSlot(int, int, arcane.MouseState, arcane.MouseButton)
    def send_mouse_event(self, x: int, y: int, state: arcane.MouseState, button: arcane.MouseButton):
        """ Send mouse event to the server """
        if self.session.presentation:
            return

        if self.client is not None and self._connected:
            self.client.write_json(
                {
                    "Id": arcane.OutputEvent.MouseClickMove.name,
                    "X": x,
                    "Y": y,
                    "Button": button.name,
                    "Type": state.name,
                }
            )

    @pyqtSlot(str)
    def send_key_event(self, keys: str):
        """ Send keyboard event to the server """
        if self.session.presentation:
            return

        if self.client is not None and self._connected:
            self.client.write_json(
                {
                    "Id": arcane.OutputEvent.Keyboard.name,
                    "Keys": keys,
                }
            )

    @pyqtSlot(int)
    def send_mouse_wheel_event(self, delta: int):
        """ Send mouse wheel event to the server """
        if self.session.presentation:
            return

        if self.client is not None and self._connected:
            self.client.write_json(
                {
                    "Id": arcane.OutputEvent.MouseWheel.name,
                    "Delta": delta,
                }
            )

    @pyqtSlot(str)
    def send_clipboard_text(self, text: str):
        """ Send clipboard text to the server """
        if self.session.clipboard_mode in {
            arcane.ClipboardMode.Disabled, arcane.ClipboardMode.Receive
        }:
            return

        if self.client is not None and self._connected:
            self.client.write_json(
                {
                    "Id": arcane.OutputEvent.ClipboardUpdated.name,
                    "Text": text,
                }
            )
