"""Module for a simple filter widget for qt."""

from PyQt4 import QtGui
from PyQt4 import QtCore


class SimpleFilterWidget(QtGui.QWidget):
    """Simple filter widget with filter callbacks.

    This is a simple widget with filter text, text area and okay button. The
    widget listens for return pressed or ok button click to call the callbacks
    with the entered filter text.
    """

    def __init__(self):
        super().__init__()
        self.callbacks = set()

        layout = QtGui.QHBoxLayout()

        filter_label = QtGui.QLabel("Filter")
        self.filter_text = QtGui.QLineEdit(self)
        self.ok_button = QtGui.QPushButton(self, text="Ok", autoDefault=True)
        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.filter_text.returnPressed.connect(self.ok_button.click)

        layout.addWidget(filter_label)
        layout.addWidget(self.filter_text)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    @QtCore.pyqtSlot()
    def ok_button_clicked(self):
        """Handler for ok button click.

        This handlers calls all registered callbacks with the text that was
        entered in the filter_text field.
        """
        text = self.filter_text.text()
        for callback in self.callbacks:
            callback(text)

    def register_callback(self, callback):
        """Register custom filter callbacks.

        Args:
            callback (callable): A custom function that takes a single
                parameter.

        Raises:
            TypeError if the argument is not callable function.
        """
        if callable(callback):
            self.callbacks.add(callback)
        else:
            raise TypeError("Callback argument must be a callable function.")
