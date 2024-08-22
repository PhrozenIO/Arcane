"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

import re
from typing import Optional, Union

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QMessageBox, QPushButton,
                             QSizePolicy, QSpacerItem, QTextEdit, QVBoxLayout)

import arcane_viewer.arcane as arcane
import arcane_viewer.ui.utilities as utilities


class ServerCertificateAddOrEditDialog(utilities.QCenteredDialog):
    def __init__(
            self,
            parent: Optional[Union[QDialog, QMainWindow]],
            settings: QSettings, fingerprint: Optional[str] = None
    ) -> None:
        super().__init__(parent)

        self.settings = settings
        self.fingerprint = fingerprint

        self.setWindowTitle("{} Trusted Server Certificate".format(
            "Add" if self.fingerprint is None else "Edit"
        ))

        core_layout = QVBoxLayout()
        self.setLayout(core_layout)

        # Create our form fields
        self.fingerprint_label = QLabel("Fingerprint:")
        core_layout.addWidget(self.fingerprint_label)

        self.fingerprint_edit = QLineEdit()
        self.fingerprint_edit.setEnabled(self.fingerprint is None)
        self.fingerprint_edit.setText(self.fingerprint)
        core_layout.addWidget(self.fingerprint_edit)

        self.display_name_label = QLabel("Display Name:")
        core_layout.addWidget(self.display_name_label)

        self.display_name_edit = QLineEdit()
        core_layout.addWidget(self.display_name_edit)

        self.description_label = QLabel("Description:")
        core_layout.addWidget(self.description_label)

        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        core_layout.addWidget(self.description_edit)

        # Load the values if we are editing
        certificate_information = self.settings.value(
            f"{arcane.SETTINGS_KEY_TRUSTED_CERTIFICATES}.{self.fingerprint}", None
        )

        if certificate_information is not None:
            if "display_name" in certificate_information:
                self.display_name_edit.setText(certificate_information["display_name"])

            if "description" in certificate_information:
                self.description_edit.setText(certificate_information["description"])

        core_layout.addSpacing(6)

        # Action Buttons
        action_buttons_layout = QHBoxLayout()
        core_layout.addLayout(action_buttons_layout)

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        action_buttons_layout.addItem(spacer)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(lambda: self.reject())
        action_buttons_layout.addWidget(self.cancel_button)

        button_caption = "Add" if self.fingerprint is None else "Save"
        self.validate_button = QPushButton(button_caption)
        self.validate_button.clicked.connect(self.save_or_update_certificate)
        self.validate_button.setDefault(True)
        action_buttons_layout.addWidget(self.validate_button)

        self.adjust_size()

    def save_or_update_certificate(self) -> None:
        """ Save or update the certificate information """
        if self.fingerprint is None:
            fingerprint = self.fingerprint_edit.text().upper()
            if re.match(r'^[a-fA-F0-9]{40}$', fingerprint) is None:
                QMessageBox.critical(
                    self,
                    "Invalid Certificate Fingerprint",
                    "The fingerprint is invalid, it must be a 40 characters hexadecimal string (SHA-1)."
                )

                self.fingerprint_edit.setFocus()

                return

        self.accept()

    def adjust_size(self) -> None:
        self.setFixedSize(400, self.sizeHint().height())
