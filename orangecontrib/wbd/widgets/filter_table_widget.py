from PyQt4 import QtGui

from orangecontrib.wbd.widgets import simple_filter_widget


class FilterTableWidget(QtGui.QWidget):

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

    def get_filtered_data(self):
        return self.table_widget.get_filtered_data()


class FilterDataTableWidget(QtGui.QTableWidget):

    def __init__(self, data=None):
        """Init data table widget.

        Args:
            data (list): List of dicts where each key in the dict represents a
                column in the table. All dicts must contain all the same keys.
        """
        super().__init__()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.filtered_data = {}
        self.data = data
        self.filter_data()

    def filter_data(self, filter_str=""):
        """Filter data with a string and refresh the table.

        Args:
            filter_str (str): String for filtering rows of data.
        """
        if filter_str:
            filtered_list = [
                item for item in self.data if
                any(filter_str in value for value in item.values())
            ]
        else:
            filtered_list = self.data

        self.draw_items(filtered_list)

    def draw_items(self, data=None):
        if data is None:
            data = self.data
        if not data:
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
