from dataclasses import fields
from datetime import date
from decimal import Decimal
from operator import iadd
from operator import isub
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Self
from typing import cast
from typing import override

from guilib.searchsheet.model import SearchableModel
from movslib.model import ZERO
from movslib.model import Row
from movslib.model import Rows
from movslib.reader import read
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtCore import QItemSelectionModel
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import QObject
from PySide6.QtCore import QPersistentModelIndex
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush
from PySide6.QtGui import QColor

if TYPE_CHECKING:
    from PySide6.QtWidgets import QStatusBar


FIELD_NAMES = [field.name for field in fields(Row)]

T_FIELDS = date | Decimal | None | str


def _abs(row: Row) -> Decimal:
    if row.addebiti is not None:
        return -row.addebiti
    if row.accrediti is not None:
        return row.accrediti
    return ZERO


T_INDEX = QModelIndex | QPersistentModelIndex


_INDEX = QModelIndex()


class ViewModel(QAbstractTableModel):
    def __init__(self, data: Rows, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._set_data(data)

    def _set_data(self, data: Rows) -> None:
        self._data = data
        abs_data = sorted([_abs(row) for row in data])
        self._min = abs_data[0] if abs_data else ZERO
        self._max = abs_data[-1] if abs_data else ZERO

    @override
    def rowCount(self, _parent: T_INDEX = _INDEX) -> int:
        return len(self._data)

    @override
    def columnCount(self, _parent: T_INDEX = _INDEX) -> int:
        return len(FIELD_NAMES)

    @override
    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation != Qt.Orientation.Horizontal:
            return None

        return FIELD_NAMES[section]

    @override
    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> T_FIELDS | QBrush | None:
        column = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DisplayRole:
            return str(getattr(self._data[row], FIELD_NAMES[column]))

        if role == Qt.ItemDataRole.BackgroundRole:
            max_, min_, val = self._max, self._min, _abs(self._data[row])
            perc = (
                (val - min_) / (max_ - min_) if max_ != min_ else Decimal('0.5')
            )

            hue = int(perc * 120)  # 0..359 ; red=0, green=120
            saturation = 223  # 0..255
            lightness = 159  # 0..255

            return QBrush(QColor.fromHsl(hue, saturation, lightness))

        if role == Qt.ItemDataRole.UserRole:
            return cast(
                'T_FIELDS', getattr(self._data[row], FIELD_NAMES[column])
            )

        return None

    @override
    def sort(
        self, index: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder
    ) -> None:
        def key(row: Row) -> date | Decimal | str:  # T_FIELDS - None
            e: T_FIELDS = getattr(row, FIELD_NAMES[index])
            if e is None:
                return ZERO
            return e

        self.layoutAboutToBeChanged.emit()
        try:
            self._data.sort(
                key=key, reverse=order == Qt.SortOrder.DescendingOrder
            )
        finally:
            self.layoutChanged.emit()

    def load(self, data: Rows) -> None:
        self.beginResetModel()
        try:
            self._set_data(data)
        finally:
            self.endResetModel()

    @property
    def name(self) -> str:
        return self._data.name


class SortFilterViewModel(SearchableModel):
    def __init__(self, data_path: str) -> None:
        super().__init__(ViewModel(Rows('')))
        self.data_path = data_path
        self.reload()

    @override
    def sourceModel(self) -> ViewModel:
        return cast('ViewModel', super().sourceModel())

    @override
    def sort(
        self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder
    ) -> None:
        self.sourceModel().sort(column, order)

    def selection_changed(
        self, selection_model: QItemSelectionModel, statusbar: 'QStatusBar'
    ) -> None:
        addebiti_index = FIELD_NAMES.index('addebiti')
        accrediti_index = FIELD_NAMES.index('accrediti')

        bigsum = 0
        for column, iop in ((addebiti_index, isub), (accrediti_index, iadd)):
            for index in selection_model.selectedRows(column):
                data = index.data(Qt.ItemDataRole.UserRole)
                if data is not None:
                    bigsum = iop(bigsum, data)

        statusbar.showMessage(f'⅀ = {bigsum}')

    def reload(self) -> Self:
        _, data = read(self.data_path, Path(self.data_path).stem)
        self.sourceModel().load(data)
        return self

    @property
    def name(self) -> str:
        return self.sourceModel().name
