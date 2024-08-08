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

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel,
                             QPushButton, QVBoxLayout)

import arcane_viewer.ui.utilities as utilities


class ScreenSelectionWindow(QDialog, utilities.CenterWindow):
    """ Screen Selection Dialog """
    def __init__(self, parent, screens):
        super().__init__(parent)

        self.screens = screens

        self.setWindowTitle(f"Screen Selection ({len(self.screens)} Available)")

        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.MSWindowsFixedSizeDialogHint
        )

        core_layout = QVBoxLayout()
        self.setLayout(core_layout)

        # Screen Selection Combo
        screen_selection_label = QLabel("Select Screen:")
        core_layout.addWidget(screen_selection_label)

        self.screen_selection_combobox = QComboBox()

        # screen_selection_combobox.addItems([screen.name for screen in screens])
        for screen in self.screens:
            self.screen_selection_combobox.addItem(
                screen.get_display_name(),
                userData=screen.name
            )

        core_layout.addWidget(self.screen_selection_combobox)

        core_layout.addSpacing(8)

        # Action Buttons
        action_buttons_layout = QHBoxLayout()
        core_layout.addLayout(action_buttons_layout)

        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(lambda: self.reject())
        action_buttons_layout.addWidget(self.cancel_button)

        self.select_button = QPushButton('Select')
        self.select_button.clicked.connect(lambda: self.accept())
        action_buttons_layout.addWidget(self.select_button)

        self.select_button.setDefault(True)
        self.select_button.setFocus()

        self.setFixedSize(290, self.sizeHint().height())

    def showEvent(self, event):
        super().showEvent(event)
        self.center_on_owner(self.parent())

    def get_selected_screen(self):
        """ Get the user-choice selected screen """
        return [screen for screen in self.screens if screen.name == self.screen_selection_combobox.currentData()][0]
