"""Model with the main Orange Widget.

This module contains the world bank data widget, used for fetching data from
world bank data API.
"""

import sys
import signal
import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

import wbpy
import Orange
from Orange.data import table
from Orange.widgets import widget
from Orange.widgets import gui
from orangecontrib.wbd.widgets import data_table_widget
from orangecontrib.wbd.widgets import indicators_widget
from orangecontrib.wbd.widgets import countries_widget
from orangecontrib.wbd.widgets import timeframe_widget


LOGGER = logging.getLogger(__name__)

class IndicatorWidget(QtGui.QWidget):

    def __init__(self, data_callback):
        super().__init__()
        self.data_callback = data_callback
        LOGGER.debug("Initializing {}".format(self.__class__.__name__))

        self.api = wbpy.IndicatorAPI()
        layout = QtGui.QVBoxLayout()
        self.button = QtGui.QPushButton("Fetch Data")
        self.button.clicked.connect(self.fetch_button_clicked)

        self.countries = countries_widget.CountriesWidget()
        self.indicators = indicators_widget.IndicatorsWidget()
        self.timeframe = timeframe_widget.TimeFrameWidget()
        layout.addWidget(self.indicators)
        layout.addWidget(self.countries)
        layout.addWidget(self.timeframe)
        layout.addWidget(self.button)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

    def fetch_button_clicked(self):
        """Fetch button clicked for wbd.

        Retrieve and display the response from world bank data if the
        indicator, countries and dates have been properly set for a valid
        query.
        """
        LOGGER.debug("Fetch indicator data")
        indicator = self.indicators.get_indicator()
        countries = self.countries.get_counries()
        timeframe = self.timeframe.get_timeframe()

        LOGGER.debug(indicator)
        LOGGER.debug(countries)
        LOGGER.debug(timeframe)
        dataset = self.api.get_dataset(indicator, country_codes=countries,
                                       **timeframe)
        data_list = dataset.as_list(use_datetime=True)
        self.data_callback(data_list)


class ClimateWidget(QtGui.QWidget):

    def __init__(self, data_callback):
        super().__init__()
        self.data_callback = data_callback


class WorldBankDataWidget(widget.OWWidget):
    """World bank data widget for Orange."""

    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Hello World"
    icon = "icons/mywidget.svg"
    category = "Data"
    want_main_area = False
    outputs = [widget.OutputSignal(
        "Data", table.Table,
        doc="Attribute-valued data set read from the input file.")]

    def __init__(self):
        super().__init__()
        LOGGER.debug("Initializing {}".format(self.__class__.__name__))

        self.api = wbpy.IndicatorAPI()
        layout = QtGui.QHBoxLayout()
        self.api_tabs = QtGui.QTabWidget()
        indicators = IndicatorWidget(self.data_updated)
        climate = ClimateWidget(self.data_updated)
        self.api_tabs.addTab(indicators, "Indicators API")
        self.api_tabs.addTab(climate, "Climate API")

        self.data_widget = data_table_widget.DataTableWidget()
        layout.addWidget(self.api_tabs)
        layout.addWidget(self.data_widget)
        gui.widgetBox(self.controlArea, margin=0, orientation=layout)

    def data_updated(self, data_list):
        self.data_widget.fill_data(data_list)

        self.send_data(data_list)

    def send_data(self, data):

        if data[0][0] == "Date":
            first_column = Orange.data.TimeVariable("Date")
            for row in data[1:]:

                LOGGER.debug(row)
                LOGGER.debug(row[0].isoformat())
                row[0] = first_column.parse(row[0].isoformat())
        elif data[0][0] == "Country":
            first_column = Orange.data.StringVariable("Country")

        LOGGER.debug(data)

        domain_columns = [first_column] + [
            Orange.data.ContinuousVariable(column_name)
            for column_name in data[0][1:]
        ]

        domain = Orange.data.Domain(domain_columns)

        data = Orange.data.Table(domain, data[1:])

        self.send("Data", data)
        print(data)

        #  from Orange.data import Table, Domain

        #  from Orange.data import ContinuousVariable, DiscreteVariable, StringVariable

        #  import numpy as np

        #  domain = Domain([ContinuousVariable("population"), DiscreteVariable("area")])

        #  data = Table(domain, [[1, 5],[2,44]])

        #  data


    def keyPressEvent(self, event):
        """Capture and ignore all key press events.

        This is used so that return key event does not trigger the exit button
        from the dialog. We need to allow the return key to be used in filters
        in the widget."""
        pass


def main():  # pragma: no cover
    """Helper for running the widget without Orange."""
    logging.basicConfig(level=logging.DEBUG)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtGui.QApplication(sys.argv)
    orange_widget = WorldBankDataWidget()
    orange_widget.show()
    app.exec_()
    orange_widget.saveSettings()


if __name__ == "__main__":
    main()
