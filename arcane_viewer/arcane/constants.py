"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

import os
import sys

ASSETS_IDENTIFIER = "arcane_viewer.assets"

# Asset path getter
if sys.version_info < (3, 9):
    import pkg_resources

    def get_asset_file(asset_name: str) -> str:
        return pkg_resources.resource_filename(ASSETS_IDENTIFIER, asset_name)

else:
    import importlib.resources as resources

    def get_asset_file(asset_name: str) -> str:
        asset_path = resources.files(ASSETS_IDENTIFIER) / asset_name
        return str(asset_path)


# Application Information
APP_VERSION = "1.0.6"
APP_NAME = "Arcane"
APP_ORGANIZATION_NAME = "Phrozen"
APP_DISPLAY_NAME = f"{APP_NAME} {APP_VERSION}"

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
