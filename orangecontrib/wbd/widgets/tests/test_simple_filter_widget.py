"""Tests for simple filter widget."""
import unittest

from PyQt4 import QtTest
from PyQt4 import QtCore

import mock
from orangecontrib.wbd.widgets import simple_filter_widget


class TestSimpleFilterWidget(unittest.TestCase):

    """Tests for simple filter widget."""

    def setUp(self):
        self.widget = simple_filter_widget.SimpleFilterWidget()

    def test_register_callback(self):
        """Test registering of callbacks."""
        def dummy_function(arg):
            return arg
        self.widget.register_callback(lambda arg: arg)
        self.assertEqual(len(self.widget.callbacks), 1)
        self.widget.register_callback(lambda arg: arg)
        self.assertEqual(len(self.widget.callbacks), 2)
        self.widget.register_callback(dummy_function)
        self.assertEqual(len(self.widget.callbacks), 3)
        self.widget.register_callback(dummy_function)
        self.assertEqual(len(self.widget.callbacks), 3)
        self.assertRaises(TypeError, lambda: self.widget.register_callback(2))

    def test_return_key_pressed(self):
        """Test calling callbacks on return press in the filter_text."""
        callback = mock.MagicMock()
        self.widget.register_callback(callback)
        self.assertEqual(callback.call_count, 0)
        QtTest.QTest.keyPress(self.widget.filter_text, QtCore.Qt.Key_Return)
        self.assertEqual(callback.call_count, 1)
        self.assertEqual(callback.call_args, (("",),))

        self.widget.filter_text.setText("Hello World")
        self.assertEqual(callback.call_count, 1)
        QtTest.QTest.keyPress(self.widget.filter_text, QtCore.Qt.Key_Return)
        self.assertEqual(callback.call_count, 2)
        self.assertEqual(callback.call_args, (("Hello World",),))

        self.widget.filter_text.setText("second string")
        QtTest.QTest.keyPress(self.widget.filter_text, QtCore.Qt.Key_Return)
        self.assertEqual(callback.call_count, 3)
        self.assertEqual(callback.call_args, (("second string",),))

        self.widget.filter_text.setText("")
        QtTest.QTest.keyPress(self.widget.filter_text, QtCore.Qt.Key_Return)
        self.assertEqual(callback.call_count, 4)
        self.assertEqual(callback.call_args, (("",),))

    def test_ok_button_pressed(self):
        """Test calling callbacks on ok button click"""
        callback = mock.MagicMock()
        self.widget.register_callback(callback)

        self.widget.filter_text.setText("Hello World")
        self.assertEqual(callback.call_count, 0)
        QtTest.QTest.mouseClick(self.widget.ok_button, QtCore.Qt.LeftButton)
        self.assertEqual(callback.call_count, 1)
        self.assertEqual(callback.call_args, (("Hello World",),))
