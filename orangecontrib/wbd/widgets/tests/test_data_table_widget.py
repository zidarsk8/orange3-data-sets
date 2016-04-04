import sys
import unittest
import mock

from PyQt4 import QtGui
from PyQt4 import QtTest
from PyQt4 import QtCore

from orangecontrib.wbd.widgets import data_table_widget


class TestSimpleFilterWidget(unittest.TestCase):

    def setUp(self):
        self.widget = data_table_widget.DataTableWidget()

    def test_fill_data(self):
        pass
