"""
Part of KeyMouseClicker.
Contains ui widgets and group boxes.

License: Attribution-NonCommercial-NoDerivatives 4.0 International
"""

import qtpy.QtCore as qtc
import qtpy.QtGui as qtg
import qtpy.QtWidgets as qtw
from pynput import keyboard, mouse

import main
import utils


class ActionWidget(qtw.QGroupBox):
    def __init__(self, app: main.MainApp):
        super().__init__()
        
        self.app = app
        self.setTitle("Action")
        
        self.mainlayout = qtw.QHBoxLayout()
        self.setLayout(self.mainlayout)

        self.autoclick_button = qtw.QRadioButton("Autoclick")
        self.autoclick_button.clicked.connect(
            lambda: self.app.autoclick_widget.setDisabled(False)
        )
        self.mainlayout.addWidget(self.autoclick_button)

        self.hold_button = qtw.QRadioButton("Hold")
        self.hold_button.clicked.connect(
            lambda: self.app.autoclick_widget.setDisabled(True)
        )
        self.mainlayout.addWidget(self.hold_button)
    
    def update_state(self):
        if self.app.config["action"] == "autoclick":
            self.autoclick_button.toggle()
        else:
            self.hold_button.toggle()
        self.app.autoclick_widget.setEnabled(self.app.config["action"] == "autoclick")

        # utils.apply_shadow(self)


class DeviceWidget(qtw.QGroupBox):
    def __init__(self, app: main.MainApp):
        super().__init__()

        self.app = app
        self.setTitle("Device")

        self.mainlayout = qtw.QHBoxLayout()
        self.setLayout(self.mainlayout)

        self.mouse_button = qtw.QRadioButton("Mouse")
        self.mouse_button.clicked.connect(
            lambda: (
                self.app.button_widget.mainlayout.setCurrentIndex(0),
                self.app.set_key(self.app.button_widget.get_mouse_button())
            )
        )
        self.mainlayout.addWidget(self.mouse_button)

        self.keyboard_button = qtw.QRadioButton("Keyboard")
        self.keyboard_button.clicked.connect(
            lambda: (
                self.app.button_widget.mainlayout.setCurrentIndex(1),
                self.app.set_key(getattr(
                    keyboard.Key,
                    self.app.button_widget.selected_key_label.text().removeprefix("Selected key: ").lower(),
                    self.app.button_widget.selected_key_label.text().removeprefix("Selected key: ").lower()
                ))
            )
        )
        self.mainlayout.addWidget(self.keyboard_button)

    def update_state(self):
        if self.app.config["device"] == "mouse":
            self.mouse_button.toggle()
            self.app.button_widget.mainlayout.setCurrentIndex(0)
        else:
            self.keyboard_button.toggle()
            self.app.button_widget.mainlayout.setCurrentIndex(1)

        # utils.apply_shadow(self)


class ButtonWidget(qtw.QGroupBox):
    def __init__(self, app: main.MainApp):
        super().__init__()

        self.app = app
        self.setTitle("Button")

        self.mainlayout = qtw.QStackedLayout()
        self.setLayout(self.mainlayout)

        self.mouse_selection_widget = qtw.QWidget()
        self.mouse_selection_layout = qtw.QHBoxLayout()
        self.mouse_selection_widget.setLayout(self.mouse_selection_layout)
        self.left_click_button = qtw.QRadioButton("Left Click")
        self.left_click_button.clicked.connect(
            lambda: self.app.set_key(mouse.Button.left)
        )
        self.left_click_button.toggle()
        self.mouse_selection_layout.addWidget(self.left_click_button)
        self.middle_click_button = qtw.QRadioButton("Middle Click")
        self.middle_click_button.clicked.connect(
            lambda: self.app.set_key(mouse.Button.middle)
        )
        self.mouse_selection_layout.addWidget(self.middle_click_button)
        self.right_click_button = qtw.QRadioButton("Right Click")
        self.right_click_button.clicked.connect(
            lambda: self.app.set_key(mouse.Button.right)
        )
        self.mouse_selection_layout.addWidget(self.right_click_button)

        self.key_selection_widget = qtw.QWidget()
        self.key_selection_layout = qtw.QVBoxLayout()
        self.key_selection_widget.setLayout(self.key_selection_layout)
        self.selected_key_label = qtw.QLabel("No key selected")
        self.selected_key_label.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        self.key_selection_layout.addWidget(self.selected_key_label)
        self.key_selection_button = qtw.QPushButton("Click and press a key")
        self.key_selection_button.clicked.connect(self.listen_for_key)
        self.key_selection_layout.addWidget(self.key_selection_button)

        self.mainlayout.addWidget(self.mouse_selection_widget)
        self.mainlayout.addWidget(self.key_selection_widget)
        self.mainlayout.setCurrentWidget(self.mouse_selection_widget)
    
    def get_mouse_button(self):
        if self.left_click_button.isChecked():
            return mouse.Button.left
        if self.middle_click_button.isChecked():
            return mouse.Button.middle
        if self.right_click_button.isChecked():
            return mouse.Button.right
    
    def update_state(self):
        if self.app.selected_key == mouse.Button.left:
            self.left_click_button.toggle()
        elif self.app.selected_key == mouse.Button.middle:
            self.middle_click_button.toggle()
        elif self.app.selected_key == mouse.Button.right:
            self.right_click_button.toggle()
        else:
            self.selected_key_label.setText(
                f"Selected key: {utils.format_key_string(self.app.selected_key)}"
            )

    def change_selected_key(self, key: keyboard.Key):
        self.selected_key_label.setText(
            f"Selected key: {utils.format_key_string(key)}"
        )
        self.key_selection_button.setText("Click and press a key")

    def listen_for_key(self):
        self.key_selection_button.setText("Listening...")
        self.app.is_setting_key = True
        self.app.root.setDisabled(True)


class AutoClickWidget(qtw.QGroupBox):
    def __init__(self, app: main.MainApp):
        super().__init__()
        
        self.app = app
        self.setTitle("Autoclick Settings")
        
        self.mainlayout = qtw.QFormLayout()
        self.setLayout(self.mainlayout)

        self.frequency_box = qtw.QLineEdit()
        self.autoclick_validator = qtg.QIntValidator(
            bottom=1,
            top=1_000_000_000,
            parent=self.frequency_box
        )
        self.frequency_box.setText("100")
        self.frequency_box.setValidator(self.autoclick_validator)
        self.mainlayout.addRow(
            "Autoclick Frequency [ms]",
            self.frequency_box
        )

        self.repeat_widget = RepeatWidget(self.app)
        self.mainlayout.addRow(self.repeat_widget)

    def update_state(self):
        self.frequency_box.setText(
            str(self.app.config["autoclick_controls"]["frequency_in_ms"])
        )

        self.repeat_widget.update_state()


class RepeatWidget(qtw.QGroupBox):
    def __init__(self, app: main.MainApp):
        super().__init__()

        self.app = app
        self.setTitle("Repeat")

        self.mainlayout = qtw.QGridLayout()
        self.setLayout(self.mainlayout)

        self.infinite_button = qtw.QRadioButton("Repeat until stopped")
        self.mainlayout.addWidget(self.infinite_button, 0, 0, 1, 3)

        self.limited_button = qtw.QRadioButton("Repeat")
        self.mainlayout.addWidget(self.limited_button, 1, 0)
        self.repeat_count_box = qtw.QLineEdit()
        self.repeat_validator = qtg.QIntValidator(bottom=1, top=100000000, parent=self.repeat_count_box)
        self.repeat_count_box.setValidator(self.repeat_validator)
        self.repeat_count_box.setText('100')
        self.mainlayout.addWidget(self.repeat_count_box, 1, 1)
        self.repeat_label = qtw.QLabel("times")
        self.mainlayout.addWidget(self.repeat_label, 1, 2)
    
    def update_state(self):
        if self.app.config["autoclick_controls"]["repeat"] == -1:
            self.infinite_button.toggle()
        else:
            self.limited_button.toggle()
            self.repeat_count_box.setText(
                str(self.app.config["autoclick_controls"]["repeat"])
            )


class HotkeyWidget(qtw.QWidget):
    def __init__(self, app: main.MainApp):
        super().__init__()

        self.app = app

        self.mainlayout = qtw.QVBoxLayout()
        self.setLayout(self.mainlayout)

        self.hotkey_label = qtw.QLabel(
            f"Press {self.app.config['hotkey'].capitalize()} to start or stop"
        )
        self.hotkey_label.setAlignment(qtc.Qt.AlignmentFlag.AlignHCenter)
        self.mainlayout.addWidget(self.hotkey_label)
        
        self.change_hotkey_button = qtw.QPushButton("Change Hotkey")
        self.change_hotkey_button.clicked.connect(self.listen_for_key)
        self.mainlayout.addWidget(self.change_hotkey_button)

    def change_selected_hotkey(self, key: keyboard.Key):
        self.hotkey_label.setText(
            f"Press {utils.format_key_string(key)} to start or stop"
        )
        self.change_hotkey_button.setText("Change Hotkey")

    def listen_for_key(self):
        self.change_hotkey_button.setText("Listening...")
        self.app.is_setting_hotkey = True
        self.app.root.setDisabled(True)
