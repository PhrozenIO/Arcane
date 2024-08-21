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

    Todo:
        - Find a workaround for the Wayland issue for positioning the window.
        - Offer connection profile (Add/Edit/Delete)
        - Implement Clipboard sharing between client and server.
        - Offer possibility to change the default theme with something retro and cool.
"""

import logging
import sys
import threading

from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QApplication

import arcane_viewer.arcane as arcane
import arcane_viewer.ui.forms as arcane_forms


def main() -> None:
    logging.basicConfig(
                        level=logging.DEBUG,
                        format="%(asctime)s - %(name)s[%(thread)d] - %(levelname)s - %(message)s"
    )

    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(arcane.APP_ICON))

    app.setStyle('Fusion')

    # Create and apply a dark palette
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

    app.setPalette(dark_palette)

    # Apply custom stylesheet
    app.setStyleSheet("""
        QGroupBox::title {
            background-color: rgb(53, 53, 53);
            padding: 4px 8px 4px 8px;
            border-radius: 4px;
            left: 8px;
            top: 8px;
        }

        QLabel#fingerprint {
            background-color: rgb(42, 42, 42);
            padding: 4px;
            border-radius: 4px;
        }

        QLabel#alert-warning {
            background-color: #d0b650;
            color: #564917;
            padding: 4px;
            border-radius: 4px;
        }

        QHeaderView::section {
            height: 26px;
        }

        QTabBar::tab {
            height: 26px;
        }

        QPushButton#danger {
            background-color: darkred;
        }

        QPushButton:disabled {
            background-color: #444444;
            color: #777777;
        }
        """)

    logging.debug(f"Main thread ID: {threading.get_ident()}")

    # Create and show the connect window
    connect_window = arcane_forms.ConnectWindow()
    connect_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
