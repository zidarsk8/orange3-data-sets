"""Data table widget module."""

from PyQt4 import QtGui


class DataTableWidget(QtGui.QTableWidget):
    """Widget for displaying world bank data.

    This widget is used for preview of world bank data fetched from the API. It
    also allows transposing of the data.
    """

    def __init__(self):
        super().__init__()

    def fill_data(self, data):
        """Fill the main data table.

        Args:
            data (list of lists): 2d array where the first column represents
            the data header.
        """
        if not data or not data[0]:
            self.setRowCount(0)
            self.setColumnCount(0)
            return
        header = data.pop(0)
        self.setRowCount(len(data))
        self.setColumnCount(len(header))
        self.setHorizontalHeaderLabels(header)
        for row, row_data in enumerate(data):
            for column, value in enumerate(row_data):
                self.setItem(row, column, QtGui.QTableWidgetItem(str(value)))
