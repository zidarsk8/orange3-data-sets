import sys
import signal
import wbpy


from PyQt4 import QtGui
from PyQt4 import QtCore
from Orange.widgets.widget import OWWidget
from Orange.widgets import gui
from orangecontrib.wbd.widgets import filter_table_widget
from orangecontrib.wbd.widgets import date_input_widget
from orangecontrib.wbd.widgets import data_table_widget


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
        self.data_widget = data_table_widget.DataTableWidget()
        self.date = date_input_widget.DateInputWidget()
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


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    a = QtGui.QApplication(sys.argv)
    ow = WorldBankDataWidget()
    ow.show()
    a.exec_()
    ow.saveSettings()
