"""Test for data table widget."""

import unittest

from orangecontrib.wbd.widgets import data_table_widget


class TestSimpleFilterWidget(unittest.TestCase):
    """Test for data table widget."""

    def setUp(self):
        self.widget = data_table_widget.DataTableWidget()
        self.data = [
            [" ", "A", "B", "C"],
            ["1", "x", "y", "z"],
            ["2", "c", "a", "b"],
            ["3", "w", "@", "+"],
        ]

    def test_fill_data(self):
        """Test setting data from normal array.

        Missing tests for headers
        """
        self.widget.fill_data(self.data)
        self.assertEqual(self.widget.item(0, 0).text(), "1")
        self.assertEqual(self.widget.item(1, 0).text(), "2")
        self.assertEqual(self.widget.item(2, 2).text(), "@")
        self.assertIsNone(self.widget.item(3, 0))

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
