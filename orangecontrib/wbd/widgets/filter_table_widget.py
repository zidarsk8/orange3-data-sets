"""Modul for the filter table widget."""

import logging
import collections

import observable
from PyQt4 import QtGui

from orangecontrib.wbd.widgets import simple_filter_widget
from orangecontrib.wbd.widgets import benchmark

logger = logging.getLogger(__name__)


class MaxWithLabel(QtGui.QLabel):

    MAX_TITLE_CHARS = 30

    def setText(self, text):
        if len(text) > self.MAX_TITLE_CHARS:
            text = text[:self.MAX_TITLE_CHARS - 3] + "..."
        super().setText(text)


class FilterTableWidget(QtGui.QWidget):
    """Main filter table widget.

    This widget is used for displaying filtering and selecting any kind of data
    fetched.
    """

    def __init__(self, **kwargs):
        super().__init__()

        layout = QtGui.QGridLayout()

        self.filter_widget = simple_filter_widget.SimpleFilterWidget()
        self.table_widget = FilterDataTableWidget(**kwargs)
        layout.addWidget(self.filter_widget)
        layout.addWidget(self.table_widget)

        self.setLayout(layout)
        if callable(getattr(self.table_widget, "filter_data", None)):
            self.filter_widget.register_callback(self.table_widget.filter_data)

    def get_selected_data(self):
        """Get data for user selected rows.

        Returns:
            list of dicts for all rows that a user has selected.
        """
        return self.table_widget.get_selected_data()


class FilterDataTableWidget(QtGui.QTableWidget, observable.Observable):
    """Widget for displaying array of dicts in a table widget."""

    DEFAULT_ORDER = [
        "id",
        "name",
        "description",
    ]

    ORDER_MAP = {name: index for index, name in enumerate(DEFAULT_ORDER)}

    def __init__(self, data=None, multi_select=False):
        """Init data table widget.

        Args:
            data (list): List of dicts where each key in the dict represents a
                column in the table. All dicts must contain all the same keys.
        """
        super(FilterDataTableWidget, self).__init__()

        self.selected_ids = []
        self.events = collections.defaultdict(list)
        self.previous_filter = None
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        if not multi_select:
            self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.filtered_data = {}
        self.itemSelectionChanged.connect(self.selection_changed)
        self.setSortingEnabled(True)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.set_data(data)

    def selection_changed(self):
        rows = self.selectionModel().selectedRows()
        self.selected_ids = []
        for row in rows:
            self.selected_ids.append(self.item(row.row(), 0).text())

        self.trigger("selection_changed", self.selected_ids)

    def set_data(self, data):
        self.data = data or []
        with benchmark.Benchmark("init filter data table"):
            self._draw_items()

    def filter_data(self, filter_str=""):
        """Filter data with a string and refresh the table.

        Args:
            filter_str (str): String for filtering rows of data.
        """
        logger.debug("filter data with: %s", filter_str)
        if self.previous_filter == filter_str:
            return
        if filter_str:
            with benchmark.Benchmark("Filtering values"):
                filtered_list = [
                    item for item in self.data if
                    any(filter_str.lower() in value.lower()
                        for value in item.values())
                ]
        else:
            filtered_list = self.data

        self._draw_items(filtered_list)
        self.previous_filter = filter_str

    def _draw_items(self, data=None):
        """Redraw all items.

        Fill the table widget with the data given. The keys of the dict are set
        for table headers and all the data is displayed below.

        Args:
            data (list of dict): Data that will be drawn. If none is given, it
                defaults to self.data.
        """
        logger.debug("Redrawing all items")
        if data is None:
            data = self.data
        if not data:
            logger.debug("No data items to draw")
            self.setRowCount(0)
            return

        headers, data = data[0], data[1:]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        self.filtered_data = data
        self.setRowCount(len(data))

        for row, row_data in enumerate(data):
            for column, cell_data in enumerate(row_data):
                self.setItem(row, column, QtGui.QTableWidgetItem(cell_data))

        if len(data) < 500:
            self.resizeColumnsToContents()
        else:
            self.setColumnWidth(0, 240)  # id field
            for i in range(len(headers) - 1):
                self.setColumnWidth(i, 400)

        if data:
            self.selectRow(0)
            self.selection_changed()

    def set_selected_data(self, filter_=None):
        self.clearSelection()
        if filter_ is None:
            return
        selection = self.selectionModel().selection()
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                if filter_.lower() in self.item(row, column).text().lower():
                    self.selectRow(row)
                    selection.merge(self.selectionModel().selection(),
                                    QtGui.QItemSelectionModel.Select)

        self.selectionModel().select(selection,
                                     QtGui.QItemSelectionModel.Select)

    def get_selected_data(self):
        """Get data for user selected rows.

        Returns:
            list of dicts for all rows that a user has selected.
        """
        return self.selected_ids
