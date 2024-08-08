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
        - (0001) LogonUI Support
"""

import logging
import struct
from typing import List  # To support python <= 3.8

from PyQt6.QtCore import QByteArray, QEventLoop, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage

import arcane_viewer.arcane as arcane

from .client_base import ClientBaseThread

logger = logging.getLogger(__name__)


class VirtualDesktopThread(ClientBaseThread):
    """ Thread to handle remote desktop streaming, at quantum level """
    open_cellar_door = pyqtSignal(arcane.Screen)
    request_screen_selection = pyqtSignal(list)
    chunk_received = pyqtSignal(QImage, int, int)

    def __init__(self, session: arcane.Session):
        super().__init__(session, arcane.WorkerKind.Desktop)

        self.selected_screen = None
        self.event_loop = None

    """`Destruction is a form of creation. So the fact they burn the money is ironic. They just want to see what happens
     when they tear the world apart. They want to change things.`, Donnie Darko"""
    def client_execute(self):
        screens_obj = self.client.read_json()
        screens = [arcane.Screen(screen) for screen in screens_obj["List"]]
        logger.info(f"{len(screens)} screen(s) detected")

        if len(screens) == 1:
            self.selected_screen = screens[0]
        else:
            self.display_screen_selection_dialog(screens)

        logger.info(f"Screen: {self.selected_screen.name} "
                    f"({self.selected_screen.width}x{self.selected_screen.height})")

        self.client.write_json(
            {
                "ScreenName": self.selected_screen.name,
                "ImageCompressionQuality": self.session.option_image_quality,
                "PacketSize": self.session.option_packet_size.value,
                "BlockSize": self.session.option_block_size.value,
                "LogonUI": False,  # TODO: 0001
            }
        )

        """ Open Cellar Door
        `This famous linguist once said, of all the phrases in the English language, of all the endless combinations
        of words in all of history, that 'cellar door' is the most beautiful.`, Karen Pomeroy"""
        self.open_cellar_door.emit(
            self.selected_screen
        )

        packet_max_size = self.session.option_packet_size.value
        while self._running:
            chunk_size, x, y = struct.unpack('III', self.client.conn.read(12))

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

            self.chunk_received.emit(
                chunk,
                x,
                y,
            )

    def stop(self):
        super().stop()

        if self.event_loop is not None:
            self.event_loop.quit()

    def display_screen_selection_dialog(self, screens: List[arcane.Screen]):
        self.event_loop = QEventLoop()

        self.request_screen_selection.emit(screens)

        self.event_loop.exec()

    @pyqtSlot(arcane.Screen)
    def on_screen_selection_dialog_closed(self, screen: arcane.Screen):
        if self.event_loop is not None:
            self.event_loop.quit()
            self.event_loop = None

        self.selected_screen = screen
