"""Modul for the filter table widget."""

import logging

from PyQt4 import QtGui

from orangecontrib.wbd.widgets import simple_filter_widget
from orangecontrib.wbd.widgets import benchmark

import observable
import collections


class MaxWithLabel(QtGui.QLabel):

    MAX_TITLE_CHARS = 30

    def setText(self, text):
        if len(text) > self.MAX_TITLE_CHARS:
            text = text[:self.MAX_TITLE_CHARS - 3] + "..."
        super().setText(text)


class HideWidgetWrapper(QtGui.QWidget):

    TITLE_TEMPLATE = "Title {}"

    def __init__(self):
        super().__init__()

        self.title_widget = QtGui.QWidget()
        self.container_widget = QtGui.QWidget()

        v_layout = QtGui.QVBoxLayout()

        h_layout = QtGui.QHBoxLayout()
        self._hidable_title = MaxWithLabel("")
        self.button = QtGui.QPushButton("Hide")
        h_layout.addWidget(self._hidable_title)
        h_layout.addWidget(self.button)
        self.title_widget.setLayout(h_layout)

        v_layout.addWidget(self.title_widget)
        v_layout.addWidget(self.container_widget)

        self.button.clicked.connect(self.toggle_widget)
        super().setLayout(v_layout)
        self.set_title()

    def set_title(self, text="-"):
        self._hidable_title.setText(self.TITLE_TEMPLATE.format(text))

    def setLayout(self, l):
        self.container_widget.setLayout(l)

    def toggle_widget(self):
        if self.container_widget.isHidden():
            self.container_widget.show()
            self.button.setText("Hide")
        else:
            self.container_widget.hide()
            self.button.setText("Show")


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


        self.events = collections.defaultdict(list)
        self.previous_filter = None
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        if not multi_select:
            self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.filtered_data = {}
        self.data = data or []
        with benchmark.Benchmark("init filter data table"):
            self.filter_data()
        self.itemSelectionChanged.connect(self.selection_changed)
        self.setSortingEnabled(True)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

    def selection_changed(self):
        rows = self.selectionModel().selectedRows()
        row_ids = []
        for row in rows:
            row_ids.append(self.item(row.row(), 0).text())

        self.trigger("selection_changed", row_ids)

    def filter_data(self, filter_str=""):
        """Filter data with a string and refresh the table.

        Args:
            filter_str (str): String for filtering rows of data.
        """
        if self.previous_filter == filter_str:
            return
        if filter_str:
            with benchmark.Benchmark("Filtering values"):
                filtered_list = [
                    item for item in self.data if
                    any(filter_str.lower() in value.lower() for value in item.values())
                ]
        else:
            filtered_list = self.data

        self.draw_items(filtered_list)
        self.previous_filter = filter_str

    def draw_items(self, data=None):
        """Redraw all items.

        Fill the table widget with the data given. The keys of the dict are set
        for table headers and all the data is displayed below.

        Args:
            data (list of dict): Data that will be drawn. If none is given, it
                defaults to self.data.
        """
        with benchmark.Benchmark("Draw items"):
            if data is None:
                data = self.data
            if not data:
                self.setRowCount(0)
                return

            headers = self._set_column_headers(data[0])
            header_index = {key: index for index, key in enumerate(headers)}

            self.filtered_data = data
            self.setRowCount(len(data))

            with benchmark.Benchmark("Fill all items"):
                for index, row_data in enumerate(data):
                    for key, value in row_data.items():
                        self.setItem(
                            index,
                            header_index[key],
                            QtGui.QTableWidgetItem(value),
                        )

            if len(data) < 500:
                with benchmark.Benchmark("Resize Columns"):
                    self.resizeColumnsToContents()
            else:
                self.setColumnWidth(0,240)
                self.setColumnWidth(1,400)
                self.setColumnWidth(2,400)

    def _set_column_headers(self, element):
        """Set column count and header text.

        Args:
            element (dict): Dictionary containing single element.

        Returns:
            List of strings containing the order of headers.
        """
        max_order_index = len(self.DEFAULT_ORDER) + 1
        self.setColumnCount(len(element.keys()))
        headers = list(sorted(
            element.keys(),
            key=lambda x: self.ORDER_MAP.get(x, max_order_index)
        ))
        self.setHorizontalHeaderLabels(headers)
        return headers

    def get_selected_data(self):
        """Get data for user selected rows.

        Returns:
            list of dicts for all rows that a user has selected.
        """
        return self.data
