import sys
import signal
import wbpy
import collections


from PyQt4 import QtGui
from PyQt4 import QtCore
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

        filter_widget = SimpleFilterWidget()
        country_list = CountryTableWidget()
        layout.addWidget(filter_widget)
        layout.addWidget(country_list)

        self.setLayout(layout)
        filter_widget.register_callback(country_list.filter_data)


class SimpleFilterWidget(QtGui.QWidget):

    def __init__(self):
        super().__init__()
        self.callbacks = set()

        layout = QtGui.QHBoxLayout()

        filter_label = QtGui.QLabel("Filter")
        self.filter_text = QtGui.QLineEdit(self)
        filter_button = QtGui.QPushButton(self, text="Ok", autoDefault=True)
        filter_button.clicked.connect(self.ok_button_clicked)
        self.filter_text.returnPressed.connect(filter_button.click)

        layout.addWidget(filter_label)
        layout.addWidget(self.filter_text)
        layout.addWidget(filter_button)

        self.setLayout(layout)

    @QtCore.pyqtSlot()
    def ok_button_clicked(self):
        text = self.filter_text.text()
        for callback in self.callbacks:
            callback(text)

    def register_callback(self, callback):
        if callable(callback):
            self.callbacks.add(callback)
        else:
            raise TypeError("Callback argument must be a callable function.")


class CountryTableWidget(QtGui.QTableWidget):

    def __init__(self):
        super().__init__()
        self.displayed_countries = {}
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
        self.displayed_countries = countries
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
