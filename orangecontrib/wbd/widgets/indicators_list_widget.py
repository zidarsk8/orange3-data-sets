"""Modul for Indicators widget.

This widget should contain all filters needed to help the user find and select
any indicator.
"""

import logging

import wbpy
from PyQt4 import QtGui
from PyQt4 import QtCore
from Orange.widgets.utils import concurrent

from orangecontrib.wbd.widgets import filter_table_widget

logger = logging.getLogger(__name__)


class IndicatorsListWidget(QtGui.QWidget):
    """Widget for filtering and selecting indicators."""

    TITLE_TEMPLATE = "Indicator: {}"
    MAX_TITLE_CHARS = 50

    def __init__(self):
        super().__init__()
        self.text_setter = None

        self.api = wbpy.IndicatorAPI()
        layout = QtGui.QGridLayout()

        self.indicators = filter_table_widget.FilterTableWidget()
        layout.addWidget(self.indicators)
        self.setLayout(layout)

        self.indicators.table_widget.on("selection_changed",
                                        self.selection_changed)
        self.indicators.table_widget.selection_changed()

        self._executor = concurrent.ThreadExecutor(
            threadPool=QtCore.QThreadPool(maxThreadCount=2)
        )
        self._task = concurrent.Task(function=self._fetch_indicators_data)
        self._task.resultReady.connect(self._fetch_indicators_completed)
        self._task.exceptionReady.connect(self._fetch_indicators_exception)
        self._executor.submit(self._task)

    def _fetch_indicators_data(self):
        logger.debug("Fetch indicator data")
        import time
        time.sleep(4)
        data = self.api.get_indicator_list(common_only=True)
        self.indicators.table_widget.set_data(data)

    def _fetch_indicators_exception(self):
        logger.error("Failed to load indicator list.")

    def _fetch_indicators_completed(self):
        logger.debug("Fetch indicator completed.")

    def set_title(self, title=""):
        if callable(self.text_setter):
            logger.debug("setting indicator widget title")
            self.text_setter(self.TITLE_TEMPLATE.format(title))

    def selection_changed(self, selected_ids):
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
            self.set_title(selected_ids[0])
        else:
            self.set_title()

    def get_indicator(self):
        selected = self.indicators.get_selected_data()
        if selected:
            return selected[0]
        return None
