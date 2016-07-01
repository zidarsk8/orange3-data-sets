"""Model with the main Orange Widget.

This module contains the world bank data widget, used for fetching data from
world bank data API.
"""

import sys
import signal
import logging

from PyQt4 import QtGui
from PyQt4 import QtCore
from Orange.data import table
from Orange.widgets import widget
from Orange.widgets import gui
from Orange.widgets.utils import concurrent

from orangecontrib.wbd import indicators_list
from orangecontrib.wbd import countries_list
from orangecontrib.wbd import api_wrapper

logger = logging.getLogger(__name__)


class IndicatorAPI(widget.OWWidget):
    """World bank data widget for Orange."""

    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Indicator API"
    icon = "icons/wb_icon.png"
    category = "Data Sets"
    want_main_area = False
    outputs = [widget.OutputSignal(
        "Data", table.Table,
        doc="Attribute-valued data set read from the input file.")]

    def __init__(self):
        super().__init__()
        logger.debug("Initializing {}".format(self.__class__.__name__))
        self.dataset_params = None
        self._init_layout()

    def _init_layout(self):
        """Initialize widget layout."""
        self.api = api_wrapper.IndicatorAPI()
        layout = QtGui.QVBoxLayout()

        self.toolbox = QtGui.QToolBox()
        self.fetch_button = QtGui.QPushButton("Fetch Data")
        self.fetch_button.clicked.connect(self.fetch_button_clicked)
        self.timeseries = QtGui.QCheckBox("As timeseries")

        self.countries = countries_list.CountriesList()
        self.indicators = indicators_list.IndicatorsListWidget()
        # self.timeframe = timeframe.TimeFrameWidget()

        self._add_toolbox_item(self.indicators, "indicators")
        self._add_toolbox_item(self.countries, "countries")
        # self._add_toolbox_item(self.timeframe, "time frame")

        layout.addWidget(self.toolbox)
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.timeseries)
        layout.setAlignment(QtCore.Qt.AlignTop)

        gui.widgetBox(self.controlArea, margin=0, orientation=layout)

    def _add_toolbox_item(self, item, name):
        logger.debug("adding item number: %s", self.toolbox.count())

        def get_text_setter(index):
            def text_setter(text):
                logger.debug("Setting text toolbox item %s to %s", index, text)
                self.toolbox.setItemText(index, text)
            return text_setter

        item.text_setter = get_text_setter(self.toolbox.count())

        self.toolbox.addItem(item, name)

    def fetch_button_clicked(self):
        """Fetch button clicked for wbd.

        Retrieve and display the response from world bank data if the
        indicator, countries and dates have been properly set for a valid
        query.
        """
        self.fetch_button.setEnabled(False)
        logger.debug("Fetch indicator data")
        self.dataset_params = [
            self.indicators.get_indicators(),
            self.countries.get_counries(),
        ]
        logger.debug("dataset parameters: %s", self.dataset_params)
        self._executor = concurrent.ThreadExecutor(
            threadPool=QtCore.QThreadPool(maxThreadCount=2)
        )
        self._task = concurrent.Task(function=self._fetch_dataset)
        self._task.resultReady.connect(self._fetch_dataset_completed)
        self._task.exceptionReady.connect(self._fetch_dataset_exception)
        self._executor.submit(self._task)

    def _fetch_dataset(self):
        """Background thread handler for fetching data from the api."""
        logger.debug("Fetch dataset data")
        self.dataset = self.api.get_dataset(*self.dataset_params)

    def _fetch_dataset_exception(self):
        logger.error("Failed to load dataset.")
        self.fetch_button.setEnabled(True)

    def _fetch_dataset_completed(self):
        """Handler for successfully completed fetch request."""
        logger.debug("Fetch dataset completed.")
        if self.dataset:
            logger.debug("Generating orange, timeseries (%s)",
                         self.timeseries.isChecked())
            data_list = self.dataset.as_orange_table(
                timeseries=self.timeseries.isChecked())
            self.send_data(data_list)
        self.fetch_button.setEnabled(True)

    def send_data(self, data):
        self.send("Data", data)

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
    orange_widget = IndicatorAPI()
    orange_widget.show()
    app.exec_()
    orange_widget.saveSettings()


if __name__ == "__main__":
    main()
