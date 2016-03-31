import sys
import signal
import wbpy
import collections


from PyQt4 import QtGui
from Orange.widgets.widget import OWWidget
from Orange.widgets import gui


class WorldBankDataWidget(OWWidget):
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Hello World"
    icon = "icons/mywidget.svg"
    want_main_area = False

    def __init__(self):
        super().__init__()

        layout = QtGui.QGridLayout()
        button = QtGui.QPushButton("hello")

        countries = CountryListWidget()
        layout.addWidget(button)
        layout.addWidget(countries)
        gui.widgetBox(self.controlArea, margin=0, orientation=layout)


class CountryListWidget(QtGui.QWidget):

    def __init__(self):
        super().__init__()

        layout = QtGui.QGridLayout()

        filter_label = QtGui.QLabel("Filter")
        filter_text = QtGui.QLineEdit()
        filter_button = QtGui.QPushButton("Ok")
        country_list = CountryTableWidget()
        layout.addWidget(filter_label, 0, 0)
        layout.addWidget(filter_text, 0, 1)
        layout.addWidget(filter_button, 0, 2)
        layout.addWidget(country_list, 1, 0, 1, 3)

        self.setLayout(layout)


class CountryTableWidget(QtGui.QTableWidget):

    def __init__(self):
        super().__init__()
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

    def filter_data(self, filter_string=None):
        self.draw_items()

    def draw_items(self, countries=None):
        if countries is None:
            countries = self.countries

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


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    a = QtGui.QApplication(sys.argv)
    ow = WorldBankDataWidget()
    ow.show()
    a.exec_()
    ow.saveSettings()
