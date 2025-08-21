"""
Copyright (c) Cutleast
"""

import logging
from typing import Optional

from pynput.keyboard import Key, KeyCode
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Button as MouseButton
from pynput.mouse import Listener as MouseListener
from PySide6.QtCore import QObject, Signal

from .button import get_button
from .device import Device


class KeyListener(QObject):
    """
    Listener for keyboard and mouse events.
    """

    key_pressed = Signal(object)
    """
    Signal emitted whenever a key on the configured device is pressed.

    Args:
        Button: The key that was pressed.
    """

    __listener: KeyboardListener | MouseListener

    log: logging.Logger = logging.getLogger("KeyListener")

    def __init__(self, device: Device = Device.Keyboard) -> None:
        """
        Args:
            device (Device, optional):
                Input device to listen to. Defaults to Device.Keyboard.
        """

        super().__init__()

        match device:
            case Device.Keyboard:
                self.__listener = KeyboardListener(on_press=self.__on_press)
            case Device.Mouse:
                self.__listener = MouseListener(
                    on_click=lambda x, y, button, pressed: self.__on_press(button)
                )

        self.__listener.start()

    def __on_press(self, key: Optional[Key | KeyCode | MouseButton]) -> None:
        try:
            self.key_pressed.emit(get_button(key))
            # self.log.info(f"Registered key press: {key}")
        except ValueError:
            pass

    def stop(self) -> None:
        """
        Stops the listener. For starting it again, create a new instance.
        """

        self.__listener.stop()
