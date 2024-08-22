"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.

    Todo:
        - (0001) : Implement remote screen resolution update, if it does, we will need to ensure it push an update of
                   selected screen object and reflect the changes where necessary.
"""

import logging
from typing import List, Optional, Union

from PyQt6.QtCore import QRect, QSize, Qt, pyqtSlot
from PyQt6.QtGui import (QCloseEvent, QImage, QPainter, QPixmap, QResizeEvent,
                         QScreen, QShowEvent, QTransform)
from PyQt6.QtWidgets import (QApplication, QDialog, QGraphicsPixmapItem,
                             QMainWindow, QMessageBox)

import arcane_viewer.arcane as arcane
import arcane_viewer.arcane.threads as arcane_threads
import arcane_viewer.ui.custom_widgets as arcane_widgets
import arcane_viewer.ui.dialogs as arcane_dialogs

logger = logging.getLogger(__name__)


class DesktopWindow(QMainWindow):
    def __init__(self, connect_window: Union[QDialog, QMainWindow], session: arcane.Session) -> None:
        super().__init__()

        self.scene_pixmap: Optional[QGraphicsPixmapItem] = None
        self.v_desktop: Optional[QPixmap] = None

        self.desktop_thread: Optional[arcane_threads.VirtualDesktopThread] = None
        self.events_thread: Optional[arcane_threads.EventsThread] = None

        self.session = session

        # Instead of using QWidget parent property, we will use a custom attribute to store the "parent" window, this
        # will prevent icon to disappear on Windows taskbar when a parent is set to a Window but parent is hidden.
        self.connect_window = connect_window

        # Set Window Properties, Layout, Title, Icon and Size
        self.setWindowTitle("🖥 {} ({}) :: {} {}".format(
            arcane.APP_DISPLAY_NAME,
            session.server_address,
            session.display_name,
            "- View Only" if session.presentation else ""
        ))
        self.resize(QSize(640, 360))
        self.setMouseTracking(True)

        self.setContentsMargins(0, 0, 0, 0)

        self.tangent_universe = arcane_widgets.TangentUniverse()
        self.setCentralWidget(self.tangent_universe)

        """
        # FPS Counter (Debugging)
        self.FPS_counter = 0
        self.FPS_Elapsed = time.time()
        """

        self.start_desktop_thread()

    def thread_finished(self, on_error: bool) -> None:
        """ Handle the thread finished event """
        if on_error:
            QMessageBox.critical(self, "Error", "Something went wrong, check console output for more information.")

        self.close()

    def start_desktop_thread(self) -> None:
        """ Start the desktop thread to handle remote desktop streaming """
        self.desktop_thread = arcane_threads.VirtualDesktopThread(self.session)
        self.desktop_thread.chunk_received.connect(self.update_scene)
        self.desktop_thread.open_cellar_door.connect(self.open_cellar_door)
        self.desktop_thread.thread_finished.connect(self.thread_finished)
        self.desktop_thread.request_screen_selection.connect(self.display_screen_selection_dialog)
        self.desktop_thread.start()

    def start_events_thread(self, screen: arcane.Screen) -> None:
        """ Start the events thread to handle remote desktop events """
        self.events_thread = arcane_threads.EventsThread(self.session)
        self.events_thread.thread_finished.connect(self.thread_finished)
        self.events_thread.start()

        # Assign our events thread to the Tangent Universe
        self.tangent_universe.set_event_thread(self.events_thread)
        self.tangent_universe.set_screen(screen)

    def close_cellar_door(self) -> None:
        """ Collapse Tangent Universe to Main Branch, We were able to save the world before 28:06:42:12 """
        if self.desktop_thread is not None:
            if self.desktop_thread.isRunning():
                self.desktop_thread.stop()
                self.desktop_thread.wait()

        if self.events_thread is not None:
            if self.events_thread.isRunning():
                self.events_thread.stop()
                self.events_thread.wait()

    def showEvent(self, event: Optional[QShowEvent]) -> None:
        super().showEvent(event)

        if self.connect_window is not None:
            self.connect_window.hide()

    def closeEvent(self, event: Optional[QCloseEvent]) -> None:
        """ Overridden close method to handle the cleanup
            `I Hope That When The World Comes To An End, I Can Breathe A Sigh Of Relief Because There Will Be So Much To
             Look Forward To.`"""

        self.close_cellar_door()

        if event is not None:
            event.accept()

        if self.connect_window is not None:
            self.connect_window.show()

    def open_cellar_door(self, screen: arcane.Screen) -> None:
        """ Initialize the virtual desktop (Tangent Universe) """
        self.v_desktop = QPixmap(screen.size())
        self.v_desktop.fill(Qt.GlobalColor.black)

        self.scene_pixmap = QGraphicsPixmapItem(self.v_desktop)
        self.tangent_universe.desktop_scene.addItem(self.scene_pixmap)

        # Initialize the size of virtual desktop window regarding our current monitor screen size
        local_screen: Optional[QScreen] = None

        for local_screen_candidate in QApplication.screens():
            if local_screen_candidate.geometry().intersects(self.geometry()):
                local_screen = local_screen_candidate

                break

        if local_screen is None:
            local_screen = QApplication.primaryScreen()

        if local_screen is None:
            logger.error("Unable to find a valid screen to initialize the virtual desktop window.")

            self.close()

            return

        local_screen_size = local_screen.size()
        remote_screen_width = int(screen.width / local_screen.devicePixelRatio())
        remote_screen_height = int(screen.height / local_screen.devicePixelRatio())

        # Calculate the new width and height of the virtual desktop window
        if local_screen_size.width() <= remote_screen_width or local_screen_size.height() <= remote_screen_height:
            adjust_vertically = local_screen_size.width() > local_screen_size.height()

            if adjust_vertically:
                new_width = round((local_screen_size.width() * arcane.VD_WINDOW_ADJUST_RATIO) / 100)
                resized_ratio = round(new_width * 100 / remote_screen_width)
                new_height = round((remote_screen_height * resized_ratio) / 100)
            else:
                new_height = round((local_screen_size.height() * arcane.VD_WINDOW_ADJUST_RATIO) / 100)
                resized_ratio = round(new_height * 100 / remote_screen_height)
                new_width = round((remote_screen_width * resized_ratio) / 100)
        else:
            new_width = remote_screen_width
            new_height = remote_screen_height

        # Resize and place the window
        self.setGeometry(
            local_screen.geometry().left() + (local_screen_size.width() - new_width) // 2,
            local_screen.geometry().top() + (local_screen_size.height() - new_height) // 2,
            new_width,
            new_height
        )

        # We can now start our events thread
        # TODO: 0001
        self.start_events_thread(screen)

    def fit_scene(self) -> None:
        """ Fit the scene (Hacky Technique) to the view """
        if (
                self.tangent_universe is None or
                self.scene_pixmap is None or
                self.v_desktop is None
        ):
            return

        # Instead of bellow code:
        #   `self.view.fitInView(self.scene_pixmap, Qt.AspectRatioMode.IgnoreAspectRatio)`
        # We will calculate the scale factor manually to avoid the aspect ratio issue and fitting correctly the view to
        # our virtual desktop host window.
        view_rect = self.tangent_universe.frameRect()

        scale_x = view_rect.width() / self.v_desktop.width()
        scale_y = view_rect.height() / self.v_desktop.height()

        transform = QTransform()
        transform.scale(scale_x, scale_y)
        self.tangent_universe.setTransform(transform, False)

    def update_scene(self, chunk: QImage, x: int, y: int) -> None:
        """ Update the virtual desktop with the received chunk """
        if self.v_desktop is None or self.scene_pixmap is None:
            return

        if chunk is None or not isinstance(chunk, QImage):
            return

        # Update the virtual desktop with the received chunk (Tangent Universe)
        rect = QRect(x, y, chunk.width(), chunk.height())

        painter = QPainter(self.v_desktop)
        painter.drawImage(rect, chunk)
        painter.end()

        # Update the scene with the updated virtual desktop
        self.scene_pixmap.setPixmap(self.v_desktop)

        self.fit_scene()

        """
        # FPS Counter (Debugging)
        self.FPS_counter += 1
        elapsed = time.time() - self.FPS_Elapsed
        if elapsed >= 1.0:
            logger.debug("FPS: {}".format(self.FPS_counter))
            self.FPS_counter = 0
            self.FPS_Elapsed = time.time()
        """

    def resizeEvent(self, event: Optional[QResizeEvent]) -> None:
        """ Overridden resizeEvent method to fit the scene to the view """
        self.fit_scene()

    def screen_selection_rejected(self) -> None:
        self.close()

    @pyqtSlot(list)
    def display_screen_selection_dialog(self, screens: List[arcane.Screen]) -> None:
        """ Display screen selection dialog """
        screen_selection_dialog = arcane_dialogs.ScreenSelectionDialog(self, screens)

        screen_selection_dialog.accepted.connect(lambda: self.desktop_thread.on_screen_selection_dialog_closed(
            screen_selection_dialog.get_selected_screen()
        ) if self.desktop_thread is not None else None)

        screen_selection_dialog.rejected.connect(self.screen_selection_rejected)
        screen_selection_dialog.exec()
