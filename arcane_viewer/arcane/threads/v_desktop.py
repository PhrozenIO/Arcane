"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

import logging
import struct
from typing import List  # To support python <= 3.8, we need to use `List`
from typing import Optional

from PyQt6.QtCore import QByteArray, QEventLoop, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage

import arcane_viewer.arcane as arcane

from .client_base import ClientBaseThread

logger = logging.getLogger(__name__)


class VirtualDesktopThread(ClientBaseThread):
    """ Thread to handle remote desktop streaming, at quantum level """
    open_cellar_door = pyqtSignal(arcane.Screen)
    request_screen_selection_dialog_signal = pyqtSignal(list)
    received_dirty_rect_signal = pyqtSignal(QImage, int, int)
    start_events_worker_signal = pyqtSignal()

    def __init__(self, session: arcane.Session) -> None:
        super().__init__(session, arcane.WorkerKind.Desktop)

        self.selected_screen: Optional[arcane.Screen] = None
        self.event_loop: Optional[QEventLoop] = None

    def open_or_refresh_cellar_door(self) -> None:
        if self.selected_screen is not None:
            self.open_cellar_door.emit(self.selected_screen)

    """`Destruction is a form of creation. So the fact they burn the money is ironic. They just want to see what happens
     when they tear the world apart. They want to change things.`, Donnie Darko"""
    def client_execute(self) -> None:
        if self.client is None:
            return

        screens_obj = self.client.read_json()
        screens = [arcane.Screen(screen) for screen in screens_obj["List"]]
        logger.info(f"{len(screens)} screen(s) detected")

        if len(screens) == 1:
            self.selected_screen = screens[0]
        else:
            self.display_screen_selection_dialog(screens)

        if self.selected_screen is None:
            return

        logger.info(f"Screen: {self.selected_screen.name} "
                    f"({self.selected_screen.width}x{self.selected_screen.height})")

        self.client.write_json(
            {
                "ScreenName": self.selected_screen.name,
                "ImageCompressionQuality": self.session.option_image_quality,
                "PacketSize": self.session.option_packet_size.value,
                "BlockSize": self.session.option_block_size.value,
            }
        )

        """ Open Cellar Door
        `This famous linguist once said, of all the phrases in the English language, of all the endless combinations
        of words in all of history, that 'cellar door' is the most beautiful.`, Karen Pomeroy"""
        self.open_or_refresh_cellar_door()

        self.start_events_worker_signal.emit()

        packet_max_size = self.session.option_packet_size.value
        while self._running:
            try:
                chunk_size, x, y, screen_updated = struct.unpack('IIIB', self.client.conn.read(13))
            except (Exception, ):
                break

            if bool(screen_updated):
                self.selected_screen = arcane.Screen(self.client.read_json())

                self.open_or_refresh_cellar_door()

                continue

            chunk_bytes = QByteArray()
            bytes_read = 0
            while bytes_read < chunk_size:
                packet_size = min(packet_max_size, chunk_size - bytes_read)
                b = self.client.conn.recv(packet_size)
                if not b:
                    break

                bytes_read += len(b)

                chunk_bytes.append(b)

            chunk = QImage()
            chunk.loadFromData(chunk_bytes)

            self.received_dirty_rect_signal.emit(
                chunk,
                x,
                y,
            )

    def stop(self) -> None:
        super().stop()

        if self.event_loop is not None:
            self.event_loop.quit()

    def display_screen_selection_dialog(self, screens: List[arcane.Screen]) -> None:
        self.event_loop = QEventLoop()

        self.request_screen_selection_dialog_signal.emit(screens)

        self.event_loop.exec()

    @pyqtSlot(arcane.Screen)
    def on_screen_selection_dialog_closed(self, screen: arcane.Screen) -> None:
        self.selected_screen = screen

        if self.event_loop is not None:
            self.event_loop.quit()
            self.event_loop = None
