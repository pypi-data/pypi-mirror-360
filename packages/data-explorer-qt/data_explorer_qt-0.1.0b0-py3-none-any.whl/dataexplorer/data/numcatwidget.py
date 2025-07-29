from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import typing

from dataexplorer.guihelper import add_callback_to_standard_signal, build_grid_layout

if typing.TYPE_CHECKING:
    from .datamodel import DataStore
    from ..dataexplorer import DataExplorer

from .dataenums import NumericConversion, NUM_TO_CAT_OPS
from .dataenums import NumericConverter


@typing.final
class NumCatWidget(QWidget):
    numeric_converter: NumericConverter

    def __init__(
        self, datastore: "DataStore", column: str, dataexplorer: "DataExplorer"
    ):
        super().__init__()
        self.setStyleSheet(dataexplorer.stylesheet)
        self.debug = dataexplorer.debug
        self.error = dataexplorer.error
        self.column = column
        self.datastore = datastore

        self._layout = QVBoxLayout(self)
        self.setMaximumHeight(200)  # To prevent detaching of title and body.
        column_label = QLabel(column)
        column_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        delete_button = QPushButton("Delete")
        delete_button.setObjectName(
            "DeleteFilter"
        )  # Not the wrong name. Just used for styling.
        _ = delete_button.clicked.connect(self.onDelete)
        self.numeric_converter = NumericConverter(
            conversion=NumericConversion.AS_CATEGORY, value=None
        )
        self.as_category_radio = QRadioButton(NUM_TO_CAT_OPS[0])
        self.as_category_radio.setChecked(True)
        self.bin_n_radio = QRadioButton(NUM_TO_CAT_OPS[1])
        self.bin_n_spinbox = QSpinBox(minimum=1, maximum=1000, value=5)
        self.bin_width_radio = QRadioButton(NUM_TO_CAT_OPS[2])
        self.bin_width_line_edit = QLineEdit()
        self.bin_width_line_edit.setPlaceholderText(
            "Comma-separated list of values: 1, 2, 3"
        )
        build_grid_layout(
            self._layout,
            [
                [column_label],
                [self.as_category_radio],
                [self.bin_n_radio, self.bin_n_spinbox],
                [self.bin_width_radio, self.bin_width_line_edit],
                [delete_button],
            ],
        )

        add_callback_to_standard_signal(
            [
                self.as_category_radio,
                self.bin_n_radio,
                self.bin_n_spinbox,
                self.bin_width_radio,
                self.bin_width_line_edit,
            ],
            self.on_change,
        )

    def on_change(self):
        if self.as_category_radio.isChecked():
            self.numeric_converter.conversion = NumericConversion.AS_CATEGORY
            self.numeric_converter.value = None
        elif self.bin_n_radio.isChecked():
            self.numeric_converter.conversion = NumericConversion.BINNED
            self.numeric_converter.value = self.bin_n_spinbox.value()
        else:
            self.numeric_converter.conversion = NumericConversion.BIN_WIDTH
            string = self.bin_width_line_edit.text()
            try:
                list_floats: list[float] = [float(val) for val in string.split(",")]
            except Exception:
                self.error(
                    "The formatting for bin widths is incorrect. Please check it."
                )
                return
            self.numeric_converter.value = list_floats

        self.datastore.replot_callbacks()

    def onDelete(self):
        self.datastore.on_num_cat_widget_delete(self)
        self.deleteLater()
