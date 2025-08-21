"""
Copyright (c) Cutleast
"""

from typing import Optional

from cutleast_core_lib.ui.widgets.enum_radiobutton_widget import EnumRadiobuttonsWidget
from cutleast_core_lib.ui.widgets.toast import Toast
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from core.autoclicker.action import Action
from core.autoclicker.autoclicker import Autoclicker
from core.autoclicker.button import Button
from core.autoclicker.device import Device
from core.autoclicker.exceptions import ButtonsMustNotBeSame
from core.autoclicker.mouse_button import MouseButton
from core.config.app_config import AppConfig
from core.config.autoclicker_config import AutoclickerConfig
from ui.autoclicker.repeat_widget import RepeatWidget
from ui.widgets.key_detector_widget import KeyDetectorWidget


class AutoclickerWidget(QWidget):
    """
    Widget for controlling the autoclicker.
    """

    __app_config: AppConfig

    __autoclicker_config: AutoclickerConfig
    __autoclicker: Autoclicker

    __ac_toggled_toast: Toast
    __config_updated_toast: Toast

    __vlayout: QVBoxLayout

    __hotkey_selector: KeyDetectorWidget
    __suppress_checkbox: QCheckBox

    __action_selector: EnumRadiobuttonsWidget[Action]
    __device_selector: EnumRadiobuttonsWidget[Device]

    __key_stacked_layout: QStackedLayout
    __kb_key_selector: KeyDetectorWidget
    __mousebutton_selector: EnumRadiobuttonsWidget[MouseButton]

    __autoclick_group_box: QGroupBox
    __interval_box: QSpinBox
    __repeat_widget: RepeatWidget

    def __init__(
        self,
        app_config: AppConfig,
        autoclicker_config: AutoclickerConfig,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Args:
            app_config (AppConfig): Configuration for the application.
            autoclicker_config (AutoclickerConfig): Configuration for the autoclicker.
            parent (Optional[QWidget], optional): Parent widget. Defaults to None.
        """

        self.__app_config = app_config

        self.__autoclicker_config = autoclicker_config
        self.__autoclicker = Autoclicker(autoclicker_config)

        super().__init__(parent)

        self.__init_ui()
        self.__init_toasts()

        self.__suppress_checkbox.setHidden(True)  # TODO: WIP

        self.__action_selector.currentValueChanged.connect(self.__toggle_action)
        self.__device_selector.currentValueChanged.connect(self.__toggle_device)

        self.__toggle_device(self.__autoclicker_config.device)
        self.__toggle_action(self.__autoclicker_config.action)

        self.__hotkey_selector.currentKeyChanged.connect(self.__on_hotkey_change)
        self.__hotkey_selector.keyChangeStarted.connect(self.__on_key_change_started)
        self.__hotkey_selector.keyChangeStopped.connect(self.__on_key_change_stopped)
        self.__action_selector.currentValueChanged.connect(lambda _: self.apply())
        self.__device_selector.currentValueChanged.connect(lambda _: self.apply())
        self.__kb_key_selector.currentKeyChanged.connect(self.__on_kb_key_change)
        self.__kb_key_selector.keyChangeStarted.connect(self.__on_key_change_started)
        self.__kb_key_selector.keyChangeStopped.connect(self.__on_key_change_stopped)
        self.__mousebutton_selector.currentValueChanged.connect(lambda _: self.apply())
        self.__interval_box.valueChanged.connect(lambda _: self.apply())
        self.__repeat_widget.changed.connect(self.apply)

        self.__autoclicker.toggled.connect(self.__on_autoclicker_toggled)
        self.__autoclicker.start()

    def __init_ui(self) -> None:
        self.__vlayout = QVBoxLayout()
        self.__vlayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.__vlayout)

        self.__init_hotkey_selector()
        self.__init_action_selector()
        self.__init_button_selector()
        self.__init_autoclick_settings()

    def __init_hotkey_selector(self) -> None:
        hlayout = QHBoxLayout()
        self.__vlayout.addLayout(hlayout)

        self.__hotkey_selector = KeyDetectorWidget(self.__autoclicker_config.hotkey)
        hlayout.addWidget(self.__hotkey_selector)

        self.__suppress_checkbox = QCheckBox(self.tr("Suppress for other apps"))
        self.__suppress_checkbox.setChecked(self.__autoclicker_config.suppress_hotkey)
        hlayout.addWidget(
            self.__suppress_checkbox, alignment=Qt.AlignmentFlag.AlignBottom
        )

    def __init_action_selector(self) -> None:
        group_box = QGroupBox(self.tr("Action"))
        self.__vlayout.addWidget(group_box)

        vlayout = QVBoxLayout()
        group_box.setLayout(vlayout)

        self.__action_selector = EnumRadiobuttonsWidget(
            enum_type=Action,
            initial_value=self.__autoclicker_config.action,
            orientation=Qt.Orientation.Horizontal,
        )
        vlayout.addWidget(self.__action_selector)

    def __init_button_selector(self) -> None:
        group_box = QGroupBox(self.tr("Button"))
        self.__vlayout.addWidget(group_box)

        vlayout = QVBoxLayout()
        group_box.setLayout(vlayout)

        self.__device_selector = EnumRadiobuttonsWidget(
            enum_type=Device,
            initial_value=self.__autoclicker_config.device,
            orientation=Qt.Orientation.Horizontal,
        )
        vlayout.addWidget(self.__device_selector)

        self.__key_stacked_layout = QStackedLayout()
        vlayout.addLayout(self.__key_stacked_layout)

        self.__kb_key_selector = KeyDetectorWidget(self.__autoclicker_config.button)
        self.__key_stacked_layout.addWidget(self.__kb_key_selector)

        self.__mousebutton_selector = EnumRadiobuttonsWidget(
            enum_type=MouseButton,
            initial_value=(
                self.__autoclicker_config.button
                if isinstance(self.__autoclicker_config.button, MouseButton)
                else None
            ),
            orientation=Qt.Orientation.Horizontal,
        )
        self.__key_stacked_layout.addWidget(self.__mousebutton_selector)

    def __init_autoclick_settings(self) -> None:
        self.__autoclick_group_box = QGroupBox(self.tr("Autoclick settings"))
        self.__vlayout.addWidget(self.__autoclick_group_box)

        vlayout = QVBoxLayout()
        self.__autoclick_group_box.setLayout(vlayout)

        hlayout = QHBoxLayout()
        vlayout.addLayout(hlayout)

        hlayout.addWidget(QLabel(self.tr("Interval (ms)") + ":"))

        self.__interval_box = QSpinBox()
        self.__interval_box.setRange(1, 1_000_000_000)
        self.__interval_box.setValue(self.__autoclicker_config.interval)
        hlayout.addWidget(self.__interval_box)

        self.__repeat_widget = RepeatWidget(self.__autoclicker_config.repeat)
        vlayout.addWidget(self.__repeat_widget)

    def __init_toasts(self) -> None:
        self.__ac_toggled_toast = Toast(
            "",
            pos=self.__app_config.toast_position,
            offset_taskbar=self.__app_config.toast_offset_taskbar,
        )
        self.__ac_toggled_toast.setIcon(QApplication.windowIcon())

        self.__config_updated_toast = Toast(
            self.tr("Autoclicker configuration updated."),
            pos=self.__app_config.toast_position,
            offset_taskbar=self.__app_config.toast_offset_taskbar,
        )
        self.__config_updated_toast.setIcon(QApplication.windowIcon())

    def __on_autoclicker_toggled(self, active: bool) -> None:
        if active:
            self.__ac_toggled_toast.setText(self.tr("Autoclicker started."))
        else:
            self.__ac_toggled_toast.setText(self.tr("Autoclicker stopped."))

        if self.__app_config.show_toast:
            self.__ac_toggled_toast.show()

    def __toggle_device(self, new_device: Device) -> None:
        match new_device:
            case Device.Keyboard:
                self.__key_stacked_layout.setCurrentWidget(self.__kb_key_selector)
            case Device.Mouse:
                self.__key_stacked_layout.setCurrentWidget(self.__mousebutton_selector)

    def __toggle_action(self, new_action: Action) -> None:
        self.__autoclick_group_box.setEnabled(new_action == Action.Autoclick)

    def __on_key_change_started(self) -> None:
        self.__autoclicker.stop()
        self.setDisabled(True)

        parent: Optional[QWidget] = self.parentWidget()
        if parent is not None:
            parent.setDisabled(True)

    def __on_key_change_stopped(self) -> None:
        self.__autoclicker.start()
        self.setEnabled(True)

        parent: Optional[QWidget] = self.parentWidget()
        if parent is not None:
            parent.setDisabled(False)

    def __on_hotkey_change(self, new_hotkey: Button) -> None:
        if new_hotkey == self.__autoclicker_config.button:
            # Reset key and raise an exception
            self.__hotkey_selector.setCurrentKey(self.__autoclicker_config.hotkey)
            raise ButtonsMustNotBeSame

        self.apply()

    def __on_kb_key_change(self, new_key: Button) -> None:
        if new_key == self.__autoclicker_config.hotkey:
            # Reset key and raise an exception
            self.__kb_key_selector.setCurrentKey(self.__autoclicker_config.button)
            raise ButtonsMustNotBeSame

        self.apply()

    def apply(self) -> None:
        """
        Applies the configuration to the autoclicker.
        """

        self.__autoclicker_config.hotkey = self.__hotkey_selector.getCurrentKey()
        self.__autoclicker_config.suppress_hotkey = self.__suppress_checkbox.isChecked()
        self.__autoclicker_config.action = self.__action_selector.getCurrentValue()
        self.__autoclicker_config.device = self.__device_selector.getCurrentValue()
        if self.__device_selector.getCurrentValue() == Device.Keyboard:
            self.__autoclicker_config.button = self.__kb_key_selector.getCurrentKey()
        else:
            self.__autoclicker_config.button = (
                self.__mousebutton_selector.getCurrentValue()
            )

        self.__autoclicker_config.interval = self.__interval_box.value()
        self.__autoclicker_config.repeat = (
            self.__repeat_widget.get_current_repeat_count()
        )

        if self.__app_config.show_toast:
            self.__config_updated_toast.show()

    def save_config(self) -> None:
        """
        Applies and saves the configuration.
        """

        self.apply()
        self.__autoclicker_config.save()
