from abc import abstractmethod
from dataclasses import dataclass
from datetime import UTC
from datetime import date
from datetime import datetime
from datetime import time
from decimal import Decimal
from itertools import accumulate
from itertools import chain
from itertools import groupby
from typing import TYPE_CHECKING
from typing import NamedTuple
from typing import Self
from typing import cast
from typing import override

from guilib.chartwidget.chartwidget import ChartWidget
from guilib.chartwidget.model import Column
from guilib.chartwidget.model import ColumnHeader
from guilib.chartwidget.model import Info
from guilib.chartwidget.model import InfoProto
from guilib.chartwidget.modelgui import SeriesModel
from guilib.chartwidget.modelgui import SeriesModelUnit
from guilib.chartwidget.viewmodel import SortFilterViewModel
from guilib.dates.converters import date2days
from guilib.dates.converters import date2QDateTime
from movslib.model import ZERO
from movslib.reader import read
from PySide6.QtCharts import QBarCategoryAxis
from PySide6.QtCharts import QBarSeries
from PySide6.QtCharts import QBarSet
from PySide6.QtCharts import QCategoryAxis
from PySide6.QtCharts import QChart
from PySide6.QtCharts import QLineSeries
from PySide6.QtCharts import QValueAxis
from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Sequence

    from movslib.model import Row
    from PySide6.QtWidgets import QGraphicsSceneMouseEvent
    from PySide6.QtWidgets import QGraphicsSceneWheelEvent


class Point(NamedTuple):
    data: date
    mov: Decimal


def to_point(row: 'Row') -> Point:
    if row.accrediti is not None:
        mov = row.accrediti
    elif row.addebiti is not None:
        mov = -row.addebiti
    else:
        mov = ZERO
    return Point(row.date, mov)


def build_series(
    data: 'Sequence[Row]', epoch: date = date(2008, 1, 1)
) -> QLineSeries:
    data = sorted(data, key=lambda row: row.date)

    series = QLineSeries()
    series.setName('data')

    # add start and today
    moves = chain(
        (Point(epoch, ZERO),),
        map(to_point, data),
        (Point(datetime.now(tz=UTC).date(), ZERO),),
    )

    def sumy(a: Point, b: Point) -> Point:
        return Point(b.data, a.mov + b.mov)

    summes = accumulate(moves, func=sumy)

    floats = (
        (datetime.combine(data, time()).timestamp() * 1000, mov)
        for data, mov in summes
    )

    # step the movements
    last_mov: Decimal | None = None
    for ts, mov in floats:
        if last_mov is not None:
            series.append(ts, float(last_mov))
        series.append(ts, float(mov))
        last_mov = mov

    return series


def build_group_by_year_series(
    data: 'Sequence[Row]',
) -> tuple[QBarSeries, QBarCategoryAxis]:
    data = sorted(data, key=lambda row: row.date)

    axis_x = QBarCategoryAxis()

    series = QBarSeries()
    barset = QBarSet('group by year')
    series.append(barset)

    def sum_points(points: 'Iterable[Point]') -> Decimal:
        return sum((point.mov for point in points), start=ZERO)

    years = []
    for year, points in groupby(
        map(to_point, data), lambda point: point.data.year
    ):
        barset.append(float(sum_points(points)))
        years.append(f'{year}')
    axis_x.setCategories(years)

    return series, axis_x


def build_group_by_month_series(
    data: 'Sequence[Row]',
) -> tuple[QBarSeries, QBarCategoryAxis]:
    data = sorted(data, key=lambda row: row.date)

    axis_x = QBarCategoryAxis()

    series = QBarSeries()
    barset = QBarSet('group by month')
    series.append(barset)

    def sum_points(points: 'Iterable[Point]') -> Decimal:
        return sum((point.mov for point in points), start=ZERO)

    year_months = []
    for (year, month), points in groupby(
        map(to_point, data), lambda point: (point.data.year, point.data.month)
    ):
        barset.append(float(sum_points(points)))
        year_months.append(f'{year}-{month}')
    axis_x.setCategories(year_months)

    return series, axis_x


class Chart(QChart):
    def __init__(self, data: 'Sequence[Row]') -> None:
        super().__init__()

        def years(data: 'Sequence[Row]') -> list[date]:
            if not data:
                return []
            data = sorted(data, key=lambda row: row.date)
            start = data[0].date.year - 1
            end = data[-1].date.year + 1
            return [date(year, 1, 1) for year in range(start, end + 1)]

        def months(data: 'Sequence[Row]', step: int = 1) -> list[date]:
            if not data:
                return []
            data = sorted(data, key=lambda row: row.date)
            start = data[0].date.year - 1
            end = data[-1].date.year + 1
            return [
                date(year, month, 1)
                for year in range(start, end + 1)
                for month in range(1, 13, step)
            ]

        def reset_axis_x_labels() -> None:
            if True:
                pass

        def ts(d: date) -> float:
            return (
                datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp() * 1000
            )

        axis_y = QValueAxis()
        axis_y.setTickType(QValueAxis.TickType.TicksDynamic)
        axis_y.setTickAnchor(0.0)
        axis_y.setTickInterval(10000.0)
        axis_y.setMinorTickCount(9)
        self.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        axis_x = QCategoryAxis()
        axis_x.setLabelsPosition(
            QCategoryAxis.AxisLabelsPosition.AxisLabelsPositionOnValue
        )
        for dt in months(data, 6):
            axis_x.append(f'{dt}', ts(dt))
        self.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        series = build_series(data)
        self.addSeries(series)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        group_by_year_series, axis_x_years = build_group_by_year_series(data)
        self.addSeries(group_by_year_series)
        self.addAxis(axis_x_years, Qt.AlignmentFlag.AlignBottom)
        group_by_year_series.attachAxis(axis_y)

        group_by_month_series, axis_x_months = build_group_by_month_series(data)
        self.addSeries(group_by_month_series)
        self.addAxis(axis_x_months, Qt.AlignmentFlag.AlignBottom)
        group_by_month_series.attachAxis(axis_y)

    @override
    def wheelEvent(self, event: 'QGraphicsSceneWheelEvent') -> None:
        super().wheelEvent(event)
        y = event.delta()
        if y < 0:
            self.zoom(0.75)  # zoomOut is ~ .5
        elif y > 0:
            self.zoomIn()

    @override
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mousePressEvent(event)
        event.accept()

    @override
    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseMoveEvent(event)

        x_curr, y_curr = cast('tuple[float, float]', event.pos().toTuple())
        x_prev, y_prev = cast('tuple[float, float]', event.lastPos().toTuple())
        self.scroll(x_prev - x_curr, y_curr - y_prev)


MONEY_HEADER = ColumnHeader('money', '€')


@dataclass
class SMFShared:
    x_min: date
    x_max: date
    y_min: Decimal
    y_max: Decimal


class SMFHelper:
    def __init__(self, line_series: QLineSeries, shared: SMFShared) -> None:
        self.line_series = line_series
        self.shared = shared
        self.acc = 0.0
        self.last: date | None = None

    @abstractmethod
    def step(
        self, when: date, when_d: int, howmuch: Decimal, howmuch_f: float
    ) -> None: ...


class SMFMoney(SMFHelper):
    @override
    def __init__(self, line_series: QLineSeries, shared: SMFShared) -> None:
        super().__init__(line_series, shared)
        self.line_series.setName('money')

    @override
    def step(
        self,
        when: date,  # @UnusedVariable
        when_d: int,
        howmuch: Decimal,
        howmuch_f: float,
    ) -> None:
        self.line_series.append(when_d, 0)
        # TODO: fix hover to deal with a variable number of items in series
        self.line_series.append(when_d, howmuch_f)

        self.shared.y_min = min(howmuch, self.shared.y_min)
        self.shared.y_max = max(self.shared.y_max, howmuch)


class SMFMoneyAcc(SMFHelper):
    @override
    def __init__(self, line_series: QLineSeries, shared: SMFShared) -> None:
        super().__init__(line_series, shared)
        self.line_series.setName('money acc')

    @override
    def step(
        self,
        when: date,  # @UnusedVariable
        when_d: int,
        howmuch: Decimal,  # @UnusedVariable
        howmuch_f: float,
    ) -> None:
        self.line_series.append(when_d, self.acc)
        self.acc += howmuch_f
        self.line_series.append(when_d, self.acc)

        if self.acc < self.shared.y_min:
            self.shared.y_min = Decimal(self.acc)
        if self.shared.y_max < self.acc:
            self.shared.y_max = Decimal(self.acc)


class SMFMoneyByMonth(SMFHelper):
    @override
    def __init__(self, line_series: QLineSeries, shared: SMFShared) -> None:
        super().__init__(line_series, shared)
        self.line_series.setName('money by month')

    @override
    def step(
        self,
        when: date,
        when_d: int,
        howmuch: Decimal,  # @UnusedVariable
        howmuch_f: float,
    ) -> None:
        # money_by_month
        self.line_series.append(when_d, self.acc)
        if self.last is None or self.last.month != when.month:
            self.acc = 0.0
        else:
            self.acc += howmuch_f
        self.line_series.append(when_d, self.acc)
        self.last = when

        if self.acc < self.shared.y_min:
            self.shared.y_min = Decimal(self.acc)
        if self.shared.y_max < self.acc:
            self.shared.y_max = Decimal(self.acc)


class SMFMoneyByYear(SMFHelper):
    @override
    def __init__(self, line_series: QLineSeries, shared: SMFShared) -> None:
        super().__init__(line_series, shared)
        self.line_series.setName('money by year')

    @override
    def step(
        self,
        when: date,
        when_d: int,
        howmuch: Decimal,  # @UnusedVariable
        howmuch_f: float,
    ) -> None:
        # money_by_year
        self.line_series.append(when_d, self.acc)
        if self.last is None or self.last.year != when.year:
            self.acc = 0.0
        else:
            self.acc += howmuch_f
        self.line_series.append(when_d, self.acc)
        self.last = when

        if self.acc < self.shared.y_min:
            self.shared.y_min = Decimal(self.acc)
        if self.shared.y_max < self.acc:
            self.shared.y_max = Decimal(self.acc)


def series_model_factory(infos: 'Sequence[InfoProto]') -> 'SeriesModel':
    """Extract money from info; accumulate and step; group by month / year."""
    shared = SMFShared(
        x_min=date.max,
        x_max=date.min,
        y_min=Decimal('inf'),
        y_max=-Decimal('inf'),
    )

    money = SMFMoney(QLineSeries(), shared)
    money_acc = SMFMoneyAcc(QLineSeries(), shared)
    money_by_month = SMFMoneyByMonth(QLineSeries(), shared)
    money_by_year = SMFMoneyByYear(QLineSeries(), shared)

    for info in infos:
        when = info.when
        howmuch = info.howmuch(MONEY_HEADER)
        if howmuch is None:
            continue

        shared.x_min = min(when, shared.x_min)
        shared.x_max = max(when, shared.x_max)

        when_d = date2days(when)
        howmuch_f = float(howmuch)

        money.step(when, when_d, howmuch, howmuch_f)
        money_acc.step(when, when_d, howmuch, howmuch_f)
        money_by_month.step(when, when_d, howmuch, howmuch_f)
        money_by_year.step(when, when_d, howmuch, howmuch_f)

    return SeriesModel(
        [
            money.line_series,
            money_acc.line_series,
            money_by_month.line_series,
            money_by_year.line_series,
        ],
        date2QDateTime(shared.x_min),
        date2QDateTime(shared.x_max),
        float(shared.y_min),
        float(shared.y_max),
        SeriesModelUnit.EURO,
    )


class ChartWidgetWrapper(ChartWidget):
    def __init__(self, data_path: str) -> None:
        self.data_path = data_path
        self.model = SortFilterViewModel()
        super().__init__(self.model, None, series_model_factory, '%d/%m/%Y')
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.reload()

    def reload(self) -> Self:
        _, data = read(self.data_path)
        # convert data to infos
        infos = [
            Info(row.date, [Column(MONEY_HEADER, row.money)])
            for row in sorted(data, key=lambda row: row.date)
        ]
        self.model.update(infos)
        return self
