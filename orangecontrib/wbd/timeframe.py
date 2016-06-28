"""Modul for Time Frame widget.

This widget should contain all filters needed to help the user find and select
any indicator.
"""

import datetime
from PyQt4 import QtGui


class TimeFrameWidget(QtGui.QWidget):

    TITLE_TEMPLATE = "Time Frame: {}"
    START_YEAR = 1960

    FROM_DATE = "date"
    LAST_VALUES = "mrv"

    def __init__(self):
        super().__init__()

        layout = QtGui.QFormLayout()
        self.source = self.FROM_DATE

        self.date_from = QtGui.QComboBox()
        self.date_to = QtGui.QComboBox()
        self.fill_combobox(self.date_from)
        self.fill_combobox(self.date_to)
        self.date_from.setCurrentIndex(0)
        self.date_to.setCurrentIndex(self.date_to.count() - 1)
        self.date_from.currentIndexChanged.connect(self.combo_box_changed)
        self.date_to.currentIndexChanged.connect(self.combo_box_changed)

        self.mrv_spinbox = QtGui.QSpinBox(self)
        self.mrv_spinbox.setMaximum(10000)
        self.gapfill_checkbox = QtGui.QCheckBox()
        self.mrv_spinbox.valueChanged.connect(self.mrv_changed)

        layout.addRow("From:", self.date_from)
        layout.addRow("To:", self.date_to)
        layout.addRow("Most Recent Values:", self.mrv_spinbox)
        layout.addRow("Fill unknown Values:", self.gapfill_checkbox)

        self.setLayout(layout)
        self.set_timeframe()

    def set_date_timeframe(self):
        self.date_from.setCurrentIndex(min(
            self.date_from.currentIndex(),
            self.date_to.currentIndex()
        ))
        self.date_to.setCurrentIndex(max(
            self.date_from.currentIndex(),
            self.date_to.currentIndex()
        ))

        if self.date_from.currentIndex() == self.date_to.currentIndex():
            self.set_title(str(self.date_from.currentText()))
        else:
            self.set_title("{} - {}".format(
                self.date_from.currentText(),
                self.date_to.currentText(),
            ))

    def set_mrv_timeframe(self):
        self.set_title("Last {} values. ".format(
            self.mrv_spinbox.value(),
            "Fill Unknown values" if self.gapfill_checkbox.isChecked() else "",
        ))

    def set_timeframe(self):
        return
        if self.source == self.FROM_DATE:
            self.set_date_timeframe()
        elif self.source == self.LAST_VALUES:
            self.set_mrv_timeframe()

    def get_timeframe(self):
        if self.source == self.FROM_DATE:
            return {
                "date": "{}:{}".format(self.date_from.currentText(),
                                       self.date_to.currentText()),
            }
        elif self.source == self.LAST_VALUES:
            return {
                "mrv": self.mrv_spinbox.value(),
                "gapfill": "y" if self.gapfill_checkbox.isChecked() else "n",
            }

    def combo_box_changed(self):
        return
        self.source = self.FROM_DATE
        self.set_timeframe()

    def mrv_changed(self):
        return
        self.source = self.LAST_VALUES
        self.set_timeframe()

    def fill_combobox(self, combobox, frequency="Y"):
        current_year = datetime.date.today().year
        for year in range(self.START_YEAR, current_year + 1):
            if frequency == "Y":
                combobox.addItem(str(year))
            elif frequency == "Q":
                for quarter in range(1, 5):
                    combobox.addItem("{}Q{}".format(year, quarter))
            elif frequency == "M":
                for month in range(1, 13):
                    combobox.addItem("{}M{}".format(year, month))

    def selection_changed(self, selected_ids):
        self.set_title(",".join(selected_ids))
