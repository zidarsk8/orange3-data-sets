"""Data table widget module."""

from PyQt4 import QtGui


class DataTableWidget(QtGui.QTableWidget):
    """Widget for displaying world bank data.

    This widget is used for preview of world bank data fetched from the API. It
    also allows transposing of the data.
    """

    def __init__(self):
        super().__init__()

    @classmethod
    def _get_unique_dates(cls, dataset):
        """Return a list of all dates found in the dataset.

        This is used when there is data missing for some countries and so we
        get a full list of dates.
        Note; maybe it would be better to replace this with range and take into
        account the quarters and months so that if there is a year missing in
        all countries, that the dataset would still contain those lines"""
        date_sets = [set(value.keys()) for value in dataset.values()]
        return sorted(set().union(*date_sets))

    def fill_data(self, dataset):
        """Fill the main data table.

        Args:
          dataset (wbpy.IndicatorDataset): indicator dataset fetch from the
              wbpy api.

        """
        data_dict = dataset.as_dict()
        dates = self._get_unique_dates(data_dict)
        self.setRowCount(len(dates))
        self.setColumnCount(len(data_dict))
        date_indexes = {date: index for index, date in enumerate(dates)}
        sorted_countries = sorted(dataset.countries.values())
        country_index = {country: index for index, country in
                         enumerate(sorted_countries)}

        for country_id, data in data_dict.items():
            column = country_index[dataset.countries[country_id]]
            for date, value in data.items():
                self.setItem(
                    date_indexes[date],
                    column,
                    QtGui.QTableWidgetItem(str(value))
                )
        self.setHorizontalHeaderLabels(sorted_countries)
        self.setVerticalHeaderLabels(dates)

    def transpose(self):
        """Transpose the displayed world bank data results."""
