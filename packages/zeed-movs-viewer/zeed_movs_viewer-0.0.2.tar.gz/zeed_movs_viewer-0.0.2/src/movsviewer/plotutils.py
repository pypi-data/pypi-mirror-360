from collections import defaultdict
from datetime import date
from datetime import timedelta
from itertools import accumulate
from operator import attrgetter
from typing import TYPE_CHECKING

from guilib.chartslider.chartslider import ChartSlider
from guilib.chartwidget.model import Column
from guilib.chartwidget.model import ColumnHeader
from guilib.chartwidget.model import ColumnProto
from guilib.chartwidget.model import Info
from guilib.chartwidget.model import InfoProto
from guilib.qwtplot.plot import Plot
from movslib.reader import read
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from collections.abc import Iterable
    from decimal import Decimal

    from guilib.chartwidget.viewmodel import SortFilterViewModel
    from movslib.model import Row
    from movslib.model import Rows


def _acc_reset_by_year(rows: 'Rows') -> 'Iterable[tuple[date, Decimal]]':
    def func(a: tuple[date, 'Decimal'], b: 'Row') -> tuple[date, 'Decimal']:
        if b.date.year != a[0].year:
            return b.date, b.money

        return b.date, a[1] + b.money

    it = iter(sorted(rows, key=attrgetter('date')))
    head = next(it)
    return accumulate(it, func, initial=(head.date, head.money))


def _acc(rows: 'Rows') -> 'Iterable[tuple[date, Decimal]]':
    def func(a: tuple[date, 'Decimal'], b: 'Row') -> tuple[date, 'Decimal']:
        return b.date, a[1] + b.money

    it = iter(sorted(rows, key=attrgetter('date')))
    head = next(it)
    return accumulate(it, func, initial=(head.date, head.money))


def load_infos(*fn_names: tuple[str, str]) -> list[InfoProto]:
    tmp = defaultdict[date, list[ColumnProto]](list)
    for fn, name in fn_names:
        _, rows = read(fn, name)

        ch = ColumnHeader(rows.name, '€')
        for d, m in _acc(rows):
            tmp[d].append(Column(ch, m))

        ch_year = ColumnHeader(f'{rows.name} (by year)', '€')
        for d, m in _acc_reset_by_year(rows):
            tmp[d].append(Column(ch_year, m))

    sorted_days = sorted(tmp)

    # add +/- 1 months of padding
    ret: list[InfoProto] = []
    ret.append(Info(sorted_days[0] - timedelta(days=30), []))
    ret.extend(Info(d, tmp[d]) for d in sorted_days)
    ret.append(Info(sorted_days[-1] + timedelta(days=30), []))

    return ret


class PlotAndSliderWidget(QWidget):
    """Composition of a Plot and a (Chart)Slider."""

    def __init__(
        self, model: 'SortFilterViewModel', parent: QWidget | None
    ) -> None:
        super().__init__(parent)

        plot = Plot(model, self)
        chart_slider = ChartSlider(model, self, dates_column=0)

        layout = QVBoxLayout(self)
        layout.addWidget(plot)
        layout.addWidget(chart_slider)
        self.setLayout(layout)

        chart_slider.start_date_changed.connect(plot.start_date_changed)
        chart_slider.end_date_changed.connect(plot.end_date_changed)
