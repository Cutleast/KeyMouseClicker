"""
Copyright (c) Cutleast
"""

from typing import Annotated

from cutleast_core_lib.core.config.app_config import AppConfig as BaseAppConfig
from cutleast_core_lib.core.utilities.base_enum import BaseEnum
from cutleast_core_lib.core.utilities.dynamic_default_model import default_factory
from cutleast_core_lib.ui.widgets.toast import Toast
from pydantic import Field


class AppConfig(BaseAppConfig):
    """
    App configuration.
    """

    class AppLanguage(BaseEnum):
        """Enum for the languages supported by the app."""

        System = "System"
        German = "de_DE"
        English = "en_US"

    language: Annotated[AppLanguage, Field(alias="ui.language")] = AppLanguage.System

    show_toast: Annotated[bool, Field(alias="toast.show")] = True
    """Whether to show toasts."""

    toast_position: Annotated[Toast.Position, Field(alias="toast.position")] = (
        Toast.Position.Bottom
    )
    """The position to show toasts at."""

    toast_offset_taskbar: Annotated[bool, Field(alias="toast.offset_taskbar")] = True
    """Whether to offset the toast position by the taskbar."""

    @default_factory("accent_color")
    @classmethod
    def get_default_accent_color(cls) -> str:
        """
        Returns:
            str: Default accent color.
        """

        return "#8197ec"
