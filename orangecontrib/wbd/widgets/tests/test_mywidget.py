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
    def test_click_events(self, _, ok_event, fetch_event):
        """Test calling callbacks on return press in the filter_text."""
        widget = mywidget.WorldBankDataWidget()
        # import ipdb; ipdb.set_trace()
        self.assertEqual(fetch_event.call_count, 0)
        self.assertEqual(ok_event.call_count, 0)
        QtTest.QTest.mouseClick(widget.button, QtCore.Qt.LeftButton)
        self.assertEqual(fetch_event.call_count, 1)
        QtTest.QTest.mouseClick(widget.countries.filter_widget.ok_button,
                                QtCore.Qt.LeftButton)
        self.assertEqual(fetch_event.call_count, 1)
        self.assertEqual(ok_event.call_count, 1)

    @mock.patch("orangecontrib.wbd.widgets.mywidget.WorldBankDataWidget"
                ".fetch_button_clicked")
    @mock.patch("orangecontrib.wbd.widgets.simple_filter_widget."
                "SimpleFilterWidget.ok_button_clicked")
    @mock.patch("wbpy.IndicatorAPI")
    def test_return_pressed_event(self, _, ok_event, fetch_event):
        """Test click events on return key pressed."""
        widget = mywidget.WorldBankDataWidget()
        # import ipdb; ipdb.set_trace()
        QtTest.QTest.keyPress(widget.countries.filter_widget.filter_text,
                              QtCore.Qt.Key_Return)
        self.assertEqual(fetch_event.call_count, 0)
        self.assertEqual(ok_event.call_count, 1)
