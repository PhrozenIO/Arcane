"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

import sys
from typing import Optional, Union

from PyQt6.QtCore import QT_VERSION_STR, QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QMainWindow,
                             QPushButton, QVBoxLayout)

import arcane_viewer.arcane as arcane
import arcane_viewer.ui.utilities as utilities


class AboutDialog(utilities.QCenteredDialog):
    def __init__(self, parent: Optional[Union[QDialog, QMainWindow]] = None) -> None:
        super().__init__(parent)

        self.setWindowTitle(f"About {arcane.APP_DISPLAY_NAME}")

        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.MSWindowsFixedSizeDialogHint
        )

        # Setup Main Layout (Core Layout)
        core_layout = QVBoxLayout()
        self.setLayout(core_layout)

        # Avatar
        avatar = QLabel(self)
        avatar.setPixmap(QIcon(arcane.APP_ICON).pixmap(QSize(96, 96)))
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        core_layout.addWidget(avatar)

        # About Author / Project
        text = QLabel(f"<h1>{arcane.APP_DISPLAY_NAME}</h1>"
                      f"<p><b>Protocol Version:</b> {arcane.PROTOCOL_VERSION}</p>"
                      f"<p><b>Python:</b> {sys.version.split()[0]} / <b>PyQt6: </b>{QT_VERSION_STR}</p>"
                      "<p>🇫🇷 Jean-Pierre LESUEUR (<a href=\"https://twitter.com/darkcodersc\">@DarkCoderSc</a>)</p>"
                      "<p><b>License:</b> Apache License 2.0</p>"
                      "<p><a href=\"https://github.com/PhrozenIO\">www.github.com/PhrozenIO</a></p>"
                      "<p>© 2024 - <a href=\"https://www.phrozen.io\">www.phrozen.io</a></p>")
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        core_layout.addWidget(text)

        # Give breath to the layout (before action buttons)
        core_layout.addSpacing(8)

        # Action Button(s)
        action_buttons_layout = QHBoxLayout()
        core_layout.addLayout(action_buttons_layout)

        action_buttons_layout.addStretch(1)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        action_buttons_layout.addWidget(close_button)

        action_buttons_layout.addStretch(1)

        self.adjust_size()

    def adjust_size(self) -> None:
        self.setFixedSize(380, self.sizeHint().height())
