"""Modul for Countries widget.

This widget should contain all filters needed to help the user find and select
any country.
"""

import logging
import time

import simple_wbd
from PyQt4 import QtGui
from PyQt4 import QtCore
from Orange.widgets.utils import concurrent

from orangecontrib.wbd.widgets import filter_table

logger = logging.getLogger(__name__)


class CountriesList(QtGui.QWidget):

    TITLE_TEMPLATE = "Countries: {}"

    def __init__(self):
        super().__init__()
        self.text_setter = None
        self.data = None

        self.api = simple_wbd.IndicatorAPI()
        layout = QtGui.QGridLayout()

        toggle_label = QtGui.QLabel("Toggle selection: ")
        toggle_all = QtGui.QPushButton("All Locations")
        toggle_countries = QtGui.QPushButton("Countries")
        toggle_aggregates = QtGui.QPushButton("Aggregates")

        toggle_all.clicked.connect(self.togle_all_click)
        toggle_countries.clicked.connect(self.togle_countries_click)
        toggle_aggregates.clicked.connect(self.togle_aggregates_click)

        self.countries = filter_table.FilterTable()

        layout.addWidget(toggle_label, 0, 0)
        layout.addWidget(toggle_all, 0, 1)
        layout.addWidget(toggle_countries, 0, 2)
        layout.addWidget(toggle_aggregates, 0, 3)
        layout.addWidget(self.countries, 1, 0, 1, 4)
        self.setLayout(layout)

        self.countries.table_widget.on(
            "selection_changed", self.selection_changed)

        self._fetch_data()

    def _fetch_data(self):
        self._executor = concurrent.ThreadExecutor(
            threadPool=QtCore.QThreadPool(maxThreadCount=2)
        )
        self._task = concurrent.Task(function=self._fetch_countries_data)
        self._task.resultReady.connect(self._fetch_countries_completed)
        self._task.exceptionReady.connect(self._fetch_countries_exception)
        self._executor.submit(self._task)

    def _fetch_countries_data(self):
        time.sleep(1)  # bug if the list is loaded before the widget gets show.
        logger.debug("Fetch countries data")
        self.data = self.api.get_country_list()

    def _fetch_countries_exception(self):
        logger.error("Failed to load countries list.")

    def _fetch_countries_completed(self):
        logger.debug("Fetch countries completed.")
        if self.data:
            self.countries.table_widget.set_data(self.data)
            self.togle_countries_click()
            self.countries.table_widget.selection_changed()

    def set_title(self, title=""):
        if callable(self.text_setter):
            logger.debug("setting countries widget title")
            self.text_setter(self.TITLE_TEMPLATE.format(title))

    def togle_all_click(self):
        self.countries.table_widget.set_selected_data("")

    def togle_countries_click(self):
        self.countries.table_widget.set_selected_data()

    def togle_aggregates_click(self):
        self.countries.table_widget.set_selected_data("Aggregates (NA)")

    def selection_changed(self, selected_ids):
        if not selected_ids:
            self.set_title("All Countries")
        else:
            self.set_title(",".join(selected_ids))

    def get_counries(self):
        return self.countries.get_selected_data()
