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

from PyQt4 import QtGui
from PyQt4 import QtCore
from Orange.data import table
from Orange.widgets import widget
from Orange.widgets import gui
from Orange.widgets.settings import Setting

from orangecontrib.wbd.countries_and_regions import CountryTreeWidget
from orangecontrib.wbd.indicators_list import IndicatorsTreeView
from orangecontrib.wbd import api_wrapper
from orangecontrib.wbd import countries
from orangecontrib.wbd import owwidget_base

logger = logging.getLogger(__name__)


class OWWorldBankIndicators(owwidget_base.OWWidgetBase):
    """World bank data widget for Orange."""
    # pylint: disable=invalid-name
    # Some names have to be invalid to override parent fields.
    # pylint: disable=too-many-ancestors
    # False positive from fetching all ancestors from QWWidget.
    # pylint: disable=too-many-instance-attributes
    # False positive from fetching all attributes from QWWidget.

    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "WB Indicators"
    icon = "icons/wb_icon.png"
    outputs = [widget.OutputSignal(
        "Data",
        table.Table,
        doc="Indicator data from World bank Indicator API"
    )]

    indicator_list_map = collections.OrderedDict([
        (0, "All"),
        (1, "Common"),
        (2, "Featured"),
    ])

    settingsList = [
        "indicator_list_selection",
        "country_selection",
        "indicator_selection",
        "splitterSettings",
        "currentGds",
        "auto_commit",
        "output_type",
    ]

    country_selection = Setting({})
    indicator_selection = Setting([])
    indicator_list_selection = Setting(True)
    output_type = Setting(True)
    auto_commit = Setting(False)

    splitterSettings = Setting((
        b'\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x01\xea'
        b'\x00\x00\x00\xd7\x01\x00\x00\x00\x07\x01\x00\x00\x00\x02',
        b'\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x01\xb5'
        b'\x00\x00\x02\x10\x01\x00\x00\x00\x07\x01\x00\x00\x00\x01'
    ))

    def __init__(self):
        super().__init__()
        self._api = api_wrapper.IndicatorAPI()
        self._init_layout()
        self._check_server_status()

    def _init_layout(self):
        """Initialize widget layout."""

        # Control area
        info_box = gui.widgetBox(self.controlArea, "Info", addSpace=True)
        self._info_label = gui.widgetLabel(info_box, "Initializing\n\n")

        indicator_filter_box = gui.widgetBox(self.controlArea, "Indicators",
                                             addSpace=True)
        gui.radioButtonsInBox(indicator_filter_box, self,
                              "indicator_list_selection",
                              self.indicator_list_map.values(), "Rows",
                              callback=self.indicator_list_selected)
        self.indicator_list_selection = 2

        gui.separator(indicator_filter_box)

        output_box = gui.widgetBox(self.controlArea, "Output", addSpace=True)
        gui.radioButtonsInBox(output_box, self, "output_type",
                              ["Countries", "Time Series"], "Rows",
                              callback=self.output_type_selected)
        self.output_type = 0

        gui.separator(output_box)
        # pylint: disable=duplicate-code
        gui.auto_commit(self.controlArea, self, "auto_commit", "Commit",
                        box="Commit")
        gui.rubber(self.controlArea)

        # Main area

        gui.widgetLabel(self.mainArea, "Filter")
        self.filter_text = QtGui.QLineEdit(
            textChanged=self.filter_indicator_list)
        self.completer = QtGui.QCompleter(
            caseSensitivity=QtCore.Qt.CaseInsensitive)
        self.completer.setModel(QtGui.QStringListModel(self))
        self.filter_text.setCompleter(self.completer)

        spliter_v = QtGui.QSplitter(QtCore.Qt.Vertical, self.mainArea)

        self.mainArea.layout().addWidget(self.filter_text)
        self.mainArea.layout().addWidget(spliter_v)

        self.indicator_widget = IndicatorsTreeView(spliter_v, main_widget=self)

        splitter_h = QtGui.QSplitter(QtCore.Qt.Horizontal, spliter_v)

        self.description_box = gui.widgetBox(splitter_h, "Description")

        self.indicator_description = QtGui.QTextEdit()
        self.indicator_description.setReadOnly(True)
        self.description_box.layout().addWidget(self.indicator_description)

        box = gui.widgetBox(splitter_h, "Countries and Regions")
        self.country_tree = CountryTreeWidget(
            splitter_h, self.country_selection)
        box.layout().addWidget(self.country_tree)
        self.country_tree.set_data(countries.get_countries_regions_dict())

        self.splitters = spliter_v, splitter_h

        for splitter, setting in zip(self.splitters, self.splitterSettings):
            splitter.splitterMoved.connect(self._splitter_moved)
            splitter.restoreState(setting)

        # self.resize(2000, 600)  # why does this not work

        self.progressBarInit()

    def filter_indicator_list(self):
        """Set the proxy model filter and update info box."""
        filter_string = self.filter_text.text()
        proxy_model = self.indicator_widget.model()
        if proxy_model:
            strings = filter_string.lower().strip().split()
            proxy_model.setFilterFixedStrings(strings)
            self.print_info()

    def output_type_selected(self):
        self.commit_if()

    def basic_indicator_filter(self):
        return self.indicator_list_map.get(self.indicator_list_selection)

    def indicator_list_selected(self):
        """Update basic indicator selection.

        Switch indicator list selection between All, Common, and Featured.
        """
        value = self.basic_indicator_filter()
        logger.debug("Indicator list selected: %s", value)
        self.indicator_widget.fetch_indicators()

    def _splitter_moved(self, *_):
        self.splitterSettings = [bytes(sp.saveState())
                                 for sp in self.splitters]

    def _fetch_dataset(self, set_progress=None):
        """Fetch indicator dataset."""
        set_progress(0)
        self._start_progerss_task()

        country_codes = self.get_country_codes()

        if len(country_codes) > 250:
            country_codes = None
        logger.debug("Fetch: selected country codes: %s", country_codes)
        logger.debug("Fetch: selected indicators: %s",
                     self.indicator_selection)
        indicator_dataset = self._api.get_dataset(self.indicator_selection,
                                                  countries=country_codes)
        self._set_progress_flag = False
        return indicator_dataset

    def _dataset_to_table(self, dataset):
        time_series = self.output_type == 1
        return dataset.as_orange_table(time_series=time_series)

    @staticmethod
    def _fetch_dataset_exception(exception):
        logger.exception(exception)

    def _dataset_progress(self, set_progress=None):
        """Update dataset download progress.

        This function reads the progress state from the world bank API and sets
        the current widgets progress to that. All This thread should only read
        data and ask the GUI thread to update the progress for this to be
        thread safe.
        """
        while self._set_progress_flag:
            indicators = self._api.progress["indicators"]
            current_indicator = self._api.progress["current_indicator"]
            indicator_pages = self._api.progress["indicator_pages"]
            current_page = self._api.progress["current_page"]
            logger.debug("api progress: %s", self._api.progress)
            if indicator_pages > 0 and indicators > 0:
                progress = (
                    ((100 / indicators) * (current_indicator - 1)) +
                    (100 / indicators) * (current_page / indicator_pages)
                )
                logger.debug("calculated progress: %s", progress)
                set_progress(math.floor(progress))
            time.sleep(1)

    def _dataset_progress_exception(self, exception):
        logger.exception(exception)
        self.print_info()


def main():  # pragma: no cover
    """Helper for running the widget without Orange."""
    logging.basicConfig(level=logging.DEBUG)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtGui.QApplication(sys.argv)
    indicators_widget = OWWorldBankIndicators()
    indicators_widget.show()
    app.exec_()
    indicators_widget.saveSettings()


if __name__ == "__main__":
    main()
