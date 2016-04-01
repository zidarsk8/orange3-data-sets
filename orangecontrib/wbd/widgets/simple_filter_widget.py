from PyQt4 import QtGui
from PyQt4 import QtCore


class SimpleFilterWidget(QtGui.QWidget):

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
        text = self.filter_text.text()
        for callback in self.callbacks:
            callback(text)

    def register_callback(self, callback):
        if callable(callback):
            self.callbacks.add(callback)
        else:
            raise TypeError("Callback argument must be a callable function.")
