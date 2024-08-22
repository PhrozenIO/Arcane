"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

from typing import Optional, Union

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QCheckBox, QDialog, QHBoxLayout, QLabel,
                             QMainWindow, QPushButton, QVBoxLayout)

import arcane_viewer.ui.utilities as utilities


class ServerCertificateDialog(utilities.QCenteredDialog):
    def __init__(self, parent: Optional[Union[QDialog, QMainWindow]], fingerprint: str) -> None:
        super().__init__(parent)

        self.setWindowTitle("Unknown Server Certificate")

        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.MSWindowsFixedSizeDialogHint
        )

        core_layout = QVBoxLayout()
        self.setLayout(core_layout)

        # Certificate Information
        certificate_info_label = QLabel("Please ensure the following fingerprint (SHA-1) matches the expected server "
                                        "fingerprint.")

        certificate_info_label.setObjectName("alert-warning")
        certificate_info_label.setWordWrap(True)

        core_layout.addWidget(certificate_info_label)

        core_layout.addSpacing(16)

        self.fingerprint = fingerprint

        core_layout.addLayout(self.setup_fingerprint_layout(0, 10))
        core_layout.addLayout(self.setup_fingerprint_layout(10, 20))
        core_layout.addLayout(self.setup_fingerprint_layout(20, 30))
        core_layout.addLayout(self.setup_fingerprint_layout(30, 40))

        core_layout.addSpacing(8)

        # Trust Certificate Option for next sessions
        self.trust_certificate_checkbox = QCheckBox("Add this certificate to the trusted certificates store")
        core_layout.addWidget(self.trust_certificate_checkbox)

        core_layout.addSpacing(8)

        # Action Buttons
        action_buttons_layout = QHBoxLayout()
        core_layout.addLayout(action_buttons_layout)

        self.reject_button = QPushButton('Reject')
        self.reject_button.clicked.connect(lambda: self.reject())
        action_buttons_layout.addWidget(self.reject_button)

        self.accept_button = QPushButton('Accept')
        self.accept_button.clicked.connect(lambda: self.accept())
        action_buttons_layout.addWidget(self.accept_button)

        self.reject_button.setDefault(True)
        self.reject_button.setFocus()

        self.adjust_size()

    def setup_fingerprint_layout(self, start: int, end: int) -> QHBoxLayout:
        layout = QHBoxLayout()
        line = [self.fingerprint[i:i + 2] for i in range(start, end, 2)]

        for index, item in enumerate(line):
            label = QLabel(item)
            label.setFont(utilities.MONOSPACE_FONTS)
            label.setObjectName("fingerprint")
            layout.addWidget(label)

            if index < len(line) - 1:
                label = QLabel(" : ")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(label)

        return layout

    def adjust_size(self) -> None:
        self.setFixedSize(
            self.sizeHint().width(),
            self.sizeHint().height()
        )
