# pyright: reportUnknownMemberType=false, reportArgumentType=false
from enum import Enum, auto
from functools import partial
import traceback
from math import ceil
from pprint import pformat
import typing
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import matplotlib
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from numpy import ndarray
import seaborn as sns
from superqt import QCollapsible, QLabeledDoubleSlider

from ..guihelper import (
    MultiSelectComboBox,
    build_grid_layout,
    build_layout_with_callbacks,
    get_label_widget_row_callback,
)

from .foundation import EmbeddedDynamicPlot, PlottingDialog, TickParams
from .foundation import (
    MARKERS,
    LINE_STYLES,
    VIOLIN_INNER,
    HIST_PLOT_STATISTICS,
    COUNT_PLOT_STATISTICS,
    CORREL_STATISTICS,
    COLOR_PALETTES,
    PALETTE_TYPES,
)

if typing.TYPE_CHECKING:
    from ..dataexplorer import DataExplorer
    from ..data.datamodel import DataStore


matplotlib.use("QtAgg")


@typing.final
class Plotter:
    plot_dialogs: dict[str, QWidget] = {}
    plot_params: dict[str, dict[str, TickParams]] = {}
    qualitative_palette: str = COLOR_PALETTES["qualitative"][0]
    circular_palette: str = COLOR_PALETTES["circular"][0]
    perceptually_uniform_palette: str = COLOR_PALETTES["perceptually_uniform"][0]
    diverging_palette: str = COLOR_PALETTES["diverging"][0]

    def __init__(self, dataexplorer: "DataExplorer"):
        self.dataexplorer = dataexplorer
        self.debug = dataexplorer.debug
        self.error = dataexplorer.error
        self.hist_dialog: HistDialog | None = None
        self.scatter_dialog: ScatterDialog | None = None
        self.cat_dialog: CatPlotDialog | None = None
        self.count_dialog: CountPlotDialog | None = None
        self.corrplot_dialog: CorrPlotDialog | None = None
        self.lineplot_dialog: LineDialog | None = None
        self.x_tick_spinbox: QDoubleSpinBox = QDoubleSpinBox(
            minimum=0.0, maximum=40.0, value=0.0, singleStep=1.0
        )
        self.y_tick_spinbox: QDoubleSpinBox = QDoubleSpinBox(
            minimum=0.0, maximum=40.0, value=0.0, singleStep=1.0
        )
        self.marker_size_spinbox: QDoubleSpinBox = QDoubleSpinBox(
            minimum=0.0, maximum=40.0, value=0.0, singleStep=1.0
        )
        self.line_width_spinbox: QDoubleSpinBox = QDoubleSpinBox(
            minimum=0.0, maximum=40.0, value=0.0, singleStep=1.0
        )
        self.title_size_spinbox: QDoubleSpinBox = QDoubleSpinBox(
            minimum=0.0, maximum=40.0, value=0.0, singleStep=1.0
        )
        self.legend_title_size_spinbox: QDoubleSpinBox = QDoubleSpinBox(
            minimum=0.0, maximum=40.0, value=0.0, singleStep=1.0
        )
        self.legend_label_size_spinbox: QDoubleSpinBox = QDoubleSpinBox(
            minimum=0.0, maximum=40.0, value=0.0, singleStep=1.0
        )
        self.axes_label_size_spinbox: QDoubleSpinBox = QDoubleSpinBox(
            minimum=0.0, maximum=40.0, value=0.0, singleStep=1.0
        )
        self.x_tick_rotation_spinbox: QSpinBox = QSpinBox(
            minimum=-180, maximum=180, value=0, singleStep=1
        )
        self.y_tick_rotation_spinbox: QSpinBox = QSpinBox(
            minimum=-180, maximum=180, value=0, singleStep=1
        )

        self.x_grid_colour_combobox: QComboBox = QComboBox()
        self.x_grid_colour_combobox.addItems(mcolors.BASE_COLORS)
        self.x_grid_alpha_slider: QLabeledDoubleSlider = QLabeledDoubleSlider()
        self.x_grid_alpha_slider.setRange(0, 1)
        self.x_grid_alpha_slider.setValue(0)
        self.y_grid_colour_combobox: QComboBox = QComboBox()
        self.y_grid_colour_combobox.addItems(mcolors.BASE_COLORS)
        self.y_grid_alpha_slider: QLabeledDoubleSlider = QLabeledDoubleSlider()
        self.y_grid_alpha_slider.setRange(0, 1)
        self.y_grid_alpha_slider.setValue(0)
        self.plot_params["tick_params"] = {}
        self.plot_params["tick_params"]["x"] = TickParams(
            axis="x",
            rotation=self.x_tick_rotation_spinbox.value(),
            grid_colour=self.x_grid_colour_combobox.currentText(),
            grid_alpha=self.x_grid_alpha_slider.value(),
        )
        self.plot_params["tick_params"]["y"] = TickParams(
            axis="y",
            rotation=self.y_tick_rotation_spinbox.value(),
            grid_colour=self.y_grid_colour_combobox.currentText(),
            grid_alpha=self.y_grid_alpha_slider.value(),
        )

        self.qualitative_palette_combobox = QComboBox()
        self.qualitative_palette_combobox.addItems(COLOR_PALETTES["qualitative"])
        self.circular_palette_combobox = QComboBox()
        self.circular_palette_combobox.addItems(COLOR_PALETTES["circular"])
        self.perceptually_uniform_palette_combobox = QComboBox()
        self.perceptually_uniform_palette_combobox.addItems(
            COLOR_PALETTES["perceptually_uniform"]
        )
        self.diverging_palette_combobox = QComboBox()
        self.diverging_palette_combobox.addItems(COLOR_PALETTES["diverging"])

        self.build_plot_settings_page()

    def histogram_plotter(self):
        datastore = self.dataexplorer.datamodel.active_dataset
        if datastore is None:
            self.error("You need a valid active dataset to do this.")
            return
        self.hist_dialog = HistDialog(self.dataexplorer, datastore)

    def scatterplot_plotter(self):
        datastore = self.dataexplorer.datamodel.active_dataset
        if datastore is None:
            self.error("You need a valid active dataset to do this.")
            return
        self.scatter_dialog = ScatterDialog(self.dataexplorer, datastore)

    def catplot_plotter(self):
        datastore = self.dataexplorer.datamodel.active_dataset
        if datastore is None:
            self.error("You need a valid active dataset to do this.")
            return
        self.cat_dialog = CatPlotDialog(self.dataexplorer, datastore)

    def countplot_plotter(self):
        datastore = self.dataexplorer.datamodel.active_dataset
        if datastore is None:
            self.error("You need a valid active dataset to do this.")
            return
        self.count_dialog = CountPlotDialog(self.dataexplorer, datastore)

    def correlmatrix_plotter(self):
        datastore = self.dataexplorer.datamodel.active_dataset
        if datastore is None:
            self.error("You need a valid active dataset to do this.")
            return
        self.corrplot_dialog = CorrPlotDialog(self.dataexplorer, datastore)

    def lineplot_plotter(self):
        datastore = self.dataexplorer.datamodel.active_dataset
        if datastore is None:
            self.error("You need a valid active dataset to do this.")
            return
        self.lineplot_dialog = LineDialog(self.dataexplorer, datastore)

    def build_plot_settings_page(self):
        layout = self.dataexplorer.gui.plot_settings_layout
        layout.setSpacing(5)
        callback = self.on_settings_change_callback
        get_label_widget_row_ = partial(
            get_label_widget_row_callback, callback=callback
        )

        title = QLabel("Plot Defaults")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("PageTitle")
        sub_label = QLabel("Overriden by plot specific settings")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        x_tick_spinbox = get_label_widget_row_("X-Axis Tick Size", self.x_tick_spinbox)
        y_tick_spinbox = get_label_widget_row_("Y-Axis Tick Size", self.y_tick_spinbox)
        marker_size_spinbox = get_label_widget_row_(
            "Marker Size", self.marker_size_spinbox
        )
        line_width_spinbox = get_label_widget_row_(
            "Line Width", self.line_width_spinbox
        )
        title_size_spinbox = get_label_widget_row_(
            "Title Size", self.title_size_spinbox
        )
        axes_label_size_spinbox = get_label_widget_row_(
            "Axes Label Size", self.axes_label_size_spinbox
        )
        legend_title_size_spinbox = get_label_widget_row_(
            "Legend Title Size", self.legend_title_size_spinbox
        )
        legend_label_size_spinbox = get_label_widget_row_(
            "X-Axis Tick Size", self.legend_label_size_spinbox
        )
        x_tick_rotation_spinbox = get_label_widget_row_(
            "X-Axis Tick Rotation", self.x_tick_rotation_spinbox
        )
        y_tick_rotation_spinbox = get_label_widget_row_(
            "Y-Axis Tick Rotation", self.y_tick_rotation_spinbox
        )
        x_grid_colour_combobox = get_label_widget_row_(
            "X-Axis Grid Colour", self.x_grid_colour_combobox
        )
        x_grid_alpha_slider = get_label_widget_row_(
            "X-Axis Grid Opacity", self.x_grid_alpha_slider
        )
        y_grid_colour_combobox = get_label_widget_row_(
            "Y-Axis Grid Colour", self.y_grid_colour_combobox
        )
        y_grid_alpha_slider = get_label_widget_row_(
            "Y-Axis Grid Opacity", self.y_grid_alpha_slider
        )
        qualitative_palette_combobox = get_label_widget_row_(
            "Qualitative Palette", self.qualitative_palette_combobox
        )
        circular_palette_combobox = get_label_widget_row_(
            "Circular Palette", self.circular_palette_combobox
        )
        perceptually_uniform_palette_combobox = get_label_widget_row_(
            "Perceptually Uniform", self.perceptually_uniform_palette_combobox
        )
        diverging_palette_combobox = get_label_widget_row_(
            "Diverging Palette", self.diverging_palette_combobox
        )
        build_grid_layout(
            layout,
            [
                [title],
                [sub_label],
                [x_tick_spinbox, y_tick_spinbox],
                [marker_size_spinbox, line_width_spinbox],
                [title_size_spinbox, axes_label_size_spinbox],
                [legend_title_size_spinbox, legend_label_size_spinbox],
                [x_tick_rotation_spinbox, y_tick_rotation_spinbox],
                [(x_grid_colour_combobox, 1), (x_grid_alpha_slider, 1)],
                [(y_grid_colour_combobox, 1), (y_grid_alpha_slider, 1)],
                [qualitative_palette_combobox, circular_palette_combobox],
                [perceptually_uniform_palette_combobox, diverging_palette_combobox],
            ],
        )
        layout.addStretch(1)

    def on_settings_change_callback(self):
        plt.rcdefaults()

        def apply_settings(label: str, target: str, value: float):
            if value == 0:
                return
            kwargs = {target: value}
            plt.rc(label, **kwargs)

        apply_settings("xtick", "labelsize", self.x_tick_spinbox.value())
        apply_settings("ytick", "labelsize", self.y_tick_spinbox.value())
        apply_settings("lines", "markersize", self.marker_size_spinbox.value())
        apply_settings("lines", "linewidth", self.line_width_spinbox.value())
        apply_settings("axes", "titlesize", self.title_size_spinbox.value())
        apply_settings(
            "legend", "title_fontsize", self.legend_title_size_spinbox.value()
        )
        apply_settings("legend", "fontsize", self.legend_label_size_spinbox.value())
        apply_settings("axes", "labelsize", self.axes_label_size_spinbox.value())

        self.plot_params["tick_params"]["x"] = TickParams(
            axis="x",
            rotation=self.x_tick_rotation_spinbox.value(),
            grid_colour=self.x_grid_colour_combobox.currentText(),
            grid_alpha=self.x_grid_alpha_slider.value(),
        )
        self.plot_params["tick_params"]["y"] = TickParams(
            axis="y",
            rotation=self.y_tick_rotation_spinbox.value(),
            grid_colour=self.y_grid_colour_combobox.currentText(),
            grid_alpha=self.y_grid_alpha_slider.value(),
        )

        self.qualitative_palette = self.qualitative_palette_combobox.currentText()
        self.circular_palette = self.circular_palette_combobox.currentText()
        self.perceptually_uniform_palette = (
            self.perceptually_uniform_palette_combobox.currentText()
        )
        self.diverging_palette = self.diverging_palette_combobox.currentText()

        datastore = self.dataexplorer.datamodel.active_dataset
        if datastore is None:
            return
        datastore.replot_callbacks()


class HistogramMode(Enum):
    UNIVARIATE = auto()
    BIVARIATE = auto()


@typing.final
class HistDialog(PlottingDialog):
    mode: HistogramMode = HistogramMode.UNIVARIATE
    hist_column: str | None = None
    y_column: str | None = None
    hue_column: str | None = None
    col_column: str | None = None
    row_column: str | None = None
    log_x: bool = False
    log_y: bool = False
    alpha: float = 1.0
    n_bins: int = 10
    element: str = "step"
    plot_statistic = "count"
    bins: str | list[float] | int = "auto"
    n_cols: int | None = None
    fill: bool = True
    rugplot: bool = False
    legend: bool = True
    cbar: bool = False
    swap_xy: bool = False

    def __init__(self, dataexplorer: "DataExplorer", datastore: "DataStore"):
        super().__init__(dataexplorer, datastore, "Histogram")

        get_label_widget_row_ = partial(
            get_label_widget_row_callback, callback=self.on_widget_change
        )

        self.hist_column_combobox = self.setup_column_combobox(True)
        hist_column_combobox = get_label_widget_row_(
            "Variable", self.hist_column_combobox
        )
        self.y_column_combobox = self.setup_column_combobox(False)
        self.y_column_combobox.setToolTip("Optional: For Bi-variate distributions.")
        y_column_combobox = get_label_widget_row_("Y-Variable", self.y_column_combobox)
        self.hue_column_combobox = self.setup_column_combobox(False)
        hue_column_combobox = get_label_widget_row_("Hue", self.hue_column_combobox)

        self.col_column_combobox = self.setup_column_combobox(False)
        col_column_combobox = get_label_widget_row_("Column", self.col_column_combobox)
        self.row_column_combobox = self.setup_column_combobox(False)
        row_column_combobox = get_label_widget_row_("Row", self.row_column_combobox)

        self.log_x_checkbox = QCheckBox("Log X")
        self.log_y_checkbox = QCheckBox("Log Y")

        collapsible = QCollapsible("Additional Settings")
        collapsible_widget = self.dataexplorer.get_widget()
        collapsible.addWidget(collapsible_widget)
        vbox_widget = QVBoxLayout(collapsible_widget)

        self.alpha_slider = QLabeledDoubleSlider()
        self.alpha_slider.setValue(1.0)
        self.alpha_slider.setRange(0, 1)
        self.alpha_slider.setEdgeLabelMode(
            QLabeledDoubleSlider.EdgeLabelMode.LabelIsValue
        )
        alpha_slider = get_label_widget_row_("Opacity", self.alpha_slider)

        self.plot_statistic_combobox = QComboBox()
        self.plot_statistic_combobox.addItems(HIST_PLOT_STATISTICS)
        plot_statistic_combobox = get_label_widget_row_(
            "Statistic", self.plot_statistic_combobox
        )

        radio_layout = QVBoxLayout()
        self.bin_auto = QRadioButton("Automatically set the bin width")
        self.bin_auto.setChecked(True)
        self.bin_num = QRadioButton("Set the number of bins")
        self.bin_num_spinbox = QSpinBox(minimum=1, maximum=1000, value=5)
        self.bin_width = QRadioButton("Manually set bin widths")
        self.bin_width_line_edit = QLineEdit()
        self.bin_width_line_edit.setPlaceholderText(
            "Comma-separated list of values: 1, 2, 3"
        )

        build_layout_with_callbacks(
            radio_layout,
            [
                self.bin_auto,
                self.bin_num,
                self.bin_num_spinbox,
                self.bin_width,
                self.bin_width_line_edit,
            ],
            self.on_widget_change,
        )

        self.n_cols_spinbox = QSpinBox(minimum=1, maximum=10, value=5)
        n_cols_spinbox = get_label_widget_row_(
            "Maximum # of columns", self.n_cols_spinbox
        )

        self.fill_checkbox = QCheckBox("Fill")
        self.fill_checkbox.setChecked(True)
        self.legend_checkbox = QCheckBox("Legend")
        self.legend_checkbox.setChecked(True)
        self.cbar_checkbox = QCheckBox("Colorbar")
        self.cbar_checkbox.setToolTip("For Bivariate Distributions")
        self.cbar_checkbox.setChecked(False)
        self.swap_xy_checkbox = QCheckBox("Swap Axes")
        self.swap_xy_checkbox.setToolTip("Rotates the plot 90 degrees")
        self.swap_xy_checkbox.setChecked(False)
        self.rugplot_checkbox = QCheckBox("Rugplot")

        self.palette_type_combobox = QComboBox()
        self.palette_type_combobox.addItems(PALETTE_TYPES)
        palette_type_combobox = get_label_widget_row_(
            "Palette Type", self.palette_type_combobox
        )

        build_layout_with_callbacks(
            vbox_widget,
            [
                [alpha_slider, plot_statistic_combobox],
                [radio_layout],
                [n_cols_spinbox],
                [self.fill_checkbox, self.legend_checkbox, self.rugplot_checkbox],
                [self.cbar_checkbox, self.swap_xy_checkbox],
                [palette_type_combobox],
            ],
            self.on_widget_change,
        )

        plot_button = QPushButton("Plot")
        _ = plot_button.clicked.connect(self.plot)
        dynamic_plot_button = QPushButton("Dynamic Plot")
        _ = dynamic_plot_button.clicked.connect(self.dynamic_plot)

        build_layout_with_callbacks(
            self._layout,
            [
                [hist_column_combobox, y_column_combobox, hue_column_combobox],
                [col_column_combobox, row_column_combobox],
                [self.log_y_checkbox, self.log_x_checkbox],
                [collapsible],
                [plot_button, dynamic_plot_button],
            ],
            self.on_widget_change,
        )
        self.show()

    def setup_column_combobox(self, mandatory: bool):
        box = QComboBox()
        if mandatory:
            box.addItems(self.datastore.columns)
        else:
            box.addItem("")
            box.addItems(self.datastore.columns)
        return box

    @typing.override
    def on_plot(self):
        super().on_plot()
        self.hist_column = self.hist_column_combobox.currentText()
        self.y_column = self.y_column_combobox.currentText()
        self.hue_column = self.hue_column_combobox.currentText()
        self.col_column = self.col_column_combobox.currentText()
        self.row_column = self.row_column_combobox.currentText()

        if self.y_column == "":
            self.y_column = None
            self.mode = HistogramMode.UNIVARIATE
        else:
            self.mode = HistogramMode.BIVARIATE
        self.hue_column = self.get_categorical_column_name(self.hue_column)
        self.col_column = self.get_categorical_column_name(self.col_column)
        self.row_column = self.get_categorical_column_name(self.row_column)

        self.log_x = self.log_x_checkbox.isChecked()
        self.log_y = self.log_y_checkbox.isChecked()
        self.alpha = self.alpha_slider.value()
        self.plot_statistic = self.plot_statistic_combobox.currentText()
        self.fill = self.fill_checkbox.isChecked()
        self.element = "step" if self.fill else "bars"
        self.legend = self.legend_checkbox.isChecked()
        self.cbar = self.cbar_checkbox.isChecked()
        self.swap_xy = self.swap_xy_checkbox.isChecked()
        self.rugplot = self.rugplot_checkbox.isChecked()
        self.palette_type = self.palette_type_combobox.currentText()

        if self.col_column is not None:
            self.n_cols = min(
                self.n_cols_spinbox.value(),
                len(self.plotting_data[self.col_column].unique()),  # pyright: ignore[reportUnknownArgumentType]
            )
        else:
            self.n_cols = None

        if self.bin_width.isChecked():
            string = self.bin_width_line_edit.text()
            try:
                list_floats: list[float] = [float(val) for val in string.split(",")]
            except Exception:
                self.error(
                    "The formatting for bin widths is incorrect. Please check it."
                )
                return
            self.bins = list_floats
        elif self.bin_num.isChecked():
            self.bins = self.bin_num_spinbox.value()
        else:
            self.bins = "auto"

        if self.swap_xy:
            self.hist_column, self.y_column = self.y_column, self.hist_column

        self.debug("Plotting Histogram:")
        self.debug(str(self.mode))
        self.debug(f"{self.hist_column} {self.y_column}")
        self.debug(f"{self.hue_column}")
        self.debug(f"{self.row_column} {self.col_column}")
        self.debug(f"{self.log_x} {self.log_y}")
        self.debug(f"{self.plot_statistic} {self.alpha}")
        self.debug(f"{self.cbar} {self.fill} {self.legend} {self.element}")

    def plotter(self) -> sns.FacetGrid:
        match self.mode:
            case HistogramMode.UNIVARIATE:
                fg = sns.displot(
                    self.plotting_data,
                    x=self.hist_column,
                    y=self.y_column,
                    hue=self.hue_column,
                    row=self.row_column,
                    col=self.col_column,
                    col_wrap=self.n_cols,
                    rug=self.rugplot,
                    log_scale=(self.log_x, self.log_y),
                    legend=self.legend,
                    palette=self.get_palette(),
                    stat=self.plot_statistic,
                    element=self.element,
                    bins=self.bins,
                    fill=self.fill,
                    alpha=self.alpha,
                )
            case HistogramMode.BIVARIATE:
                fg = sns.displot(
                    self.plotting_data,
                    x=self.hist_column,
                    y=self.y_column,
                    hue=self.hue_column,
                    row=self.row_column,
                    col=self.col_column,
                    col_wrap=self.n_cols,
                    rug=self.rugplot,
                    log_scale=(self.log_x, self.log_y),
                    legend=self.legend,
                    palette=self.get_palette(),
                    stat=self.plot_statistic,
                    alpha=self.alpha,
                    cbar=self.cbar,
                )
        for ax in fg.axes.flatten():
            assert isinstance(ax, Axes)
            ax.grid()
        fg = fg.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["x"].to_kwargs()
        )
        fg = fg.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["y"].to_kwargs()
        )
        return fg

    @typing.override
    def plot(self):
        self.on_plot()
        try:
            facetgrid = self.plotter()
            facetgrid.figure.show()
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())

    @typing.override
    def dynamic_plot(self):
        if self.dynamic_plot_widget is None:
            self.dynamic_plot_widget = EmbeddedDynamicPlot(
                self.dataexplorer,
                self.datastore,
                f"Histogram: {self.datastore.name}",
                self,
            )
            self.dynamic_callback_id = self.datastore.add_filter_change_callback(
                self.redraw_dynamic_plot
            )
            self.redraw_dynamic_plot()
        else:
            self.error(
                "You cannot make more than two dynamic plots for each plotting widget dialog."
            )

    @typing.override
    def redraw_dynamic_plot(self):
        if self.dynamic_plot_widget is None:
            self.debug("Incorrect call of self.dynamic_plot_widget")
            return
        self.on_plot()
        try:
            plot = self.plotter()
            self.dynamic_plot_widget.update_dynamic_widget(plot)
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())
            return

    @typing.override
    def delete_dynamic_plot(self):
        self.debug("Dynamic Plot Widget Deleted")
        self.dynamic_plot_widget = None
        self.datastore.remove_filter_change_callback(self.dynamic_callback_id)
        self.dynamic_callback_id = -1

    @typing.override
    def closeEvent(self, event: QCloseEvent):
        if self.dynamic_plot_widget is not None:
            _ = self.dynamic_plot_widget.close()

        return super().closeEvent(event)

    @typing.override
    def on_widget_change(self):
        if self.dynamic_plot_widget is not None:
            self.redraw_dynamic_plot()


class ScatterPlotMode(Enum):
    RELPLOT = auto()
    MULTI_Y_SUBPLOT = auto()
    MULTI_Y_SINGLE_Y_AX = auto()
    MULTI_Y_MULTI_Y_AX = auto()
    SINGLE_Y_COLORBAR = auto()
    INVALID = auto()


@typing.final
class ScatterDialog(PlottingDialog):
    x_column: str = ""
    y_columns: list[str] = []
    y_column: str = ""
    colorbar_column: str = ""
    hue_column: str | None = None
    style_column: str | None = None
    col_column: str | None = None
    row_column: str | None = None
    size_column: str | None = None
    n_cols: int = 3
    log_x: bool = False
    log_y: bool = False
    multi_y_handler: str = ""
    alpha: float = 1.0
    marker: str = MARKERS[1]
    plot_mode = ScatterPlotMode.RELPLOT

    def __init__(self, dataexplorer: "DataExplorer", datastore: "DataStore"):
        super().__init__(dataexplorer, datastore, "Scatter")

        get_label_widget_row_ = partial(
            get_label_widget_row_callback, callback=self.on_widget_change
        )

        self.x_column_combobox = self.setup_column_combobox(True)
        x_column_combobox = get_label_widget_row_(
            "X Axis Variable", self.x_column_combobox
        )
        self.y_columns_combobox = self.setup_column_combobox(True, True)
        y_columns_combobox = get_label_widget_row_(
            "Y Axis Variables", self.y_columns_combobox
        )
        self.colorbar_column_combobox = self.setup_column_combobox(False)
        colorbar_column_combobox = get_label_widget_row_(
            "Colorbar Variable", self.colorbar_column_combobox
        )

        self.hue_column_combobox = self.setup_column_combobox(False)
        self.hue_column_combobox.setToolTip(
            "Does not work with multiple y-variables or colorbar."
        )
        hue_column_combobox = get_label_widget_row_("Hue", self.hue_column_combobox)
        self.style_column_combobox = self.setup_column_combobox(False)
        self.style_column_combobox.setToolTip(
            "Does not work with multiple y-variables or colorbar."
        )
        style_column_combobox = get_label_widget_row_(
            "Style", self.style_column_combobox
        )

        self.col_column_combobox = self.setup_column_combobox(False)
        col_column_combobox = get_label_widget_row_("Column", self.col_column_combobox)
        self.col_column_combobox.setToolTip(
            "Does not work with multiple y-variables or colorbar."
        )
        self.row_column_combobox = self.setup_column_combobox(False)
        self.row_column_combobox.setToolTip(
            "Does not work with multiple y-variables or colorbar."
        )
        row_column_combobox = get_label_widget_row_("Row", self.row_column_combobox)
        self.size_column_combobox = self.setup_column_combobox(False)
        self.size_column_combobox.setToolTip(
            "Does not work with multiple y-variables or colorbar."
        )
        size_column_combobox = get_label_widget_row_("Size", self.size_column_combobox)

        self.log_x_checkbox = QCheckBox("Log X")
        self.log_y_checkbox = QCheckBox("Log Y")

        collapsible = QCollapsible("Additional Settings")
        collapsible_widget = self.dataexplorer.get_widget()
        collapsible.addWidget(collapsible_widget)
        vbox_widget = QVBoxLayout(collapsible_widget)

        self.multi_y_handler_combo_box = QComboBox()
        self.multi_y_handler_combo_box.addItems(
            ["Subplots", "Single y-axis", "Upto 4 y-axes"]
        )
        self.multi_y_handler_combo_box.setToolTip("Only Subplots works with colorbar.")
        multi_y_handler_combo_box = get_label_widget_row_(
            ">1 y variable", self.multi_y_handler_combo_box
        )

        self.n_cols_spinbox = QSpinBox(minimum=1, maximum=10, value=3)
        n_cols_spinbox = get_label_widget_row_(
            "Max # of subplot columns", self.n_cols_spinbox
        )

        self.alpha_slider = QLabeledDoubleSlider()
        self.alpha_slider.setValue(1.0)
        self.alpha_slider.setRange(0, 1)
        self.alpha_slider.setEdgeLabelMode(
            QLabeledDoubleSlider.EdgeLabelMode.LabelIsValue
        )
        alpha_slider = get_label_widget_row_("Opacity", self.alpha_slider)

        self.marker_combobox = QComboBox()
        self.marker_combobox.addItems(MARKERS)
        self.marker_combobox.setCurrentIndex(1)
        marker_combobox = get_label_widget_row_("Marker:", self.marker_combobox)

        self.palette_type_combobox = QComboBox()
        self.palette_type_combobox.addItems(PALETTE_TYPES)
        palette_type_combobox = get_label_widget_row_(
            "Palette Type", self.palette_type_combobox
        )
        build_layout_with_callbacks(
            vbox_widget,
            [
                [multi_y_handler_combo_box, n_cols_spinbox],
                [alpha_slider, marker_combobox],
                [palette_type_combobox],
            ],
            self.on_widget_change,
        )

        plot_button = QPushButton("Plot")
        _ = plot_button.clicked.connect(self.plot)
        dynamic_plot_button = QPushButton("Dynamic Plot")
        _ = dynamic_plot_button.clicked.connect(self.dynamic_plot)

        build_layout_with_callbacks(
            self._layout,
            [
                [x_column_combobox, y_columns_combobox],
                [colorbar_column_combobox, hue_column_combobox],
                [style_column_combobox, col_column_combobox],
                [row_column_combobox, size_column_combobox],
                [self.log_y_checkbox, self.log_x_checkbox],
                [collapsible],
                [plot_button, dynamic_plot_button],
            ],
            self.on_widget_change,
        )
        self.show()

    def setup_column_combobox(self, mandatory: bool, multi_variable: bool = False):
        if multi_variable:
            box = MultiSelectComboBox()
        else:
            box = QComboBox()
        if mandatory:
            box.addItems(self.datastore.columns)
        else:
            box.addItem("")
            box.addItems(self.datastore.columns)
        return box

    @typing.override
    def on_plot(self):
        self.plot_mode = ScatterPlotMode.INVALID
        super().on_plot()
        self.x_column = self.x_column_combobox.currentText()
        self.y_columns = self.y_columns_combobox.currentData()
        self.multi_y_handler = self.multi_y_handler_combo_box.currentText()
        self.colorbar_column = self.colorbar_column_combobox.currentText()

        self.log_x = self.log_x_checkbox.isChecked()
        self.log_y = self.log_y_checkbox.isChecked()
        self.n_cols = self.n_cols_spinbox.value()
        self.alpha = self.alpha_slider.value()
        self.marker = self.marker_combobox.currentText()
        self.palette_type = self.palette_type_combobox.currentText()

        if len(self.y_columns) == 0:
            self.error("No Y columns selected!")
            return

        self.debug("Plotting ScatterPlot:")
        self.debug(f"{self.x_column} {self.y_columns}")
        self.debug(f"{self.colorbar_column}")
        self.debug(f"{self.log_x} {self.log_y}")

        if len(self.y_columns) > 1:
            self.debug(f"{self.multi_y_handler}")
            match self.multi_y_handler:
                case "Subplots":
                    self.plot_mode = ScatterPlotMode.MULTI_Y_SUBPLOT
                case "Single y-axis":
                    self.plot_mode = ScatterPlotMode.MULTI_Y_SINGLE_Y_AX
                case "Upto 4 y-axes":
                    if len(self.y_columns) > 4:
                        self.error(">4 y columns selected")
                        return
                    self.plot_mode = ScatterPlotMode.MULTI_Y_MULTI_Y_AX
                case _:
                    self.error("Invalid multi_y_handler selected.")
                    self.debug(self.multi_y_handler)
                    return
            return

        self.y_column = self.y_columns[0]
        if self.colorbar_column != "":
            self.plot_mode = ScatterPlotMode.SINGLE_Y_COLORBAR
            return
        else:
            self.plot_mode = ScatterPlotMode.RELPLOT

        self.hue_column = self.hue_column_combobox.currentText()
        self.style_column = self.style_column_combobox.currentText()
        self.col_column = self.col_column_combobox.currentText()
        self.row_column = self.row_column_combobox.currentText()
        self.size_column = self.size_column_combobox.currentText()

        self.debug(f"{self.hue_column} {self.style_column}")
        self.debug(f"{self.col_column} {self.row_column} {self.size_column}")

        self.hue_column = self.get_categorical_column_name(self.hue_column)
        self.style_column = self.get_categorical_column_name(self.style_column)
        self.col_column = self.get_categorical_column_name(self.col_column)
        self.row_column = self.get_categorical_column_name(self.row_column)
        self.size_column = self.get_categorical_column_name(self.size_column)

    def plotter(self) -> Figure | sns.FacetGrid:
        self.debug(str(self.plot_mode))
        match self.plot_mode:
            case ScatterPlotMode.RELPLOT:
                col_wrap = None if self.col_column is None else self.n_cols
                fg = sns.relplot(
                    self.plotting_data,
                    x=self.x_column,
                    y=self.y_column,
                    hue=self.hue_column,
                    size=self.size_column,
                    style=self.style_column,
                    row=self.row_column,
                    col=self.col_column,
                    col_wrap=col_wrap,
                    palette=self.get_palette(),
                    alpha=self.alpha,
                )
                for ax in fg.axes.flatten():
                    ax.grid()
                fg = fg.tick_params(
                    **self.dataexplorer.plotter.plot_params["tick_params"][
                        "x"
                    ].to_kwargs()
                )
                fg = fg.tick_params(
                    **self.dataexplorer.plotter.plot_params["tick_params"][
                        "y"
                    ].to_kwargs()
                )
                return fg
            case ScatterPlotMode.SINGLE_Y_COLORBAR:
                return self._single_y_colorbar()
            case ScatterPlotMode.MULTI_Y_SUBPLOT:
                return self._subplots()
            case ScatterPlotMode.MULTI_Y_SINGLE_Y_AX:
                return self._multi_y_single_ax()
            case ScatterPlotMode.MULTI_Y_MULTI_Y_AX:
                return self._multi_y_multi_ax()
            case ScatterPlotMode.INVALID:
                return plt.figure()

    def _single_y_colorbar(self) -> Figure:
        fig, ax = plt.subplots()
        im = ax.scatter(
            self.plotting_data[self.x_column],  # pyright: ignore[reportUnknownArgumentType]
            self.plotting_data[self.y_column],  # pyright: ignore[reportUnknownArgumentType]
            c=self.plotting_data[self.colorbar_column],  # pyright: ignore[reportUnknownArgumentType]
            marker=self.marker,
            alpha=self.alpha,
        )
        _ = ax.set_title(
            f"{self.y_column} vs {self.x_column}. Color: {self.colorbar_column}"
        )
        _ = ax.set_xlabel(self.x_column)
        _ = ax.set_ylabel(self.y_column)
        _ = fig.colorbar(im, ax=ax, label=self.colorbar_column)
        ax.grid(True)
        ax.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["x"].to_kwargs()
        )
        ax.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["y"].to_kwargs()
        )
        return fig

    def _subplots(self) -> Figure:
        n_rows = ceil(len(self.y_columns) / self.n_cols)
        fig, axs = plt.subplots(nrows=n_rows, ncols=self.n_cols, sharex=True)  # pyright: ignore[reportAny]
        assert isinstance(axs, ndarray)
        axs = axs.flatten()
        mode_colorbar = self.colorbar_column != ""
        c = None
        if mode_colorbar:
            c = self.plotting_data[self.colorbar_column]  # pyright: ignore[reportUnknownVariableType]

        for ax, y_col in zip(axs, self.y_columns):  # pyright: ignore[reportAny]
            if not isinstance(ax, Axes):
                self.error("Not an axis instance (subplots)")
                return fig
            im = ax.scatter(
                self.plotting_data[self.x_column],  # pyright: ignore[reportUnknownArgumentType]
                self.plotting_data[y_col],  # pyright: ignore[reportUnknownArgumentType]
                c=c,  # pyright: ignore[reportUnknownArgumentType]
                marker=self.marker,
                alpha=self.alpha,
            )
            _ = ax.set_title(f"{y_col} vs {self.x_column}")
            _ = ax.set_ylabel(y_col)
            _ = ax.set_xlabel(self.x_column)
            ax.grid(True)
            ax.tick_params(
                **self.dataexplorer.plotter.plot_params["tick_params"]["x"].to_kwargs()
            )
            ax.tick_params(
                **self.dataexplorer.plotter.plot_params["tick_params"]["y"].to_kwargs()
            )
            if mode_colorbar:
                _ = fig.colorbar(im, ax=ax)

        return fig

    def _multi_y_single_ax(self) -> Figure:
        fig, ax = plt.subplots()
        for y_col in self.y_columns:
            _ = ax.scatter(
                self.plotting_data[self.x_column],  # pyright: ignore[reportUnknownArgumentType]
                self.plotting_data[y_col],  # pyright: ignore[reportUnknownArgumentType]
                label=y_col,
                marker=self.marker,
                alpha=self.alpha,
            )
        ax.grid(True)
        _ = ax.set_title(", ".join(self.y_columns) + f" vs {self.x_column}", wrap=True)
        _ = ax.set_xlabel(self.x_column)
        _ = ax.set_ylabel(", ".join(self.y_columns), wrap=True)
        ax.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["x"].to_kwargs()
        )
        ax.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["y"].to_kwargs()
        )
        _ = plt.legend()
        return fig

    def _multi_y_multi_ax(self) -> Figure:
        fig, ax = plt.subplots()
        assert isinstance(ax, Axes)

        if len(self.y_columns) > 2:
            fig.subplots_adjust(right=0.8)
        loc_array = [0, 0, 1.1, 1.2]
        colors = ["black", "red", "green", "magenta"]

        axes = [ax]

        while len(axes) < len(self.y_columns):
            axes.append(ax.twinx())

        for color, loc, y_col, axis in zip(colors, loc_array, self.y_columns, axes):
            if loc != 0:
                axis.spines.right.set_position(("axes", loc))
            _ = axis.scatter(
                self.plotting_data[self.x_column],  # pyright: ignore[reportUnknownArgumentType]
                self.plotting_data[y_col],  # pyright: ignore[reportUnknownArgumentType]
                c=color,
                marker=self.marker,
                alpha=self.alpha,
            )
            if self.log_x:
                axis.set_xscale("log")
            if self.log_y:
                axis.set_yscale("log")

            _ = axis.set_ylabel(y_col)
            axis.grid(True)
            axis.tick_params(axis="y", colors=color)
            axis.tick_params(
                **self.dataexplorer.plotter.plot_params["tick_params"]["x"].to_kwargs()
            )
            axis.tick_params(
                **self.dataexplorer.plotter.plot_params["tick_params"]["y"].to_kwargs()
            )
            axis.yaxis.label.set_color(color)

        _ = ax.set_title(", ".join(self.y_columns) + f" vs {self.x_column}", wrap=True)

        return fig

    @typing.override
    def plot(self):
        self.on_plot()
        if self.plot_mode == ScatterPlotMode.INVALID:
            return
        try:
            facetgrid = self.plotter()
            if isinstance(facetgrid, Figure):
                facetgrid.show()
            else:
                facetgrid.figure.show()
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())

    @typing.override
    def dynamic_plot(self):
        if self.dynamic_plot_widget is None:
            self.dynamic_plot_widget = EmbeddedDynamicPlot(
                self.dataexplorer,
                self.datastore,
                f"Scatter Plot: {self.datastore.name}",
                self,
            )
            self.dynamic_callback_id = self.datastore.add_filter_change_callback(
                self.redraw_dynamic_plot
            )
            self.redraw_dynamic_plot()
        else:
            self.error(
                "You cannot make more than two dynamic plots for each plotting widget dialog."
            )

    @typing.override
    def redraw_dynamic_plot(self):
        if self.dynamic_plot_widget is None:
            self.debug("Incorrect call of self.dynamic_plot_widget")
            return
        self.on_plot()
        if self.plot_mode == ScatterPlotMode.INVALID:
            return
        try:
            plot = self.plotter()
            self.dynamic_plot_widget.update_dynamic_widget(plot)
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())
            return

    @typing.override
    def delete_dynamic_plot(self):
        self.debug("Dynamic Plot Widget Deleted")
        self.dynamic_plot_widget = None
        self.datastore.remove_filter_change_callback(self.dynamic_callback_id)
        self.dynamic_callback_id = -1

    @typing.override
    def closeEvent(self, event: QCloseEvent):
        if self.dynamic_plot_widget is not None:
            _ = self.dynamic_plot_widget.close()

        return super().closeEvent(event)

    @typing.override
    def on_widget_change(self):
        if self.dynamic_plot_widget is not None:
            self.redraw_dynamic_plot()


class CatPlotMode(Enum):
    SWARM = "Swarm Plot"
    STRIP = "Strip Plot"
    BOX = "Box Plot"
    VIOLIN = "Violin Plot"
    BOXEN = "Boxen Plot"
    POINT = "Point Plot"
    BAR = "Bar Plot"


@typing.final
class CatPlotDialog(PlottingDialog):
    mode: CatPlotMode = CatPlotMode.BOX
    x_column: str | None = None
    y_column: str | None = None
    hue_column: str | None = None
    col_column: str | None = None
    row_column: str | None = None
    log_x: bool = False
    log_y: bool = False
    n_cols: int | None = None
    legend: bool = True
    swap_xy: bool = False
    kwargs: dict[str, typing.Any] = {}
    settings_widgets: dict[CatPlotMode, QWidget] = {}

    swarm_marker_combobox: QComboBox | None = None
    swarm_dodge_checkbox: QCheckBox | None = None
    swarm_size_spinbox: QSpinBox | None = None
    swarm_alpha_slider: QLabeledDoubleSlider | None = None

    strip_marker_combobox: QComboBox | None = None
    strip_dodge_checkbox: QCheckBox | None = None
    strip_size_spinbox: QSpinBox | None = None
    strip_alpha_slider: QLabeledDoubleSlider | None = None

    box_saturation_spinbox: QDoubleSpinBox | None = None
    box_dodge_checkbox: QCheckBox | None = None
    box_fill_checkbox: QCheckBox | None = None
    box_gap_spinbox: QDoubleSpinBox | None = None
    box_size_spinbox: QSpinBox | None = None
    box_alpha_slider: QLabeledDoubleSlider | None = None

    violin_saturation_spinbox: QDoubleSpinBox | None = None
    violin_inner_combobox: QComboBox | None = None
    violin_split_checkbox: QCheckBox | None = None
    violin_dodge_checkbox: QCheckBox | None = None
    violin_fill_checkbox: QCheckBox | None = None
    violin_gap_spinbox: QDoubleSpinBox | None = None
    violin_alpha_slider: QLabeledDoubleSlider | None = None

    boxen_saturation_spinbox: QDoubleSpinBox | None = None
    boxen_dodge_checkbox: QCheckBox | None = None
    boxen_fill_checkbox: QCheckBox | None = None
    boxen_gap_spinbox: QDoubleSpinBox | None = None
    boxen_alpha_slider: QLabeledDoubleSlider | None = None

    point_linestyle_combobox: QComboBox | None = None
    point_marker_combobox: QComboBox | None = None
    point_dodge_checkbox: QCheckBox | None = None
    point_alpha_slider: QLabeledDoubleSlider | None = None

    bar_saturation_spinbox: QDoubleSpinBox | None = None
    bar_dodge_checkbox: QCheckBox | None = None
    bar_fill_checkbox: QCheckBox | None = None
    bar_gap_spinbox: QDoubleSpinBox | None = None
    bar_alpha_slider: QLabeledDoubleSlider | None = None

    def __init__(self, dataexplorer: "DataExplorer", datastore: "DataStore"):
        super().__init__(dataexplorer, datastore, "Categorical")

        get_label_widget_row_ = partial(
            get_label_widget_row_callback, callback=self.on_widget_change
        )

        self.mode_combobox = QComboBox()
        self.mode_combobox.addItems([e.value for e in CatPlotMode])
        self.mode_combobox.setCurrentIndex(2)
        _ = self.mode_combobox.currentTextChanged.connect(
            lambda: self.set_active_settings()
        )
        mode_combobox = get_label_widget_row_("Plot Type: ", self.mode_combobox)

        self.categorical_column_combobox = self.setup_column_combobox(True)
        categorical_column_combobox = get_label_widget_row_(
            "Categorical Variable", self.categorical_column_combobox
        )
        self.continuous_column_combobox = self.setup_column_combobox(True)
        continuous_column_combobox = get_label_widget_row_(
            "Continuous Variable", self.continuous_column_combobox
        )
        self.hue_column_combobox = self.setup_column_combobox(False)
        hue_column_combobox = get_label_widget_row_("Hue", self.hue_column_combobox)

        self.col_column_combobox = self.setup_column_combobox(False)
        col_column_combobox = get_label_widget_row_("Column", self.col_column_combobox)
        self.row_column_combobox = self.setup_column_combobox(False)
        row_column_combobox = get_label_widget_row_("Row", self.row_column_combobox)

        self.log_x_checkbox = QCheckBox("Log X")
        self.log_y_checkbox = QCheckBox("Log Y")
        self.swap_xy_checkbox = QCheckBox("Swap X-Y axes")
        self.legend_checkbox = QCheckBox("Legend")
        self.legend_checkbox.setChecked(True)

        self.n_cols_spinbox = QSpinBox(minimum=1, maximum=10, value=5)
        n_cols_spinbox = get_label_widget_row_(
            "Maximum # of columns", self.n_cols_spinbox
        )
        self.palette_type_combobox = QComboBox()
        self.palette_type_combobox.addItems(PALETTE_TYPES)
        palette_type_combobox = get_label_widget_row_(
            "Palette Type", self.palette_type_combobox
        )
        collapsible = QCollapsible("Additional Settings")
        collapsible_widget = self.dataexplorer.get_widget()
        collapsible.addWidget(collapsible_widget)
        vbox_widget = QVBoxLayout(collapsible_widget)

        settings_frame = QFrame()
        settings_vbox = QVBoxLayout(settings_frame)
        vbox_widget.addWidget(settings_frame, stretch=1)

        def add_new_settings_widget(type: CatPlotMode, widget: QWidget):
            self.debug(str(type))
            self.settings_widgets[type] = widget
            settings_vbox.addWidget(widget)
            widget.setVisible(False)

        add_new_settings_widget(*self._swarm_plot_settings())
        add_new_settings_widget(*self._strip_plot_settings())
        add_new_settings_widget(*self._box_plot_settings())
        add_new_settings_widget(*self._violin_plot_settings())
        add_new_settings_widget(*self._boxen_plot_settings())
        add_new_settings_widget(*self._point_plot_settings())
        add_new_settings_widget(*self._bar_plot_settings())
        self.settings_widgets[CatPlotMode.BOX].setVisible(True)

        plot_button = QPushButton("Plot")
        _ = plot_button.clicked.connect(self.plot)
        dynamic_plot_button = QPushButton("Dynamic Plot")
        _ = dynamic_plot_button.clicked.connect(self.dynamic_plot)

        build_layout_with_callbacks(
            self._layout,
            [
                [mode_combobox],
                [categorical_column_combobox, continuous_column_combobox],
                [hue_column_combobox, col_column_combobox, row_column_combobox],
                [
                    self.log_y_checkbox,
                    self.log_x_checkbox,
                    self.swap_xy_checkbox,
                    self.legend_checkbox,
                    n_cols_spinbox,
                ],
                [palette_type_combobox],
                [collapsible],
                [plot_button, dynamic_plot_button],
            ],
            self.on_widget_change,
        )
        self.show()

    def _swarm_plot_settings(self) -> tuple[CatPlotMode, QWidget]:
        widget = self.dataexplorer.get_widget()
        layout = QVBoxLayout(widget)
        self.swarm_marker_combobox = QComboBox()
        self.swarm_marker_combobox.addItems(MARKERS)
        swarm_marker_combobox = get_label_widget_row_callback(
            "Marker:", self.swarm_marker_combobox, self.on_widget_change
        )
        self.swarm_dodge_checkbox = QCheckBox("Dodge")
        self.swarm_dodge_checkbox.setChecked(True)
        self.swarm_dodge_checkbox.setToolTip("Useful with overlapping hues")
        self.swarm_size_spinbox = QSpinBox(minimum=1, maximum=50, value=10)
        swarm_size_spinbox = get_label_widget_row_callback(
            "Marker Size:", self.swarm_size_spinbox, self.on_widget_change
        )

        self.swarm_alpha_slider = QLabeledDoubleSlider()
        self.swarm_alpha_slider.setRange(min=0.0, max=1.0)
        self.swarm_alpha_slider.setValue(1.0)
        swarm_alpha_slider = get_label_widget_row_callback(
            "Opacity:", self.swarm_alpha_slider, self.on_widget_change
        )

        build_layout_with_callbacks(
            layout,
            [
                swarm_marker_combobox,
                self.swarm_dodge_checkbox,
                swarm_size_spinbox,
                swarm_alpha_slider,
            ],
            self.on_widget_change,
        )
        return (CatPlotMode.SWARM, widget)

    def _strip_plot_settings(self) -> tuple[CatPlotMode, QWidget]:
        widget = self.dataexplorer.get_widget()
        layout = QVBoxLayout(widget)
        self.strip_marker_combobox = QComboBox()
        self.strip_marker_combobox.addItems(MARKERS)
        strip_marker_combobox = get_label_widget_row_callback(
            "Marker:", self.strip_marker_combobox, self.on_widget_change
        )
        self.strip_dodge_checkbox = QCheckBox("Dodge")
        self.strip_dodge_checkbox.setChecked(True)
        self.strip_dodge_checkbox.setToolTip("Useful with overlapping hues")
        self.strip_size_spinbox = QSpinBox(minimum=1, maximum=50, value=10)
        strip_size_spinbox = get_label_widget_row_callback(
            "Marker Size:", self.strip_size_spinbox, self.on_widget_change
        )

        self.strip_alpha_slider = QLabeledDoubleSlider()
        self.strip_alpha_slider.setRange(min=0.0, max=1.0)
        self.strip_alpha_slider.setValue(1.0)
        strip_alpha_slider = get_label_widget_row_callback(
            "Opacity:", self.strip_alpha_slider, self.on_widget_change
        )
        build_layout_with_callbacks(
            layout,
            [
                strip_marker_combobox,
                self.strip_dodge_checkbox,
                strip_size_spinbox,
                strip_alpha_slider,
            ],
            self.on_widget_change,
        )
        return (CatPlotMode.STRIP, widget)

    def _box_plot_settings(self) -> tuple[CatPlotMode, QWidget]:
        widget = self.dataexplorer.get_widget()
        layout = QVBoxLayout(widget)
        self.box_saturation_spinbox = QDoubleSpinBox(
            minimum=0.1,
            maximum=1.0,
            value=0.75,
            singleStep=0.1,
        )
        box_saturation_spinbox = get_label_widget_row_callback(
            "Saturation:", self.box_saturation_spinbox, self.on_widget_change
        )
        self.box_gap_spinbox = QDoubleSpinBox(
            minimum=0, maximum=1.0, value=0, singleStep=0.1
        )
        box_gap_spinbox = get_label_widget_row_callback(
            "Gap:", self.box_gap_spinbox, self.on_widget_change
        )
        self.box_dodge_checkbox = QCheckBox("Dodge")
        self.box_dodge_checkbox.setToolTip("Useful with overlapping hues")
        self.box_dodge_checkbox.setChecked(True)
        self.box_fill_checkbox = QCheckBox("Fill")
        self.box_fill_checkbox.setChecked(True)
        self.box_size_spinbox = QSpinBox(minimum=1, maximum=50, value=10)
        box_size_spinbox = get_label_widget_row_callback(
            "Marker Size:", self.box_size_spinbox, self.on_widget_change
        )

        self.box_alpha_slider = QLabeledDoubleSlider()
        self.box_alpha_slider.setRange(min=0.0, max=1.0)
        self.box_alpha_slider.setValue(1.0)
        box_alpha_slider = get_label_widget_row_callback(
            "Opacity:", self.box_alpha_slider, self.on_widget_change
        )
        build_layout_with_callbacks(
            layout,
            [
                [box_saturation_spinbox, box_gap_spinbox],
                [self.box_dodge_checkbox, self.box_fill_checkbox],
                [box_size_spinbox, box_alpha_slider],
            ],
            self.on_widget_change,
        )
        return (CatPlotMode.BOX, widget)

    def _violin_plot_settings(self) -> tuple[CatPlotMode, QWidget]:
        widget = self.dataexplorer.get_widget()
        layout = QVBoxLayout(widget)
        self.violin_saturation_spinbox = QDoubleSpinBox(
            minimum=0.1,
            maximum=1.0,
            value=0.75,
            singleStep=0.1,
        )
        violin_saturation_spinbox = get_label_widget_row_callback(
            "Saturation:", self.violin_saturation_spinbox, self.on_widget_change
        )
        self.violin_gap_spinbox = QDoubleSpinBox(
            minimum=0, maximum=1.0, value=0, singleStep=0.1
        )
        violin_gap_spinbox = get_label_widget_row_callback(
            "Gap:", self.violin_gap_spinbox, self.on_widget_change
        )
        self.violin_dodge_checkbox = QCheckBox("Dodge")
        self.violin_dodge_checkbox.setToolTip("Useful with overlapping hues")
        self.violin_dodge_checkbox.setChecked(True)
        self.violin_split_checkbox = QCheckBox("Split")
        self.violin_fill_checkbox = QCheckBox("Fill")
        self.violin_fill_checkbox.setChecked(True)
        self.violin_inner_combobox = QComboBox()
        self.violin_inner_combobox.addItems(VIOLIN_INNER)
        violin_inner_combobox = get_label_widget_row_callback(
            "Inner:", self.violin_inner_combobox, self.on_widget_change
        )

        self.violin_alpha_slider = QLabeledDoubleSlider()
        self.violin_alpha_slider.setRange(min=0.0, max=1.0)
        self.violin_alpha_slider.setValue(1.0)
        violin_alpha_slider = get_label_widget_row_callback(
            "Opacity:", self.violin_alpha_slider, self.on_widget_change
        )
        build_layout_with_callbacks(
            layout,
            [
                [violin_saturation_spinbox, violin_gap_spinbox],
                [
                    self.violin_dodge_checkbox,
                    self.violin_split_checkbox,
                    self.violin_fill_checkbox,
                ],
                [violin_inner_combobox, violin_alpha_slider],
            ],
            self.on_widget_change,
        )
        return (CatPlotMode.VIOLIN, widget)

    def _boxen_plot_settings(self) -> tuple[CatPlotMode, QWidget]:
        widget = self.dataexplorer.get_widget()
        layout = QVBoxLayout(widget)
        self.boxen_saturation_spinbox = QDoubleSpinBox(
            minimum=0.1,
            maximum=1.0,
            value=0.75,
            singleStep=0.1,
        )
        boxen_saturation_spinbox = get_label_widget_row_callback(
            "Saturation:", self.boxen_saturation_spinbox, self.on_widget_change
        )
        self.boxen_gap_spinbox = QDoubleSpinBox(
            minimum=0, maximum=1.0, value=0, singleStep=0.1
        )
        boxen_gap_spinbox = get_label_widget_row_callback(
            "Gap:", self.boxen_gap_spinbox, self.on_widget_change
        )
        self.boxen_dodge_checkbox = QCheckBox("Dodge")
        self.boxen_dodge_checkbox.setToolTip("Useful with overlapping hues")
        self.boxen_dodge_checkbox.setChecked(True)
        self.boxen_fill_checkbox = QCheckBox("Fill")
        self.boxen_fill_checkbox.setChecked(True)

        self.boxen_alpha_slider = QLabeledDoubleSlider()
        self.boxen_alpha_slider.setRange(min=0.0, max=1.0)
        self.boxen_alpha_slider.setValue(1.0)
        boxen_alpha_slider = get_label_widget_row_callback(
            "Opacity:", self.boxen_alpha_slider, self.on_widget_change
        )
        build_layout_with_callbacks(
            layout,
            [
                [boxen_saturation_spinbox, boxen_gap_spinbox],
                [self.boxen_dodge_checkbox, self.boxen_fill_checkbox],
                [boxen_alpha_slider],
            ],
            self.on_widget_change,
        )
        return (CatPlotMode.BOXEN, widget)

    def _point_plot_settings(self) -> tuple[CatPlotMode, QWidget]:
        widget = self.dataexplorer.get_widget()
        layout = QVBoxLayout(widget)
        self.point_marker_combobox = QComboBox()
        self.point_marker_combobox.addItems(MARKERS)
        point_marker_combobox = get_label_widget_row_callback(
            "Marker:", self.point_marker_combobox, self.on_widget_change
        )
        self.point_linestyle_combobox = QComboBox()
        self.point_linestyle_combobox.addItems(LINE_STYLES)
        point_linestyle_combobox = get_label_widget_row_callback(
            "Line Styles:", self.point_linestyle_combobox, self.on_widget_change
        )
        self.point_dodge_checkbox = QCheckBox("Dodge")
        self.point_dodge_checkbox.setChecked(True)
        self.point_dodge_checkbox.setToolTip("Useful with overlapping hues")

        self.point_alpha_slider = QLabeledDoubleSlider()
        self.point_alpha_slider.setRange(min=0.0, max=1.0)
        self.point_alpha_slider.setValue(1.0)
        point_alpha_slider = get_label_widget_row_callback(
            "Opacity:", self.point_alpha_slider, self.on_widget_change
        )
        build_layout_with_callbacks(
            layout,
            [
                [point_marker_combobox, point_linestyle_combobox],
                [self.point_dodge_checkbox, point_alpha_slider],
            ],
            self.on_widget_change,
        )
        return (CatPlotMode.POINT, widget)

    def _bar_plot_settings(self) -> tuple[CatPlotMode, QWidget]:
        widget = self.dataexplorer.get_widget()
        layout = QVBoxLayout(widget)
        self.bar_saturation_spinbox = QDoubleSpinBox(
            minimum=0.1,
            maximum=1.0,
            value=0.75,
            singleStep=0.1,
        )
        bar_saturation_spinbox = get_label_widget_row_callback(
            "Saturation:", self.bar_saturation_spinbox, self.on_widget_change
        )
        self.bar_gap_spinbox = QDoubleSpinBox(
            minimum=0, maximum=1.0, value=0, singleStep=0.1
        )
        bar_gap_spinbox = get_label_widget_row_callback(
            "Gap:", self.bar_gap_spinbox, self.on_widget_change
        )
        self.bar_dodge_checkbox = QCheckBox("Dodge")
        self.bar_dodge_checkbox.setToolTip("Useful with overlapping hues")
        self.bar_dodge_checkbox.setChecked(True)
        self.bar_fill_checkbox = QCheckBox("Fill")
        self.bar_fill_checkbox.setChecked(True)

        self.bar_alpha_slider = QLabeledDoubleSlider()
        self.bar_alpha_slider.setRange(min=0.0, max=1.0)
        self.bar_alpha_slider.setValue(1.0)
        bar_alpha_slider = get_label_widget_row_callback(
            "Opacity:", self.bar_alpha_slider, self.on_widget_change
        )
        build_layout_with_callbacks(
            layout,
            [
                [bar_saturation_spinbox, bar_gap_spinbox],
                [self.bar_dodge_checkbox, self.bar_fill_checkbox],
                [bar_alpha_slider],
            ],
            self.on_widget_change,
        )
        return (CatPlotMode.BAR, widget)

    def _read_bar_plot_settings(self):
        self.kwargs = {}
        if (
            self.bar_saturation_spinbox is None
            or self.bar_gap_spinbox is None
            or self.bar_dodge_checkbox is None
            or self.bar_fill_checkbox is None
            or self.bar_alpha_slider is None
        ):
            self.debug("Bar Settings are None")
            return

        self.kwargs["saturation"] = self.bar_saturation_spinbox.value()
        self.kwargs["gap"] = self.bar_gap_spinbox.value()
        self.kwargs["alpha"] = self.bar_alpha_slider.value()
        self.kwargs["dodge"] = self.bar_dodge_checkbox.isChecked()
        self.kwargs["fill"] = self.bar_fill_checkbox.isChecked()

    def _read_point_plot_settings(self):
        self.kwargs = {}
        if (
            self.point_marker_combobox is None
            or self.point_dodge_checkbox is None
            or self.point_linestyle_combobox is None
            or self.point_alpha_slider is None
        ):
            self.debug("Point Settings are None")
            return
        self.kwargs["markers"] = self.point_marker_combobox.currentText()
        self.kwargs["alpha"] = self.point_alpha_slider.value()
        self.kwargs["linestyles"] = self.point_linestyle_combobox.currentText()
        self.kwargs["dodge"] = self.point_dodge_checkbox.isChecked()

    def _read_boxen_plot_settings(self):
        self.kwargs = {}
        if (
            self.boxen_saturation_spinbox is None
            or self.boxen_gap_spinbox is None
            or self.boxen_dodge_checkbox is None
            or self.boxen_fill_checkbox is None
            or self.boxen_alpha_slider is None
        ):
            self.debug("Boxen Settings are None")
            return
        self.kwargs["saturation"] = self.boxen_saturation_spinbox.value()
        self.kwargs["gap"] = self.boxen_gap_spinbox.value()
        self.kwargs["alpha"] = self.boxen_alpha_slider.value()
        self.kwargs["dodge"] = self.boxen_dodge_checkbox.isChecked()
        self.kwargs["fill"] = self.boxen_fill_checkbox.isChecked()

    def _read_violin_plot_settings(self):
        self.kwargs = {}
        if (
            self.violin_saturation_spinbox is None
            or self.violin_gap_spinbox is None
            or self.violin_dodge_checkbox is None
            or self.violin_fill_checkbox is None
            or self.violin_split_checkbox is None
            or self.violin_inner_combobox is None
            or self.violin_alpha_slider is None
        ):
            self.debug("Violin Settings are None")
            return
        self.kwargs["saturation"] = self.violin_saturation_spinbox.value()
        self.kwargs["gap"] = self.violin_gap_spinbox.value()
        self.kwargs["alpha"] = self.violin_alpha_slider.value()
        self.kwargs["dodge"] = self.violin_dodge_checkbox.isChecked()
        self.kwargs["split"] = self.violin_split_checkbox.isChecked()
        self.kwargs["fill"] = self.violin_fill_checkbox.isChecked()
        self.kwargs["inner"] = self.violin_inner_combobox.currentText()

    def _read_box_plot_settings(self):
        self.kwargs = {}
        if (
            self.box_saturation_spinbox is None
            or self.box_gap_spinbox is None
            or self.box_dodge_checkbox is None
            or self.box_size_spinbox is None
            or self.box_fill_checkbox is None
            or self.box_alpha_slider is None
        ):
            self.debug("Box Settings are None")
            return
        self.kwargs["saturation"] = self.box_saturation_spinbox.value()
        self.kwargs["gap"] = self.box_gap_spinbox.value()
        self.kwargs["boxprops"] = {"alpha": self.box_alpha_slider.value()}
        self.kwargs["dodge"] = self.box_dodge_checkbox.isChecked()
        self.kwargs["fill"] = self.box_fill_checkbox.isChecked()
        self.kwargs["fliersize"] = self.box_size_spinbox.value()

    def _read_strip_plot_settings(self):
        self.kwargs = {}
        if (
            self.strip_marker_combobox is None
            or self.strip_dodge_checkbox is None
            or self.strip_size_spinbox is None
            or self.strip_alpha_slider is None
        ):
            self.debug("Strip Settings are None")
            return
        self.kwargs["marker"] = self.strip_marker_combobox.currentText()
        self.kwargs["dodge"] = self.strip_dodge_checkbox.isChecked()
        self.kwargs["size"] = self.strip_size_spinbox.value()
        self.kwargs["alpha"] = self.strip_alpha_slider.value()

    def _read_swarm_plot_settings(self):
        self.kwargs = {}
        if (
            self.swarm_marker_combobox is None
            or self.swarm_dodge_checkbox is None
            or self.swarm_size_spinbox is None
            or self.swarm_alpha_slider is None
        ):
            self.debug("Swarm Settings are None")
            return
        self.kwargs["marker"] = self.swarm_marker_combobox.currentText()
        self.kwargs["dodge"] = self.swarm_dodge_checkbox.isChecked()
        self.kwargs["size"] = self.swarm_size_spinbox.value()
        self.kwargs["alpha"] = self.swarm_alpha_slider.value()

    def setup_column_combobox(self, mandatory: bool):
        box = QComboBox()
        if mandatory:
            box.addItems(self.datastore.columns)
        else:
            box.addItem("")
            box.addItems(self.datastore.columns)
        return box

    def set_active_settings(self):
        mode_string = self.mode_combobox.currentText()
        for widg in self.settings_widgets.values():
            widg.setVisible(False)
        self.mode = CatPlotMode(mode_string)
        self.settings_widgets[self.mode].setVisible(True)

    def setup_kwargs(self):
        match self.mode:
            case CatPlotMode.SWARM:
                self._read_swarm_plot_settings()
            case CatPlotMode.STRIP:
                self._read_strip_plot_settings()
            case CatPlotMode.BOX:
                self._read_box_plot_settings()
            case CatPlotMode.VIOLIN:
                self._read_violin_plot_settings()
            case CatPlotMode.BOXEN:
                self._read_boxen_plot_settings()
            case CatPlotMode.POINT:
                self._read_point_plot_settings()
            case CatPlotMode.BAR:
                self._read_bar_plot_settings()

    @typing.override
    def on_plot(self):
        super().on_plot()
        cat_col = self.categorical_column_combobox.currentText()
        categorical_column: str | None = self.get_categorical_column_name(cat_col)
        if categorical_column is None:
            self.error("Invalid Categorical column")
            return
        else:
            self.x_column = categorical_column
        self.y_column = self.continuous_column_combobox.currentText()
        self.hue_column = self.hue_column_combobox.currentText()
        self.col_column = self.col_column_combobox.currentText()
        self.row_column = self.row_column_combobox.currentText()

        self.hue_column = self.get_categorical_column_name(self.hue_column)
        self.col_column = self.get_categorical_column_name(self.col_column)
        self.row_column = self.get_categorical_column_name(self.row_column)

        self.log_x = self.log_x_checkbox.isChecked()
        self.log_y = self.log_y_checkbox.isChecked()
        self.legend = self.legend_checkbox.isChecked()
        self.swap_xy = self.swap_xy_checkbox.isChecked()
        self.palette_type = self.palette_type_combobox.currentText()

        if self.col_column is not None:
            self.n_cols = min(
                self.n_cols_spinbox.value(),
                len(self.plotting_data[self.col_column].unique()),  # pyright: ignore[reportUnknownArgumentType]
            )
        else:
            self.n_cols = None

        if self.swap_xy:
            self.x_column, self.y_column = self.y_column, self.x_column

        self.setup_kwargs()

        self.debug(str(self.mode))
        self.debug(f"{self.x_column} {self.y_column}")
        self.debug(f"{self.hue_column}")
        self.debug(f"{self.row_column} {self.col_column}")
        self.debug(f"{self.log_x} {self.log_y}")
        self.debug(f"{self.legend}")
        self.debug(pformat(self.kwargs))

    def plotter(self) -> sns.FacetGrid:
        match self.mode:
            case CatPlotMode.SWARM:
                kind = "swarm"
            case CatPlotMode.STRIP:
                kind = "strip"
            case CatPlotMode.BOX:
                kind = "box"
            case CatPlotMode.VIOLIN:
                kind = "violin"
            case CatPlotMode.BOXEN:
                kind = "boxen"
            case CatPlotMode.POINT:
                kind = "point"
            case CatPlotMode.BAR:
                kind = "bar"
        fg = sns.catplot(
            self.plotting_data,
            kind=kind,
            x=self.x_column,
            y=self.y_column,
            hue=self.hue_column,
            row=self.row_column,
            col=self.col_column,
            col_wrap=self.n_cols,
            log_scale=(self.log_x, self.log_y),
            legend=self.legend,
            palette=self.get_palette(),
            **self.kwargs,  # pyright: ignore[reportAny]
        )
        for ax in fg.axes.flatten():
            ax.grid()
        fg = fg.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["x"].to_kwargs()
        )
        fg = fg.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["y"].to_kwargs()
        )
        return fg

    @typing.override
    def plot(self):
        self.on_plot()
        try:
            facetgrid = self.plotter()
            facetgrid.figure.show()
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())

    @typing.override
    def dynamic_plot(self):
        if self.dynamic_plot_widget is None:
            self.dynamic_plot_widget = EmbeddedDynamicPlot(
                self.dataexplorer,
                self.datastore,
                f"Categorical Plot: {self.datastore.name}",
                self,
            )
            self.dynamic_callback_id = self.datastore.add_filter_change_callback(
                self.redraw_dynamic_plot
            )
            self.redraw_dynamic_plot()
        else:
            self.error(
                "You cannot make more than two dynamic plots for each plotting widget dialog."
            )

    @typing.override
    def redraw_dynamic_plot(self):
        if self.dynamic_plot_widget is None:
            self.debug("Incorrect call of self.dynamic_plot_widget")
            return
        self.on_plot()
        try:
            plot = self.plotter()
            self.dynamic_plot_widget.update_dynamic_widget(plot)
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())
            return

    @typing.override
    def delete_dynamic_plot(self):
        self.debug("Dynamic Plot Widget Deleted")
        self.dynamic_plot_widget = None
        self.datastore.remove_filter_change_callback(self.dynamic_callback_id)
        self.dynamic_callback_id = -1

    @typing.override
    def closeEvent(self, event: QCloseEvent):
        if self.dynamic_plot_widget is not None:
            _ = self.dynamic_plot_widget.close()

        return super().closeEvent(event)

    @typing.override
    def on_widget_change(self):
        if self.dynamic_plot_widget is not None:
            self.redraw_dynamic_plot()


@typing.final
class CountPlotDialog(PlottingDialog):
    x_column: str | None = None
    y_column: str | None = None
    hue_column: str | None = None
    col_column: str | None = None
    row_column: str | None = None
    log_x: bool = False
    log_y: bool = False
    n_cols: int | None = None
    fill: bool = True
    legend: bool = True
    dodge: bool = True
    gap: float = 0.0
    alpha: float = 1.0
    saturation: float = 0.75
    plot_statistic = "count"
    swap_xy: bool = False

    def __init__(self, dataexplorer: "DataExplorer", datastore: "DataStore"):
        super().__init__(dataexplorer, datastore, "Count")

        get_label_widget_row_ = partial(
            get_label_widget_row_callback, callback=self.on_widget_change
        )

        self.categorical_column_combobox = self.setup_column_combobox(True)
        categorical_column_combobox = get_label_widget_row_(
            "Categorical Variable", self.categorical_column_combobox
        )
        self.hue_column_combobox = self.setup_column_combobox(False)
        hue_column_combobox = get_label_widget_row_("Hue", self.hue_column_combobox)

        self.col_column_combobox = self.setup_column_combobox(False)
        col_column_combobox = get_label_widget_row_("Column", self.col_column_combobox)
        self.row_column_combobox = self.setup_column_combobox(False)
        row_column_combobox = get_label_widget_row_("Row", self.row_column_combobox)

        self.log_x_checkbox = QCheckBox("Log X")
        self.log_y_checkbox = QCheckBox("Log Y")

        self.n_cols_spinbox = QSpinBox(minimum=1, maximum=10, value=5)
        n_cols_spinbox = get_label_widget_row_(
            "Maximum # of columns", self.n_cols_spinbox
        )

        collapsible = QCollapsible("Additional Settings")
        collapsible_widget = self.dataexplorer.get_widget()
        collapsible.addWidget(collapsible_widget)
        vbox_widget = QVBoxLayout(collapsible_widget)
        self.alpha_slider = QLabeledDoubleSlider()
        self.alpha_slider.setValue(1.0)
        self.alpha_slider.setRange(0, 1)
        self.alpha_slider.setEdgeLabelMode(
            QLabeledDoubleSlider.EdgeLabelMode.LabelIsValue
        )
        alpha_slider = get_label_widget_row_("Opacity", self.alpha_slider)

        self.saturation_spinbox = QDoubleSpinBox(
            minimum=0.0, maximum=1.0, value=0.75, singleStep=0.1
        )
        saturation_spinbox = get_label_widget_row_(
            "Saturation", self.saturation_spinbox
        )

        self.plot_statistic_combobox = QComboBox()
        self.plot_statistic_combobox.addItems(COUNT_PLOT_STATISTICS)
        plot_statistic_combobox = get_label_widget_row_(
            "Statistic", self.plot_statistic_combobox
        )
        self.gap_spinbox = QDoubleSpinBox(
            minimum=0.0, maximum=1.0, value=0, singleStep=0.1
        )
        gap_spinbox = get_label_widget_row_("Gap", self.gap_spinbox)

        self.fill_checkbox = QCheckBox("Fill")
        self.fill_checkbox.setChecked(self.fill)
        self.legend_checkbox = QCheckBox("Legend")
        self.legend_checkbox.setChecked(self.legend)
        self.dodge_checkbox = QCheckBox("Dodge")
        self.dodge_checkbox.setChecked(self.dodge)
        self.swap_xy_checkbox = QCheckBox("Swap Axes")
        self.swap_xy_checkbox.setToolTip("Rotates the plot 90 degrees")
        self.swap_xy_checkbox.setChecked(self.swap_xy)

        self.palette_type_combobox = QComboBox()
        self.palette_type_combobox.addItems(PALETTE_TYPES)
        palette_type_combobox = get_label_widget_row_(
            "Palette Type", self.palette_type_combobox
        )

        build_layout_with_callbacks(
            vbox_widget,
            [
                [alpha_slider, saturation_spinbox],
                [plot_statistic_combobox, gap_spinbox],
                [
                    self.fill_checkbox,
                    self.legend_checkbox,
                    self.dodge_checkbox,
                    self.swap_xy_checkbox,
                ],
                [palette_type_combobox],
            ],
            self.on_widget_change,
        )

        plot_button = QPushButton("Plot")
        _ = plot_button.clicked.connect(self.plot)
        dynamic_plot_button = QPushButton("Dynamic Plot")
        _ = dynamic_plot_button.clicked.connect(self.dynamic_plot)

        build_layout_with_callbacks(
            self._layout,
            [
                [categorical_column_combobox, hue_column_combobox],
                [col_column_combobox, row_column_combobox],
                [self.log_y_checkbox, self.log_x_checkbox, n_cols_spinbox],
                [collapsible],
                [plot_button, dynamic_plot_button],
            ],
            self.on_widget_change,
        )
        self.show()

    def setup_column_combobox(self, mandatory: bool):
        box = QComboBox()
        if mandatory:
            box.addItems(self.datastore.columns)
        else:
            box.addItem("")
            box.addItems(self.datastore.columns)
        return box

    @typing.override
    def on_plot(self):
        super().on_plot()
        self.y_column = None
        self.x_column = self.categorical_column_combobox.currentText()
        self.hue_column = self.hue_column_combobox.currentText()
        self.col_column = self.col_column_combobox.currentText()
        self.row_column = self.row_column_combobox.currentText()

        self.x_column = self.get_categorical_column_name(self.x_column)
        self.hue_column = self.get_categorical_column_name(self.hue_column)
        self.col_column = self.get_categorical_column_name(self.col_column)
        self.row_column = self.get_categorical_column_name(self.row_column)

        self.log_x = self.log_x_checkbox.isChecked()
        self.log_y = self.log_y_checkbox.isChecked()
        self.gap = self.gap_spinbox.value()
        self.alpha = self.alpha_slider.value()
        self.plot_statistic = self.plot_statistic_combobox.currentText()
        self.fill = self.fill_checkbox.isChecked()
        self.saturation = self.saturation_spinbox.value()
        self.dodge = self.dodge_checkbox.isChecked()
        self.legend = self.legend_checkbox.isChecked()
        self.swap_xy = self.swap_xy_checkbox.isChecked()
        self.palette_type = self.palette_type_combobox.currentText()

        if self.col_column is not None:
            self.n_cols = min(
                self.n_cols_spinbox.value(),
                len(self.plotting_data[self.col_column].unique()),  # pyright: ignore[reportUnknownArgumentType]
            )
        else:
            self.n_cols = None

        if self.swap_xy:
            self.x_column, self.y_column = self.y_column, self.x_column

        self.debug("Plotting Count Plot:")
        self.debug(f"{self.x_column} {self.y_column}")
        self.debug(f"{self.hue_column}")
        self.debug(f"{self.row_column} {self.col_column}")
        self.debug(f"{self.log_x} {self.log_y}")
        self.debug(f"{self.plot_statistic} {self.alpha}")
        self.debug(f"{self.dodge} {self.fill} {self.legend} {self.saturation}")

    def plotter(self) -> sns.FacetGrid:
        fg = sns.catplot(
            self.plotting_data,
            kind="count",
            x=self.x_column,
            y=self.y_column,
            hue=self.hue_column,
            row=self.row_column,
            col=self.col_column,
            col_wrap=self.n_cols,
            log_scale=(self.log_x, self.log_y),
            legend=self.legend,
            palette=self.get_palette(),
            stat=self.plot_statistic,
            gap=self.gap,
            dodge=self.dodge,
            saturation=self.saturation,
            fill=self.fill,
            alpha=self.alpha,
        )
        for ax in fg.axes.flatten():
            ax.grid()
        fg = fg.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["x"].to_kwargs()
        )
        fg = fg.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["y"].to_kwargs()
        )
        return fg

    @typing.override
    def plot(self):
        self.on_plot()
        try:
            facetgrid = self.plotter()
            facetgrid.figure.show()
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())

    @typing.override
    def dynamic_plot(self):
        if self.dynamic_plot_widget is None:
            self.dynamic_plot_widget = EmbeddedDynamicPlot(
                self.dataexplorer,
                self.datastore,
                f"Count Plot: {self.datastore.name}",
                self,
            )
            self.dynamic_callback_id = self.datastore.add_filter_change_callback(
                self.redraw_dynamic_plot
            )
            self.redraw_dynamic_plot()
        else:
            self.error(
                "You cannot make more than two dynamic plots for each plotting widget dialog."
            )

    @typing.override
    def redraw_dynamic_plot(self):
        if self.dynamic_plot_widget is None:
            self.debug("Incorrect call of self.dynamic_plot_widget")
            return
        self.on_plot()
        try:
            plot = self.plotter()
            self.dynamic_plot_widget.update_dynamic_widget(plot)
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())
            return

    @typing.override
    def delete_dynamic_plot(self):
        self.debug("Dynamic Plot Widget Deleted")
        self.dynamic_plot_widget = None
        self.datastore.remove_filter_change_callback(self.dynamic_callback_id)
        self.dynamic_callback_id = -1

    @typing.override
    def closeEvent(self, event: QCloseEvent):
        if self.dynamic_plot_widget is not None:
            _ = self.dynamic_plot_widget.close()

        return super().closeEvent(event)

    @typing.override
    def on_widget_change(self):
        if self.dynamic_plot_widget is not None:
            self.redraw_dynamic_plot()


@typing.final
class CorrPlotDialog(PlottingDialog):
    variable_columns: list[str] = []
    y_columns: list[str] = []
    correl_statistic: str = "pearson"
    annot: bool = False
    linewidths: float = 0
    vmin: float | None = None
    vmax: float | None = None

    def __init__(self, dataexplorer: "DataExplorer", datastore: "DataStore"):
        super().__init__(dataexplorer, datastore, "Correlation Matrix")

        get_label_widget_row_ = partial(
            get_label_widget_row_callback, callback=self.on_widget_change
        )

        self.variable_columns_combobox = self.setup_column_combobox()
        variable_columns_combobox = get_label_widget_row_(
            "Variables", self.variable_columns_combobox
        )
        self.y_columns_combobox = self.setup_column_combobox()
        self.y_columns_combobox.setToolTip(
            "Optional: select variables here if you do not want a square heatmap."
        )
        y_columns_combobox = get_label_widget_row_(
            "Y Variables", self.y_columns_combobox
        )

        self.annot_checkbox = QCheckBox("Annotate")

        self.set_vmin_checkbox = QCheckBox()
        _ = self.set_vmin_checkbox.toggled.connect(lambda: self.toggle_vmin())
        self.vmin_spinbox = QDoubleSpinBox(
            minimum=-1.0, maximum=1.0, value=-1.0, singleStep=0.1
        )
        self.vmin_spinbox.setEnabled(False)
        vmin_spinbox = get_label_widget_row_(
            "Minimum colorbar value", self.vmin_spinbox
        )

        self.set_vmax_checkbox = QCheckBox()
        _ = self.set_vmax_checkbox.toggled.connect(lambda: self.toggle_vmax())
        self.vmax_spinbox = QDoubleSpinBox(
            minimum=-1.0, maximum=1.0, value=1.0, singleStep=0.1
        )
        self.vmax_spinbox.setEnabled(False)
        vmax_spinbox = get_label_widget_row_(
            "Maximum colorbar value", self.vmax_spinbox
        )

        self.linewidths_spinbox = QDoubleSpinBox(
            minimum=0.0, maximum=1.0, value=0.0, singleStep=0.1
        )
        linewidths_spinbox = get_label_widget_row_(
            "Box Separation Linewidth", self.linewidths_spinbox
        )
        self.correl_statistic_combobox = QComboBox()
        self.correl_statistic_combobox.addItems(CORREL_STATISTICS)
        correl_statistic_combobox = get_label_widget_row_(
            "Correlation Statistic", self.correl_statistic_combobox
        )

        plot_button = QPushButton("Plot")
        _ = plot_button.clicked.connect(self.plot)
        dynamic_plot_button = QPushButton("Dynamic Plot")
        _ = dynamic_plot_button.clicked.connect(self.dynamic_plot)

        build_layout_with_callbacks(
            self._layout,
            [
                [variable_columns_combobox, y_columns_combobox],
                [self.annot_checkbox],
                [
                    self.set_vmin_checkbox,
                    vmin_spinbox,
                    self.set_vmax_checkbox,
                    vmax_spinbox,
                ],
                [linewidths_spinbox, correl_statistic_combobox],
                [plot_button, dynamic_plot_button],
            ],
            self.on_widget_change,
        )
        self.show()

    def toggle_vmin(self):
        self.vmin_spinbox.setEnabled(not self.vmin_spinbox.isEnabled())

    def toggle_vmax(self):
        self.vmax_spinbox.setEnabled(not self.vmax_spinbox.isEnabled())

    def setup_column_combobox(self):
        box = MultiSelectComboBox()
        box.addItems(self.datastore.numeric_columns + self.datastore.datetime_columns)
        return box

    @typing.override
    def on_plot(self):
        super().on_plot()
        self.plotting_data = self.plotting_data[  # pyright: ignore[reportAttributeAccessIssue]
            self.datastore.numeric_columns + self.datastore.datetime_columns
        ]
        self.variable_columns = self.variable_columns_combobox.currentData()
        self.y_columns = self.y_columns_combobox.currentData()

        self.correl_statistic = self.correl_statistic_combobox.currentText()

        self.vmin = self.vmin_spinbox.value() if self.vmin_spinbox.isEnabled() else None
        self.vmax = self.vmax_spinbox.value() if self.vmax_spinbox.isEnabled() else None

        if self.vmin is not None and self.vmax is not None:
            if self.vmin >= self.vmax:
                self.error("Minimum colorbar value is greater than maximum")
                return

        if len(self.variable_columns) == 0:
            self.error("No variable columns selected for correlation plotting.")
            return

        if len(self.y_columns) > 0:
            self.plotting_data = self.plotting_data.corr(self.correl_statistic)
            self.plotting_data = self.plotting_data[  # pyright: ignore[reportAttributeAccessIssue]
                self.plotting_data.index.isin(self.y_columns)
            ]
            self.plotting_data = self.plotting_data[self.variable_columns]  # pyright: ignore[reportAttributeAccessIssue]
        else:
            self.plotting_data = self.plotting_data[self.variable_columns].corr(  # pyright: ignore[reportAttributeAccessIssue]
                self.correl_statistic
            )

        self.annot = self.annot_checkbox.isChecked()
        self.linewidths = self.linewidths_spinbox.value()

        self.debug("Correlation Matrix Plot")
        self.debug(f"{self.variable_columns} {self.y_columns}")
        self.debug(f"{self.correl_statistic} {self.annot} {self.linewidths}")
        self.debug(f"{self.vmin} {self.vmax}")

    def plotter(self) -> Figure:
        fig = plt.figure()
        _ = sns.heatmap(
            self.plotting_data,
            vmin=self.vmin,
            vmax=self.vmax,
            annot=self.annot,
            linewidths=self.linewidths,
        )
        ax = plt.gca()
        ax.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["x"].to_kwargs()
        )
        ax.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["y"].to_kwargs()
        )
        return fig

    @typing.override
    def plot(self):
        self.on_plot()
        try:
            self.plotter().show()
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())

    @typing.override
    def dynamic_plot(self):
        if self.dynamic_plot_widget is None:
            self.dynamic_plot_widget = EmbeddedDynamicPlot(
                self.dataexplorer,
                self.datastore,
                f"Correlation Matrix: {self.datastore.name}",
                self,
            )
            self.dynamic_callback_id = self.datastore.add_filter_change_callback(
                self.redraw_dynamic_plot
            )
            self.redraw_dynamic_plot()
        else:
            self.error(
                "You cannot make more than two dynamic plots for each plotting widget dialog."
            )

    @typing.override
    def redraw_dynamic_plot(self):
        if self.dynamic_plot_widget is None:
            self.debug("Incorrect call of self.dynamic_plot_widget")
            return
        self.on_plot()
        try:
            plot = self.plotter()
            self.dynamic_plot_widget.update_dynamic_widget(plot)
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())
            return

    @typing.override
    def delete_dynamic_plot(self):
        self.debug("Dynamic Plot Widget Deleted")
        self.dynamic_plot_widget = None
        self.datastore.remove_filter_change_callback(self.dynamic_callback_id)
        self.dynamic_callback_id = -1

    @typing.override
    def closeEvent(self, event: QCloseEvent):
        if self.dynamic_plot_widget is not None:
            _ = self.dynamic_plot_widget.close()

        return super().closeEvent(event)

    @typing.override
    def on_widget_change(self):
        if self.dynamic_plot_widget is not None:
            self.redraw_dynamic_plot()


class LinePlotMode(Enum):
    RELPLOT = auto()
    MULTI_Y_SUBPLOT = auto()
    MULTI_Y_SINGLE_Y_AX = auto()
    MULTI_Y_MULTI_Y_AX = auto()
    INVALID = auto()


@typing.final
class LineDialog(PlottingDialog):
    x_column: str = ""
    y_columns: list[str] = []
    y_column: str = ""
    hue_column: str | None = None
    style_column: str | None = None
    col_column: str | None = None
    row_column: str | None = None
    size_column: str | None = None
    n_cols: int = 3
    log_x: bool = False
    log_y: bool = False
    multi_y_handler: str = ""
    alpha: float = 1.0
    add_marker: bool = False
    marker: str = MARKERS[0]
    linestyle: str = LINE_STYLES[0]
    plot_mode = LinePlotMode.RELPLOT

    def __init__(self, dataexplorer: "DataExplorer", datastore: "DataStore"):
        super().__init__(dataexplorer, datastore, "Line")

        get_label_widget_row_ = partial(
            get_label_widget_row_callback, callback=self.on_widget_change
        )

        self.x_column_combobox = self.setup_column_combobox(True)
        x_column_combobox = get_label_widget_row_(
            "X Axis Variable", self.x_column_combobox
        )
        self.y_columns_combobox = self.setup_column_combobox(True, True)
        y_columns_combobox = get_label_widget_row_(
            "Y Axis Variables", self.y_columns_combobox
        )

        self.hue_column_combobox = self.setup_column_combobox(False)
        self.hue_column_combobox.setToolTip("Does not work with multiple y-variables.")
        hue_column_combobox = get_label_widget_row_("Hue", self.hue_column_combobox)
        self.style_column_combobox = self.setup_column_combobox(False)
        self.style_column_combobox.setToolTip(
            "Does not work with multiple y-variables."
        )
        style_column_combobox = get_label_widget_row_(
            "Style", self.style_column_combobox
        )

        self.col_column_combobox = self.setup_column_combobox(False)
        col_column_combobox = get_label_widget_row_("Column", self.col_column_combobox)
        self.col_column_combobox.setToolTip("Does not work with multiple y-variables.")
        self.row_column_combobox = self.setup_column_combobox(False)
        self.row_column_combobox.setToolTip("Does not work with multiple y-variables.")
        row_column_combobox = get_label_widget_row_("Row", self.row_column_combobox)
        self.size_column_combobox = self.setup_column_combobox(False)
        self.size_column_combobox.setToolTip("Does not work with multiple y-variables.")
        size_column_combobox = get_label_widget_row_("Size", self.size_column_combobox)

        self.log_x_checkbox = QCheckBox("Log X")
        self.log_y_checkbox = QCheckBox("Log Y")

        collapsible = QCollapsible("Additional Settings")
        collapsible_widget = self.dataexplorer.get_widget()
        collapsible.addWidget(collapsible_widget)
        vbox_widget = QVBoxLayout(collapsible_widget)

        self.multi_y_handler_combo_box = QComboBox()
        self.multi_y_handler_combo_box.addItems(
            ["Subplots", "Single y-axis", "Upto 4 y-axes"]
        )
        multi_y_handler_combo_box = get_label_widget_row_(
            ">1 y variable", self.multi_y_handler_combo_box
        )

        self.n_cols_spinbox = QSpinBox(minimum=1, maximum=10, value=3)
        n_cols_spinbox = get_label_widget_row_(
            "Max # of subplot columns", self.n_cols_spinbox
        )

        self.alpha_slider = QLabeledDoubleSlider()
        self.alpha_slider.setValue(1.0)
        self.alpha_slider.setRange(0, 1)
        self.alpha_slider.setEdgeLabelMode(
            QLabeledDoubleSlider.EdgeLabelMode.LabelIsValue
        )
        alpha_slider = get_label_widget_row_("Opacity", self.alpha_slider)

        self.marker_combobox = QComboBox()
        self.marker_combobox.addItems(MARKERS)
        marker_combobox = get_label_widget_row_("Marker:", self.marker_combobox)
        self.linestyle_combobox = QComboBox()
        self.linestyle_combobox.addItems(LINE_STYLES)
        linestyle_combobox = get_label_widget_row_(
            "Line Style:", self.linestyle_combobox
        )

        self.palette_type_combobox = QComboBox()
        self.palette_type_combobox.addItems(PALETTE_TYPES)
        palette_type_combobox = get_label_widget_row_(
            "Palette Type", self.palette_type_combobox
        )

        build_layout_with_callbacks(
            vbox_widget,
            [
                [multi_y_handler_combo_box, n_cols_spinbox],
                [alpha_slider, marker_combobox],
                [linestyle_combobox],
                [palette_type_combobox],
            ],
            self.on_widget_change,
        )

        plot_button = QPushButton("Plot")
        _ = plot_button.clicked.connect(self.plot)
        dynamic_plot_button = QPushButton("Dynamic Plot")
        _ = dynamic_plot_button.clicked.connect(self.dynamic_plot)

        build_layout_with_callbacks(
            self._layout,
            [
                [x_column_combobox, y_columns_combobox],
                [hue_column_combobox, style_column_combobox, size_column_combobox],
                [col_column_combobox, row_column_combobox],
                [self.log_y_checkbox, self.log_x_checkbox],
                [collapsible],
                [plot_button, dynamic_plot_button],
            ],
            self.on_widget_change,
        )
        self.show()

    def setup_column_combobox(self, mandatory: bool, multi_variable: bool = False):
        if multi_variable:
            box = MultiSelectComboBox()
        else:
            box = QComboBox()
        if mandatory:
            box.addItems(self.datastore.columns)
        else:
            box.addItem("")
            box.addItems(self.datastore.columns)
        return box

    @typing.override
    def on_plot(self):
        self.plot_mode = LinePlotMode.INVALID
        super().on_plot()
        self.x_column = self.x_column_combobox.currentText()
        self.y_columns = self.y_columns_combobox.currentData()
        self.multi_y_handler = self.multi_y_handler_combo_box.currentText()

        self.log_x = self.log_x_checkbox.isChecked()
        self.log_y = self.log_y_checkbox.isChecked()
        self.n_cols = self.n_cols_spinbox.value()
        self.alpha = self.alpha_slider.value()
        self.marker = self.marker_combobox.currentText()
        self.linestyle = self.linestyle_combobox.currentText()
        self.palette_type = self.palette_type_combobox.currentText()

        if len(self.y_columns) == 0:
            self.error("No Y columns selected!")
            return

        self.debug("Plotting LinePlot:")
        self.debug(f"{self.x_column} {self.y_columns}")
        self.debug(f"{self.log_x} {self.log_y}")

        if len(self.y_columns) > 1:
            self.debug(f"{self.multi_y_handler}")
            match self.multi_y_handler:
                case "Subplots":
                    self.plot_mode = LinePlotMode.MULTI_Y_SUBPLOT
                case "Single y-axis":
                    self.plot_mode = LinePlotMode.MULTI_Y_SINGLE_Y_AX
                case "Upto 4 y-axes":
                    if len(self.y_columns) > 4:
                        self.error(">4 y columns selected")
                        return
                    self.plot_mode = LinePlotMode.MULTI_Y_MULTI_Y_AX
                case _:
                    self.error("Invalid multi_y_handler selected.")
                    self.debug(self.multi_y_handler)
                    return
            return

        self.y_column = self.y_columns[0]
        self.plot_mode = LinePlotMode.RELPLOT

        self.hue_column = self.hue_column_combobox.currentText()
        self.style_column = self.style_column_combobox.currentText()
        self.col_column = self.col_column_combobox.currentText()
        self.row_column = self.row_column_combobox.currentText()
        self.size_column = self.size_column_combobox.currentText()

        self.debug(f"{self.hue_column} {self.style_column}")
        self.debug(f"{self.col_column} {self.row_column} {self.size_column}")

        self.hue_column = self.get_categorical_column_name(self.hue_column)
        self.style_column = self.get_categorical_column_name(self.style_column)
        self.col_column = self.get_categorical_column_name(self.col_column)
        self.row_column = self.get_categorical_column_name(self.row_column)
        self.size_column = self.get_categorical_column_name(self.size_column)

    def plotter(self) -> Figure | sns.FacetGrid:
        self.debug(str(self.plot_mode))
        match self.plot_mode:
            case LinePlotMode.RELPLOT:
                col_wrap = None if self.col_column is None else self.n_cols
                fg = sns.relplot(
                    self.plotting_data,
                    x=self.x_column,
                    y=self.y_column,
                    hue=self.hue_column,
                    size=self.size_column,
                    style=self.style_column,
                    row=self.row_column,
                    col=self.col_column,
                    col_wrap=col_wrap,
                    palette=self.get_palette(),
                    kind="line",
                    alpha=self.alpha,
                )
                for ax in fg.axes.flatten():
                    ax.grid()
                fg = fg.tick_params(
                    **self.dataexplorer.plotter.plot_params["tick_params"][
                        "x"
                    ].to_kwargs()
                )
                fg = fg.tick_params(
                    **self.dataexplorer.plotter.plot_params["tick_params"][
                        "y"
                    ].to_kwargs()
                )
                return fg
            case LinePlotMode.MULTI_Y_SUBPLOT:
                return self._subplots()
            case LinePlotMode.MULTI_Y_SINGLE_Y_AX:
                return self._multi_y_single_ax()
            case LinePlotMode.MULTI_Y_MULTI_Y_AX:
                return self._multi_y_multi_ax()
            case LinePlotMode.INVALID:
                return plt.figure()

    def _subplots(self) -> Figure:
        n_rows = ceil(len(self.y_columns) / self.n_cols)
        fig, axs = plt.subplots(nrows=n_rows, ncols=self.n_cols, sharex=True)  # pyright: ignore[reportAny]
        assert isinstance(axs, ndarray)
        axs = axs.flatten()

        for ax, y_col in zip(axs, self.y_columns):  # pyright: ignore[reportAny]
            if not isinstance(ax, Axes):
                self.error("Not an axis instance (subplots)")
                return fig
            _ = ax.plot(
                self.plotting_data[self.x_column],  # pyright: ignore[reportUnknownArgumentType]
                self.plotting_data[y_col],  # pyright: ignore[reportUnknownArgumentType]
                marker=self.marker,
                linestyle=self.linestyle,
                alpha=self.alpha,
            )
            _ = ax.set_title(f"{y_col} vs {self.x_column}")
            _ = ax.set_ylabel(y_col)
            _ = ax.set_xlabel(self.x_column)
            ax.tick_params(
                **self.dataexplorer.plotter.plot_params["tick_params"]["x"].to_kwargs()
            )
            ax.tick_params(
                **self.dataexplorer.plotter.plot_params["tick_params"]["y"].to_kwargs()
            )
        return fig

    def _multi_y_single_ax(self) -> Figure:
        fig, ax = plt.subplots()
        for y_col in self.y_columns:
            _ = ax.plot(
                self.plotting_data[self.x_column],  # pyright: ignore[reportUnknownArgumentType]
                self.plotting_data[y_col],  # pyright: ignore[reportUnknownArgumentType]
                label=y_col,
                marker=self.marker,
                linestyle=self.linestyle,
                alpha=self.alpha,
            )
        _ = ax.set_title(", ".join(self.y_columns) + f" vs {self.x_column}", wrap=True)
        _ = ax.set_xlabel(self.x_column)
        _ = ax.set_ylabel(", ".join(self.y_columns), wrap=True)
        ax.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["x"].to_kwargs()
        )
        ax.tick_params(
            **self.dataexplorer.plotter.plot_params["tick_params"]["y"].to_kwargs()
        )
        _ = plt.legend()
        return fig

    def _multi_y_multi_ax(self) -> Figure:
        fig, ax = plt.subplots()
        assert isinstance(ax, Axes)

        if len(self.y_columns) > 2:
            fig.subplots_adjust(right=0.8)
        loc_array = [0, 0, 1.1, 1.2]
        colors = ["black", "red", "green", "magenta"]

        axes = [ax]

        while len(axes) < len(self.y_columns):
            axes.append(ax.twinx())

        for color, loc, y_col, axis in zip(colors, loc_array, self.y_columns, axes):
            if loc != 0:
                axis.spines.right.set_position(("axes", loc))
            _ = axis.plot(
                self.plotting_data[self.x_column],  # pyright: ignore[reportUnknownArgumentType]
                self.plotting_data[y_col],  # pyright: ignore[reportUnknownArgumentType]
                c=color,
                marker=self.marker,
                linestyle=self.linestyle,
                alpha=self.alpha,
            )
            if self.log_x:
                axis.set_xscale("log")
            if self.log_y:
                axis.set_yscale("log")

            _ = axis.set_ylabel(y_col)
            axis.tick_params(axis="y", colors=color)
            axis.tick_params(
                **self.dataexplorer.plotter.plot_params["tick_params"]["x"].to_kwargs()
            )
            axis.tick_params(
                **self.dataexplorer.plotter.plot_params["tick_params"]["y"].to_kwargs()
            )
            axis.yaxis.label.set_color(color)

        _ = ax.set_title(", ".join(self.y_columns) + f" vs {self.x_column}", wrap=True)

        return fig

    @typing.override
    def plot(self):
        self.on_plot()
        if self.plot_mode == LinePlotMode.INVALID:
            return
        try:
            facetgrid = self.plotter()
            if isinstance(facetgrid, Figure):
                facetgrid.show()
            else:
                facetgrid.figure.show()
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())

    @typing.override
    def dynamic_plot(self):
        if self.dynamic_plot_widget is None:
            self.dynamic_plot_widget = EmbeddedDynamicPlot(
                self.dataexplorer,
                self.datastore,
                f"Line Plot: {self.datastore.name}",
                self,
            )
            self.dynamic_callback_id = self.datastore.add_filter_change_callback(
                self.redraw_dynamic_plot
            )
            self.redraw_dynamic_plot()
        else:
            self.error(
                "You cannot make more than two dynamic plots for each plotting widget dialog."
            )

    @typing.override
    def redraw_dynamic_plot(self):
        if self.dynamic_plot_widget is None:
            self.debug("Incorrect call of self.dynamic_plot_widget")
            return
        self.on_plot()
        if self.plot_mode == LinePlotMode.INVALID:
            return
        try:
            plot = self.plotter()
            self.dynamic_plot_widget.update_dynamic_widget(plot)
        except Exception:
            self.error("Unable to plot. Err: " + traceback.format_exc())
            return

    @typing.override
    def delete_dynamic_plot(self):
        self.debug("Dynamic Plot Widget Deleted")
        self.dynamic_plot_widget = None
        self.datastore.remove_filter_change_callback(self.dynamic_callback_id)
        self.dynamic_callback_id = -1

    @typing.override
    def closeEvent(self, event: QCloseEvent):
        if self.dynamic_plot_widget is not None:
            _ = self.dynamic_plot_widget.close()

        return super().closeEvent(event)

    @typing.override
    def on_widget_change(self):
        if self.dynamic_plot_widget is not None:
            self.redraw_dynamic_plot()
