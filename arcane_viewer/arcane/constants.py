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

import os
import sys

ASSETS_IDENTIFIER = "arcane_viewer.assets"

# Asset path getter
if sys.version_info < (3, 9):
    import pkg_resources

    def get_asset_file(asset_name):
        return pkg_resources.resource_filename(ASSETS_IDENTIFIER, asset_name)

else:
    import importlib.resources as resources

    def get_asset_file(asset_name):
        with resources.files(ASSETS_IDENTIFIER) / asset_name as asset_path:
            return str(asset_path)


# Application Information
APP_VERSION = "1.0.4"
APP_NAME = "Arcane"
APP_ORGANIZATION_NAME = "Phrozen"
APP_DISPLAY_NAME = f"{APP_NAME} {APP_VERSION} (βeta)"

# Remote Desktop Engine Hardcoded Values
VD_WINDOW_ADJUST_RATIO = 90

# Assets absolute paths
DEFAULT_JSON = os.path.join(get_asset_file("default.json"))
APP_ICON = os.path.join(get_asset_file("app_icon.png"))

# Settings Key Names
SETTINGS_KEY_TRUSTED_CERTIFICATES = "trusted_certificates"
SETTINGS_KEY_IMAGE_QUALITY = "image_quality"
SETTINGS_KEY_PACKET_SIZE = "packet_size"
SETTINGS_KEY_BLOCK_SIZE = "block_size"
SETTINGS_KEY_CLIPBOARD_MODE = "clipboard_mode"
