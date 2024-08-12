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
        - (0001) : Implement remote screen resolution update, if it does, we will need to ensure it push an update of
                   selected screen object and reflect the changes where necessary.
"""

import logging

from PyQt6.QtCore import QRect, QSize, Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPainter, QPixmap, QTransform
from PyQt6.QtWidgets import (QApplication, QGraphicsPixmapItem, QMainWindow,
                             QMessageBox)

import arcane_viewer.arcane as arcane
import arcane_viewer.arcane.threads as arcane_threads
import arcane_viewer.ui.custom_widgets as arcane_widgets
import arcane_viewer.ui.dialogs as arcane_dialogs

logger = logging.getLogger(__name__)


class DesktopWindow(QMainWindow):
    def __init__(self, parent, session):
        super().__init__()

        self.tangent_universe = None
        self.scene_pixmap = None
        self.v_desktop = None
        self.desktop_thread = None
        self.events_thread = None
        self.universe_collapsed = False

        self.session = session

        # Instead of using QWidget parent property, we will use a custom attribute to store the parent window, this will
        # prevent icon to disappear on Windows taskbar when a parent is set to a Window but parent is hidden.
        self.parent = parent

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

        self.start_desktop_thread()

    def thread_finished(self, on_error):
        """ Handle the thread finished event """
        if on_error:
            QMessageBox.critical(self, "Error", "Something went wrong, check console output for more information.")

            """ If one thread (desktop or events) failed, we will close the other one, it is considered as a critical
                error """
            self.universe_collapsed = True

        self.close()

    def start_desktop_thread(self):
        """ Start the desktop thread to handle remote desktop streaming """
        self.desktop_thread = arcane_threads.VirtualDesktopThread(self.session)
        self.desktop_thread.chunk_received.connect(self.update_scene)
        self.desktop_thread.open_cellar_door.connect(self.open_cellar_door)
        self.desktop_thread.thread_finished.connect(self.thread_finished)
        self.desktop_thread.request_screen_selection.connect(self.display_screen_selection_dialog)
        self.desktop_thread.start()

    def start_events_thread(self, screen):
        """ Start the events thread to handle remote desktop events """
        self.events_thread = arcane_threads.EventsThread(self.session)
        self.events_thread.thread_finished.connect(self.thread_finished)
        self.events_thread.start()

        # Assign our events thread to the Tangent Universe
        self.tangent_universe.set_event_thread(self.events_thread)
        self.tangent_universe.set_screen(screen)

    def close_cellar_door(self):
        """ Collapse Tangent Universe to Main Branch, We were able to save the world before 28:06:42:12 """
        if self.desktop_thread is not None:
            if self.desktop_thread.isRunning():
                self.desktop_thread.stop()
                self.desktop_thread.wait()

        if self.events_thread is not None:
            if self.events_thread.isRunning():
                self.events_thread.stop()
                self.events_thread.wait()

    def showEvent(self, event):
        super().showEvent(event)

        if self.parent is not None:
            self.parent.hide()

    def closeEvent(self, event):
        """ Overridden close method to handle the cleanup
            `I Hope That When The World Comes To An End, I Can Breathe A Sigh Of Relief Because There Will Be So Much To
             Look Forward To.`"""

        if self.universe_collapsed:
            do_close = True
        else:
            do_close = QMessageBox.question(
                self,
                "Close",
                "Are you sure you want to close the remote desktop session?"
            ) == QMessageBox.StandardButton.Yes

        if do_close:
            self.close_cellar_door()

            event.accept()

            if self.parent is not None:
                self.parent.show()
        else:
            event.ignore()

    def open_cellar_door(self, screen):
        """ Initialize the virtual desktop (Tangent Universe) """
        self.v_desktop = QPixmap(screen.size())
        self.v_desktop.fill(Qt.GlobalColor.black)

        self.scene_pixmap = QGraphicsPixmapItem(self.v_desktop)
        self.tangent_universe.scene.addItem(self.scene_pixmap)

        # Initialize the size of virtual desktop window regarding our current monitor screen size
        local_screen = None

        for local_screen_candidate in QApplication.screens():
            if local_screen_candidate.geometry().intersects(self.geometry()):
                local_screen = local_screen_candidate

                break

        if local_screen is None:
            local_screen = QApplication.primaryScreen()

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

    def fit_scene(self):
        """ Fit the scene (Hacky Technique) to the view """
        if self.tangent_universe is None or self.scene_pixmap is None:
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

    def update_scene(self, chunk, x, y):
        """ Update the virtual desktop with the received chunk """
        if self.v_desktop is None:
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

    def resizeEvent(self, event):
        """ Overridden resizeEvent method to fit the scene to the view """
        self.fit_scene()

    def screen_selection_rejected(self):
        self.universe_collapsed = True
        self.close()

    @pyqtSlot(list)
    def display_screen_selection_dialog(self, screens):
        """ Display screen selection dialog """
        screen_selection_dialog = arcane_dialogs.ScreenSelectionWindow(self, screens)
        screen_selection_dialog.accepted.connect(lambda: self.desktop_thread.on_screen_selection_dialog_closed(
            screen_selection_dialog.get_selected_screen()
        ))
        screen_selection_dialog.rejected.connect(self.screen_selection_rejected)
        screen_selection_dialog.exec()
