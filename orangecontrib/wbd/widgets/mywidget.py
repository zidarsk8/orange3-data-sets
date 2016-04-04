"""Model with the main Orange Widget.

This module contains the world bank data widget, used for fetching data from
world bank data API.
"""

import sys
import signal

from PyQt4 import QtGui

import wbpy
from Orange.widgets.widget import OWWidget
from Orange.widgets import gui
from orangecontrib.wbd.widgets import filter_table_widget
from orangecontrib.wbd.widgets import date_input_widget
from orangecontrib.wbd.widgets import data_table_widget


class WorldBankDataWidget(OWWidget):
    """World bank data widget for Orange."""

    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Hello World"
    icon = "icons/mywidget.svg"
    want_main_area = False

    def __init__(self):
        super().__init__()

        self.api = wbpy.IndicatorAPI()
        layout = QtGui.QGridLayout()
        self.button = QtGui.QPushButton("Fetch Data", autoDefault=True)
        self.button.clicked.connect(self.fetch_button_clicked)

        self.countries = filter_table_widget.FilterTableWidget(
            data=self.api.get_country_list()
        )
        self.indicators = filter_table_widget.FilterTableWidget(
            data=self.api.get_indicator_list()
        )
        self.data_widget = data_table_widget.DataTableWidget()
        self.date = date_input_widget.DateInputWidget()
        layout.addWidget(self.button, 0, 0)
        layout.addWidget(self.indicators, 1, 0)
        layout.addWidget(self.countries, 2, 0)
        layout.addWidget(self.date, 3, 0)
        layout.addWidget(self.data_widget, 0, 1, 4, 1)
        gui.widgetBox(self.controlArea, margin=0, orientation=layout)

    def fetch_button_clicked(self):
        """Fetch button clicked for wbd.

        Retrieve and display the response from world bank data if the
        indicator, countries and dates have been properly set for a valid
        query.
        """
        print("fetch button clicked")


def main():
    """Helper for running the widget without Orange."""
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtGui.QApplication(sys.argv)
    orange_widget = WorldBankDataWidget()
    orange_widget.show()
    app.exec_()
    orange_widget.saveSettings()

if __name__ == "__main__":
    main()
