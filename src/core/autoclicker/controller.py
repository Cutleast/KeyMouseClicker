"""
Copyright (c) Cutleast
"""

from pynput import keyboard, mouse

from .button import Button, get_pynput_key


class Controller:
    """
    Helper class for controlling the mouse and keyboard.
    """

    __mouse_controller: mouse.Controller = mouse.Controller()
    __keyboard_controller: keyboard.Controller = keyboard.Controller()

    @classmethod
    def press(cls, button: Button) -> None:
        """
        Presses the specified button. Release it by calling `release()`.

        Args:
            button (Button): The button to press.
        """

        key = get_pynput_key(button)

        if isinstance(key, (keyboard.Key, keyboard.KeyCode, str)):
            cls.__keyboard_controller.press(key)
        else:
            cls.__mouse_controller.press(key)

    @classmethod
    def release(cls, button: Button) -> None:
        """
        Releases the specified button.

        Args:
            button (Button): The button to release.
        """

        key = get_pynput_key(button)

        if isinstance(key, (keyboard.Key, keyboard.KeyCode, str)):
            cls.__keyboard_controller.release(key)
        else:
            cls.__mouse_controller.release(key)
