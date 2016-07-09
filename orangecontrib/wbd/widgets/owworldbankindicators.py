"""Model with the main Orange Widget.

This module contains the world bank data widget, used for fetching data from
world bank data API.
"""

import sys
import signal
import logging
from functools import partial

from PyQt4 import QtGui
from PyQt4 import QtCore
from Orange.data import table
from Orange.widgets import widget
from Orange.widgets import gui
from Orange.widgets.utils import concurrent

from Orange.widgets.settings import Setting
from orangecontrib.wbd.countries_and_regions import CountryTreeWidget
# from Orange.widgets.gui import LinkStyledItemDelegate, LinkRole

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

        # GUI
        info_box = gui.widgetBox(self.controlArea, "Info", addSpace=True)
        self.infoBox = gui.widgetLabel(info_box, "Initializing\n\n")

        info_box = gui.widgetBox(self.controlArea, "Indicators", addSpace=True)
        gui.radioButtonsInBox(info_box, self, "indicator_list",
                              ["All", "Common", "Featured"], "Rows",
                              callback=self.indicator_list_selected)

        gui.separator(info_box)

        info_box = gui.widgetBox(self.controlArea, "Output", addSpace=True)
        gui.radioButtonsInBox(info_box, self, "output_type",
                              ["Countries", "Time Series"], "Rows",
                              callback=self.indicator_list_selected)

        gui.separator(info_box)

        info_box = gui.widgetBox(self.controlArea, "Commit", addSpace=True)
        self.commitButton = gui.button(
            info_box, self, "Commit", callback=self.commit)

        # TODO: setStopper does not work.
        # cb = gui.checkBox(info_box, self, "autoCommit",
        #                    "Commit on any change")
        # gui.setStopper(self, self.commitButton, cb, "selectionChanged",
        #                self.commit)

        gui.rubber(self.controlArea)

        gui.widgetLabel(self.mainArea, "Filter")
        self.filterLineEdit = QtGui.QLineEdit(
            textChanged=self.filter_indicator_list)
        #  self.completer = QCompleter(caseSensitivity=Qt.CaseInsensitive)
        #  self.completer.setModel(QStringListModel(self))
        #  self.filterLineEdit.setCompleter(self.completer)

        splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self.mainArea)

        self.mainArea.layout().addWidget(self.filterLineEdit)
        self.mainArea.layout().addWidget(splitter)

        self.treeWidget = QtGui.QTreeView(splitter)
        self.treeWidget.setAlternatingRowColors(True)
        self.treeWidget.setEditTriggers(QtGui.QTreeView.NoEditTriggers)
        self.treeWidget.setRootIsDecorated(False)
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.setUniformRowHeights(True)
        self.treeWidget.viewport().setMouseTracking(True)

        # linkdelegate = LinkStyledItemDelegate(self.treeWidget)
        # self.treeWidget.setItemDelegateForColumn(1, linkdelegate)
        # self.treeWidget.setItemDelegateForColumn(8, linkdelegate)

        splitterH = QtGui.QSplitter(QtCore.Qt.Horizontal, splitter)

        box = gui.widgetBox(splitterH, "Description")
        self.infoGDS = gui.widgetLabel(box, "")
        self.infoGDS.setWordWrap(True)
        gui.rubber(box)

        box = gui.widgetBox(splitterH, "Sample Annotations")
        self.country_tree = CountryTreeWidget(box, self.country_selection)
        box.layout().addWidget(self.country_tree)
        self._annotationsUpdating = False

        self.splitters = splitter, splitterH

        for sp, setting in zip(self.splitters, self.splitterSettings):
            sp.splitterMoved.connect(self._splitter_moved)
            sp.restoreState(setting)

        # self.resize(2000, 600)  # why does this not work

        self.setBlocking(True)
        self.setEnabled(False)
        self.progressBarInit()

        self._executor = concurrent.ThreadExecutor()

        func = partial(self.get_gds_model,
                       concurrent.methodinvoke(self, "_setProgress", (float,)))
        self._inittask = concurrent.Task(function=func)
        self._inittask.finished.connect(self._init_task_finished)
        self._inittask.exceptionReady.connect(self._init_exception)

        self._executor.submit(self._inittask)

    @QtCore.pyqtSlot(float)
    def _setProgress(self, value):
        self.progressBarValue = value

    def _init_exception(self):
        pass

    def _init_task_finished(self):
        self.setEnabled(True)

    def filter_indicator_list(self):
        pass

    def indicator_list_selected(self):
        pass

    def radio_selected(self):
        pass

    def _splitter_moved(self, *args):
        self.splitterSettings = [bytes(sp.saveState())
                                 for sp in self.splitters]

    def get_gds_model(self, progress=lambda val: None):
        import time
        time.sleep(1)
        return


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
