"""Broken events demo."""

import sys
import signal
import unittest

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtTest

from Orange.widgets.widget import OWWidget
from Orange.widgets import gui


class TestMVP(unittest.TestCase):
    """Test for broken events."""

    def test_return_event(self):
        """Test raised events on user input.

        These tests are how the app should pass and they actually work. The
        issue is that when running the app it actually works differently than
        it is shown in these tests.

        The tests and the app work fine if we replace OWWidget with
        QtGui.QWidget.
        """
        _ = QtGui.QApplication(sys.argv)  # noqa
        widget = MVP()
        widget.show()
        QtTest.QTest.qWaitForWindowShown(widget)
        self.assertEqual(widget.events, [0, 0, 0])


        # This event works differently here in the tests as it does in the
        # actual app. The result from the app is [1, 1, 0] because the first
        # button in the app also gets clicked.
        QtTest.QTest.keyPress(widget.some_text, QtCore.Qt.Key_Return)
        self.assertEqual(widget.events, [0, 1, 0])

        # All these buttons work as expected
        QtTest.QTest.mouseClick(widget.ok_button, QtCore.Qt.LeftButton)
        self.assertEqual(widget.events, [1, 1, 0])
        QtTest.QTest.mouseClick(widget.other_button, QtCore.Qt.LeftButton)
        self.assertEqual(widget.events, [1, 1, 1])
        QtTest.QTest.mouseClick(widget.not_ok_button, QtCore.Qt.LeftButton)
        self.assertEqual(widget.events, [1, 2, 1])


class MVP(QtGui.QDialog):
    """Minimal widget for showing event issues."""

    name = "Hello World"
    icon = "icons/mywidget.svg"
    want_main_area = False

    def __init__(self):
        super().__init__()
        self.events = [0, 0, 0]

        layout = QtGui.QVBoxLayout()
        self.ok_button = QtGui.QPushButton(
            self, text="Okay", autoDefault=True)
        self.not_ok_button = QtGui.QPushButton(
            self, text="Not Okay", autoDefault=True)
        self.other_button = QtGui.QPushButton(
            self, text="Other", autoDefault=True)
        self.some_text = QtGui.QLineEdit(self)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.not_ok_button)
        layout.addWidget(self.other_button)
        layout.addWidget(self.some_text)

        self.ok_button.clicked.connect(self.ok_clicked)
        self.not_ok_button.clicked.connect(self.not_ok_clicked)
        self.other_button.clicked.connect(self.other_clicked)
        self.some_text.returnPressed.connect(self.not_ok_button.click)

        self.setLayout(layout)
        # gui.widgetBox(self.controlArea, margin=0, orientation=layout)

    def ok_clicked(self):
        self.events[0] += 1
        print("okay     ", self.events)

    def not_ok_clicked(self):
        self.events[1] += 1
        print("not okay ", self.events)

    def other_clicked(self):
        self.events[2] += 1
        print("ooo      ", self.events)


def main():
    """Helper for running the widget without Orange."""
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtGui.QApplication(sys.argv)
    orange_widget = MVP()
    orange_widget.show()
    app.exec_()
    orange_widget.saveSettings()

if __name__ == "__main__":
    main()


    indictor = "DP.DOD.DECX.CR.BC.Z1"
    date = "2010Q4:2015Q4"
    data_key = "KR"
