"""
Copyright (c) Cutleast
"""

import re
from typing import Optional

from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode

from .mouse_button import MouseButton

type Button = MouseButton | Key | str
"""Type alias for a mouse button or key."""


def get_button(key: Optional[keyboard.Key | keyboard.KeyCode | mouse.Button]) -> Button:
    """
    Gets the button from a raw pynput key.

    Args:
        key (Optional[keyboard.Key | keyboard.KeyCode | mouse.Button]):
            The key to get the button from.

    Raises:
        ValueError: If the key is unknown.

    Returns:
        Button: The button.
    """

    match key:
        case keyboard.Key():
            return key

        case mouse.Button():
            match key:
                case mouse.Button.left:
                    return MouseButton.Left
                case mouse.Button.right:
                    return MouseButton.Right
                case mouse.Button.middle:
                    return MouseButton.Middle

        case keyboard.KeyCode():
            return str(key).strip("'").removeprefix("Key.").capitalize()

    raise ValueError(f"Unknown key: {key}")


KEYCODE_PATTERN: re.Pattern[str] = re.compile(r"^<([0-9]+)>$")
"""Pattern for serialized key codes (e.g. "<102>")."""


def get_pynput_key(
    button: Button,
) -> keyboard.Key | keyboard.KeyCode | str | mouse.Button:
    """
    Gets the raw pynput key from a button.

    Args:
        button (Button): The button.

    Returns:
        keyboard.Key | keyboard.KeyCode | str | mouse.Button: The raw pynput key.
    """

    if isinstance(button, MouseButton):
        match button:
            case MouseButton.Left:
                return mouse.Button.left
            case MouseButton.Right:
                return mouse.Button.right
            case MouseButton.Middle:
                return mouse.Button.middle

    elif (
        isinstance(button, str) and (match := KEYCODE_PATTERN.match(button)) is not None
    ):
        return KeyCode.from_vk(int(match.group(1)))

    return button
