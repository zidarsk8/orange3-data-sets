import sys
import signal
import wbpy


from PyQt4 import QtGui
from PyQt4 import QtCore
from Orange.widgets.widget import OWWidget
from Orange.widgets import gui
from orangecontrib.wbd.widgets import simple_filter_widget
from orangecontrib.wbd.widgets import indicator_table_widget
from orangecontrib.wbd.widgets import country_table_widget


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

        self.countries = Country2Widget(data=[
            {"A": "1", "bb": "something"},
            {"A": "2", "bb": "something"},
            {"A": "4", "bb": "something"},
        ])
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


class FilteredTableWidget(QtGui.QWidget):

    def __init__(self, table_widget_class, **kwargs):
        super().__init__()

        layout = QtGui.QGridLayout()

        self.filter_widget = simple_filter_widget.SimpleFilterWidget()
        self.table_widget = table_widget_class(**kwargs)
        layout.addWidget(self.filter_widget)
        layout.addWidget(self.table_widget)

        self.setLayout(layout)
        if callable(getattr(self.table_widget, "filter_data", None)):
            self.filter_widget.register_callback(self.table_widget.filter_data)

    def get_filtered_data(self):
        return self.table_widget.get_filtered_data()


class IndicatorFilterWidget(FilteredTableWidget):

    def __init__(self):
        super().__init__(indicator_table_widget.IndicatorTableWidget)
        self.filter_widget.filter_text.setText("DT.DOD.DECT.CD.GG.AR.US")
        self.filter_widget.ok_button_clicked()


class CountryFilterWidget(FilteredTableWidget):

    def __init__(self, data=None):
        super().__init__(country_table_widget.CountryTableWidget, data)


class Country2Widget(FilteredTableWidget):

    def __init__(self, data=None):
        super().__init__(FilterDataTableWidget, data=data)


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
        header_index = {key:index for index, key in enumerate(headers)}

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


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    a = QtGui.QApplication(sys.argv)
    ow = WorldBankDataWidget()
    ow.show()
    a.exec_()
    ow.saveSettings()
