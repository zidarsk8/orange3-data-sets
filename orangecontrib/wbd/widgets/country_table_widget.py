import wbpy
import collections


from PyQt4 import QtGui
from orangecontrib.wbd.widgets import filter_table_widget


class CountryTableWidget(filter_table_widget.FilterTableWidget):

    def __init__(self):
        super().__init__()
        self.filtered_data = {}
        self.fetch_country_data()
        self.setColumnCount(3)
        self.filter_data()

    def fetch_country_data(self):
        api = wbpy.IndicatorAPI()
        countries = api.get_countries()
        self.countries = collections.OrderedDict(sorted(
            countries.items(),
            key=lambda item: item[1]["name"]
        ))

    def filter_data(self, filter_str=""):
        def check_item(item):
            return (
                filter_str.lower() in item[0].lower() or
                filter_str.lower() in item[1]["name"].lower() or
                filter_str.lower() in item[1]["incomeLevel"]["id"].lower() or
                filter_str.lower() in item[1]["incomeLevel"]["value"].lower()
            )
        if filter_str:
            filtered_list = collections.OrderedDict(
                item for item in self.countries.items() if check_item(item)
            )
        else:
            filtered_list = self.countries

        self.draw_items(filtered_list)

    def draw_items(self, countries=None):
        if countries is None:
            countries = self.countries
        self.filtered_data = countries
        self.setRowCount(len(countries))
        for index, data in enumerate(countries):
            income_level = "{} ({})".format(
                countries[data]["incomeLevel"]["value"],
                countries[data]["incomeLevel"]["id"],
            )
            self.setItem(index, 0, QtGui.QTableWidgetItem(data))
            self.setItem(index, 1, QtGui.QTableWidgetItem(income_level))
            self.setItem(index, 2, QtGui.QTableWidgetItem(
                countries[data]["name"]))
        self.setHorizontalHeaderLabels([
            "Id",
            "Income Level",
            "Name",
        ])
