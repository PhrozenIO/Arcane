"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

from PyQt6.QtCore import QSize


class Screen:
    """ Screen class to store screen information """
    def __init__(self, screen_information_json: dict) -> None:
        if not all(k in screen_information_json for k in (
                "Id",
                "Name",
                "Width",
                "Height",
                "X",
                "Y",
                "Primary",
        )):
            raise Exception("Invalid screen information received")

        self.id = screen_information_json["Id"]
        self.name = screen_information_json["Name"]
        self.width = screen_information_json["Width"]
        self.height = screen_information_json["Height"]
        self.x = screen_information_json["X"]
        self.y = screen_information_json["Y"]
        self.primary = screen_information_json["Primary"]

    def get_display_name(self) -> str:
        return "#{} - {} ({}x{})".format(
            self.id,
            self.name,
            self.width,
            self.height
        )

    def size(self) -> QSize:
        return QSize(self.width, self.height)
