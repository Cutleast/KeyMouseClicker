"""
Copyright (c) Cutleast
"""

from typing import override

from cutleast_core_lib.core.utilities.localized_enum import LocalizedEnum
from PySide6.QtWidgets import QApplication


class Action(LocalizedEnum):
    """Enum for the autoclicker actions."""

    Autoclick = "autoclick"
    """A set key is pressed in a continuous loop with a set interval."""

    Hold = "hold"
    """A set key is held down until the hotkey is pressed again."""

    @override
    def get_localized_name(self) -> str:
        locs: dict[Action, str] = {
            Action.Autoclick: QApplication.translate("Action", "Autoclick"),
            Action.Hold: QApplication.translate("Action", "Hold"),
        }

        return locs[self]

    @override
    def get_localized_description(self) -> str:
        locs: dict[Action, str] = {
            Action.Autoclick: QApplication.translate(
                "Action",
                "The set key is pressed in a continuous loop with the set interval.",
            ),
            Action.Hold: QApplication.translate(
                "Action", "The set key is held down until the hotkey is pressed again."
            ),
        }

        return locs[self]
