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
from orangecontrib.wbd.indicators_list import IndicatorsTreeView
from orangecontrib.wbd import api_wrapper

TextFilterRole = next(gui.OrangeUserRole)
logger = logging.getLogger(__name__)


class OWWorldBankIndicators(widget.OWWidget):
    """World bank data widget for Orange."""

    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "World Bank Indicators"
    icon = "icons/wb_icon.png"
    category = "Data Sets"
    outputs = [widget.OutputSignal(
        "Data", table.Table,
        doc="Attribute-valued data set read from the input file.")]

    indicator_list_map = collections.OrderedDict([
        (0, "All"),
        (1, "Common"),
        (2, "Featured"),
    ])

    settingsList = ["indicator_list_selection", "mergeSpots", "country_selection",
                    "indicator_selection"
                    "splitterSettings", "currentGds", "auto_commit",
                    "datasetNames", "output_type"]

    country_selection = Setting({})
    indicator_selection = Setting([])
    indicator_list_selection = Setting(True)
    output_type = Setting(True)
    mergeSpots = Setting(True)
    datasetNames = Setting({})
    auto_commit = Setting(False)

    splitterSettings = Setting(
        (b'\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x01\xea\x00\x00\x00\xd7\x01\x00\x00\x00\x07\x01\x00\x00\x00\x02',  # noqa
         b'\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x01\xb5\x00\x00\x02\x10\x01\x00\x00\x00\x07\x01\x00\x00\x00\x01')  # noqa
    )

    def __init__(self):
        super().__init__()
        logger.debug("Initializing {}".format(self.__class__.__name__))
        self._api = api_wrapper.IndicatorAPI()
        self.dataset_params = None
        self.datasetName = ""
        self.selection_changed = False
        self._set_progress_flag = False
        self._executor = concurrent.ThreadExecutor()
        self.info_data = collections.OrderedDict([
            ("Server Status", None),
            ("Indicators", None),
            ("Rows", None),
            ("Columns", None),
        ])

        self._init_layout()

    def _init_layout(self):
        """Initialize widget layout."""

        # Control area
        info_box = gui.widgetBox(self.controlArea, "Info", addSpace=True)
        self._info_label = gui.widgetLabel(info_box, "Initializing\n\n")

        indicator_filter_box = gui.widgetBox(self.controlArea, "Indicators",
                                             addSpace=True)
        gui.radioButtonsInBox(indicator_filter_box, self, "indicator_list_selection",
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

        splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self.mainArea)

        self.mainArea.layout().addWidget(self.filter_text)
        self.mainArea.layout().addWidget(splitter)

        self.indicator_widget = IndicatorsTreeView(splitter, main_widget=self)

        # linkdelegate = LinkStyledItemDelegate(self.indacator_tree)
        # self.indacator_tree.setItemDelegateForColumn(1, linkdelegate)
        # self.indacator_tree.setItemDelegateForColumn(8, linkdelegate)

        splitterH = QtGui.QSplitter(QtCore.Qt.Horizontal, splitter)

        box = gui.widgetBox(splitterH, "Description")

        self.indicator_description = QtGui.QTextEdit()
        self.indicator_description.setReadOnly(True)
        box.layout().addWidget(self.indicator_description)

        box = gui.widgetBox(splitterH, "Sample Annotations")
        self.country_tree = CountryTreeWidget(
            splitterH, self.country_selection)
        box.layout().addWidget(self.country_tree)
        self._annotationsUpdating = False

        self.splitters = splitter, splitterH

        for sp, setting in zip(self.splitters, self.splitterSettings):
            sp.splitterMoved.connect(self._splitter_moved)
            sp.restoreState(setting)

        # self.resize(2000, 600)  # why does this not work

        self.progressBarInit()

    @QtCore.pyqtSlot(float)
    def set_progress(self, value):
        logger.debug("Set progress: %s", value)
        self.progressBarValue = value
        if value == 100:
            self.progressBarFinished()

    def filter_indicator_list(self):
        pass

    def output_type_selected(self):
        pass

    def basic_indicator_filter(self):
        return self.indicator_list_map.get(self.indicator_list_selection)

    def indicator_list_selected(self):
        value = self.basic_indicator_filter()
        logger.debug("Indicator list selected: %s", value)
        self.indicator_widget.fetch_indicators()

    def _splitter_moved(self, *args):
        self.splitterSettings = [bytes(sp.saveState())
                                 for sp in self.splitters]

    def commit_if(self):
        logger.debug("Commit If - auto_commit: %s", self.auto_commit)
        if self.auto_commit:
            self.commit()
        else:
            self.selection_changed = True

    def commit(self):
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

        set_progress(0)

        func = partial(
            self._dataset_progress,
            concurrent.methodinvoke(self, "set_progress", (float,))
        )
        progress_task = concurrent.Task(function=func)
        progress_task.finished.connect(self._dataset_progress_finished)
        progress_task.exceptionReady.connect(self._dataset_progress_exception)
        self._executor.submit(progress_task)


        country_codes = [k for k, v in self.country_selection.items()
                         if v == 2 and len(str(k)) == 3]
        if len(country_codes) > 250:
            country_codes = None
        logger.debug("Fetch: selected country codes: %s", country_codes)
        logger.debug("Fetch: selected indicators: %s", self.indicator_selection)
        indicator_dataset = self._api.get_dataset(self.indicator_selection,
                                                  countries=country_codes)
        self._set_progress_flag = False
        return indicator_dataset

    def _fetch_dataset_finished(self):
        assert self.thread() is QtCore.QThread.currentThread()
        self.setEnabled(True)
        self._set_progress_flag = False
        self.set_progress(100)

        if self._fetch_task is None:
            return

        indicator_dataset = self._fetch_task.result()
        data_table = indicator_dataset.as_orange_table()
        self.info_data["Rows"] = data_table.n_rows

        self.print_info()

    def _fetch_dataset_exception(self, exception):
        logger.exception(exception)

    def _dataset_progress(self, set_progress=None):
        while self._set_progress_flag:
            indicators = self._api.progress["indicators"]
            current_indicator = self._api.progress["current_indicator"]
            indicator_pages = self._api.progress["indicator_pages"]
            current_page = self._api.progress["current_page"]
            logger.debug("api progress: %s", self._api.progress)
            if indicator_pages > 0 and indicators > 0:
                progress = (
                    ((100 / indicators) * (current_indicator - 1)) +
                    (100 / indicators) * (current_page/ indicator_pages)
                )
                logger.debug("calculated progress: %s", progress)
                set_progress(math.floor(progress))
            time.sleep(1)

    def _dataset_progress_finished(self):
        pass

    def _dataset_progress_exception(self, exception):
        logger.exception(exception)

    def print_info(self):
        lines = ["{}: {}".format(k, v) for k, v in self.info_data.items()
                 if v is not None]
        self._info_label.setText("\n".join(lines))


def main():  # pragma: no cover
    """Helper for running the widget without Orange."""
    logging.basicConfig(level=logging.DEBUG)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtGui.QApplication(sys.argv)
    orange_widget = OWWorldBankIndicators()
    orange_widget.show()
    app.exec_()
    orange_widget.saveSettings()


if __name__ == "__main__":
    main()
