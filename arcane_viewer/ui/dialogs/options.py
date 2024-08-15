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

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (QComboBox, QDialog, QGridLayout, QGroupBox,
                             QHBoxLayout, QLabel, QMessageBox, QPushButton,
                             QSizePolicy, QSpacerItem, QSpinBox, QTabWidget,
                             QTreeView, QVBoxLayout, QWidget)

import arcane_viewer.arcane as arcane
import arcane_viewer.ui.utilities as utilities

from .options_dialogs import ServerCertificateAddOrEditDialog


class RemoteDesktopOptionsTab(QWidget):
    """ Remote Desktop Options Tab """
    def __init__(self, settings: QSettings):
        super().__init__()

        self.settings = settings

        core_layout = QVBoxLayout()
        self.setLayout(core_layout)

        # Options
        options_layout = QGridLayout()
        options_layout.setContentsMargins(0, 8, 0, 0)
        core_layout.addLayout(options_layout)

        clipboard_sharing_label = QLabel("Clipboard Sharing:")

        self.clipboard_sharing_combobox = QComboBox()
        for value in arcane.ClipboardMode:
            self.clipboard_sharing_combobox.addItem(value.name, userData=value)

        options_layout.addWidget(clipboard_sharing_label, 0, 0)
        options_layout.addWidget(self.clipboard_sharing_combobox, 0, 1)

        # Capture Settings (Fieldset)
        desktop_capture_group = QGroupBox("Capture Settings")
        desktop_capture_group_layout = QGridLayout()
        desktop_capture_group.setLayout(desktop_capture_group_layout)
        core_layout.addWidget(desktop_capture_group)

        desktop_capture_group_layout.setContentsMargins(8, 16, 8, 8)

        # Virtual Desktop Image Quality
        image_quality_label = QLabel("Image Quality:")

        self.image_quality_input = QSpinBox()
        self.image_quality_input.setMinimum(10)
        self.image_quality_input.setMaximum(100)
        self.image_quality_input.setValue(80)

        # Packet Size (Optimization)
        packet_size_label = QLabel("Packet Size:")
        self.packet_size_input = QComboBox()
        for value in arcane.PacketSize:
            self.packet_size_input.addItem(value.display_name, userData=value)

        # Block Size (Optimization)
        block_size_label = QLabel("Block Size:")
        self.block_size_input = QComboBox()
        for value in arcane.BlockSize:
            self.block_size_input.addItem(value.display_name, userData=value)

        # Place Inputs in our Grid Layout
        desktop_capture_group_layout.addWidget(image_quality_label, 0, 0)
        desktop_capture_group_layout.addWidget(self.image_quality_input, 0, 1)

        desktop_capture_group_layout.addWidget(packet_size_label, 1, 0)
        desktop_capture_group_layout.addWidget(self.packet_size_input, 1, 1)

        desktop_capture_group_layout.addWidget(block_size_label, 2, 0)
        desktop_capture_group_layout.addWidget(self.block_size_input, 2, 1)

        core_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def load_settings(self):
        """ Load remote desktop settings from the settings """
        # Load Options
        self.clipboard_sharing_combobox.setCurrentIndex(
            self.clipboard_sharing_combobox.findData(
                self.settings.value(arcane.SETTINGS_KEY_CLIPBOARD_MODE, arcane.ClipboardMode.Both)
            )
        )

        # Load Capture Options
        self.image_quality_input.setValue(self.settings.value(arcane.SETTINGS_KEY_IMAGE_QUALITY, 80))

        self.packet_size_input.setCurrentIndex(
            self.packet_size_input.findData(
                self.settings.value(arcane.SETTINGS_KEY_PACKET_SIZE, arcane.PacketSize.Size4096)
            )
        )

        self.block_size_input.setCurrentIndex(
            self.block_size_input.findData(
                self.settings.value(arcane.SETTINGS_KEY_BLOCK_SIZE, arcane.BlockSize.Size64)
            )
        )

    def save_settings(self):
        """ Save remote desktop settings to the settings """
        # Save Options
        self.settings.setValue(arcane.SETTINGS_KEY_CLIPBOARD_MODE, self.clipboard_sharing_combobox.currentData())

        # Save Capture Options
        self.settings.setValue(arcane.SETTINGS_KEY_IMAGE_QUALITY, self.image_quality_input.value())
        self.settings.setValue(arcane.SETTINGS_KEY_PACKET_SIZE, self.packet_size_input.currentData())
        self.settings.setValue(arcane.SETTINGS_KEY_BLOCK_SIZE, self.block_size_input.currentData())


class TrustedCertificateModel(QStandardItemModel):
    """ Trusted Certificate Model (Disables editing of the fingerprint) """
    def flags(self, index):
        if index.column() == 1:  # Fingerprint
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

        return super().flags(index)


class TrustedCertificatesOptionsTab(QWidget):
    """ Trusted Certificates Options Tab """
    def __init__(self, settings: QSettings):
        super().__init__()

        self.settings = settings

        core_layout = QHBoxLayout()
        self.setLayout(core_layout)

        # Setup Certificate List
        self.tree_view = QTreeView()
        core_layout.addWidget(self.tree_view)

        self.model = TrustedCertificateModel()

        self.tree_view.setModel(self.model)
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.selectionModel().selectionChanged.connect(self.tree_view_selection_changed)
        self.tree_view.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)

        # Setup Action Buttons
        action_buttons_layout = QVBoxLayout()
        core_layout.addLayout(action_buttons_layout)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(lambda: self.add_or_edit_certificate(False))
        action_buttons_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Edit")
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(lambda: self.add_or_edit_certificate(True))
        action_buttons_layout.addWidget(self.edit_button)

        self.remove_button = QPushButton("Remove")
        self.remove_button.setEnabled(False)
        self.remove_button.clicked.connect(self.remove_button_clicked)
        action_buttons_layout.addWidget(self.remove_button)

        action_buttons_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def add_or_edit_row(self, fingerprint: str, display_name: str, description: str):
        """ Add a certificate to the list """
        # Edit row if it already exists
        for i in range(self.model.rowCount()):
            if self.model.item(i, 1).text() == fingerprint:
                self.model.item(i, 0).setText(display_name)
                self.model.item(i, 2).setText(description)

                return

        # (Or) Add a new row
        self.model.appendRow([
            QStandardItem(display_name),
            QStandardItem(fingerprint),
            QStandardItem(description),
        ])

    def tree_view_selection_changed(self):
        """ Update the state of the action buttons based on the selection """
        b = self.tree_view.currentIndex().isValid()
        self.edit_button.setEnabled(b)
        self.remove_button.setEnabled(b)

    def remove_button_clicked(self):
        """ Remove the selected certificate from the list """
        selected_index = self.tree_view.currentIndex()
        if not selected_index.isValid():
            return

        self.model.removeRow(selected_index.row())

    def add_or_edit_certificate(self, edit_selected: bool):
        """ Add or edit a certificate """
        fingerprint = None
        if edit_selected and self.tree_view.currentIndex().isValid():
            fingerprint = self.model.item(self.tree_view.currentIndex().row(), 1).text()

        dialog = ServerCertificateAddOrEditDialog(self, self.settings, fingerprint)
        dialog.exec()

        if dialog.result() == QDialog.DialogCode.Accepted:
            self.add_or_edit_row(
                dialog.fingerprint_edit.text(),
                dialog.display_name_edit.text(),
                dialog.description_edit.toPlainText()
            )

    def load_settings(self):
        """ Load trusted certificates from the settings """
        # First we clear the list
        self.model.clear()

        self.model.setHorizontalHeaderLabels([
            "Display Name",
            "SHA-256 Fingerprint",
            "Description",
        ])

        certificates = self.settings.value(arcane.SETTINGS_KEY_TRUSTED_CERTIFICATES, [])

        for certificate in certificates:
            certificate_information = self.settings.value(
                f"{arcane.SETTINGS_KEY_TRUSTED_CERTIFICATES}.{certificate}", {}
            )

            if not all(k in certificate_information for k in (
                "display_name",
                # Additional not mandatory fields must be added here (if any are added in the future)
            )):
                continue

            description = ""
            if "description" in certificate_information:
                description = certificate_information["description"]

            self.add_or_edit_row(certificate, certificate_information["display_name"], description)

        for i in range(self.model.columnCount()):
            self.tree_view.resizeColumnToContents(i)

    def save_settings(self):
        """ Save trusted certificates to the settings """
        certificates = []
        for i in range(self.model.rowCount()):
            certificate = self.model.item(i, 1).text().upper().strip()

            certificates.append(certificate)

            # Save extra information about the certificate
            certificate_information = {
                "display_name": self.model.item(i, 0).text(),
                "description": self.model.item(i, 2).text(),
                # Additional extra information fields to be placed here (if any are added in the future)
            }

            self.settings.setValue(
                f"{arcane.SETTINGS_KEY_TRUSTED_CERTIFICATES}.{certificate}",
                certificate_information
            )

        # Save the list of trusted certificates (Just the fingerprints)
        self.settings.setValue(arcane.SETTINGS_KEY_TRUSTED_CERTIFICATES, certificates)


class OptionsDialog(QDialog, utilities.CenterWindow):
    """ Arcane Options Dialog """
    def __init__(self, parent):
        super().__init__(parent)

        self.settings = QSettings(arcane.APP_ORGANIZATION_NAME, arcane.APP_NAME)

        self.setWindowTitle(f"{arcane.APP_DISPLAY_NAME} :: Options")

        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.MSWindowsFixedSizeDialogHint
        )

        core_layout = QVBoxLayout()
        self.setLayout(core_layout)

        core_layout.setContentsMargins(8, 8, 8, 8)

        # Setup Options Tab Control
        self.options_tab_widget = QTabWidget()
        core_layout.addWidget(self.options_tab_widget)

        # General Tab
        self.remote_desktop_tab = RemoteDesktopOptionsTab(self.settings)
        self.options_tab_widget.addTab(self.remote_desktop_tab, "Remote Desktop")

        # Trusted Certificates Tab
        self.trusted_certificates_tab = TrustedCertificatesOptionsTab(self.settings)
        self.options_tab_widget.addTab(self.trusted_certificates_tab, "Trusted Certificates")

        # Action Buttons
        action_buttons_layout = QHBoxLayout()
        core_layout.addLayout(action_buttons_layout)

        self.reset_button = QPushButton('Reset')
        self.reset_button.setObjectName('danger')
        self.reset_button.clicked.connect(self.reset_settings)
        action_buttons_layout.addWidget(self.reset_button)

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        action_buttons_layout.addItem(spacer)

        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(lambda: self.reject())
        action_buttons_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_settings)
        action_buttons_layout.addWidget(self.save_button)

        self.save_button.setDefault(True)
        self.save_button.setFocus()

        self.adjust_size()

    def load_settings(self):
        self.remote_desktop_tab.load_settings()
        self.trusted_certificates_tab.load_settings()

    def save_settings(self):
        self.remote_desktop_tab.save_settings()
        self.trusted_certificates_tab.save_settings()

        self.accept()

    def reset_settings(self):
        if QMessageBox.question(
                self,
                "Reset Settings",
                "Are you sure you want to reset all settings to their defaults? (This action cannot be undone)",
        ) == QMessageBox.StandardButton.Yes:
            self.settings.clear()

            self.load_settings()

    def adjust_size(self):
        self.setFixedSize(420, self.sizeHint().height())

    def showEvent(self, event):
        super().showEvent(event)

        self.load_settings()
