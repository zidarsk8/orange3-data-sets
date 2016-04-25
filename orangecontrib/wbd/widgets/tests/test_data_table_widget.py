"""Test for data table widget."""

import unittest

from PyQt4 import QtTest

from orangecontrib.wbd.widgets import data_table_widget


class TestSimpleFilterWidget(unittest.TestCase):
    """Test for data table widget."""

    def setUp(self):
        self.widget = data_table_widget.DataTableWidget()
        self.widget.show()
        QtTest.QTest.qWaitForWindowShown(self.widget)
        self.data = [
            [" ", "A", "B", "C"],
            ["1", "x", "y", "z"],
            ["2", "c", "a", "b"],
            ["3", "w", "@", "+"],
        ]

    def test_fill_data_headers(self):
        """Test setting headers from normal array."""
        self.widget.fill_data(self.data)

        headers = self.data[0]

        for column, header in enumerate(headers):
            self.assertEqual(self.widget.horizontalHeaderItem(column).text(),
                             header)

        self.assertIsNone(self.widget.horizontalHeaderItem(-1))
        self.assertIsNone(self.widget.horizontalHeaderItem(len(headers) + 1))

    def test_fill_data(self):
        """Test setting data from normal array."""

        self.widget.fill_data(self.data)
        data = self.data[1:]

        for row, row_data in enumerate(data):
            for column, cell in enumerate(row_data):
                self.assertEqual(self.widget.item(row, column).text(), cell)

        self.assertIsNone(self.widget.item(len(data) + 1, len(data[0])))
        self.assertIsNone(self.widget.item(len(data), len(data[0]) + 1))
        self.assertIsNone(self.widget.item(-1, 0))
        self.assertIsNone(self.widget.item(0, -1))

    def test_empty_data(self):
        """Test that data gets removed when filling with empty array."""
        self.widget.fill_data(self.data)
        self.assertIsNotNone(self.widget.item(0, 0))
        self.widget.fill_data([[]])
        self.assertIsNone(self.widget.item(0, 0))

        self.widget.fill_data(self.data)
        self.assertIsNotNone(self.widget.item(0, 0))
        self.widget.fill_data([])
        self.assertIsNone(self.widget.item(0, 0))
