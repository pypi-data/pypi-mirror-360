# pyright: reportUnknownMemberType=false
import typing
from typing import Callable, Literal, override
import pprint
from dataclasses import dataclass

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QHBoxLayout, QTextEdit, QWidget, QVBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from seaborn import FacetGrid
import pandas as pd

from ..data.dataenums import NumericConversion
from ..guihelper import build_layout

if typing.TYPE_CHECKING:
    from ..dataexplorer import DataExplorer
    from ..data.datamodel import DataStore

FILTER_DISPLAY_STARTING_TEXT = "Filters: "

MARKERS = [
    " ",
    ".",
    ",",
    "o",
    "v",
    "^",
    "<",
    ">",
    "1",
    "2",
    "3",
    "4",
    "8",
    "s",
    "p",
    "P",
    "*",
    "h",
    "H",
    "+",
    "x",
    "X",
    "D",
    "d",
]

LINE_STYLES = ["-", "--", "-.", ":", "None"]

VIOLIN_INNER = ["box", "quart", "point", "stick"]

HIST_PLOT_STATISTICS = ["count", "frequency", "proportion", "percent", "density"]

COUNT_PLOT_STATISTICS = ["count", "proportion", "percent"]

CORREL_STATISTICS = ["pearson", "kendall", "spearman"]

COLOR_PALETTES = {
    "qualitative": [
        "tab10",
        "deep",
        "muted",
        "pastel",
        "bright",
        "dark",
        "colorblind",
        "tab20",
        "tab20b",
        "tab20c",
    ],
    "circular": ["hls", "husl"],
    "perceptually_uniform": [
        "rocket",
        "mako",
        "flare",
        "crest",
        "viridis",
        "plasma",
        "inferno",
        "magma",
        "cividis",
    ],
    "diverging": ["vlag", "icefire", "coolwarm", "bwr", "seismic"],
}

PALETTE_TYPES = list(COLOR_PALETTES.keys())


@typing.final
@dataclass
class TickParams:
    axis: Literal["x", "y"]
    rotation: int
    grid_colour: str
    grid_alpha: float

    def to_kwargs(self) -> dict[str, int | str | float]:
        return {
            "axis": self.axis,
            "labelrotation": self.rotation,
            "grid_color": self.grid_colour,
            "grid_alpha": self.grid_alpha,
        }


@typing.final
class EmbeddedDynamicPlot(QWidget):
    filter_display: QTextEdit
    plot: QWidget
    figure: Figure

    def __init__(
        self,
        dataexplorer: "DataExplorer",
        datastore: "DataStore",
        name: str,
        parent: "PlottingDialog",
    ):
        super().__init__()
        self.setWindowTitle(name)
        self.debug = dataexplorer.debug
        self.error = dataexplorer.error
        self.dataexplorer = dataexplorer
        self._parent = parent
        self.name = name
        self.resize(1200, 1200)
        self.setStyleSheet(dataexplorer.stylesheet)
        self.datastore = datastore
        self._layout = QHBoxLayout(self)
        self.filter_display = QTextEdit()
        self.filter_display.setReadOnly(True)
        self.filter_display.setText(self._generate_filter_text())
        self.dataexplorer.owned_widgets.append(self)

        self.plot_subwidget = self.dataexplorer.get_widget()
        self.figure = plt.figure()
        self.plot = FigureCanvas(plt.figure())

        self.plot_toolbar: QWidget = NavigationToolbar2QT(self.plot)

        self.plot_vbox = QVBoxLayout(self.plot_subwidget)

        build_layout(self.plot_vbox, [self.plot_toolbar, self.plot])

        self._layout.addWidget(self.plot_subwidget, stretch=1)
        self._layout.addWidget(self.filter_display)

        self.show()

    def update_dynamic_widget(self, plot: Figure | FacetGrid):
        self._draw_plot(plot)
        self.filter_display.setText(self._generate_filter_text())

    def _draw_plot(self, plot: Figure | FacetGrid):
        old_plot = self.plot
        old_toolbar = self.plot_toolbar
        old_figure = self.figure
        old_plot_subwidget = self.plot_subwidget
        if isinstance(plot, Figure):
            self.figure = plot
        else:
            self.figure = plot.figure

        plt.close(old_figure)
        self.plot = FigureCanvas(self.figure)
        self.plot_toolbar = NavigationToolbar2QT(self.plot)

        self.plot_subwidget = self.dataexplorer.get_widget()
        self.plot_vbox = QVBoxLayout(self.plot_subwidget)
        build_layout(self.plot_vbox, [self.plot_toolbar, self.plot])
        _ = self._layout.replaceWidget(old_plot_subwidget, self.plot_subwidget)
        old_plot.deleteLater()
        old_toolbar.deleteLater()
        old_plot_subwidget.deleteLater()
        self.update()
        self.debug(f"{self.name} updated!")

    def _generate_filter_text(self) -> str:
        filter_text = FILTER_DISPLAY_STARTING_TEXT
        for column in self.datastore.filters:
            filter_text += f"<br>- {column}"  # Newline + bullet list start
            for fs in self.datastore.filters[column]:
                if fs.active:
                    filter_text += pprint.pformat(fs.filter_value)
        return filter_text

    @typing.override
    def closeEvent(self, event: QCloseEvent):
        self.dataexplorer.owned_widgets.remove(self)
        self._parent.delete_dynamic_plot()
        return super().closeEvent(event)


class PlottingDialog(QWidget):
    dynamic_plot_widget: EmbeddedDynamicPlot | None = None
    dynamic_callback_id: int = -1
    plotting_data: pd.DataFrame
    palette_type: str = PALETTE_TYPES[0]

    def __init__(self, dataexplorer: "DataExplorer", datastore: "DataStore", name: str):
        super().__init__()
        self.setWindowTitle(f"{name} Plotting Dialog")
        self.dataexplorer: "DataExplorer" = dataexplorer
        self.debug: Callable[[str], None] = dataexplorer.debug
        self.error: Callable[[str], None] = dataexplorer.error
        self.datastore: "DataStore" = datastore

        self._generate_plotting_data()
        self.dataexplorer.owned_widgets.append(self)
        self._layout: QVBoxLayout = QVBoxLayout(self)
        self.setStyleSheet(dataexplorer.stylesheet)
        self.resize(600, 800)

    def cat_name(self, col_name: str):
        return col_name + "_categorical_"

    def _generate_plotting_data(self):
        self.plotting_data = self.datastore.filtered_data.copy()
        cat_name = self.cat_name

        for column, nc in self.datastore.numeric_to_categorical.items():
            self.debug(f"{column} {nc.conversion} {nc.value}")
            match nc.conversion:
                case NumericConversion.AS_CATEGORY:
                    self.plotting_data[cat_name(column)] = self.plotting_data[column]
                case NumericConversion.BINNED:
                    if not isinstance(nc.value, int):
                        self.error("Incorrect type for numeric->categorical bin_N")
                        return
                    self.plotting_data[cat_name(column)] = pd.cut(
                        self.plotting_data[column], nc.value
                    )
                case NumericConversion.BIN_WIDTH:
                    if not isinstance(nc.value, list) or all(
                        isinstance(value, float) for value in nc.value
                    ):
                        self.error("Incorrect type for numeric->categorical bin width")
                        return
                    self.plotting_data[cat_name(column)] = pd.cut(
                        self.plotting_data[column], nc.value
                    )

    def get_categorical_column_name(self, col_name: str):
        if col_name == "":
            return None
        else:
            cat_name = self.cat_name(col_name)
            if cat_name in self.plotting_data.columns:
                return cat_name
            else:
                return col_name

    def get_palette(self):
        match self.palette_type:
            case "qualitative":
                return self.dataexplorer.plotter.qualitative_palette
            case "circular":
                return self.dataexplorer.plotter.circular_palette
            case "perceptually_uniform":
                return self.dataexplorer.plotter.perceptually_uniform_palette
            case "diverging":
                return self.dataexplorer.plotter.diverging_palette
            case _:
                return ""

    def on_plot(self):
        self._generate_plotting_data()

    def plot(self): ...

    def dynamic_plot(self): ...

    def redraw_dynamic_plot(self): ...

    def delete_dynamic_plot(self): ...

    def on_widget_change(self): ...

    @override
    def closeEvent(self, event: QCloseEvent) -> None:
        self.dataexplorer.owned_widgets.remove(self)
        return super().closeEvent(event)
