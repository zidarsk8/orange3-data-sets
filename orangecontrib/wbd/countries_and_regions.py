"""Module contains countries and regions tree widget."""

import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

logger = logging.getLogger(__name__)


class CountryTreeWidget(QtGui.QTreeWidget):
    """Display a list of countries and their codes.

    The aggregates list was taken from:
        https://datahelpdesk.worldbank.org/knowledgebase/articles/898614-api-aggregates-regions-and-income-levels
    Groups were taken from:
        https://datahelpdesk.worldbank.org/knowledgebase/articles/906519
    """

    _country_selector = [
        ("Aggregates", [
            ("Income Levels", [
                ("Low income", "LIC"),
                ("Middle income", "MIC"),
                ("Lower middle income", "LMC"),
                ("Upper middle income", "UMC"),
                ("High income", "HIC"),
            ]),
            ("Regions", [
                ("East Asia & Pacific (all income levels)", "EAS"),
                ("Europe & Central Asia (all income levels)", "ECS"),
                ("Latin America & Caribbean (all income levels)", "LCN"),
                ("Middle East & North Africa (all income levels)", "MEA"),
                ("North America", "NAC"),
                ("South Asia", "SAS"),
                ("Sub-Saharan Africa (all income levels)", "SSF"),
            ]),
            ("Other", [
                ("World", "WLD"),
                ("Africa", "AFR"),
                ("Arab World", "ARB"),
                ("Low & middle income", [
                    ("All low and middle income regions", "LMV"),
                    ("East Asia & Pacific (developing only)", "EAP"),
                    ("Europe & Central Asia (developing only)", "ECA"),
                    ("Latin America & Caribbean (developing only)", "LAC"),
                    ("Middle East & North Africa (developing only)", "MNA"),
                    ("Sub-Saharan Africa (developing only)", "SSA"),
                ]),
                ("High income", [
                    ("Euro area", "EMU"),
                    ("High income: OECD", "OEC"),
                    ("High income: nonOECD", "NOC"),
                ]),
                ("Central Europe and the Baltics", "CEB"),
                ("European Union", "EUU"),
                ("Fragile and conflict affected situations", "FCS"),
                ("Heavily indebted poor countries (HIPC)", "HPC"),
                ("IBRD only", "IBD"),
                ("IDA & IBRD total", "IBT"),
                ("IDA blend", "IDB"),
                ("IDA only", "IDX"),
                ("IDA total", "IDA"),
                ("Least developed countries: UN classification", "LDC"),
                ("OECD members", "OED"),
                ("Small states", [
                    ("All small states", "SST"),
                    ("Caribbean small states", "CSS"),
                    ("Pacific island small states", "PSS"),
                    ("Other small states", "OSS"),
                ]),
            ]),
        ]),
    ]

    def __init__(self, parent, selection_list):
        super().__init__(parent)
        self._selection_list = selection_list
        self._busy = False
        self._init_view()
        self._set_data()
        self._init_listeners()

    def _init_listeners(self):
        self.itemChanged.connect(self.selection_changed)
        self.itemCollapsed.connect(self._item_collapsed)
        self.itemExpanded.connect(self._item_expanded)

    def _item_expanded(self, item):
        self._selection_list[("collapsed", item.key)] = False

    def _item_collapsed(self, item):
        self._selection_list[("collapsed", item.key)] = True

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
        for name, value in data:
            display_key = value if isinstance(value, str) else ""

            item = QtGui.QTreeWidgetItem(parent, [name, display_key])
            item.setFlags(item.flags() | tristate)
            item.key = value if isinstance(value, str) else name

            item.setCheckState(0, defaults.get(item.key, QtCore.Qt.Checked))
            if isinstance(value, list):
                self._fill_values(value, item)

    def _collapse_items(self, root=None):
        """Collapse items that were marked as collapsed in previous sessions.

        Args:
            root: Item whose children we want to check and collapse. If none is
                set, root item is chosen and we iterate through all top level
                items.
        """
        if root is None:
            root = self.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            if not item.childCount():
                continue
            if self._selection_list.get(("collapsed", item.key)):
                item.setExpanded(False)
            self._collapse_items(item)

    def _set_data(self):
        self._busy = True
        self.clear()
        self._fill_values(self._country_selector)

        self.expandAll()
        self._collapse_items()

        for i in range(self.columnCount()):
            self.resizeColumnToContents(i)
        self._busy = False
