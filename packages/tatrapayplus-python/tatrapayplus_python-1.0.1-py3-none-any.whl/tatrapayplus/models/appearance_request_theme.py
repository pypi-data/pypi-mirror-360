from enum import Enum


class AppearanceRequestTheme(str, Enum):
    DARK = "DARK"
    LIGHT = "LIGHT"
    SYSTEM = "SYSTEM"

    def __str__(self) -> str:
        return str(self.value)
