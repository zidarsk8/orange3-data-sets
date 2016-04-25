"""Tests for main world bank data widget."""
import unittest

from PyQt4 import QtTest
from PyQt4 import QtCore

import mock
from orangecontrib.wbd.widgets import mywidget


class TestWorldBankDataWidget(unittest.TestCase):
    """Tests for simple filter widget."""

    @mock.patch("orangecontrib.wbd.widgets.mywidget.WorldBankDataWidget"
                ".fetch_button_clicked")
    @mock.patch("orangecontrib.wbd.widgets.simple_filter_widget."
                "SimpleFilterWidget.ok_button_clicked")
    @mock.patch("wbpy.IndicatorAPI")
    def setUp(self, _, ok_event, fetch_event):
        # pylint: disable=arguments-differ
        # This function has more arguments because of the patches and we can
        # ignore this warning.
        self.widget = mywidget.WorldBankDataWidget()
        self.widget.show()
        QtTest.QTest.qWaitForWindowShown(self.widget)
        self.ok_event = ok_event
        self.fetch_event = fetch_event

    def test_click_events(self):
        """Test calling callbacks on return press in the filter_text."""
        self.assertEqual(self.fetch_event.call_count, 0)
        self.assertEqual(self.ok_event.call_count, 0)
        QtTest.QTest.mouseClick(self.widget.button, QtCore.Qt.LeftButton)
        self.assertEqual(self.fetch_event.call_count, 1)
        QtTest.QTest.mouseClick(self.widget.countries.filter_widget.ok_button,
                                QtCore.Qt.LeftButton)
        self.assertEqual(self.fetch_event.call_count, 1)
        self.assertEqual(self.ok_event.call_count, 1)

    def test_return_pressed_event(self):
        """Test click events on return key pressed."""
        QtTest.QTest.keyPress(self.widget.countries.filter_widget.filter_text,
                              QtCore.Qt.Key_Return)
        self.assertEqual(self.fetch_event.call_count, 0)
        self.assertEqual(self.ok_event.call_count, 1)
