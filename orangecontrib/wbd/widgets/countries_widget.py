"""Modul for Countries widget.

This widget should contain all filters needed to help the user find and select
any indicator.
"""


from PyQt4 import QtGui

from orangecontrib.wbd.widgets import filter_table_widget

import wbpy


class CountriesWidget(filter_table_widget.HideWidgetWrapper):

    TITLE_TEMPLATE = "Countries: {}"

    def __init__(self):
        super().__init__()

        self.api = wbpy.IndicatorAPI()
        layout = QtGui.QGridLayout()

        toggle_label = QtGui.QLabel("Toggle selection: ")
        toggle_all = QtGui.QPushButton("All")
        toggle_countries = QtGui.QPushButton("Countries")
        toggle_aggregates = QtGui.QPushButton("Aggregates")

        self.countries = filter_table_widget.FilterTableWidget(
            data=self.api.get_country_list(),
            multi_select=True,
        )

        layout.addWidget(toggle_label, 0, 0)
        layout.addWidget(toggle_all, 0, 1)
        layout.addWidget(toggle_countries, 0, 2)
        layout.addWidget(toggle_aggregates, 0, 3)
        layout.addWidget(self.countries, 1, 0, 1, 4)
        self.setLayout(layout)

        self.countries.table_widget.on("selection_changed",
                                       self.selection_changed)

    def selection_changed(self, selected_ids):
        self.set_title(",".join(selected_ids))

    def get_counries(self):
        return self.countries.get_selected_data()
