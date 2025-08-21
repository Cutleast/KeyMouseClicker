"""
Copyright (c) Cutleast
"""

from typing import Annotated, override

from cutleast_core_lib.core.config.base_config import BaseConfig
from pydantic import BeforeValidator, PlainSerializer
from pynput.keyboard import Key

from core.utilities.enum_utils import get_member_by_name

from ..autoclicker.action import Action
from ..autoclicker.button import Button
from ..autoclicker.device import Device
from ..autoclicker.mouse_button import MouseButton

type ConfigButton = Annotated[
    Button,
    # Deserialize by name
    BeforeValidator(
        lambda member: (
            get_member_by_name(
                member, Key, get_member_by_name(member, MouseButton, member)
            )
            if isinstance(member, str)
            else member
        )
    ),
    # Serialize by name
    PlainSerializer(
        lambda member: member.name if isinstance(member, Key) else member,
        return_type=str,
        when_used="always",
    ),
]


class AutoclickerConfig(BaseConfig):
    """
    Configuration for the auto clicker itself.
    """

    action: Action = Action.Autoclick
    """The action to perform."""

    device: Device = Device.Mouse
    """The input device to use."""

    button: ConfigButton = MouseButton.Left
    """The button to use."""

    interval: int = 100
    """The interval (in ms) to use."""

    repeat: int = -1
    """The repeat count to use (-1 = infinity)."""

    hotkey: ConfigButton = Key.f6
    """The hotkey to use."""

    suppress_hotkey: bool = False
    """Whether to suppress the hotkey for other apps."""

    @override
    @staticmethod
    def get_config_name() -> str:
        return "autoclicker.json"
