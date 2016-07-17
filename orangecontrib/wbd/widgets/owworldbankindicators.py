"""Model with the main Orange Widget.

This module contains the world bank data widget, used for fetching data from
world bank data API.
"""

import sys
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
        self.indicator_list_selection = 1

        gui.separator(indicator_filter_box)

        output_box = gui.widgetBox(self.controlArea, "Output", addSpace=True)
        gui.radioButtonsInBox(output_box, self, "output_type",
                              ["Countries", "Time Series"], "Rows",
                              callback=self.output_type_selected)

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
        self.infoGDS = gui.widgetLabel(box, "")
        self.infoGDS.setWordWrap(True)
        gui.rubber(box)

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
        country_codes = [k for k, v in self.country_selection.items()
                         if v == 2 and len(str(k)) == 3]
        if len(country_codes) > 250:
            country_codes = None
        print(country_codes)
        print(self.indicator_selection)
        indicator_dataset = self._api.get_dataset(self.indicator_selection,
                                                  countries=country_codes)
        print(indicator_dataset.as_orange_table())


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
