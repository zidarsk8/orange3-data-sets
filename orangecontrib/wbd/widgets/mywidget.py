import sys
import signal

from PyQt4 import QtCore
from PyQt4 import QtGui
from Orange.widgets.widget import OWWidget
from Orange.widgets import gui


class WorldBankDataWidget(OWWidget):
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Hello World"
    icon = "icons/mywidget.svg"
    want_main_area = False

    def __init__(self):
        super().__init__()

        layout = QtGui.QGridLayout()
        button = QtGui.QPushButton("hello")

        countries = CountryListWidget()
        layout.addWidget(button)
        layout.addWidget(countries)
        gui.widgetBox(self.controlArea, margin=0, orientation=layout)


class CountryListWidget(QtGui.QWidget):

    def __init__(self):
        super().__init__()

        layout = QtGui.QGridLayout()

        filter_label = QtGui.QLabel("Filter")
        filter_text = QtGui.QLineEdit()
        filter_button = QtGui.QPushButton("Ok")
        country_list = QtGui.QTableWidget()
        layout.addWidget(filter_label,0,0)
        layout.addWidget(filter_text,0,1)
        layout.addWidget(filter_button,0,2)
        layout.addWidget(country_list,1,0,1,3)


        self.setLayout(layout)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    a = QtGui.QApplication(sys.argv)
    ow = WorldBankDataWidget()
    ow.show()
    a.exec_()
    ow.saveSettings()
