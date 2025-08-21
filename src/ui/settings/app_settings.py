"""
Copyright (c) Cutleast
"""

from typing import cast, override

from cutleast_core_lib.core.config.app_config import AppConfig as BaseAppConfig
from cutleast_core_lib.ui.settings.app_settings import AppSettings as BaseAppSettings
from cutleast_core_lib.ui.widgets.enum_dropdown import EnumDropdown
from cutleast_core_lib.ui.widgets.toast import Toast
from PySide6.QtWidgets import QCheckBox, QLabel

from core.config.app_config import AppConfig


class AppSettings(BaseAppSettings):
    """
    App settings widget with language dropdown.
    """

    __language_box: EnumDropdown[AppConfig.AppLanguage]

    __show_toast_box: QCheckBox
    __toast_position_label: QLabel
    __toast_position_box: EnumDropdown[Toast.Position]
    __toast_offset_taskbar_box: QCheckBox

    def __init__(self, initial_config: BaseAppConfig) -> None:
        super().__init__(initial_config)

        self.__language_box.currentValueChanged.connect(
            lambda _: self.changed_signal.emit()
        )
        self.__language_box.currentValueChanged.connect(
            lambda _: self.restart_required_signal.emit()
        )

        self.__show_toast_box.stateChanged.connect(self.__on_toast_toggle)
        self.__show_toast_box.stateChanged.connect(lambda _: self.changed_signal.emit())
        self.__toast_position_box.currentValueChanged.connect(
            lambda _: self.changed_signal.emit()
        )
        self.__toast_position_box.currentValueChanged.connect(
            lambda _: self.restart_required_signal.emit()
        )
        self.__toast_offset_taskbar_box.stateChanged.connect(
            lambda _: self.changed_signal.emit()
        )
        self.__toast_offset_taskbar_box.stateChanged.connect(
            lambda _: self.restart_required_signal.emit()
        )

    @override
    def _init_ui(self) -> None:
        super()._init_ui()

        config = cast(AppConfig, self._initial_config)
        self.__language_box = EnumDropdown(AppConfig.AppLanguage, config.language)
        self.__language_box.installEventFilter(self)
        self._basic_flayout.insertRow(
            5, "*" + self.tr("App language:"), self.__language_box
        )

        self.__show_toast_box = QCheckBox(self.tr("Show toast notifications"))
        self.__show_toast_box.setChecked(config.show_toast)
        self._basic_flayout.addRow(self.__show_toast_box)

        self.__toast_position_label = QLabel("*" + self.tr("Toast position:"))
        self.__toast_position_label.setEnabled(config.show_toast)
        self.__toast_position_box = EnumDropdown(Toast.Position, config.toast_position)
        self.__toast_position_box.setEnabled(config.show_toast)
        self._basic_flayout.addRow(
            self.__toast_position_label, self.__toast_position_box
        )

        self.__toast_offset_taskbar_box = QCheckBox(
            "*" + self.tr("Offset taskbar when positioning toast")
        )
        self.__toast_offset_taskbar_box.setChecked(config.toast_offset_taskbar)
        self.__toast_offset_taskbar_box.setEnabled(config.show_toast)
        self._basic_flayout.addRow(self.__toast_offset_taskbar_box)

    def __on_toast_toggle(self, enabled: bool) -> None:
        self.__toast_position_label.setEnabled(enabled)
        self.__toast_position_box.setEnabled(enabled)
        self.__toast_offset_taskbar_box.setEnabled(enabled)

    @override
    def apply(self, config: BaseAppConfig) -> None:
        super().apply(config)

        config = cast(AppConfig, config)
        config.language = self.__language_box.getCurrentValue()
        config.show_toast = self.__show_toast_box.isChecked()
        config.toast_position = self.__toast_position_box.getCurrentValue()
        config.toast_offset_taskbar = self.__toast_offset_taskbar_box.isChecked()
