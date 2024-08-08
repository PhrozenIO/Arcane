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
from PyQt6.QtWidgets import (QComboBox, QDialog, QGridLayout, QGroupBox,
                             QHBoxLayout, QLabel, QMessageBox, QPushButton,
                             QSizePolicy, QSpacerItem, QSpinBox, QTabWidget,
                             QVBoxLayout, QWidget)

import arcane_viewer.arcane as arcane
import arcane_viewer.ui.utilities as utilities


class RemoteDesktopOptionsTab(QWidget):
    def __init__(self):
        super().__init__()

        core_layout = QVBoxLayout()
        self.setLayout(core_layout)

        # Advanced Settings (Fieldset)
        desktop_capture_group = QGroupBox("Capture Settings")
        advanced_settings_group_layout = QGridLayout()
        desktop_capture_group.setLayout(advanced_settings_group_layout)
        core_layout.addWidget(desktop_capture_group)

        advanced_settings_group_layout.setContentsMargins(8, 16, 8, 8)

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
        advanced_settings_group_layout.addWidget(image_quality_label, 0, 0)
        advanced_settings_group_layout.addWidget(self.image_quality_input, 0, 1)

        advanced_settings_group_layout.addWidget(packet_size_label, 1, 0)
        advanced_settings_group_layout.addWidget(self.packet_size_input, 1, 1)

        advanced_settings_group_layout.addWidget(block_size_label, 2, 0)
        advanced_settings_group_layout.addWidget(self.block_size_input, 2, 1)

    def load_settings(self, settings: QSettings):
        self.image_quality_input.setValue(settings.value(arcane.SETTINGS_KEY_IMAGE_QUALITY, 80))
        self.packet_size_input.setCurrentIndex(
            self.packet_size_input.findData(settings.value(arcane.SETTINGS_KEY_PACKET_SIZE, arcane.PacketSize.Size4096))
        )
        self.block_size_input.setCurrentIndex(
            self.block_size_input.findData(settings.value(arcane.SETTINGS_KEY_BLOCK_SIZE, arcane.BlockSize.Size64))
        )

    def save_settings(self, settings: QSettings):
        settings.setValue(arcane.SETTINGS_KEY_IMAGE_QUALITY, self.image_quality_input.value())
        settings.setValue(arcane.SETTINGS_KEY_PACKET_SIZE, self.packet_size_input.currentData())
        settings.setValue(arcane.SETTINGS_KEY_BLOCK_SIZE, self.block_size_input.currentData())


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
        self.remote_desktop_tab = RemoteDesktopOptionsTab()
        self.options_tab_widget.addTab(self.remote_desktop_tab, "Remote Desktop")

        # Trusted Certificates Tab
        self.trusted_certificates_tab = QWidget()
        self.options_tab_widget.addTab(self.trusted_certificates_tab, "Trusted Certificates")

        # Action Buttons
        action_buttons_layout = QHBoxLayout()
        core_layout.addLayout(action_buttons_layout)

        self.reset_button = QPushButton('Reset')
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
        self.remote_desktop_tab.load_settings(self.settings)

    def save_settings(self):
        self.remote_desktop_tab.save_settings(self.settings)

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
