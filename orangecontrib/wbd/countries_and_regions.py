"""Module contains countries and regions tree widget."""

import collections
import logging

import simple_wbd
from PyQt4 import QtGui
from PyQt4 import QtCore

from orangecontrib.wbd import countries

logger = logging.getLogger(__name__)


class CountryTreeWidget(QtGui.QTreeWidget):
    """Display a list of countries and their codes.

    The aggregates list was taken from:
        https://datahelpdesk.worldbank.org/knowledgebase/articles/898614-api-aggregates-regions-and-income-levels
    Groups were taken from:
        https://datahelpdesk.worldbank.org/knowledgebase/articles/906519
    """

    def __init__(self, parent, selection_list, commit_callback=None):
        super().__init__(parent)
        self._commit_callback = commit_callback
        self._selection_list = selection_list
        self._busy = False
        self._api = simple_wbd.IndicatorAPI()
        self._init_view()
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

    def selection_changed(self, item, _):
        """Country selection change handler.

        This function updates the settings dict with the new selection and
        triggers commit on change callback.

        Args:
            item: list item that has changed.
        """
        if self._busy:
            return
        state = item.checkState(0)
        self._selection_list[item.key] = state
        logger.debug("Selection for item '%s' set to %s", item.key, state)
        if self._commit_callback:
            self._commit_callback()

    def _fill_values(self, data, parent=None):
        if not parent:
            parent = self

        tristate = QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate
        defaults = self._selection_list
        for key, value in data.items():
            name = countries.RENAME_MAP.get(key, value.get("name", key))
            display_key = "" if name == key else key

            item = QtGui.QTreeWidgetItem(parent, [name, display_key])
            item.setFlags(item.flags() | tristate)
            item.key = value if isinstance(value, str) else key

            defaults[item.key] = defaults.get(item.key, QtCore.Qt.Checked)
            item.setCheckState(0, defaults[item.key])
            if isinstance(value, collections.OrderedDict):
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

    def set_data(self, data):
        """Fill the country and region list with new data.

        Args:
            data: dict of dictionaries. The last dictionary must contain a
                field "name" which is displayed in the list.
        """
        self._busy = True
        self.clear()
        self._fill_values(data)
        self.expandAll()
        self._collapse_items()

        for i in range(self.columnCount()):
            self.resizeColumnToContents(i)
        self._busy = False
