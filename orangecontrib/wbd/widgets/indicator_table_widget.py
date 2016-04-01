import wbpy
import collections

from PyQt4 import QtGui
from orangecontrib.wbd.widgets import filter_table_widget


class IndicatorTableWidget(filter_table_widget.FilterTableWidget):

    def __init__(self):
        super().__init__()
        self.fetch_country_data()
        self.setColumnCount(4)
        self.filter_data()

    def fetch_country_data(self):
        api = wbpy.IndicatorAPI()
        indicators = api.get_indicators(common_only=True)
        self.indicators = collections.OrderedDict(sorted(
            indicators.items(),
            key=lambda item: item[1]["name"]
        ))

    def filter_data(self, filter_str=""):
        def check_item(item):
            return (
                filter_str.lower() in item[0].lower() or
                filter_str.lower() in item[1]["name"].lower() or
                filter_str.lower() in item[1]["source"]["id"].lower() or
                filter_str.lower() in item[1]["source"]["value"].lower()
            )
        if filter_str:
            filtered_list = collections.OrderedDict(
                item for item in self.indicators.items() if check_item(item)
            )
        else:
            filtered_list = self.indicators

        self.draw_items(filtered_list)

    def draw_items(self, indicators=None):
        if indicators is None:
            indicators = self.indicators
        self.filtered_data = indicators
        self.setRowCount(len(indicators))
        for index, data in enumerate(indicators):
            source = "{} ({})".format(
                indicators[data]["source"]["value"],
                indicators[data]["source"]["id"],
            )
            self.setItem(index, 0, QtGui.QTableWidgetItem(data))
            self.setItem(index, 1, QtGui.QTableWidgetItem(
                indicators[data]["name"]))
            self.setItem(index, 2, QtGui.QTableWidgetItem(source))
        self.setHorizontalHeaderLabels([
            "Id",
            "Source",
            "Name",
        ])
