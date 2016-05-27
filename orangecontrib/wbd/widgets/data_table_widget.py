"""Data table widget module."""

from PyQt4 import QtGui


class DataTableWidget(QtGui.QTableWidget):
    """Widget for displaying world bank data.

    This widget is used for preview of world bank data fetched from the API. It
    also allows transposing of the data.
    """

    def __init__(self):
        super().__init__()

    def fill_data(self, table_data):
        """Fill the main data table.

        Args:
            table_data (list of lists): 2d array where the first column
            represents the data header.
        """
        if not table_data or not table_data[0]:
            self.setRowCount(0)
            self.setColumnCount(0)
            return
        header, cell_data = table_data[0], table_data[1:]
        self.setRowCount(len(cell_data))
        self.setColumnCount(len(header))
        self.setHorizontalHeaderLabels(header)
        for row, row_data in enumerate(cell_data):
            for column, value in enumerate(row_data):
                self.setItem(row, column, QtGui.QTableWidgetItem(str(value)))

        self.resizeColumnsToContents()
