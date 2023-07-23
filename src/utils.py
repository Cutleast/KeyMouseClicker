"""
Part of KeyMouseClicker.
Contains utility functions and classes.

License: Attribution-NonCommercial-NoDerivatives 4.0 International
"""

import ctypes
import logging
from pynput import keyboard, mouse
from typing import Callable

import qtpy.QtCore as qtc
import qtpy.QtWidgets as qtw

import main


class Thread(qtc.QThread):
    """
    Inherited by QThread and designed for easier usage.
    """

    def __init__(self, target: Callable, name: str=None, parent: qtw.QWidget=None):
        super().__init__(parent)

        self.target = target

        if name is not None:
            self.setObjectName(name)

    def run(self):
        self.target()


class KeyboardListener:
    def __init__(self, app: main.MainApp):
        self.app = app

        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def on_press(self, key: keyboard.Key):
        if self.app.is_setting_key:
            if self.app.root.isActiveWindow():
                if key == self.app.selected_hotkey:
                    # raise Exception("Cannot select the current hotkey as key to press!")
                    self.app.is_setting_key = False
                    self.app.button_widget.key_selection_button.setText("Click and press a key")
                    self.app.root.setEnabled(True)
                    self.app.invalid_key_signal.emit()
                    return

                self.app.selected_key = key
                self.app.button_widget.change_selected_key(key)
                self.app.is_setting_key = False
                self.app.root.setEnabled(True)
        elif self.app.is_setting_hotkey:
            if self.app.root.isActiveWindow():
                if key == self.app.selected_key:
                    # raise Exception("Cannot select the current key as hotkey!")
                    self.app.is_setting_hotkey = False
                    self.app.hotkey_widget.change_hotkey_button.setText("Change Hotkey")
                    self.app.root.setEnabled(True)
                    self.app.invalid_hotkey_signal.emit()
                    return

                self.app.selected_hotkey = key
                self.app.hotkey_widget.change_selected_hotkey(key)
                self.app.is_setting_hotkey = False
                self.app.root.setEnabled(True)
        elif ((not self.app.is_setting_key) and (not self.app.is_setting_hotkey)
              and key == self.app.selected_hotkey):
            # Check if already running
            if self.app.is_running:
                self.app.is_running = False
                self.app.root.setWindowTitle(self.app.name)
            else:
                self.app.save_config()

                if self.app.config["action"] == "autoclick":
                    frequency = self.app.config["autoclick_controls"]["frequency_in_ms"]
                    if not frequency:
                        # raise Exception("0 ms is not a valid frequency!")
                        self.app.invalid_frequency_signal.emit()
                        return

                    if self.app.config["device"] == "mouse":
                        self.app.press_thread = Thread(
                            self.app.mouse_autoclick
                        )
                    else:
                        self.app.press_thread = Thread(
                            self.app.key_autoclick
                        )
                else:
                    if self.app.config["device"] == "mouse":
                        self.app.press_thread = Thread(
                            self.app.hold_mouse_button
                        )
                    else:
                        self.app.press_thread = Thread(
                            self.app.hold_key
                        )

                self.app.is_running = True
                self.app.root.setWindowTitle(f"{self.app.name} - Running")
                self.app.thread_signal.emit()


def strlevel2intlevel(level: str) -> int:
    """
    Converts logging level from string to integer.
    Returns 20 (info level) if string is invalid.
    
    Example: "debug" -> 10
    """

    intlevel: int = getattr(logging, level.upper(), 20)

    return intlevel

def intlevel2strlevel(level: int) -> str:
    """
    Converts logging level from integer to string.
    Returns "info" if integer is invalid.
    
    Example: 10 -> "debug"
    """

    if level == logging.DEBUG:
        return "debug"
    elif level == logging.INFO:
        return "info"
    elif level == logging.CRITICAL:
        return "critical"
    elif level == logging.ERROR:
        return "error"
    elif level == logging.FATAL:
        return "fatal"
    else:
        return "info"

def center(widget: qtw.QWidget, referent: qtw.QWidget = None) -> None:
    """
    Moves <widget> to center of its parent or if given to
    center of <referent>.
    
    Parameters:
        widget: QWidget (widget to move)
        referent: QWidget (widget reference for center coords;
        uses widget.parent() if None)
    """

    size = widget.size()
    w = size.width()
    h = size.height()

    if referent is None:
        rsize = qtw.QApplication.primaryScreen().size()
    else:
        rsize = referent.size()
    rw = rsize.width()
    rh = rsize.height()

    x = int((rw / 2) - (w / 2))
    y = int((rh / 2) - (h / 2))

    widget.move(x, y)

def apply_shadow(widget: qtw.QWidget, color: str = "#181818") -> None:
    """
    Applies standardized shadow effect to <widget>.
    """

    shadoweffect = qtw.QGraphicsDropShadowEffect(widget)
    shadoweffect.setBlurRadius(4)
    shadoweffect.setOffset(4, 4)
    shadoweffect.setColor(color)
    widget.setGraphicsEffect(shadoweffect)

def apply_dark_title_bar(widget: qtw.QWidget):
    """
    Applies dark title bar to <widget>.

    
    More information here:

    https://docs.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    """

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
    hwnd = widget.winId()
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2 # on
    value = ctypes.c_int(value)
    set_window_attribute(
        hwnd,
        rendering_policy,
        ctypes.byref(value),
        ctypes.sizeof(value)
    )

def format_key_string(key: keyboard.Key):
    """
    Formats key to string.
    Example: Key.f6 -> F6
    """

    formatted_key = str(key).strip()
    formatted_key = formatted_key.removeprefix("Key.")

    # If the key to format is the ' key, this makes it show as ' instead of "'"
    # The raw format of "'" is '"\'"'
    if repr(formatted_key) != repr('"\'"'):
        formatted_key = formatted_key.replace("'", "")
    else:
        formatted_key = "'"

    return formatted_key.capitalize()
