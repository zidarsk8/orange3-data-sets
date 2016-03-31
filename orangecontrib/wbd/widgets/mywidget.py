from PyQt4 import QtCore, QtGui
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

        label = QtGui.QLabel("Hello, World!")
        self.controlArea.layout().addWidget(
            label, QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)


if __name__ == "__main__":
    import sys
    a = QtGui.QApplication(sys.argv)
    ow = WorldBankDataWidget()
    ow.show()
    a.exec_()
    ow.saveSettings()
