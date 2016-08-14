"""Tests for main world bank data widget."""

# pylint: disable=protected-access

import unittest
import time

from PyQt4 import QtTest
from PyQt4 import QtCore

from orangecontrib.wbd.widgets import owworldbankindicators
from Orange.widgets.utils import concurrent
# from concurrent.futures import wait


class TestWorldBankDataWidget(unittest.TestCase):
    """Dummy tests for widgets."""

    @staticmethod
    def _busy_wait(futures):
        """Wait for all concurrent tasks to finish.

        This should be done with concurrent.futures.wait but Orange uses its
        own Future implementation that is not supported by the default wait
        function.

        Args:
            futures: list of Orange.widgets.utils.concurrent.Future
        """
        done_states = [
            concurrent.Future.Finished,
            concurrent.Future.Canceled,
        ]
        counter = 0
        done = False
        while not done and counter < 1000:
            time.sleep(0.1)
            done = all(f._state in done_states for f in futures)
            counter += 1
            if counter > 60:
                return

    def test_click_events(self):
        """Test calling callbacks on return press in the filter_text."""
        widget = owworldbankindicators.OWWorldBankIndicators()
        futures = widget._executor._futures + \
            widget.indicator_widget._executor._futures
        self._busy_wait(futures)
        QtTest.QTest.keyPress(widget.filter_text, QtCore.Qt.Key_Return)
