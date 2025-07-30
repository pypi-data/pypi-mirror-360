from typing import TYPE_CHECKING

from movsvalidator.movsvalidator import validate
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from movsviewer.settings import Settings


class Validator:
    def __init__(self, parent: QWidget, settings: 'Settings') -> None:
        self.parent = parent
        self.settings = settings

    def validate(self) -> bool:
        for fn in self.settings.data_paths:
            messages: list[str] = []
            if not validate(fn, messages):
                button = QMessageBox.warning(
                    self.parent,
                    f'{fn} seems has some problems!',
                    '\n'.join(messages),
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                )
                return button is QMessageBox.StandardButton.Yes
        return True
