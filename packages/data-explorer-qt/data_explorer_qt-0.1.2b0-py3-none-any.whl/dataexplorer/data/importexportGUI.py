# pyright: reportAny=false, reportUnknownVariableType=false, reportUninitializedInstanceVariable=false
from collections.abc import Iterable
import typing
from pathlib import Path
from functools import partial
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QRadioButton,
    QWidget,
    QGridLayout,
)
from PySide6.QtCore import (
    Qt,
)
import pandas as pd

from dataexplorer.data.dataenums import (
    NAN_CAT,
    NAN_DATETIME,
    NAN_NUM,
    VALID_DTYPES,
    NaNOperation,
)
from ..guihelper import build_layout
from ..guihelper import get_dynamic_scroll_area
from .datamodel import (
    DataModel,
    categorical_comparator,
    datetime_comparator,
    handle_dtype_operation,
    handle_nan_operation,
    numeric_comparator,
)

if typing.TYPE_CHECKING:
    from ..dataexplorer import DataExplorer


@typing.final
class DataImporter:
    data: pd.DataFrame

    def __init__(self, dataexplorer: "DataExplorer"):
        self.dataexplorer: "DataExplorer" = dataexplorer
        self.datamodel: DataModel = dataexplorer.datamodel
        self.error = dataexplorer.error
        self.debug = dataexplorer.debug

        file_types: list[str] = dataexplorer.config["File Types"]["import"]
        file_path: str
        filetype: str
        file_path, filetype = QFileDialog.getOpenFileName(
            parent=None,
            caption="Open Data File",
            filter=";;".join(file_types),
        )
        if not file_path:
            self.error("Empty File Path.")
            return

        self.dataexplorer.info(f"File Selected: {file_path}")
        self._read_file(file_path, filetype)
        self.debug(f"{self.data.head()}")
        self.debug(f"{self.data.shape}")
        self.file_name: str = Path(file_path).stem

        self._validate_import()

    def _validate_import(self):
        self._validate_import_widget = self._create_widget(800, 600)
        self.layout = QVBoxLayout(self._validate_import_widget)
        self.layout.setSpacing(5)

        top_label = QLabel("Data Details")
        top_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        shape_label = QLabel(
            f"Rows: {self.data.shape[0]},\nColumns: {self.data.shape[1]}"
        )
        shape_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        column_label = QLabel("Column Names:\n")
        column_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        columns_scroll_area, scroll_area_widget = get_dynamic_scroll_area(
            self.dataexplorer.get_widget, width=750
        )
        scroll_area_vbox = QVBoxLayout(scroll_area_widget)
        scroll_area_layout = QGridLayout()

        for i, column in enumerate(self.data.columns):
            label = QLabel(column)  # pyright: ignore[reportUnknownArgumentType]
            scroll_area_layout.addWidget(label, self._row(i), self._col(i))
        build_layout(scroll_area_vbox, [column_label, scroll_area_layout])
        nan_label = QLabel("Default NaN Handling")

        nan_hbox = QHBoxLayout()
        nan_hbox.setSpacing(5)
        nan_sub_vbox = QVBoxLayout()

        categorical_hbox = QHBoxLayout()
        label_nan_categorical = QLabel("Categorical: ")
        self.default_nan_categorical: QComboBox = QComboBox()
        build_layout(
            categorical_hbox, [label_nan_categorical, self.default_nan_categorical]
        )

        numeric_hbox = QHBoxLayout()
        label_nan_numeric = QLabel("Numeric: ")
        self.default_nan_numeric: QComboBox = QComboBox()
        build_layout(numeric_hbox, [label_nan_numeric, self.default_nan_numeric])

        datetime_hbox = QHBoxLayout()
        label_nan_datetime = QLabel("Datetime: ")
        self.default_nan_datetime: QComboBox = QComboBox()
        build_layout(datetime_hbox, [label_nan_datetime, self.default_nan_datetime])

        build_layout(nan_sub_vbox, [categorical_hbox, numeric_hbox, datetime_hbox])
        build_layout(nan_hbox, [nan_label, nan_sub_vbox])

        self.default_nan_categorical.addItems(NAN_CAT)
        self.default_nan_numeric.addItems(NAN_NUM)
        self.default_nan_datetime.addItems(NAN_DATETIME)

        continue_button = QPushButton("Continue to set dtype")
        _ = continue_button.clicked.connect(self._set_dtypes)

        self.default_custom_radio_button = (
            QRadioButton("Handle missing values by dtype using defaults"),
            QRadioButton("Handle missing values on a per-column basis"),
        )
        self.default_custom_radio_button[1].setChecked(True)
        radio_button_vbox = QVBoxLayout()
        build_layout(radio_button_vbox, [*self.default_custom_radio_button])

        widget_list = [
            top_label,
            shape_label,
            columns_scroll_area,
            nan_hbox,
            radio_button_vbox,
            continue_button,
        ]
        build_layout(self.layout, widget_list)
        self._validate_import_widget.setLayout(self.layout)
        self._validate_import_widget.update()
        self._validate_import_widget.show()

    def _set_dtypes(self):
        self.default_nan_cat: str = self.default_nan_categorical.currentText()
        self.default_nan_num: str = self.default_nan_numeric.currentText()
        self.default_nan_dt: str = self.default_nan_datetime.currentText()
        self._close_widget(self._validate_import_widget)

        self._dtype_widget = self._create_widget(800, 600)
        self.dtypes: dict[str, str] = {}
        self.layout = QVBoxLayout()

        dtype_grid = QGridLayout()
        self.dtype_widgets: dict[str, QComboBox] = {}

        for i, column in enumerate(self.data.columns):
            try:
                hbox = QHBoxLayout()
                label = QLabel(f"{column}:")
                if numeric_comparator(self.data[column]):
                    widg = self.dtype_widgets[column] = QComboBox()
                    widg.addItems(VALID_DTYPES)
                    widg.setCurrentText(VALID_DTYPES[1])
                elif categorical_comparator(self.data[column]):
                    widg = self.dtype_widgets[column] = QComboBox()
                    widg.addItems(VALID_DTYPES)
                    widg.setCurrentText(VALID_DTYPES[0])
                elif datetime_comparator(self.data[column]):
                    widg = self.dtype_widgets[column] = QComboBox()
                    widg.addItems(VALID_DTYPES)
                    widg.setCurrentText(VALID_DTYPES[2])
                else:
                    self.error(f"Invalid dtype seen. {column}")
                    self._close_widget(self._dtype_widget)
                    return
                function = partial(self._dtype_setter, column=column)  # pyright: ignore[reportUnkownMemberType]
                _ = widg.currentTextChanged.connect(function)
                build_layout(hbox, [label, widg])
                dtype_grid.addLayout(hbox, self._row(i), self._col(i))
                self.debug(
                    f'Dtype, Row, Col: "{widg.currentText()}", {self._row(i)}, {self._col(i)}'
                )
            except TypeError as e:
                self.error(f"Error reading column {column}: {e}")
                self._close_widget(self._dtype_widget)
                return

        button = QPushButton("Continue")
        _ = button.clicked.connect(self._process_dtypes)
        scroll_content_widget, content_widget = get_dynamic_scroll_area(
            self.dataexplorer.get_widget, width=750
        )
        content_widget.setLayout(dtype_grid)
        build_layout(self.layout, [scroll_content_widget, button])
        self._dtype_widget.setLayout(self.layout)
        self._dtype_widget.show()

    def _dtype_setter(self, *value, column: str):
        self.debug(f"{column} ComboBox Changed")
        self.dtypes[column] = value[0]

    def _process_dtypes(self):
        for column in self.dtypes:
            self.data[column] = handle_dtype_operation(
                self.data.loc[:, column], self.dtypes[column], self.debug
            )
            self.debug(
                f"Dtype conversion applied: {self.dtypes[column]} to column {column}"
            )
        self._handle_nans()

    def _row(self, n: int) -> int:
        grid_max_col = self.dataexplorer.config["Grid"]["grid_max_col"]
        return int(n / grid_max_col)

    def _col(self, n: int) -> int:
        grid_max_col = self.dataexplorer.config["Grid"]["grid_max_col"]
        return n % grid_max_col

    def _handle_nans(self):
        self._close_widget(self._dtype_widget)
        self._nan_widget = self._create_widget(800, 600)
        self.layout = QVBoxLayout()

        label = QLabel("Handle Missing Values")
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        nan_grid = QGridLayout()
        self.nan_widgets = {}

        nan_columns: Iterable[str] = self.data.columns[self.data.isnull().any()]

        if len(nan_columns) == 0:
            self._process_nans()
            return

        for i, column in enumerate(nan_columns):
            try:
                hbox = QHBoxLayout()
                label = QLabel(f"{column}:")
                self.debug(f"{column}: {self.data[column].dtype}")
                if numeric_comparator(self.data[column]):
                    widg = self.nan_widgets[column] = QComboBox()
                    widg.addItems(NAN_NUM)
                    widg.setCurrentText(self.default_nan_num)
                elif categorical_comparator(self.data[column]):
                    widg = self.nan_widgets[column] = QComboBox()
                    widg.addItems(NAN_CAT)
                    widg.setCurrentText(self.default_nan_cat)
                elif datetime_comparator(self.data[column]):
                    widg = self.nan_widgets[column] = QComboBox()
                    widg.addItems(NAN_DATETIME)
                    widg.setCurrentText(self.default_nan_dt)
                else:
                    self.error(f"Invalid dtype seen {column}.")
                    self._close_widget(self._nan_widget)
                    return
                build_layout(hbox, [label, widg])
                nan_grid.addLayout(hbox, self._row(i), self._col(i))
                self.debug(
                    f'NaN, Row, Col: "{widg.currentText()}", {self._row(i)}, {self._col(i)}'
                )
            except TypeError as e:
                self.error(f"Error reading column {column}: {e}")
                self._close_widget(self._nan_widget)
                return

        if self.default_custom_radio_button[0].isChecked():
            self._process_nans()
            return

        nan_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button = QPushButton("Continue")
        _ = button.clicked.connect(self._process_nans)
        scroll_content_widget, content_widget = get_dynamic_scroll_area(
            self.dataexplorer.get_widget, width=750
        )
        content_widget.setLayout(nan_grid)
        build_layout(self.layout, [label, scroll_content_widget, button])
        self._nan_widget.setLayout(self.layout)
        self._nan_widget.show()

    def _process_nans(self):
        self.nans = {}
        n_rows = self.data.shape[0]
        for column in self.nan_widgets:
            self.nans[column] = self.nan_widgets[column].currentText()
            self.data = handle_nan_operation(
                self.data, self.nans[column], column, self.debug
            )
            if self.nans[column] == NaNOperation.DROP_ROWS.value:
                self.debug(
                    f"Dropped {n_rows - self.data.shape[0]} rows for column {column}"
                )
                n_rows = self.data.shape[0]
        self._close_widget(self._nan_widget)
        self._add_data()

    def _add_data(self):
        self.debug(self.nans)
        self.debug(self.dtypes)
        self.datamodel.add_dataset_to_model(
            self.data, self.file_name, {"NaN": self.nans, "dtype": self.dtypes}
        )

    def _create_widget(self, w: int, h: int) -> QWidget:
        widget = self.dataexplorer.get_widget()
        widget.setObjectName("DataImporter")
        widget.setWindowTitle("Data Importer")
        widget.resize(w, h)
        widget.setFont(QFont(self.dataexplorer.font, self.dataexplorer.font_size))
        self.dataexplorer.owned_widgets.append(widget)
        return widget

    def _read_file(self, file_path: str, filetype: str):
        if filetype.startswith("Excel"):
            excel_file = pd.ExcelFile(file_path)
            if len(excel_file.sheet_names) > 1:
                self.error(
                    "Excel file has more than 1 sheet. Importing the first sheet."
                )
            self.data = pd.read_excel(file_path, engine="calamine")
        elif filetype.startswith("CSV"):
            self.data = pd.read_csv(file_path)
        elif filetype.startswith("Parquet"):
            self.data = pd.read_parquet(file_path)
        elif filetype.startswith("Feather"):
            self.data = pd.read_feather(file_path)
        else:
            self.error("Import failed! Invalid filetype.")

    def _close_widget(self, widget: QWidget):
        self.dataexplorer.owned_widgets.remove(widget)
        _ = widget.close()


def export_data(dataexplorer: "DataExplorer", data: pd.DataFrame):
    file_path, selFilter = QFileDialog.getSaveFileName(
        parent=None,
        caption="Save Data File",
        filter=";;".join(dataexplorer.config["File Types"]["export"]),
    )
    if file_path:
        try:
            if selFilter.startswith("Excel"):
                data = get_naive_dataframe(data)
                data.to_excel(file_path, index=True)
            elif selFilter.startswith("CSV"):
                data.to_csv(file_path, index=True)
            elif selFilter.startswith("Parquet"):
                data.to_parquet(file_path, index=True)
            elif selFilter.startswith("Feather"):
                data.to_feather(file_path)
        except Exception as e:
            dataexplorer.error(str(e))
        else:
            dataexplorer.status_message("File saved")
    else:
        dataexplorer.status_message("No save file set.")


def get_naive_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        try:
            df[col] = df[col].dt.tz_localize(None)
        except Exception:
            pass
    try:
        df.index = df.index.tz_localize(None)  # pyright: ignore[reportAttributeAccessIssue]
    except Exception:
        pass
    return df
