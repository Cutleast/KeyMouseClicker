"""
Copyright (c) Cutleast
"""

from typing import override

from cutleast_core_lib.core.utilities.updater import Updater
from cutleast_core_lib.ui.widgets.about_dialog import AboutDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox

from core.config.app_config import AppConfig
from core.config.autoclicker_config import AutoclickerConfig
from licenses import LICENSES

from .autoclicker.autoclicker_widget import AutoclickerWidget
from .menubar import MenuBar
from .settings.settings_dialog import SettingsDialog
from .statusbar import StatusBar


class MainWindow(QMainWindow):
    """
    Main window of the application.
    """

    __app_config: AppConfig
    __autoclicker_config: AutoclickerConfig

    __menu_bar: MenuBar
    __main_widget: AutoclickerWidget
    __status_bar: StatusBar

    def __init__(
        self, app_config: AppConfig, autoclicker_config: AutoclickerConfig
    ) -> None:
        super().__init__()

        self.__app_config = app_config
        self.__autoclicker_config = autoclicker_config

        self.__init_ui()

        self.__menu_bar.settings_signal.connect(self.__open_settings)
        self.__menu_bar.updater_signal.connect(self.__check_for_updates)
        self.__menu_bar.about_signal.connect(self.__show_about)
        self.__menu_bar.about_qt_signal.connect(self.__show_about_qt)
        self.__menu_bar.exit_signal.connect(self.close)

    def __init_ui(self) -> None:
        self.__init_menu_bar()
        self.__init_main_widget()
        self.__init_status_bar()

    def __init_menu_bar(self) -> None:
        self.__menu_bar = MenuBar()
        self.setMenuBar(self.__menu_bar)

    def __init_main_widget(self) -> None:
        self.__main_widget = AutoclickerWidget(
            self.__app_config, self.__autoclicker_config, self
        )
        self.setCentralWidget(self.__main_widget)

    def __init_status_bar(self) -> None:
        self.__status_bar = StatusBar(self.__app_config.log_visible)
        self.setStatusBar(self.__status_bar)

    @override
    def closeEvent(self, event: QCloseEvent) -> None:
        if not self.isEnabled():  # Do not exit while the window is disabled
            return event.ignore()

        self.__main_widget.save_config()

        event.accept()

    def __open_settings(self) -> None:
        SettingsDialog(self.__app_config).exec()

    def __check_for_updates(self) -> None:
        upd = Updater.get()
        if upd.is_update_available():
            upd.run()
        else:
            messagebox = QMessageBox(self)
            messagebox.setWindowTitle(self.tr("No Updates Available"))
            messagebox.setText(self.tr("There are no updates available."))
            messagebox.setTextFormat(Qt.TextFormat.RichText)
            messagebox.setIcon(QMessageBox.Icon.Information)
            messagebox.exec()

    def __show_about(self) -> None:
        from app import App

        AboutDialog(
            app_name=App.APP_NAME,
            app_version=App.APP_VERSION,
            app_icon=App.get().windowIcon(),
            app_license="MIT License",
            licenses=LICENSES,
            parent=self,
        ).exec()

    def __show_about_qt(self) -> None:
        QMessageBox.aboutQt(self, self.tr("About Qt"))
