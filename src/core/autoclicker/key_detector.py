"""
Copyright (c) Cutleast
"""

import logging
from typing import Optional

from pynput import keyboard, mouse

from .button import Button, get_button
from .device import Device


class KeyDetector:
    """
    Class for detecting a key input on a specified input device.
    """

    __device: Device

    __listener: keyboard.Listener | mouse.Listener
    __pressed_key: Optional[Button] = None

    log: logging.Logger = logging.getLogger("KeyDetector")

    def __init__(self, device: Device = Device.Keyboard) -> None:
        """
        Args:
            device (Device, optional):
                Input device to listen to. Defaults to Device.Keyboard.
        """

        self.__device = device

    def __init_listener(self) -> None:
        match self.__device:
            case Device.Keyboard:
                self.__listener = keyboard.Listener(on_press=self.__on_press)
            case Device.Mouse:
                self.__listener = mouse.Listener(
                    on_click=lambda x, y, button, pressed: self.__on_press(button)
                )

    def __on_press(
        self, key: Optional[keyboard.Key | keyboard.KeyCode | mouse.Button]
    ) -> None:
        try:
            self.__pressed_key = get_button(key)
        except ValueError:
            pass

    def detect_key(self) -> Button:
        """
        Blocks until a key is pressed on the configured device and returns it.

        Returns:
            Button: The key that was pressed.
        """

        self.__init_listener()
        self.__pressed_key = None
        self.__listener.start()
        self.log.info("Started key detection. Waiting for input...")

        while self.__pressed_key is None:
            pass

        self.__listener.stop()
        self.log.info(f"Stopped key detection. Detected key: {self.__pressed_key}")

        return self.__pressed_key
