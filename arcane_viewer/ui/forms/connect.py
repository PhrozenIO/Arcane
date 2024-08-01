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

import json
import os.path
import socket

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit, QMainWindow, QMessageBox,
                             QPushButton, QSpinBox, QVBoxLayout, QWidget)

import arcane_viewer.arcane as arcane
import arcane_viewer.arcane.threads as arcane_threads
import arcane_viewer.ui.forms as arcane_forms
import arcane_viewer.ui.utilities as utilities


class ConnectWindow(QMainWindow, utilities.CenterWindow):
    """ Connect Window to establish a connection to the server """

    __connect_thread = None
    __connecting_form = None
    desktop_window = None
    session = None

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{arcane.APP_NAME} :: Connect")

        self.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.MSWindowsFixedSizeDialogHint
        )

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Setup Main Layout (Core Layout)
        core_layout = QVBoxLayout()
        self.central_widget.setLayout(core_layout)

        # Server Address Form Input
        self.server_address_label = QLabel("Server Address / Port:")
        core_layout.addWidget(self.server_address_label)

        server_address_layout = QHBoxLayout()

        self.server_address_input = QLineEdit()
        self.server_address_input.setText("127.0.0.1")
        server_address_layout.addWidget(self.server_address_input)

        separator_label = QLabel(":")
        server_address_layout.addWidget(separator_label)

        self.server_port_input = QSpinBox()
        self.server_port_input.setMinimum(0)
        self.server_port_input.setMaximum(65535)
        self.server_port_input.setValue(2801)
        server_address_layout.addWidget(self.server_port_input)

        server_address_layout.setStretch(0, 5)
        server_address_layout.setStretch(1, 0)
        server_address_layout.setStretch(2, 2)

        core_layout.addLayout(server_address_layout)

        core_layout.addSpacing(4)

        # Password Form Input
        self.password_label = QLabel("Password:")
        core_layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        core_layout.addWidget(self.password_input)

        core_layout.addSpacing(4)

        # Advanced Settings (Fieldset)
        advanced_settings_group = QGroupBox("Advanced Settings")
        advanced_settings_group_layout = QGridLayout()
        advanced_settings_group.setLayout(advanced_settings_group_layout)
        core_layout.addWidget(advanced_settings_group)

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

        self.packet_size_input.setCurrentIndex(2)  # Default to 4096 bytes

        # Block Size (Optimization)
        block_size_label = QLabel("Block Size:")
        self.block_size_input = QComboBox()
        for value in arcane.BlockSize:
            self.block_size_input.addItem(value.display_name, userData=value)

        self.block_size_input.setCurrentIndex(1)  # Default to 64x64

        # Place Inputs in our Grid Layout
        advanced_settings_group_layout.addWidget(image_quality_label, 0, 0)
        advanced_settings_group_layout.addWidget(self.image_quality_input, 0, 1)

        advanced_settings_group_layout.addWidget(packet_size_label, 1, 0)
        advanced_settings_group_layout.addWidget(self.packet_size_input, 1, 1)

        advanced_settings_group_layout.addWidget(block_size_label, 2, 0)
        advanced_settings_group_layout.addWidget(self.block_size_input, 2, 1)

        # Give Breath to Action Buttons
        core_layout.addSpacing(6)

        # Action Buttons
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.show_about_dialog)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(lambda: self.close())

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.submit_form)
        self.connect_button.setDefault(True)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.about_button)
        action_layout.addWidget(self.cancel_button)
        action_layout.addWidget(self.connect_button)

        core_layout.addLayout(action_layout)

        # Read Default Settings: Mostly for development purposes, until custom profiles are implemented
        self.read_default()

        self.adjust_size()

    def showEvent(self, event):
        super().showEvent(event)
        self.center_on_owner()

    def read_default(self):
        """ Read default settings from the default.json file """
        if not os.path.isfile(arcane.DEFAULT_JSON):
            return

        with open(arcane.DEFAULT_JSON, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return

            if "use" in data and data["use"] is False:
                return

            if "server_address" in data:
                self.server_address_input.setText(data["server_address"])

            if "server_port" in data:
                self.server_port_input.setValue(data["server_port"])

            if "server_password" in data:
                self.password_input.setText(data["server_password"])

    def submit_form(self):
        """ Validate the form and submit it """
        try:
            # Check if the ip/hostname is valid
            hostname = self.server_address_input.text()
            try:
                if socket.gethostbyname(hostname) == hostname:
                    pass
            except socket.gaierror:
                self.server_address_input.setFocus()
                raise Exception("Invalid hostname or IP address.")

            # Check password input
            if len(self.password_input.text().strip()) == 0:
                self.password_input.setFocus()
                raise Exception("Password field cannot be empty.")

            # Attempt connection
            self.__connect_thread = arcane_threads.ConnectThread(
                self.server_address_input.text(),
                self.server_port_input.value(),
                self.password_input.text(),
            )

            self.__connect_thread.thread_started.connect(self.connect_thread_started)
            self.__connect_thread.session_error.connect(self.session_error)
            self.__connect_thread.thread_finished.connect(self.connect_thread_finished)
            self.__connect_thread.start()
        except Exception as e:
            QMessageBox.critical(self, "Form Error", str(e))

    def adjust_size(self):
        self.setFixedSize(350, self.sizeHint().height())

    def show_about_dialog(self):
        about_window = arcane_forms.AboutWindow(self)
        about_window.exec()

    def get_packet_size_option(self):
        return self.packet_size_input.currentData()

    def get_block_size_option(self):
        return self.block_size_input.currentData()

    def get_image_quality_option(self):
        return self.image_quality_input.value()

    @pyqtSlot(str)
    def session_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

    @pyqtSlot()
    def connect_thread_started(self):
        self.__connecting_form = arcane_forms.ConnectingWindow(self)
        self.__connecting_form.exec()

    @pyqtSlot(object)
    def connect_thread_finished(self, session: arcane.Session = None):
        # Close the connecting form if it is still open
        if self.__connecting_form is not None and self.__connecting_form.isVisible():
            self.__connecting_form.close()

        if session is None:
            return

        self.session = session

        # Assign Advanced Options
        self.session.option_packet_size = self.get_packet_size_option()
        self.session.option_block_size = self.get_block_size_option()
        self.session.option_image_quality = self.get_image_quality_option()

        # Show the Remote Desktop Window
        self.desktop_window = arcane_forms.DesktopWindow(self, self.session)
        self.desktop_window.show()
