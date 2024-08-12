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

from typing import Union

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QMainWindow

MONOSPACE_FONTS = QFont("Consolas, 'Courier New', Monaco, 'DejaVu Sans Mono', 'Liberation Mono', monospace")


class CenterWindow:
    """ Mixin to center a window on the screen or on another window """
    def center_on_owner(self: Union[QDialog, QMainWindow], owner: Union[QDialog, QMainWindow] = None):
        if owner is None:
            owner_geometry = self.screen().availableGeometry()
        else:
            owner_geometry = owner.frameGeometry()

        subform_geometry = self.frameGeometry()

        center_point = owner_geometry.center()

        subform_geometry.moveCenter(center_point)
        self.move(subform_geometry.topLeft())
