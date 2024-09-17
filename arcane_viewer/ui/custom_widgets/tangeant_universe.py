"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.

    Todo:
        - (0002) : Implement a way to handle additional special characters that are not correctly interpreted by QT
                    (Examples: ê, ã, `).
"""

import logging
from typing import Optional, Tuple, Union

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QClipboard, QKeyEvent, QMouseEvent, QWheelEvent
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView

import arcane_viewer.arcane as arcane
import arcane_viewer.arcane.threads as arcane_threads

logger = logging.getLogger(__name__)


class TangentUniverse(QGraphicsView):
    """ Virtual Desktop Host (Tangent Universe)
    `In the shadowed folds of temporal threads, how does one discern the whisper of the true path from the echo of the
    diverging veil? When the cosmic mirror distorts, do you walk the ordained spiral or the fragmented loop of the
    twilight realm?`"""

    def __init__(self) -> None:
        super().__init__()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setMouseTracking(True)

        self.events_thread: Optional[arcane_threads.EventsThread] = None
        self.desktop_screen: Optional[arcane.Screen] = None

        # instead of doing a simple ``setScene(QGraphicsScene())``, we will keep a reference to the scene to be updated
        # and avoid slight overhead when calling `.scene()` method repeatedly.
        self.desktop_scene = QGraphicsScene()
        self.setScene(self.desktop_scene)

        self.clipboard = QApplication.clipboard()
        if self.clipboard is not None:
            self.clipboard.dataChanged.connect(self.clipboard_data_changed)

    def reset_scene(self) -> None:
        if self.desktop_scene is not None:
            self.desktop_scene.clear()

    def set_event_thread(self, events_thread: arcane_threads.EventsThread) -> None:
        """ Set the events thread """
        self.events_thread = events_thread

        self.events_thread.update_mouse_cursor.connect(self.update_mouse_cursor)
        self.events_thread.update_clipboard.connect(self.update_clipboard)

    def set_screen(self, screen: arcane.Screen) -> None:
        """ Set the captured screen original information """
        self.desktop_screen = screen

    def fix_mouse_position(self, x: Union[int, float], y: Union[int, float]) -> Tuple[int, int]:
        """ Fix the virtual desktop mouse position to the original screen position """
        x = int(x)
        y = int(y)

        if self.desktop_screen is None:
            return x, y

        if self.desktop_screen.width > self.width():
            x_ratio = self.desktop_screen.width / self.width()
        else:
            x_ratio = self.width() / self.desktop_screen.width

        if self.desktop_screen.height > self.height():
            y_ratio = self.desktop_screen.height / self.height()
        else:
            y_ratio = self.height() / self.desktop_screen.height

        # We must take in account both virtual desktop size and original screen X, Y position.
        return (self.desktop_screen.x + (x * x_ratio),
                self.desktop_screen.y + (y * y_ratio))

    def send_mouse_event(self, x: Union[int, float], y: Union[int, float], state: arcane.MouseState,
                         button: arcane.MouseButton) -> None:
        x = int(x)
        y = int(y)

        """ Push mouse event to the events thread """
        if self.events_thread is None:
            return

        self.events_thread.send_mouse_event(
            x,
            y,
            state,
            button
        )

    def mouse_action_handler(self, event: QMouseEvent, is_pressed: bool) -> None:
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

    def mouse_click(self, event: QMouseEvent) -> None:
        """ Simulate mouse click event """
        self.mouse_action_handler(event, True)
        self.mouse_action_handler(event, False)

    def mousePressEvent(self, event: Optional[QMouseEvent]) -> None:
        if event is None:
            return

        self.mouse_action_handler(event, True)

    def mouseReleaseEvent(self, event: Optional[QMouseEvent]) -> None:
        if event is None:
            return

        self.mouse_action_handler(event, False)

    def mouseDoubleClickEvent(self, event: Optional[QMouseEvent]) -> None:
        """ Override mouseDoubleClickEvent method to simulate a remote double click event
        Do something better than this is possible? (cross-platform) """
        if event is None:
            return

        self.mouse_click(event)
        self.mouse_click(event)

    def mouseMoveEvent(self, event: Optional[QMouseEvent]) -> None:
        """ Override mouseMoveEvent method to handle mouse move events """
        if self.events_thread is None or event is None:
            return

        pos = event.position()
        x, y = self.fix_mouse_position(pos.x(), pos.y())

        self.send_mouse_event(x, y, arcane.MouseState.Move, arcane.MouseButton.Void)

    def clipboard_data_changed(self) -> None:
        """ Handle clipboard data changed event """
        if self.events_thread is None or self.clipboard is None:
            return

        text = self.clipboard.text(QClipboard.Mode.Clipboard)

        self.events_thread.send_clipboard_text(
            text
        )

    @staticmethod
    def parse_f_keys(event: QKeyEvent) -> Optional[str]:
        if event.key() == Qt.Key.Key_F1:
            return "{F1}"
        elif event.key() == Qt.Key.Key_F2:
            return "{F2}"
        elif event.key() == Qt.Key.Key_F3:
            return "{F3}"
        elif event.key() == Qt.Key.Key_F4:
            return "{F4}"
        elif event.key() == Qt.Key.Key_F5:
            return "{F5}"
        elif event.key() == Qt.Key.Key_F6:
            return "{F6}"
        elif event.key() == Qt.Key.Key_F7:
            return "{F7}"
        elif event.key() == Qt.Key.Key_F8:
            return "{F8}"
        elif event.key() == Qt.Key.Key_F9:
            return "{F9}"
        elif event.key() == Qt.Key.Key_F10:
            return "{F10}"
        elif event.key() == Qt.Key.Key_F11:
            return "{F11}"
        elif event.key() == Qt.Key.Key_F12:
            return "{F12}"
        elif event.key() == Qt.Key.Key_F13:
            return "{F13}"
        elif event.key() == Qt.Key.Key_F14:
            return "{F14}"
        elif event.key() == Qt.Key.Key_F15:
            return "{F15}"
        elif event.key() == Qt.Key.Key_F16:
            return "{F16}"
        else:
            return None

    def keyPressEvent(self, event: Optional[QKeyEvent]) -> None:
        """ Override keyPressEvent method to handle key press events
            For a maximum of compatibility, we will not yet use match case from Python > 3.10 to handle such big enum"""
        if self.events_thread is None or event is None:
            return

        if not event.isInputEvent():
            return

        key_text: Optional[str] = None
        is_shortcut = False

        # Handle Ctrl + C, Ctrl + V, Ctrl + X etc.. CTRL + [A-Z]
        if (Qt.Key.Key_A <= event.key() <= Qt.Key.Key_Z) and \
                event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            key_text = "{^}" + event.text().upper()
            is_shortcut = True

        # Handle [F1-F12] and/or ALT + [F1-F12]
        elif Qt.Key.Key_F1 <= event.key() <= Qt.Key.Key_F12:
            key_text = self.parse_f_keys(event)

            if event.modifiers() == Qt.KeyboardModifier.AltModifier and key_text is not None:
                key_text = "{%}" + key_text
                is_shortcut = True

        # Handle WIN + L
        elif (event.key() == Qt.Key.Key_L) and event.modifiers() == Qt.KeyboardModifier.MetaModifier:
            key_text = "{LOCKWORKSTATION}"

        # Reserved for future use
        # Handle Ctrl + Alt + Del
        # elif (event.key() == Qt.Key.Key_Delete and
        #        event.modifiers() == (
        #                Qt.KeyboardModifier.ControlModifier |
        #                Qt.KeyboardModifier.AltModifier
        #        )):
        #    key_text = "{CTRL+ALT+DEL}"

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

        # Modifier Keys
        elif event.key() == Qt.Key.Key_Meta:
            key_text = "{!}"
        elif event.key() == Qt.Key.Key_Control:
            pass
        elif event.key() == Qt.Key.Key_Alt:
            pass
        elif event.key() == Qt.Key.Key_Shift:
            pass

        # Special Character to Escape
        elif event.key() == Qt.Key.Key_BraceLeft:
            key_text = "{{"

        else:
            key_text = event.text()

        if key_text is not None:
            self.events_thread.send_key_event(key_text, is_shortcut)

    def wheelEvent(self, event: Optional[QWheelEvent]) -> None:
        """ Override wheelEvent method to handle mouse wheel events """
        if self.events_thread is None or event is None:
            return

        delta = event.angleDelta().y()

        self.events_thread.send_mouse_wheel_event(delta)

    @pyqtSlot(Qt.CursorShape)
    def update_mouse_cursor(self, cursor: Qt.CursorShape) -> None:
        self.setCursor(cursor)

    @pyqtSlot(str)
    def update_clipboard(self, text: str) -> None:
        if self.clipboard is not None:
            self.clipboard.setText(text)
