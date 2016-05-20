"""Modul for Time Frame widget.

This widget should contain all filters needed to help the user find and select
any indicator.
"""

import datetime
from PyQt4 import QtGui

import wbpy

from orangecontrib.wbd.widgets import filter_table_widget


class TimeFrameWidget(filter_table_widget.HideWidgetWrapper):

    TITLE_TEMPLATE = "Time Frame: {}"
    START_YEAR = 1960

    def __init__(self):
        super().__init__()

        self.api = wbpy.IndicatorAPI()
        layout = QtGui.QGridLayout()

        # filter_label = QtGui.QLabel("Date")
        self.date_from = QtGui.QComboBox()
        self.date_to = QtGui.QComboBox()
        self.fill_combobox(self.date_from)
        self.fill_combobox(self.date_to)

        self.date_from.currentIndexChanged.connect(self.combo_box_changed)
        self.date_to.currentIndexChanged.connect(self.combo_box_changed)

        self.mrv_text = QtGui.QSpinBox(self)
        mrv_gapfill = QtGui.QCheckBox("Fill Unknown Values")
        layout.addWidget(self.date_from, 0, 0)
        layout.addWidget(self.date_to, 0, 1)
        layout.addWidget(self.mrv_text, 1, 0)
        layout.addWidget(mrv_gapfill, 1, 1)

        self.setLayout(layout)

    def combo_box_changed(self):
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
        pass

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
