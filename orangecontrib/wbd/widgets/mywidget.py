"""Model with the main Orange Widget.

This module contains the world bank data widget, used for fetching data from
world bank data API.
"""

import sys
import signal
import logging

from PyQt4 import QtGui

import wbpy
from Orange.widgets.widget import OWWidget
from Orange.widgets import gui
from orangecontrib.wbd.widgets import data_table_widget
from orangecontrib.wbd.widgets import indicators_widget
from orangecontrib.wbd.widgets import countries_widget
from orangecontrib.wbd.widgets import timeframe_widget
from orangecontrib.wbd.widgets import benchmark


LOGGER = logging.getLogger(__name__)


class WorldBankDataWidget(OWWidget):
    """World bank data widget for Orange."""

    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Hello World"
    icon = "icons/mywidget.svg"
    want_main_area = False

    def __init__(self):
        super().__init__()
        LOGGER.debug("Initializing {}".format(self.__class__.__name__))

        self.api = wbpy.IndicatorAPI()
        layout = QtGui.QGridLayout()
        self.button = QtGui.QPushButton("Fetch Data", autoDefault=True)
        self.button.clicked.connect(self.fetch_button_clicked)

        self.countries = countries_widget.CountriesWidget()
        with benchmark.Benchmark("indicators init"):
            self.indicators = indicators_widget.IndicatorsWidget()
        self.data_widget = data_table_widget.DataTableWidget()
        self.timeframe = timeframe_widget.TimeFrameWidget()
        layout.addWidget(self.button, 3, 0)
        layout.addWidget(self.indicators, 0, 0)
        layout.addWidget(self.countries, 1, 0)
        layout.addWidget(self.timeframe, 2, 0)
        layout.addWidget(self.data_widget, 0, 1, 4, 2)
        gui.widgetBox(self.controlArea, margin=0, orientation=layout)

    def fetch_button_clicked(self):
        """Fetch button clicked for wbd.

        Retrieve and display the response from world bank data if the
        indicator, countries and dates have been properly set for a valid
        query.
        """
        print("fetch button clicked")

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
