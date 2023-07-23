"""
Name: KeyMouseClicker
Author: Cutleast
License: Attribution-NonCommercial-NoDerivatives 4.0 International
Python Version: 3.11.2
Qt Version: 6.5.1
"""

import ctypes
import json
import logging
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path
from pynput import keyboard, mouse

import assets
import qtpy.QtCore as qtc
import qtpy.QtGui as qtg
import qtpy.QtWidgets as qtw


class MainApp(qtw.QApplication):
    """
    Main application class.
    Contains main interface and windows.
    """

    # Application attributes
    name = "KeyMouseClicker"
    author = "Cutleast"
    version = "1.0"

    # Paths
    cur_path = Path(__file__).parent # Current path of file
    app_path = Path(os.getenv("APPDATA")) / author / name
    con_path = app_path / "config.json"
    res_path = cur_path / "assets"
    qss_path = app_path.parent / "style.qss"
    ico_path = ":/icon.png"

    # Configuration
    default_config = {
        "action": "autoclick",
        "device": "mouse",
        "button": "left",
        "autoclick_controls": {
            "frequency_in_ms": 100,
            "repeat": -1
        },
        "hotkey": "f6"
    }
    config = default_config

    # State variables
    is_running = False
    is_setting_key = False
    is_setting_hotkey = False

    # Keys
    selected_key: keyboard.Key | mouse.Button | str = None
    selected_hotkey: keyboard.Key | str = None

    # Thread
    press_thread = None
    thread_signal = qtc.Signal()

    # Errors
    invalid_key_signal = qtc.Signal()
    invalid_hotkey_signal = qtc.Signal()
    invalid_frequency_signal = qtc.Signal()

    def __init__(self):
        super().__init__()

        if not self.app_path.is_dir():
            os.makedirs(self.app_path, exist_ok=True)

        # Load or create user configuration
        self.__load_config()

        # Initialize keyboard listener
        self.keyboard_listener = utils.KeyboardListener(self)

        # Initialize main window and widgets
        self.__init_mainui()

    def start_thread(self):
        if self.press_thread is not None:
            self.press_thread.start()

    def exec(self):
        self.thread_signal.connect(self.start_thread)
        self.invalid_key_signal.connect(lambda: qtw.QMessageBox.warning(
            self.root,
            "Invalid key",
            "Cannot select the current hotkey as key to press!"
        ))
        self.invalid_hotkey_signal.connect(lambda: qtw.QMessageBox.warning(
            self.root,
            "Invalid hotkey",
            "Cannot select the current key as hotkey!"
        ))
        self.invalid_frequency_signal.connect(lambda: qtw.QMessageBox.warning(
            self.root,
            "Invalid frequency",
            "0 ms is not a valid frequency!"
        ))

        self.root.show()

        super().exec()

        # Save config
        self.save_config()

    def __load_config(self):
        if not self.con_path.is_file():
            with open(self.con_path, mode="w", encoding="utf8") as file:
                json.dump(self.default_config, file, indent=4)
        else:
            with open(self.con_path, mode="r", encoding="utf8") as file:
                self.config: dict = json.load(file)

        if self.config["device"] == "keyboard":
            self.selected_key = getattr(
                keyboard.Key,
                self.config["button"],
                self.config["button"]
            )
        else:
            self.selected_key = getattr(
                mouse.Button,
                self.config["button"],
                self.config["button"]
            )
        self.selected_hotkey = getattr(
            keyboard.Key,
            self.config["hotkey"],
            self.config["hotkey"]
        )

    def save_config(self):
        self.config["action"] = "autoclick" if self.action_widget.autoclick_button.isChecked() else "hold"
        self.config["device"] = "mouse" if self.device_widget.mouse_button.isChecked() else "keyboard"
        self.config["button"] = str(self.selected_key).split(".")[-1].replace("'", "")
        self.config["autoclick_controls"] = {
            "frequency_in_ms": int(self.autoclick_widget.frequency_box.text()),
            "repeat": (
                -1 if self.autoclick_widget.repeat_widget.infinite_button.isChecked()
                else int(self.autoclick_widget.repeat_widget.repeat_count_box.text())
            )
        }
        self.config["hotkey"] = str(self.selected_hotkey).split(".")[-1].replace("'", "")

        with open(self.con_path, "w", encoding="utf8") as file:
            json.dump(self.config, file, indent=4, ensure_ascii=False)

    def __init_mainui(self):
        self.root = qtw.QMainWindow()
        self.root.setObjectName("root")
        self.root.setWindowTitle(self.name)

        # Fix taskbar icon
        appid = "cutleast.KeyMouseClicker"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

        # Extract stylesheet to appdata folder if it does not exist there
        if not self.qss_path.is_file():
            os.makedirs(self.qss_path.parent, exist_ok=True)
            with open(self.qss_path, "wb") as file:
                style_file = qtc.QFile(":/style.qss")
                style_file.open(qtc.QFile.OpenModeFlag.ReadOnly)
                file.write(style_file.readAll().data())
                style_file.close()
        # Load and apply stylesheet
        self.root.setStyleSheet(self.qss_path.read_text())
        self.root.setWindowIcon(qtg.QIcon(str(self.ico_path)))

        # Fix link color
        palette = self.palette()
        palette.setColor(
            palette.ColorRole.Link,
            qtg.QColor("#8197ec")
        )
        self.setPalette(palette)

        # Apply dark titlebar
        utils.apply_dark_title_bar(self.root)

        # Menu and about dialog
        self.about_menu = qtw.QMenu()
        self.about_menu.setTitle("About")
        self.about_menu.setWindowFlags(
            qtc.Qt.WindowType.FramelessWindowHint
            | qtc.Qt.WindowType.Popup
            | qtc.Qt.WindowType.NoDropShadowWindowHint
        )
        self.about_menu.setAttribute(
            qtc.Qt.WidgetAttribute.WA_TranslucentBackground,
            on=True
        )
        self.about_menu.setStyleSheet(self.root.styleSheet())
        self.about_qt_action = qtg.QAction("About Qt", self.root)
        self.about_qt_action.triggered.connect(self.aboutQt)
        self.about_menu.addAction(self.about_qt_action)
        self.about_action = qtg.QAction(f"About {self.name}", self.root)
        self.about_action.triggered.connect(self.about)
        self.about_menu.addAction(self.about_action)
        self.root.menuBar().addMenu(self.about_menu)

        self.main_widget = qtw.QWidget()
        self.root.setCentralWidget(self.main_widget)
        self.layout = qtw.QVBoxLayout()
        self.layout.setAlignment(qtc.Qt.AlignmentFlag.AlignTop)
        self.main_widget.setLayout(self.layout)

        self.hotkey_widget = widgets.HotkeyWidget(self)
        self.layout.addWidget(self.hotkey_widget)

        self.layout.addSpacing(15)

        self.action_widget = widgets.ActionWidget(self)
        self.layout.addWidget(self.action_widget)

        self.layout.addSpacing(15)

        self.device_widget = widgets.DeviceWidget(self)
        self.layout.addWidget(self.device_widget)

        self.layout.addSpacing(15)

        self.button_widget = widgets.ButtonWidget(self)
        self.layout.addWidget(self.button_widget)

        self.layout.addSpacing(15)

        self.autoclick_widget = widgets.AutoClickWidget(self)
        self.layout.addWidget(self.autoclick_widget)

        self.action_widget.update_state()
        self.device_widget.update_state()
        self.button_widget.update_state()
        self.autoclick_widget.update_state()

    def set_key(self, key: keyboard.Key | mouse.Button | str):
        self.selected_key = key

    def mouse_autoclick(self):
        mouse_controller = mouse.Controller()

        frequency = self.config["autoclick_controls"]["frequency_in_ms"] / 1000
        repeat_times = self.config["autoclick_controls"]["repeat"]

        if repeat_times <= 0:
            while self.is_running:
                mouse_controller.click(self.selected_key)
                time.sleep(frequency)
        else:
            for c in range(repeat_times):
                if self.is_running:
                    mouse_controller.click(self.selected_key)
                    time.sleep(frequency)
                else:
                    break
            self.is_running = False
    
    def hold_mouse_button(self):
        mouse_controller = mouse.Controller()
        mouse_controller.press(self.selected_key)
        while self.is_running:
            pass
        mouse_controller.release(self.selected_key)

    def key_autoclick(self):
        keyboard_controller = keyboard.Controller()

        frequency = self.config["autoclick_controls"]["frequency_in_ms"] / 1000
        repeat_times = self.config["autoclick_controls"]["repeat"]

        if repeat_times <= 0:
            while self.is_running:
                keyboard_controller.press(self.selected_key)
                time.sleep(frequency)
        else:
            for c in range(repeat_times):
                if self.is_running:
                    keyboard_controller.press(self.selected_key)
                    time.sleep(frequency)
                else:
                    break
            self.is_running = False

    def hold_key(self):
        keyboard_controller = keyboard.Controller()

        while self.is_running:
            keyboard_controller.press(self.selected_key)
            time.sleep(0.03)

        keyboard_controller.release(self.selected_key)
    
    def about(self):
        dialog = qtw.QMessageBox(self.root)
        icon = self.root.windowIcon()
        pixmap = icon.pixmap(128, 128)
        dialog.setIconPixmap(pixmap)
        dialog.setWindowTitle(f"About {self.name}")
        dialog.setWindowIcon(self.root.windowIcon())
        dialog.setTextFormat(qtc.Qt.TextFormat.RichText)
        text = f"""
{self.name} v{self.version} by Cutleast
<br>
License: Attribution-NonCommercial-NoDerivatives 4.0 International
<br><br>
App icon from <a href='https://icons8.com'>icons8.com</a>.
"""

        dialog.setText(text)
        dialog.setStandardButtons(qtw.QMessageBox.StandardButton.Ok)

        # hacky way to set label width
        for label in dialog.findChildren(qtw.QLabel):
            if label.text() == text:
                label.setFixedWidth(400)
                break

        dialog.exec()


if __name__ == "__main__":
    import utils
    import widgets

    app = MainApp()
    app.exec()
