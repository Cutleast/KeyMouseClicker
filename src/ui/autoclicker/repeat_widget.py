"""
Copyright (c) Cutleast
"""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QRadioButton, QSpinBox, QWidget


class RepeatWidget(QWidget):
    """
    Widget for setting the repeat options.
    """

    changed = Signal()
    """Signal emitted when the repeat options change."""

    __infinite_button: QRadioButton
    __limited_button: QRadioButton
    __repeat_count_box: QSpinBox

    def __init__(
        self, initial_repeat_count: int, parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)

        self.__init_ui()
        self.__infinite_button.toggled.connect(lambda _: self.__on_toggle())

        if initial_repeat_count == -1:
            self.__infinite_button.setChecked(True)
        else:
            self.__limited_button.setChecked(True)
            self.__repeat_count_box.setValue(initial_repeat_count)

        self.__limited_button.toggled.connect(lambda _: self.changed.emit())
        self.__repeat_count_box.valueChanged.connect(lambda _: self.changed.emit())

    def __init_ui(self) -> None:
        glayout = QGridLayout()
        self.setLayout(glayout)

        self.__infinite_button = QRadioButton(self.tr("Repeat until stopped"))
        glayout.addWidget(self.__infinite_button, 0, 0, 1, 3)

        self.__limited_button = QRadioButton(self.tr("Repeat"))
        glayout.addWidget(self.__limited_button, 1, 0)

        self.__repeat_count_box = QSpinBox()
        self.__repeat_count_box.setRange(1, 1_000_000_000)
        glayout.addWidget(self.__repeat_count_box, 1, 1)

        glayout.addWidget(QLabel(self.tr("times")), 1, 2)

    def __on_toggle(self) -> None:
        self.__repeat_count_box.setEnabled(self.__limited_button.isChecked())

    def get_current_repeat_count(self) -> int:
        """
        Returns the current repeat count.

        Returns:
            int: The current repeat count.
        """

        if self.__infinite_button.isChecked():
            return -1
        else:
            return self.__repeat_count_box.value()
