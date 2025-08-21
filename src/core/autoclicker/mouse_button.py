"""
Copyright (c) Cutleast
"""

from typing import override

from cutleast_core_lib.core.utilities.localized_enum import LocalizedEnum
from PySide6.QtWidgets import QApplication


class MouseButton(LocalizedEnum):
    """Enum for mouse buttons."""

    Left = "Left"
    Middle = "Middle"
    Right = "Right"

    @override
    def get_localized_name(self) -> str:
        locs: dict[MouseButton, str] = {
            MouseButton.Left: QApplication.translate("MouseButton", "Left"),
            MouseButton.Middle: QApplication.translate("MouseButton", "Middle"),
            MouseButton.Right: QApplication.translate("MouseButton", "Right"),
        }

        return locs[self]
