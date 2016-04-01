import collections

from PyQt4 import QtGui


class FilterTableWidget(QtGui.QTableWidget):

    def __init__(self):
        super().__init__()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.filtered_data = collections.OrderedDict()

    def get_filtered_data(self):
        indexes = [item.row() for item in self.selectionModel().selectedRows()]
        key_list = list(self.filtered_data.keys())
        indicators = self.filtered_data
        selected_data = {key_list[index]: indicators[key_list[index]]
                         for index in indexes}
        return selected_data
