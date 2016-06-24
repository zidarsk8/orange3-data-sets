"""Modul for Indicators widget.

This widget should contain all filters needed to help the user find and select
any indicator.
"""

import time
import logging

import simple_wbd
from PyQt4 import QtGui
from PyQt4 import QtCore
from Orange.widgets.utils import concurrent

from orangecontrib.wbd.widgets import filter_table

logger = logging.getLogger(__name__)


class IndicatorsListWidget(QtGui.QWidget):
    """Widget for filtering and selecting indicators."""

    TITLE_TEMPLATE = "Indicators: {}"
    MAX_TITLE_CHARS = 50

    def __init__(self):
        super().__init__()
        self.text_setter = None
        self.data = None
        self.filter_ = None
        self.api = simple_wbd.IndicatorAPI()

        self._init_layout()
        self._init_listeners()

        self._fetch_data()

    def _init_listeners(self):
        """Initialize the widget event listeners."""
        self.indicators.table_widget.on(
            "selection_changed", self._selection_changed)

    def _init_layout(self):
        """Initialize the widget layout."""
        layout = QtGui.QGridLayout()

        self.indicators = filter_table.FilterTable()

        filter_label = QtGui.QLabel("Show: ")
        radio_all = QtGui.QRadioButton("All")
        radio_common = QtGui.QRadioButton("Common")
        radio_featured = QtGui.QRadioButton("Featured")
        radio_all.toggled.connect(
            lambda: self._radio_selected(radio_all))
        radio_common.toggled.connect(
            lambda: self._radio_selected(radio_common))
        radio_featured.toggled.connect(
            lambda: self._radio_selected(radio_featured))

        layout.addWidget(filter_label, 0, 0)
        layout.addWidget(radio_all, 0, 1)
        layout.addWidget(radio_common, 0, 2)
        layout.addWidget(radio_featured, 0, 3)
        layout.addWidget(self.indicators, 1, 0, 1, 4)

        self.setLayout(layout)

    def _fetch_data(self, filter_=None):
        """Dispatch a fetch data request in a background thread.

        Args:
            filter_ (str): Either "common" or "featured" string to filter the
                indicator list. Anything else will be interpreted as "all".
        """
        self.filter_ = filter_
        self._executor = concurrent.ThreadExecutor(
            threadPool=QtCore.QThreadPool(maxThreadCount=2)
        )
        self._task = concurrent.Task(function=self._fetch_indicators_data)
        self._task.resultReady.connect(self._fetch_indicators_completed)
        self._task.exceptionReady.connect(self._fetch_indicators_exception)
        self._executor.submit(self._task)

    def _radio_selected(self, button):
        """Radio button change handler.

        Args:
            button (QRadioButton): The currently selected radio button.
        """
        logger.debug("%s radio button selected", button.text())
        self._fetch_data(button.text())

    def _fetch_indicators_data(self):
        """Background thread handler for fetching data from the api."""
        logger.debug("Fetch indicator data")
        self.data = self.api.get_indicator_list(filter_=self.filter_)

    def _fetch_indicators_exception(self):
        logger.error("Failed to load indicator list.")

    def _fetch_indicators_completed(self):
        """Handler for successfully completed fetch request."""
        logger.debug("Fetch indicator completed.")
        if self.data:
            self.indicators.table_widget.set_data(self.data)

    def _set_title(self, title=""):
        """Set the title of the parent qtoolbox.

        Args:
            title (str): String containing a list of all selected indicators.
        """
        if callable(self.text_setter):
            logger.debug("setting indicator widget title")
            self.text_setter(self.TITLE_TEMPLATE.format(title))

    def _selection_changed(self, selected_ids):
        """Callback function for selected indicators.

        This function sets the title of the current widget to display the
        selected indicator.

        Args:
            selected_ids (list of str): List of selected indicator ids. This
                list should always contain just one indicator. If more
                indicators are given, only the first one will be used.
        """
        logger.debug("selection changed: %s", selected_ids)
        if selected_ids:
            self._set_title(", ".join(selected_ids))
        else:
            self._set_title()

    def get_indicators(self):
        """Get the list of selected indicators.

        Returs:
            list(str): List of selected indicator ids.
        """
        return self.indicators.get_selected_data()
