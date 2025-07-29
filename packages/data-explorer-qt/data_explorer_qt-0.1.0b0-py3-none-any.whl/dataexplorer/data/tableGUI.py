from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTableView, QVBoxLayout, QWidget
import pandas as pd


class TableViewer:
    def __init__(self, dataexplorer, data: pd.DataFrame, name: str):
        self.table_viewer = self.dataexplorer.get_widget()
        self.table_viewer.setObjectName("TableViewer")
        self.table_viewer.setStyleSheet(dataexplorer.stylesheet)
        self.table_viewer.setWindowTitle(f"Table Viewer: {name}")
        self.table_viewer.setGeometry(100, 100, 800, 400)
        self.table_viewer.setFont(QFont(dataexplorer.font, dataexplorer.font_size))
        self.table_view = QTableView()
        self.model = TableViewModel(data)
        self.table_view.setModel(self.model)
        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        self.table_viewer.setLayout(layout)
        self.table_viewer.show()


class TableViewModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            elif orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
        return None
