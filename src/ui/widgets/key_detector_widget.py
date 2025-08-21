"""
Copyright (c) Cutleast
"""

from typing import Optional

from cutleast_core_lib.core.utilities.blocking_thread import BlockingThread
from pynput.keyboard import Key
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from core.autoclicker.button import Button
from core.autoclicker.device import Device
from core.autoclicker.key_detector import KeyDetector
from core.utilities.format_key import format_key_string


class KeyDetectorWidget(QWidget):
    """
    Widget for configuring a key.

    **The parent is responsible that there can't be two active listeners at the same
    time!**
    """

    currentKeyChanged = Signal(object)
    """
    Signal emitted when the user sets a new key.

    Args:
        Button: The new key.
    """

    keyChangeStarted = Signal()
    """Signal emitted when the user starts changing the key."""

    keyChangeStopped = Signal()
    """Signal emitted when the user stops changing the key."""

    __current_key: Button
    __detector: KeyDetector

    __current_key_label: QLabel
    __change_key_button: QPushButton

    def __init__(
        self,
        initial_key: Button,
        device: Device = Device.Keyboard,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Args:
            initial_key (Button): The initial key.
            device (Device, optional):
                The device to listen to. Defaults to Device.Keyboard.
            parent (Optional[QWidget], optional): Parent widget. Defaults to None.
        """

        super().__init__(parent)

        self.__init_ui()

        self.setDevice(device)
        self.setCurrentKey(initial_key)

        self.__change_key_button.clicked.connect(self.__change_key)

    def __init_ui(self) -> None:
        self.setContentsMargins(0, 0, 0, 0)

        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vlayout)

        self.__current_key_label = QLabel()
        vlayout.addWidget(self.__current_key_label)

        self.__change_key_button = QPushButton(self.tr("Change key..."))
        vlayout.addWidget(self.__change_key_button)

    def setDevice(self, device: Device) -> None:
        """
        Sets the device to listen to.

        Args:
            device (Device): The device to listen to.
        """

        self.__detector = KeyDetector(device)

    def setCurrentKey(self, key: Button) -> None:
        """
        Sets the current key.

        Args:
            key (Button): The key to set.
        """

        self.__current_key = key

        key_name: str
        if isinstance(key, Key):
            key_name = format_key_string(key)
        else:
            key_name = str(key)

        self.__current_key_label.setText(self.tr("Current key: %s") % key_name)

    def getCurrentKey(self) -> Button:
        """
        Returns:
            Button: The current key.
        """

        return (
            self.__current_key.strip("'")
            if isinstance(self.__current_key, str)
            else self.__current_key
        )

    def __change_key(self) -> None:
        self.__change_key_button.setText(
            self.tr("Waiting for input (press Escape to cancel)...")
        )
        self.setDisabled(True)

        self.keyChangeStarted.emit()

        thread = BlockingThread(self.__detector.detect_key)
        key: Button = thread.start()

        if key is not Key.esc:
            self.setCurrentKey(key)
            self.currentKeyChanged.emit(key)

        self.setDisabled(False)
        self.__change_key_button.setText(self.tr("Change key..."))

        self.keyChangeStopped.emit()
