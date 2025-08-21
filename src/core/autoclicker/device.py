"""
Copyright (c) Cutleast
"""

from typing import override

from cutleast_core_lib.core.utilities.localized_enum import LocalizedEnum
from PySide6.QtWidgets import QApplication


class Device(LocalizedEnum):
    """Enum for the supported input devices."""

    Keyboard = "keyboard"
    """The key is pressed on the keyboard."""

    Mouse = "mouse"
    """The key is pressed on the mouse."""

    @override
    def get_localized_name(self) -> str:
        locs: dict[Device, str] = {
            Device.Keyboard: QApplication.translate("Device", "Keyboard"),
            Device.Mouse: QApplication.translate("Device", "Mouse"),
        }

        return locs[self]

    @override
    def get_localized_description(self) -> str:
        locs: dict[Device, str] = {
            Device.Keyboard: QApplication.translate(
                "Device", "The key is pressed on the keyboard."
            ),
            Device.Mouse: QApplication.translate(
                "Device", "The key is pressed on the mouse."
            ),
        }

        return locs[self]
