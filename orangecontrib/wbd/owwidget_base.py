"""Model with the main Orange Widget.

This module contains the world bank data widget, used for fetching data from
world bank data API.
"""

import logging
import collections
from functools import partial

import requests
from PyQt4 import QtCore
from Orange.widgets import widget
from Orange.widgets.utils import concurrent


logger = logging.getLogger(__name__)


class OWWidgetBase(widget.OWWidget):
    """Base class for Indicators and Climate widgets."""

    # pylint: disable=invalid-name
    # Some names have to be invalid to override parent fields.
    # pylint: disable=too-many-ancestors
    # False positive from fetching all ancestors from QWWidget.
    # pylint: disable=too-many-instance-attributes
    # False positive from fetching all attributes from QWWidget.

    category = "Data Sets"
    country_selection = None

    def __init__(self):
        super().__init__()
        logger.debug("Initializing %s", self.__class__.__name__)
        self._fetch_task = None
        self._info_label = None
        self._selection_changed = False
        self._set_progress_flag = False
        self._executor = concurrent.ThreadExecutor()
        self.info_data = collections.OrderedDict([
            ("Server status", None),
            ("Indicators", None),
            ("Selected countries", None),
            ("Rows", None),
            ("Columns", None),
            ("Warning", None),
        ])

    def _check_server_status(self):
        try:
            requests.get('http://api.worldbank.org', timeout=1)
            self.info_data["Server status"] = "Up"
        except requests.exceptions.Timeout:
            self.info_data["Server status"] = "Down"
        self.print_info()

    def print_info(self):
        """Refresh info in the info label."""
        if not self._info_label:
            return
        lines = ["{}: {}".format(k, v) for k, v in self.info_data.items()
                 if v is not None]
        self._info_label.setText("\n".join(lines))

    def commit_if(self):
        """Auto commit handler.

        This function must be called on every action that should trigger an
        auto commit.
        """
        logger.debug("Commit If - auto_commit: %s", self.auto_commit)
        if self.auto_commit:
            self.commit()
        else:
            self._selection_changed = True

    def commit(self):
        """Fetch the climate data and send a new orange table."""
        logger.debug("commit data")
        self.setEnabled(False)
        self._set_progress_flag = True

        func = partial(
            self._fetch_dataset,
            concurrent.methodinvoke(self, "set_progress", (float,))
        )
        self._fetch_task = concurrent.Task(function=func)
        self._fetch_task.finished.connect(self._fetch_dataset_finished)
        self._fetch_task.exceptionReady.connect(self._fetch_dataset_exception)
        self._executor.submit(self._fetch_task)

    def _fetch_dataset(self, set_progress=None):
        raise NotImplementedError(
            "Missing implementation for _fetch_dataset.")

    def _dataset_to_table(self, dataset):
        raise NotImplementedError(
            "Missing implementation for _dataset_to_table.")

    def _fetch_dataset_finished(self):
        """Send data signal on finished dataset fetch."""
        assert self.thread() is QtCore.QThread.currentThread()
        self.setEnabled(True)
        self._set_progress_flag = False
        self.set_progress(100)

        if self._fetch_task is None:
            return

        dataset = self._fetch_task.result()
        data_table = self._dataset_to_table(dataset)

        self.print_info()
        self.send("Data", data_table)

    @staticmethod
    def _fetch_dataset_exception(exception):
        logger.exception(exception)

    @QtCore.pyqtSlot(float)
    def set_progress(self, value):
        """set widgets progress indicator.

        Args:
            value: integer indicating number of percent finished.
        """
        # pylint: disable=invalid-name
        # the progressBarValue is defined in a super class and can not be
        # changed here.
        logger.debug("Set progress: %s", value)
        self.progressBarValue = value
        if value == 100:
            self.progressBarFinished()

    def get_country_codes(self):
        """Get a list of alpha3 codes for selected countries or regions."""
        if self.country_selection:
            # pylint: disable=no-member
            # Settings instance can have items member if it is defined as dict.
            return [k for k, v in self.country_selection.items()
                    if v == 2 and len(str(k)) == 3]
        return []

    def _dataset_progress(self, set_progress=None):
        pass

    def _start_progerss_task(self):
        func = partial(
            self._dataset_progress,
            concurrent.methodinvoke(self, "set_progress", (float,))
        )
        progress_task = concurrent.Task(function=func)
        progress_task.exceptionReady.connect(self._dataset_progress_exception)
        self._executor.submit(progress_task)
