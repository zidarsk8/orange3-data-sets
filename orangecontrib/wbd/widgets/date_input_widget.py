from PyQt4 import QtGui


class DateInputWidget(QtGui.QWidget):

    def __init__(self):
        super().__init__()
        layout = QtGui.QHBoxLayout()

        filter_label = QtGui.QLabel("Date")
        self.date_text = QtGui.QLineEdit(self, text="2001:2016")
        layout.addWidget(filter_label)
        layout.addWidget(self.date_text)

        self.setLayout(layout)

    def get_date_string(self):
        # todo: validation
        return self.date_text.text()
