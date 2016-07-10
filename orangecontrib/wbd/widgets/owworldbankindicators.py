"""Model with the main Orange Widget.

This module contains the world bank data widget, used for fetching data from
world bank data API.
"""

import sys
import signal
import logging
from functools import partial

from functools import lru_cache


from PyQt4.QtGui import (
    QLineEdit, QCompleter, QSortFilterProxyModel, QSplitter,
    QTreeView, QItemSelectionModel, QTreeWidget, QTreeWidgetItem,
    QApplication, QStandardItemModel, QStandardItem, QStringListModel
)
from PyQt4.QtCore import Qt, QThread, QCoreApplication


from PyQt4 import QtGui
from PyQt4 import QtCore
from Orange.data import table
from Orange.widgets import widget
from Orange.widgets import gui
from Orange.widgets.utils import concurrent

from Orange.widgets.settings import Setting
from orangecontrib.wbd.countries_and_regions import CountryTreeWidget
from Orange.widgets.gui import LinkRole

TextFilterRole = next(gui.OrangeUserRole)
logger = logging.getLogger(__name__)

class MySortFilterProxyModel(QtGui.QSortFilterProxyModel):

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self._filter_strings = []
        self._cache = {}
        self._cache_fixed = {}
        self._cache_prefix = {}
        self._row_text = {}

        # Create a cached version of _filteredRows
        self._filteredRows = lru_cache(100)(self._filteredRows)

    def setSourceModel(self, model):
        """Set the source model for the filter.
        """
        self._filter_strings = []
        self._cache = {}
        self._cache_fixed = {}
        self._cache_prefix = {}
        self._row_text = {}
        QSortFilterProxyModel.setSourceModel(self, model)

    def addFilterFixedString(self, string, invalidate=True):
        """ Add `string` filter to the list of filters. If invalidate is
        True the filter cache will be recomputed.
        """
        self._filter_strings.append(string)
        all_rows = range(self.sourceModel().rowCount())
        row_text = [self.rowFilterText(row) for row in all_rows]
        self._cache[string] = [string in text for text in row_text]
        if invalidate:
            self.updateCached()
            self.invalidateFilter()

    def removeFilterFixedString(self, index=-1, invalidate=True):
        """ Remove the `index`-th filter string. If invalidate is True the
        filter cache will be recomputed.
        """
        string = self._filter_strings.pop(index)
        del self._cache[string]
        if invalidate:
            self.updateCached()
            self.invalidate()

    def setFilterFixedStrings(self, strings):
        """Set a list of string to be the new filters.
        """
        to_remove = set(self._filter_strings) - set(strings)
        to_add = set(strings) - set(self._filter_strings)
        for str in to_remove:
            self.removeFilterFixedString(
                self._filter_strings.index(str),
                invalidate=False)

        for str in to_add:
            self.addFilterFixedString(str, invalidate=False)
        self.updateCached()
        self.invalidate()

    def _filteredRows(self, filter_strings):
        """Return a dictionary mapping row indexes to True False values.

        .. note:: This helper function is wrapped in the __init__ method.

        """
        all_rows = range(self.sourceModel().rowCount())
        cache = self._cache
        return dict([(row, all([cache[str][row] for str in filter_strings]))
                     for row in all_rows])

    def updateCached(self):
        """Update the combined filter cache.
        """
        self._cache_fixed = self._filteredRows(
            tuple(sorted(self._filter_strings)))

    def setFilterFixedString(self, string):
        """Should this raise an error? It is not being used.
        """
        QSortFilterProxyModel.setFilterFixedString(self, string)

    def rowFilterText(self, row):
        """Return text for `row` to filter on.
        """
        f_role = self.filterRole()
        f_column = self.filterKeyColumn()
        s_model = self.sourceModel()
        data = s_model.data(s_model.index(row, f_column), f_role)
        return str(data)

    def filterAcceptsRow(self, row, parent):
        return self._cache_fixed.get(row, True)

    def lessThan(self, left, right):
        # TODO: Remove fixed column handling
        if left.column() == 1 and right.column():
            left_gds = str(left.data(Qt.DisplayRole))
            right_gds = str(right.data(Qt.DisplayRole))
            left_gds = left_gds.lstrip("GDS")
            right_gds = right_gds.lstrip("GDS")
            try:
                return int(left_gds) < int(right_gds)
            except ValueError:
                pass
        return QSortFilterProxyModel.lessThan(self, left, right)

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

        proxyModel = MySortFilterProxyModel(self.treeWidget)
        self.treeWidget.setModel(proxyModel)
        self.treeWidget.selectionModel().selectionChanged.connect(
            self.updateSelection
        )
        self.treeWidget.viewport().setMouseTracking(True)


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

        func = partial(self._fetch_indicators,
                       concurrent.methodinvoke(self, "_setProgress", (float,)))
        self._fetch_task = concurrent.Task(function=func)
        self._fetch_task.finished.connect(self._fetch_indicators_finished)
        self._fetch_task.exceptionReady.connect(self._init_exception)

        self._executor.submit(self._fetch_task)

    @QtCore.pyqtSlot(float)
    def _setProgress(self, value):
        self.progressBarValue = value

    def _init_exception(self):
        pass

    def _fetch_indicators_finished(self):
        assert self.thread() is QtCore.QThread.currentThread()
        model = self._fetch_task.result()
        model.setParent(self)

        proxy = self.treeWidget.model()
        proxy.setFilterKeyColumn(0)
        proxy.setFilterRole(TextFilterRole)
        proxy.setFilterCaseSensitivity(False)
        # proxy.setFilterFixedString(self.filterString)

        proxy.setSourceModel(model)
        proxy.sort(0, QtCore.Qt.DescendingOrder)

        self.progressBarFinished()
        self.setBlocking(False)
        self.setEnabled(True)

    def updateSelection(self):
        pass

    def filter_indicator_list(self):
        pass

    def indicator_list_selected(self):
        pass

    def _splitter_moved(self, *args):
        self.splitterSettings = [bytes(sp.saveState())
                                 for sp in self.splitters]

    def _fetch_indicators(self, progress=lambda val: None):
        def item(displayvalue, item_values={}):
            item = QStandardItem()
            item.setData(displayvalue, Qt.DisplayRole)
            item.setData("https"+displayvalue, LinkRole)
            return item

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["", "ID", "Title"])
        model.appendRow([item(""), item("22"), item("25"), ])
        model.appendRow([item(" "), item("24"), item("39"), ])

        if QThread.currentThread() is not QCoreApplication.instance().thread():
            model.moveToThread(QCoreApplication.instance().thread())

        return model


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
