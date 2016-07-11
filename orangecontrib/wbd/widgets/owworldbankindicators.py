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
from Orange.widgets.settings import Setting

from orangecontrib.wbd.countries_and_regions import CountryTreeWidget
from orangecontrib.wbd.indicators_list import IndicatorsTreeView

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

    settingsList = ["indicator_list", "mergeSpots", "country_selection",
                    "splitterSettings", "currentGds", "autoCommit",
                    "datasetNames", "output_type"]

    country_selection = Setting({})
    indicator_list = Setting(True)
    output_type = Setting(True)
    mergeSpots = Setting(True)
    datasetNames = Setting({})
    autoCommit = Setting(False)

    splitterSettings = Setting(
        (b'\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x01\xea\x00\x00\x00\xd7\x01\x00\x00\x00\x07\x01\x00\x00\x00\x02',  # noqa
         b'\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x01\xb5\x00\x00\x02\x10\x01\x00\x00\x00\x07\x01\x00\x00\x00\x01')  # noqa
    )

    def __init__(self):
        super().__init__()
        logger.debug("Initializing {}".format(self.__class__.__name__))
        self.dataset_params = None
        self.datasetName = ""

        self._init_layout()

    def commit(self):
        pass

    def _init_layout(self):
        """Initialize widget layout."""

        # Control area
        info_box = gui.widgetBox(self.controlArea, "Info", addSpace=True)
        self._info_label = gui.widgetLabel(info_box, "Initializing\n\n")

        info_box = gui.widgetBox(self.controlArea, "Indicators", addSpace=True)
        gui.radioButtonsInBox(info_box, self, "indicator_list",
                              ["All", "Common", "Featured"], "Rows",
                              callback=self.indicator_list_selected)

        gui.separator(info_box)

        output_box = gui.widgetBox(self.controlArea, "Output", addSpace=True)
        gui.radioButtonsInBox(output_box, self, "output_type",
                              ["Countries", "Time Series"], "Rows",
                              callback=self.indicator_list_selected)

        gui.separator(output_box)

        gui.auto_commit(self.controlArea, self, "autoCommit", "Commit",
                        box="Commit")
        self.commitIf = self.commit

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

        self.treeWidget = IndicatorsTreeView(splitter, main_widget=self)

        # linkdelegate = LinkStyledItemDelegate(self.treeWidget)
        # self.treeWidget.setItemDelegateForColumn(1, linkdelegate)
        # self.treeWidget.setItemDelegateForColumn(8, linkdelegate)

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
    def _setProgress(self, value):
        self.progressBarValue = value

    def filter_indicator_list(self):
        pass

    def indicator_list_selected(self):
        pass

    def _splitter_moved(self, *args):
        self.splitterSettings = [bytes(sp.saveState())
                                 for sp in self.splitters]


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
