"""
Copyright (c) Cutleast
"""

from cutleast_core_lib.test.base_test import BaseTest
from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from core.config.app_config import AppConfig
from resources_rc import qt_resource_data as qt_resource_data


class TestAppLanguage(BaseTest):
    """
    Tests `core.config.app_config.AppConfig.AppLanguage`.
    """

    def test_all_langs_can_be_loaded(self, qtbot: QtBot) -> None:
        """
        Tests that all required .qm files are bundled and can be loaded by the
        QTranslator.
        """

        # given
        qm_files: list[str] = [
            f":/loc/{lang.value}.qm"
            for lang in AppConfig.AppLanguage
            if lang not in [AppConfig.AppLanguage.System, AppConfig.AppLanguage.English]
        ]
        translator = QTranslator(QApplication.instance())

        # then
        for qm_file in qm_files:
            assert translator.load(qm_file), (
                f"Failed to load '{qm_file}'! Make sure to add "
                f'"<file>{qm_file.removeprefix(":/")}</file>" to ./res/resources.qrc!'
            )
