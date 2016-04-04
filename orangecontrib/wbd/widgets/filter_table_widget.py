"""Modul for the filter table widget."""

from PyQt4 import QtGui

from orangecontrib.wbd.widgets import simple_filter_widget


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


class FilterDataTableWidget(QtGui.QTableWidget):
    """Widget for displaying array of dicts in a table widget."""

    def __init__(self, data=None):
        """Init data table widget.

        Args:
            data (list): List of dicts where each key in the dict represents a
                column in the table. All dicts must contain all the same keys.
        """
        super().__init__()
        self.previous_filter = None
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.filtered_data = {}
        self.data = data or []
        self.filter_data()

    def filter_data(self, filter_str=""):
        """Filter data with a string and refresh the table.

        Args:
            filter_str (str): String for filtering rows of data.
        """
        if self.previous_filter == filter_str:
            return
        if filter_str:
            filtered_list = [
                item for item in self.data if
                any(filter_str in value for value in item.values())
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
        if data is None:
            data = self.data
        if not data:
            self.setRowCount(0)
            return

        headers = self._set_column_headers(data[0])
        header_index = {key: index for index, key in enumerate(headers)}

        self.filtered_data = data
        self.setRowCount(len(data))
        for index, data in enumerate(data):
            for key, value in data.items():
                self.setItem(
                    index,
                    header_index[key],
                    QtGui.QTableWidgetItem(value),
                )

    def _set_column_headers(self, element):
        """Set column count and header text.

        Args:
            element (dict): Dictionary containing single element.

        Returns:
            List of strings containing the order of headers.
        """
        self.setColumnCount(len(element.keys()))
        headers = list(element.keys())
        self.setHorizontalHeaderLabels(headers)
        return headers

    def get_selected_data(self):
        """Get data for user selected rows.

        Returns:
            list of dicts for all rows that a user has selected.
        """
        return self.data
