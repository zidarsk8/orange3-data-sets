import sys
import signal
import wbpy
import collections


from PyQt4 import QtGui
from PyQt4 import QtCore
from Orange.widgets.widget import OWWidget
from Orange.widgets import gui


def set_trace(self):
    import ipdb
    QtCore.pyqtRemoveInputHook()
    ipdb.set_trace()
    # QtCore.pyqtRestoreInputHook()


class WorldBankDataWidget(OWWidget):
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Hello World"
    icon = "icons/mywidget.svg"
    want_main_area = False

    def __init__(self):
        super().__init__()

        self.api = wbpy.IndicatorAPI()
        layout = QtGui.QGridLayout()
        button = QtGui.QPushButton("Fetch Data")
        button.clicked.connect(self.fetch_button_clicked)

        self.countries = CountryFilterWidget()
        self.indicators = IndicatorFilterWidget()
        self.data_widget = DataTableWidget()
        self.date = DateInputWidget()
        layout.addWidget(button, 0, 0)
        layout.addWidget(self.indicators, 1, 0)
        layout.addWidget(self.countries, 2, 0)
        layout.addWidget(self.date, 3, 0)
        layout.addWidget(self.data_widget, 0, 1, 4, 1)
        gui.widgetBox(self.controlArea, margin=0, orientation=layout)

    def fetch_button_clicked(self):

        # for now we'll support ony a single indicator since we can only do one
        # indicator lookup per request. And we don't want to make too many
        # requests
        indicators = self.indicators.get_filtered_data()
        if not indicators:
            return
        indicator = next(iter(indicators))

        countries = self.countries.get_filtered_data()
        if not countries:
            countries = None
        else:
            countries = countries.keys()

        date = self.date.get_date_string()

        data = self.api.get_dataset(indicator, country_codes=countries, date=date)
        self.data_widget.fill_data(data)


class DateInputWidget(QtGui.QWidget):

    def __init__(self):
        super().__init__()
        layout = QtGui.QHBoxLayout()

        filter_label = QtGui.QLabel("Date")
        self.date_text = QtGui.QLineEdit(self, text="2001:2016")
        layout.addWidget(filter_label)
        layout.addWidget(self.date_text)

        self.setLayout(layout)

    def get_date_string(self):
        # todo: validation
        return self.date_text.text()


class DataTableWidget(QtGui.QTableWidget):

    def __init__(self):
        super().__init__()

    def _get_unique_dates(self, dataset):
        """Return a list of all dates found in the dataset.

        This is used when there is data missing for some countries and so we
        get a full list of dates.
        Note; maybe it would be better to replace this with range and take into
        account the quarters and months so that if there is a year missing in
        all countries, that the dataset would still contain those lines"""
        date_sets = [set(value.keys()) for value in dataset.values()]
        return sorted(set().union(*date_sets))

    def fill_data(self, dataset):
        data_dict = dataset.as_dict()
        dates = self._get_unique_dates(data_dict)
        self.setRowCount(len(dates))
        self.setColumnCount(len(data_dict))
        date_indexes = {date: index for index, date in enumerate(dates)}
        sorted_countries = sorted(dataset.countries.values())
        country_index = {country:index for index,country in
                           enumerate(sorted_countries)}

        for country_id, data in data_dict.items():
            column = country_index[dataset.countries[country_id]]
            for date, value in data.items():
                self.setItem(
                    date_indexes[date],
                    column,
                    QtGui.QTableWidgetItem(str(value))
                )
        self.setHorizontalHeaderLabels(sorted_countries)
        self.setVerticalHeaderLabels(dates)


class FilteredTableWidget(QtGui.QWidget):

    def __init__(self, table_widget_class):
        super().__init__()

        layout = QtGui.QGridLayout()

        self.filter_widget = SimpleFilterWidget()
        self.table_widget = table_widget_class()
        layout.addWidget(self.filter_widget)
        layout.addWidget(self.table_widget)

        self.setLayout(layout)
        if callable(getattr(self.table_widget, "filter_data", None)):
            self.filter_widget.register_callback(self.table_widget.filter_data)

    def get_filtered_data(self):
        return self.table_widget.get_filtered_data()


class IndicatorFilterWidget(FilteredTableWidget):

    def __init__(self):
        super().__init__(IndicatorTableWidget)
        self.filter_widget.filter_text.setText("DT.DOD.DECT.CD.GG.AR.US")
        self.filter_widget.ok_button_clicked()


class CountryFilterWidget(FilteredTableWidget):

    def __init__(self):
        super().__init__(CountryTableWidget)


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


class CountryTableWidget(FilterTableWidget):

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


class IndicatorTableWidget(FilterTableWidget):

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


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    a = QtGui.QApplication(sys.argv)
    ow = WorldBankDataWidget()
    ow.show()
    a.exec_()
    ow.saveSettings()
