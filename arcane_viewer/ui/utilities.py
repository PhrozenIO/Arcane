"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

from PyQt6.QtGui import QFont, QShowEvent
from PyQt6.QtWidgets import QDialog, QMainWindow, QWidget

MONOSPACE_FONTS = QFont("Consolas, 'Courier New', Monaco, 'DejaVu Sans Mono', 'Liberation Mono', monospace")


class CenteredWindowMixin(QWidget):
    """ Mixin to center a widget on the screen or on another widget """
    def center_on_owner(self) -> None:
        if self.parent() is None:
            owner_geometry = self.screen().availableGeometry()
        else:
            owner_geometry = self.parent().frameGeometry()

        subform_geometry = self.frameGeometry()

        center_point = owner_geometry.center()

        subform_geometry.moveCenter(center_point)
        self.move(subform_geometry.topLeft())


class QCenteredDialog(QDialog, CenteredWindowMixin):
    def showEvent(self, event: QShowEvent) -> None:
        self.center_on_owner()


class QCenteredMainWindow(QMainWindow, CenteredWindowMixin):
    def showEvent(self, event: QShowEvent) -> None:
        self.center_on_owner()
