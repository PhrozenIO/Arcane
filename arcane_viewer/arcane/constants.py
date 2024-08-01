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


# Constants or hard-coded values
APP_VERSION = "1.0.0"
APP_NAME = f"Arcane {APP_VERSION} (βeta)"
VD_WINDOW_ADJUST_RATIO = 90

DEFAULT_JSON = os.path.join(get_asset_file("default.json"))
APP_ICON = os.path.join(get_asset_file("app_icon.png"))
