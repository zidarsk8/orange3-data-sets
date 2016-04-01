import sys
import unittest
import mock

from PyQt4 import QtGui
from PyQt4 import QtTest
from PyQt4 import QtCore

from orangecontrib.wbd.widgets import simple_filter_widget


class testSimpleFilterWidget(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QtGui.QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls.app.exit()

    def setUp(self):
        self.widget = simple_filter_widget.SimpleFilterWidget()

    def test_register_callback(self):
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
        callback = mock.MagicMock()
        self.widget.register_callback(callback)

        self.widget.filter_text.setText("Hello World")
        self.assertEqual(callback.call_count, 0)
        QtTest.QTest.mouseClick(self.widget.ok_button, QtCore.Qt.LeftButton)
        self.assertEqual(callback.call_count, 1)
        self.assertEqual(callback.call_args, (("Hello World",),))
