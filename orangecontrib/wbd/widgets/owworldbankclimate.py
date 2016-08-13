"""Model with the main Orange Widget.

This module contains the world bank data widget, used for fetching data from
world bank data API.
"""

import sys
import time
import math
import signal
import logging
import collections
from functools import partial

from PyQt4 import QtGui
from PyQt4 import QtCore
from Orange.data import table
from Orange.widgets import widget
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.utils import concurrent

from orangecontrib.wbd.countries_and_regions import CountryTreeWidget
from orangecontrib.wbd import api_wrapper
from orangecontrib.wbd import countries
from orangecontrib.wbd import owwidget_base

logger = logging.getLogger(__name__)


class OWWorldBankClimate(owwidget_base.OWWidgetBase):
    """World bank data widget for Orange."""
    # pylint: disable=invalid-name
    # Some names have to be invalid to override parent fields.
    # pylint: disable=too-many-ancestors
    # False positive from fetching all ancestors from QWWidget.
    # pylint: disable=too-many-instance-attributes
    # False positive from fetching all attributes from QWWidget.

    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "WB Climate"
    icon = "icons/climate.png"
    category = "Data Sets"
    outputs = [widget.OutputSignal(
        "Data", table.Table,
        doc="Attribute-valued data set read from the input file.")]

    climate_list_map = collections.OrderedDict([
        (0, "All"),
        (1, "Common"),
        (2, "Featured"),
    ])

    settingsList = [
        "auto_commit",
        "country_selection",
        "mergeSpots",
        "output_type"
        "splitterSettings",
    ]

    country_selection = Setting({})
    output_type = Setting(True)
    mergeSpots = Setting(True)
    auto_commit = Setting(False)
    use_country_names = Setting(False)

    include_intervals = Setting([])
    include_data_types = Setting([])

    def _data_type_setter(self, name, value):
        intervals = set(self.include_data_types) | {name}
        if not value:
            intervals.remove(name)
        self.include_data_types = list(intervals)
        logger.debug("New intervals: %s", self.include_data_types)

    def _interval_setter(self, name, value):
        intervals = set(self.include_intervals) | {name}
        if not value:
            intervals.remove(name)
        self.include_intervals = list(intervals)
        logger.debug("New intervals: %s", self.include_intervals)

    @property
    def include_month(self):
        return "month" in self.include_intervals

    @include_month.setter
    def include_month(self, value):
        self._interval_setter("month", value)

    @property
    def include_year(self):
        return "year" in self.include_intervals

    @include_year.setter
    def include_year(self, value):
        self._interval_setter("year", value)

    @property
    def include_decade(self):
        return "decade" in self.include_intervals

    @include_decade.setter
    def include_decade(self, value):
        self._interval_setter("decade", value)

    @property
    def include_temperature(self):
        return "tas" in self.include_data_types

    @include_temperature.setter
    def include_temperature(self, value):
        self._data_type_setter("tas", value)

    @property
    def include_precipitation(self):
        return "pr" in self.include_data_types

    @include_precipitation.setter
    def include_precipitation(self, value):
        self._data_type_setter("pr", value)

    splitterSettings = Setting((
        b'\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x01\xea\x00'
        b'\x00\x00\xd7\x01\x00\x00\x00\x07\x01\x00\x00\x00\x02',
        b'\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x01\xb5\x00'
        b'\x00\x02\x10\x01\x00\x00\x00\x07\x01\x00\x00\x00\x01'
    ))

    def __init__(self):
        super().__init__()
        logger.debug("Initializing %s", self.__class__.__name__)
        self._api = api_wrapper.ClimateAPI()
        self.dataset_params = None
        self._fetch_task = None
        self._set_progress_flag = False
        self._executor = concurrent.ThreadExecutor()
        self.info_data = collections.OrderedDict([
            ("Server status", None),
            ("Selected countries", None),
            ("Warning", None),
        ])

        self._init_layout()
        self.print_selection_count()
        self._check_server_status()

    def print_selection_count(self):
        """Update info widget with new selection count."""
        country_codes = self.get_country_codes()
        self.info_data["Selected countries"] = len(country_codes)
        self.print_info()

    def _init_layout(self):
        """Initialize widget layout."""

        # Control area
        info_box = gui.widgetBox(self.controlArea, "Info", addSpace=True)
        self._info_label = gui.widgetLabel(info_box, "Initializing\n\n")

        box = gui.vBox(self.controlArea, "Average intervals:")
        self.ch_month = gui.checkBox(box, self, "include_month", "Month",
                                     callback=self.commit_if)
        self.ch_year = gui.checkBox(box, self, "include_year", 'Year',
                                    callback=self.commit_if)
        self.ch_decade = gui.checkBox(box, self, "include_decade", 'Decade',
                                      callback=self.commit_if)

        box = gui.vBox(self.controlArea, "Data Types")
        gui.checkBox(box, self, "include_temperature", "Temperature",
                     callback=self.commit_if)
        gui.checkBox(box, self, "include_precipitation", 'Precipitation',
                     callback=self.commit_if)

        output_box = gui.widgetBox(self.controlArea, "Output", addSpace=True)
        gui.radioButtonsInBox(output_box, self, "output_type",
                              ["Countries", "Time Series"], "Rows",
                              callback=self.output_type_selected)

        gui.checkBox(output_box, self, "use_country_names",
                     "Use Country names", callback=self.commit_if)

        self.output_type = 0

        gui.separator(output_box)

        gui.auto_commit(self.controlArea, self, "auto_commit", "Commit",
                        box="Commit")

        gui.rubber(self.controlArea)

        # Main area

        box = gui.widgetBox(self.mainArea, "Countries")
        self.country_tree = CountryTreeWidget(
            self.mainArea, self.country_selection, commit_callback=self.commit_if)
        self.country_tree.set_data(countries.get_countries_dict())
        box.layout().addWidget(self.country_tree)

    def output_type_selected(self):
        """Output type handle."""
        logger.debug("output type set to: %s", self.output_type)
        if self.output_type == 1:  # Time series
            self.ch_decade.setEnabled(False)
            self.ch_month.setEnabled(False)
            self.ch_year.setEnabled(False)
            self.include_year = True
            self.include_month = False
            self.include_decade = False
        else:
            self.ch_decade.setEnabled(True)
            self.ch_month.setEnabled(True)
            self.ch_year.setEnabled(True)
        self.commit_if()

    def _splitter_moved(self, *_):
        self.splitterSettings = [bytes(sp.saveState())
                                 for sp in self.splitters]

    def _check_big_selection(self):
        types = len(self.include_data_types) if self.include_data_types else 2
        intervals = len(
            self.include_intervals) if self.include_intervals else 2
        country_codes = self.get_country_codes()
        selected_countries = len(country_codes)
        if types * intervals * selected_countries > 100:
            self.info_data[
                "Warning"] = "Fetching data\nmight take a few minutes."
        else:
            self.info_data["Warning"] = None
        self.print_info()

    def commit_if(self):
        """Auto commit handler.

        This function must be called on every action that should trigger an
        auto commit.
        """
        self._check_big_selection()
        self.print_selection_count()
        super().commit_if()

    def _fetch_dataset(self, set_progress=None):

        set_progress(0)

        func = partial(
            self._dataset_progress,
            concurrent.methodinvoke(self, "set_progress", (float,))
        )
        progress_task = concurrent.Task(function=func)
        progress_task.exceptionReady.connect(self._dataset_progress_exception)
        self._executor.submit(progress_task)

        # pylint: disable=no-member
        # Settings instance can have items member if it is defined as dict.
        country_codes = [k for k, v in self.country_selection.items()
                         if v == 2 and len(str(k)) == 3]

        logger.debug("Fetch: selected country codes: %s", country_codes)
        climate_dataset = self._api.get_instrumental(
            country_codes,
            data_types=self.include_data_types,
            intervals=self.include_intervals
        )
        self._set_progress_flag = False
        return climate_dataset

    def _fetch_dataset_finished(self):
        assert self.thread() is QtCore.QThread.currentThread()
        self.setEnabled(True)
        self._set_progress_flag = False
        self.set_progress(100)

        if self._fetch_task is None:
            return

        climate_dataset = self._fetch_task.result()
        time_series = self.output_type == 1
        data_table = climate_dataset.as_orange_table(
            time_series=time_series,
            use_names=self.use_country_names,
        )

        self.print_info()
        self.send("Data", data_table)

    @staticmethod
    def _fetch_dataset_exception(exception):
        logger.exception(exception)

    def _dataset_progress(self, set_progress=None):
        while self._set_progress_flag:
            pages = self._api.progress["pages"]
            current_page = self._api.progress["current_page"]
            logger.debug("api progress: %s", self._api.progress)
            if pages > 0:
                progress = ((100 / pages) * (current_page - 1))
                logger.debug("calculated progress: %s", progress)
                set_progress(math.floor(progress))
            time.sleep(1)

    @staticmethod
    def _dataset_progress_exception(exception):
        logger.exception(exception)

    def print_info(self):
        """Refresh info in the info label."""
        lines = ["{}: {}".format(k, v) for k, v in self.info_data.items()
                 if v is not None]
        self._info_label.setText("\n".join(lines))


def main():  # pragma: no cover
    """Helper for running the widget without Orange."""
    logging.basicConfig(level=logging.DEBUG)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtGui.QApplication(sys.argv)
    orange_widget = OWWorldBankClimate()
    orange_widget.show()
    app.exec_()
    orange_widget.saveSettings()


if __name__ == "__main__":
    main()
