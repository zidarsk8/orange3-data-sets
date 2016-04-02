import sys
import signal
import wbpy


from PyQt4 import QtGui
from PyQt4 import QtCore
from Orange.widgets.widget import OWWidget
from Orange.widgets import gui
from orangecontrib.wbd.widgets import filter_table_widget


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

        self.countries = filter_table_widget.FilterTableWidget()
        self.indicators = filter_table_widget.FilterTableWidget()
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

        data = self.api.get_dataset(
            indicator, country_codes=countries, date=date)
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
        country_index = {country: index for index, country in
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


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    a = QtGui.QApplication(sys.argv)
    ow = WorldBankDataWidget()
    ow.show()
    a.exec_()
    ow.saveSettings()
