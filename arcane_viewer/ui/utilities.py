"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

from typing import Optional

from PyQt6.QtGui import QFont, QShowEvent
from PyQt6.QtWidgets import QDialog, QMainWindow, QWidget

MONOSPACE_FONTS = QFont("Consolas, 'Courier New', Monaco, 'DejaVu Sans Mono', 'Liberation Mono', monospace")


class CenteredWindowMixin(QWidget):
    """ Mixin to center a widget on the screen or on another widget """
    def center_on_owner(self) -> None:
        parent = self.parent()
        screen = self.screen()

        if parent is not None and isinstance(parent, QWidget):
            owner_geometry = parent.frameGeometry()
        elif screen is not None:
            owner_geometry = screen.availableGeometry()
        else:
            return

        subform_geometry = self.frameGeometry()

        center_point = owner_geometry.center()

        subform_geometry.moveCenter(center_point)
        self.move(subform_geometry.topLeft())


class QCenteredDialog(QDialog, CenteredWindowMixin):
    def showEvent(self, event: Optional[QShowEvent]) -> None:
        self.center_on_owner()


class QCenteredMainWindow(QMainWindow, CenteredWindowMixin):
    def showEvent(self, event: Optional[QShowEvent]) -> None:
        self.center_on_owner()
