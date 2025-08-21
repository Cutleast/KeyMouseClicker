"""
Copyright (c) Cutleast
"""

import logging
import time
from typing import TYPE_CHECKING, Optional

from cutleast_core_lib.core.utilities.thread import Thread
from PySide6.QtCore import QObject, Qt, Signal

from core.autoclicker.action import Action
from core.autoclicker.controller import Controller
from core.autoclicker.device import Device

from .button import Button
from .key_listener import KeyListener

if TYPE_CHECKING:
    from ..config.autoclicker_config import AutoclickerConfig


class Autoclicker(QObject):
    """
    Main class for the autoclicker.
    """

    toggled = Signal(bool)
    """
    Signal emitted whenever the user presses the hotkey.

    Args:
        bool: Whether the autoclicker is active or not.
    """

    __config: "AutoclickerConfig"

    __autoclicker_thread: Optional[Thread] = None

    __listener: Optional[KeyListener] = None
    """
    The key listener for the autoclicker. Must be reinitialized everytime the configured
    input device changes.
    """

    __running: bool = False
    """Whether the autoclicker thread is running."""

    __active: bool = False
    """Whether the autoclicker is performing actions."""

    log: logging.Logger = logging.getLogger("Autoclicker")

    def __init__(
        self, config: "AutoclickerConfig", parent: Optional[QObject] = None
    ) -> None:
        super().__init__(parent)

        self.__config = config

        self.__init_listener()

    def __init_listener(self) -> None:
        self.__listener = KeyListener(Device.Keyboard)
        self.__listener.key_pressed.connect(
            self.__on_key_press, Qt.ConnectionType.QueuedConnection
        )

    def __on_key_press(self, key: Button) -> None:
        if key == self.__config.hotkey and self.__running:
            self.__active = not self.__active
            self.log.debug(f"Toggled autoclicker. Active: {self.__active}")
            self.toggled.emit(self.__active)

    def __thread(self) -> None:
        self.log.info("Thread started.")

        try:
            while self.__running:
                # Wait until the hotkey is pressed
                while self.__running and not self.__active:
                    time.sleep(0.01)

                # 'Freeze' the configured button so that it can't be changed while the
                # autoclicker is active
                button: Button = self.__config.button

                # Autoclick indefinitely with the configured interval
                if (
                    self.__config.repeat == -1
                    and self.__config.action == Action.Autoclick
                ):
                    while self.__active:
                        Controller.press(button)
                        Controller.release(button)
                        time.sleep(self.__config.interval / 1000)

                # Autoclick a configured number of times with the configured interval
                elif self.__config.action == Action.Autoclick:
                    for _ in range(self.__config.repeat):
                        if not self.__active:
                            break

                        Controller.press(button)
                        Controller.release(button)
                        time.sleep(self.__config.interval / 1000)

                    # Stop autoclicking after the configured number of times
                    if self.__active:
                        self.__active = False
                        self.toggled.emit(self.__active)

                # Hold key until the hotkey is pressed again
                else:
                    Controller.press(button)
                    while self.__active:
                        time.sleep(0.01)
                    Controller.release(button)

        except Exception as ex:
            self.log.critical(f"Thread crashed! Exception: {ex}", exc_info=ex)
            self.__running = self.__active = False
            raise

        else:
            self.log.info("Thread stopped.")

    def start(self) -> None:
        """
        Starts the autoclicker thread if it is not already running.
        """

        if self.__autoclicker_thread is not None:
            return

        self.__running = True
        self.__autoclicker_thread = Thread(target=self.__thread)
        self.__autoclicker_thread.start()

    def stop(self) -> None:
        """
        Stops the autoclicker thread if it is running.
        """

        self.__active = False
        self.__running = False

        if self.__autoclicker_thread is not None:
            self.__autoclicker_thread.wait()

        self.__autoclicker_thread = None
