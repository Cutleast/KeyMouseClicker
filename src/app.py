"""
Copyright (c) Cutleast
"""

from argparse import Namespace
from typing import Optional, cast, override

from cutleast_core_lib.base_app import BaseApp
from cutleast_core_lib.core.utilities.localisation import detect_system_locale
from cutleast_core_lib.core.utilities.singleton import Singleton
from PySide6.QtCore import QTranslator
from PySide6.QtGui import QIcon

from core.config.app_config import AppConfig
from core.config.autoclicker_config import AutoclickerConfig
from ui.main_window import MainWindow
from ui.utilities.theme_manager import ThemeManager


class App(BaseApp, Singleton):
    """
    Main application class.
    """

    APP_NAME: str = "KeyMouseClicker"
    APP_VERSION: str = "development"

    __autoclicker_config: AutoclickerConfig

    def __init__(self, args: Namespace) -> None:
        Singleton.__init__(self)
        super().__init__(args)

    @override
    def _init(self) -> None:
        self.setApplicationName(App.APP_NAME)
        self.setApplicationVersion(App.APP_VERSION)
        self.setWindowIcon(QIcon(":/icons/icon.png"))

        super()._init()

    @override
    def _load_app_config(self) -> AppConfig:
        return AppConfig.load(self.config_path)

    @override
    def _get_theme_manager(self) -> Optional[ThemeManager]:
        return ThemeManager(self.app_config.accent_color, self.app_config.ui_mode)

    @override
    def _init_main_window(self) -> MainWindow:
        self.__load_translation()
        self.__autoclicker_config = AutoclickerConfig.load(self.config_path)

        return MainWindow(cast(AppConfig, self.app_config), self.__autoclicker_config)

    def __load_translation(self) -> None:
        """
        Loads translation for the configured language and installs the translator into
        the app.
        """

        translator = QTranslator(self)

        app_config: AppConfig = cast(AppConfig, self.app_config)

        language: str
        if app_config.language == AppConfig.AppLanguage.System:
            language = detect_system_locale() or "en_US"
        else:
            language = app_config.language.value

        if language != "en_US":
            res_file: str = f":/loc/{language}.qm"
            if not translator.load(res_file):
                self.log.error(
                    f"Failed to load localisation for {language} from '{res_file}'."
                )
            else:
                self.installTranslator(translator)
                self.log.info(f"Loaded localisation for {language}.")

    @override
    @classmethod
    def get_repo_owner(cls) -> Optional[str]:
        return "Cutleast"

    @override
    @classmethod
    def get_repo_name(cls) -> Optional[str]:
        return "KeyMouseClicker"

    @override
    @classmethod
    def get_repo_branch(cls) -> Optional[str]:
        return "main"
