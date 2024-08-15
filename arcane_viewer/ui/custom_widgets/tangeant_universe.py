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

    Todo:
        - (0001) : Find a way to correctly handle the Meta key from Viewer to Server especially from MacOs systems.
        - (0002) : Implement a way to handle additional special characters that are not correctly interpreted by QT.
        - (0003) : Handle shortcuts (CTRL+, WIN+, ALT+ etc..).
        - (0004) : Investigate for a generic way to handle special characters for all keyboard layouts, not just AZERTY.
"""

import logging
from sys import platform

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QClipboard
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView

import arcane_viewer.arcane as arcane

logger = logging.getLogger(__name__)


class TangentUniverse(QGraphicsView):
    """ Virtual Desktop Host (Tangent Universe)
    `In the shadowed folds of temporal threads, how does one discern the whisper of the true path from the echo of the
    diverging veil? When the cosmic mirror distorts, do you walk the ordained spiral or the fragmented loop of the
    twilight realm?`"""

    def __init__(self):
        super().__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setMouseTracking(True)

        self.events_thread = None
        self.screen = None

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.clipboard_data_changed)

    def set_event_thread(self, events_thread):
        """ Set the events thread """
        self.events_thread = events_thread

        self.events_thread.update_mouse_cursor.connect(self.update_mouse_cursor)
        self.events_thread.update_clipboard.connect(self.update_clipboard)

    def set_screen(self, screen: arcane.Screen):
        """ Set the captured screen original information """
        self.screen = screen

    def fix_mouse_position(self, x, y):
        """ Fix the virtual desktop mouse position to the original screen position """
        if self.screen is None:
            return x, y

        if self.screen.width > self.width():
            x_ratio = self.screen.width / self.width()
        else:
            x_ratio = self.width() / self.screen.width

        if self.screen.height > self.height():
            y_ratio = self.screen.height / self.height()
        else:
            y_ratio = self.height() / self.screen.height

        # We must take in account both virtual desktop size and original screen X, Y position.
        return (self.screen.x + (x * x_ratio),
                self.screen.y + (y * y_ratio))

    def send_mouse_event(self, x: int, y: int, state: arcane.MouseState, button: arcane.MouseButton):
        """ Push mouse event to the events thread """
        self.events_thread.send_mouse_event(
            x,
            y,
            state,
            button
        )

    def mouse_action_handler(self, event, is_pressed):
        """ Handle mouse press and release events """

        if self.events_thread is None:
            return

        pos = event.position()
        x, y = self.fix_mouse_position(pos.x(), pos.y())

        button = event.button()

        mouse_button = {
            Qt.MouseButton.LeftButton: arcane.MouseButton.Left,
            Qt.MouseButton.RightButton: arcane.MouseButton.Right,
            Qt.MouseButton.MiddleButton: arcane.MouseButton.Middle,
        }.get(button, arcane.MouseButton.Void)

        self.send_mouse_event(x, y, arcane.MouseState.Down if is_pressed else arcane.MouseState.Up, mouse_button)

    def mouse_click(self, event):
        """ Simulate mouse click event """
        self.mouse_action_handler(event, True)
        self.mouse_action_handler(event, False)

    def mousePressEvent(self, event):
        self.mouse_action_handler(event, True)

    def mouseReleaseEvent(self, event):
        self.mouse_action_handler(event, False)

    def mouseDoubleClickEvent(self, event):
        """ Override mouseDoubleClickEvent method to simulate a remote double click event
        Do something better than this is possible? (cross-platform) """
        self.mouse_click(event)
        self.mouse_click(event)

    def mouseMoveEvent(self, event):
        """ Override mouseMoveEvent method to handle mouse move events """
        if self.events_thread is None:
            return

        pos = event.position()
        x, y = self.fix_mouse_position(pos.x(), pos.y())

        self.send_mouse_event(x, y, arcane.MouseState.Move, arcane.MouseButton.Void)

    def clipboard_data_changed(self):
        """ Handle clipboard data changed event """
        text = self.clipboard.text(QClipboard.Mode.Clipboard)

        self.events_thread.send_clipboard_text(
            text
        )

    def keyPressEvent(self, event):
        """ Override keyPressEvent method to handle key press events """
        if self.events_thread is None:
            return

        if not event.isInputEvent():
            return

        # For a maximum of compatibility, we will not yet use match case from Python > 3.10 to handle such big enum
        # F Keys
        if event.key() == Qt.Key.Key_F1:
            key_text = "{F1}"
        elif event.key() == Qt.Key.Key_F2:
            key_text = "{F2}"
        elif event.key() == Qt.Key.Key_F3:
            key_text = "{F3}"
        elif event.key() == Qt.Key.Key_F4:
            key_text = "{F4}"
        elif event.key() == Qt.Key.Key_F5:
            key_text = "{F5}"
        elif event.key() == Qt.Key.Key_F6:
            key_text = "{F6}"
        elif event.key() == Qt.Key.Key_F7:
            key_text = "{F7}"
        elif event.key() == Qt.Key.Key_F8:
            key_text = "{F8}"
        elif event.key() == Qt.Key.Key_F9:
            key_text = "{F9}"
        elif event.key() == Qt.Key.Key_F10:
            key_text = "{F10}"
        elif event.key() == Qt.Key.Key_F11:
            key_text = "{F11}"
        elif event.key() == Qt.Key.Key_F12:
            key_text = "{F12}"
        elif event.key() == Qt.Key.Key_F13:
            key_text = "{F13}"
        elif event.key() == Qt.Key.Key_F14:
            key_text = "{F14}"
        elif event.key() == Qt.Key.Key_F15:
            key_text = "{F15}"
        elif event.key() == Qt.Key.Key_F16:
            key_text = "{F16}"

        # Arrow Keys
        elif event.key() == Qt.Key.Key_Up:
            key_text = "{UP}"
        elif event.key() == Qt.Key.Key_Down:
            key_text = "{DOWN}"
        elif event.key() == Qt.Key.Key_Left:
            key_text = "{LEFT}"
        elif event.key() == Qt.Key.Key_Right:
            key_text = "{RIGHT}"

        # Make RETURN (Numpad) key to be the same as ENTER key
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            key_text = "{ENTER}"

        # Other Special Keys
        elif event.key() == Qt.Key.Key_Backspace:
            key_text = "{BACKSPACE}"
        elif event.key() == Qt.Key.Key_Tab:
            key_text = "{TAB}"
        elif event.key() == Qt.Key.Key_Control:
            key_text = "{CTRL}"
        elif event.key() == Qt.Key.Key_Alt:
            key_text = "{ALT}"
        elif event.key() == Qt.Key.Key_Shift:
            key_text = "{SHIFT}"
        elif event.key() == Qt.Key.Key_Escape:
            key_text = "{ESC}"
        elif event.key() == Qt.Key.Key_CapsLock:
            key_text = "{CAPSLOCK}"
        elif event.key() == Qt.Key.Key_Delete:
            key_text = "{DEL}"
        elif event.key() == Qt.Key.Key_Home:
            key_text = "{HOME}"
        elif event.key() == Qt.Key.Key_End:
            key_text = "{END}"
        elif event.key() == Qt.Key.Key_PageUp:
            key_text = "{PGUP}"
        elif event.key() == Qt.Key.Key_PageDown:
            key_text = "{PGDN}"
        elif event.key() == Qt.Key.Key_Insert:
            key_text = "{INS}"
        elif event.key() == Qt.Key.Key_Help:
            key_text = "{HELP}"
        elif event.key() == Qt.Key.Key_Print:
            key_text = "{PRTSC}"
        elif event.key() == Qt.Key.Key_ScrollLock:
            key_text = "{SCROLLLOCK}"

        # TODO: 0001
        elif event.key() == Qt.Key.Key_Meta and platform != "darwin":
            key_text = "^{ESC}"

        # TODO: 0004
        # elif event.key() == Qt.Key.Key_Egrave and event.modifiers() & Qt.KeyboardModifier.AltModifier:
        #    key_text = "{`}"

        else:
            # Handle others keys that might not be correctly interpreted by PowerShell
            if event.text() in ["+", "{", "}", "%", "(", ")"]:
                key_text = f"{{{event.text()}}}"
            else:
                key_text = event.text()

        self.events_thread.send_key_event(key_text)

    def wheelEvent(self, event):
        """ Override wheelEvent method to handle mouse wheel events """
        if self.events_thread is None:
            return

        delta = event.angleDelta().y()

        self.events_thread.send_mouse_wheel_event(delta)

    @pyqtSlot(Qt.CursorShape)
    def update_mouse_cursor(self, cursor):
        self.setCursor(cursor)

    @pyqtSlot(str)
    def update_clipboard(self, text):
        self.clipboard.setText(text)
