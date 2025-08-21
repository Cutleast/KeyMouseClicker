"""
Copyright (c) Cutleast
"""

from typing import override

from cutleast_core_lib.core.utilities.exceptions import LocalizedException
from PySide6.QtWidgets import QApplication


class ButtonsMustNotBeSame(LocalizedException):
    """
    Exception raised when hotkey and autoclicker button are the same.
    """

    @override
    def getLocalizedMessage(self) -> str:
        return QApplication.translate(
            "Autoclicker", "Hotkey and autoclicker button must not be the same!"
        )
