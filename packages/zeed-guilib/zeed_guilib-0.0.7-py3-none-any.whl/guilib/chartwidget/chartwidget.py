from typing import TYPE_CHECKING

from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from guilib.chartslider.chartslider import ChartSlider
from guilib.chartwidget.chartview import ChartView

if TYPE_CHECKING:
    from guilib.chartwidget.modelgui import SeriesModelFactory
    from guilib.chartwidget.viewmodel import SortFilterViewModel


class ChartWidget(QWidget):
    """Composition of a ChartView and a slider."""

    def __init__(
        self,
        model: 'SortFilterViewModel',
        parent: QWidget | None,
        factory: 'SeriesModelFactory',
        precision: str = '%B %Y',
    ) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        chart_view = ChartView(model, self, factory, precision)
        chart_slider = ChartSlider(model, self)
        layout.addWidget(chart_view)
        layout.addWidget(chart_slider)
        self.setLayout(layout)

        chart_slider.start_date_changed.connect(chart_view.start_date_changed)
        chart_slider.end_date_changed.connect(chart_view.end_date_changed)
