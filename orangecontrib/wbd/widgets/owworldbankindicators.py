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
            sp.splitterMoved.connect(self.splitterMoved)
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

    def splitterMoved(self, *args):
        self.splitterSettings = [bytes(sp.saveState())
                                 for sp in self.splitters]

    def get_gds_model(self, progress=lambda val: None):
        import time
        for i in range(1, 100):
            time.sleep(0.01)
            self._setProgress(i)


class CountryTreeWidget(QtGui.QTreeWidget):
    """Display a list of countries and their codes.
    Aggregates:

        Income Levels:
            2   Low income  LIC
            3   Middle income   MIC
            4   - Lower middle income   LMC
            5   - Upper middle income   UMC
            13  High income HIC

        Regions:
            20  East Asia & Pacific (all income levels) EAS
            21  Europe & Central Asia (all income levels)   ECS
            30  Latin America & Caribbean (all income levels)   LCN
            32  Middle East & North Africa (all income levels)  MEA
            33  North America   NAC
            11  South Asia    SAS
            39  Sub-Saharan Africa (all income levels)  SSF

        Other:

            1   World   WLD
            17  Africa  AFR
            18  Arab World  ARB

            6   Low & middle income - LMY
                  All low and middle income regions LMV
            7     East Asia & Pacific (developing only) EAP
            8     Europe & Central Asia (developing only)   ECA
            9     Latin America & Caribbean (developing only)   LAC
            10    Middle East & North Africa (developing only)  MNA
            11    South Asia    SAS
            12    Sub-Saharan Africa (developing only)  SSA

            13  High income - HIC
                  All high income Regions HIC
            14    Euro area EMU
            15    High income: OECD OEC
            16    High income: nonOECD  NOC

            19  Central Europe and the Baltics  CEB
            22  European Union  EUU
            23  Fragile and conflict affected situations    FCS
            24  Heavily indebted poor countries (HIPC)  HPC
            25  IBRD only   IBD
            26  IDA & IBRD total    IBT
            28  IDA blend   IDB
            29  IDA only    IDX
            27  IDA total   IDA
            31  Least developed countries: UN classification    LDC
            34  OECD members    OED
            35  Small states    - SST
                  All small states SST
            36    Caribbean small states    CSS
            37    Pacific island small states   PSS
            38    Other small states    OSS

    Countries:
        # list of all countries
    """

    _country_selector = {
        "Aggregates": {

            "Income Levels": {
                "Low income":  "LIC",
                "Middle income": "MIC",
                "Lower middle income": "LMC",
                "Upper middle income": "UMC",
                "High income": "HIC",
            },

            "Regions": {
                "East Asia & Pacific (all income levels)": "EAS",
                "Europe & Central Asia (all income levels)": "ECS",
                "Latin America & Caribbean (all income levels)": "LCN",
                "Middle East & North Africa (all income levels)": "MEA",
                "North America": "NAC",
                "South Asia": "SAS",
                "Sub-Saharan Africa (all income levels)": "SSF",
            },

            "Other": {

                "World": "WLD",
                "Africa": "AFR",
                "Arab World": "ARB",

                "Low & middle income": {
                    "All low and middle income regions": "LMV",
                    "East Asia & Pacific (developing only)": "EAP",
                    "Europe & Central Asia (developing only)": "ECA",
                    "Latin America & Caribbean (developing only)": "LAC",
                    "Middle East & North Africa (developing only)": "MNA",
                    "South Asia": "SAS",
                    "Sub-Saharan Africa (developing only)": "SSA",
                },

                "High income": {
                    "All high income Regions": "HIC",
                    "Euro area": "EMU",
                    "High income: OECD": "OEC",
                    "High income: nonOECD": "NOC",
                },

                "Central Europe and the Baltics": "CEB",
                "European Union": "EUU",
                "Fragile and conflict affected situations": "FCS",
                "Heavily indebted poor countries (HIPC)": "HPC",
                "IBRD only": "IBD",
                "IDA & IBRD total": "IBT",
                "IDA blend": "IDB",
                "IDA only": "IDX",
                "IDA total": "IDA",
                "Least developed countries: UN classification": "LDC",
                "OECD members": "OED",
                "Small states": {
                    "All small states": "SST",
                    "Caribbean small states": "CSS",
                    "Pacific island small states": "PSS",
                    "Other small states": "OSS",
                },
            },
        }
    }

    def __init__(self, parent, selection_list):
        super().__init__(parent)
        self._selection_list = selection_list
        self._init_view()
        self._set_data()
        self._init_listeners()
        self._busy = False

    def _init_listeners(self):
        self.itemChanged.connect(self.selection_changed)

    def _init_view(self):
        self.setHeaderLabels(["Regions and countries", "Code"])
        self.setRootIsDecorated(True)

    def selection_changed(self, item, column):
        if self._busy:
            return
        self._selection_list[item.key] = item.checkState(0)

    def _fill_values(self, data, parent=None):
        if not parent:
            parent = self

        tristate = QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate
        defaults = self._selection_list
        for name, value in data.items():
            display_key = value if isinstance(value, str) else ""

            item = QtGui.QTreeWidgetItem(parent, [name, display_key])
            item.setFlags(item.flags() | tristate)
            item.key = value if isinstance(value, str) else name

            item.setCheckState(0, defaults.get(item.key, QtCore.Qt.Checked))
            if isinstance(value, dict):
                self._fill_values(value, item)

    def _set_data(self):
        self._annotationsUpdating = True
        self.clear()
        self._fill_values(self._country_selector)

        self.expandAll()
        for i in range(self.columnCount()):
            self.resizeColumnToContents(i)
        self._annotationsUpdating = False


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
