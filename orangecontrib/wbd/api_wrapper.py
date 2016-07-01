"""Wrapper for simple_wbd api.

This wrapper adds extra functionality to the IndicatorDataset class, for easier
data manipulation and generating Orange data tables.
"""

import datetime
import logging

import Orange
import simple_wbd

logger = logging.getLogger(__name__)


class IndicatorDataset(simple_wbd.IndicatorDataset):

    def test_function(self):
        return "aa"

    def _get_iso_date(self, date_str):
        """Convert wbd date string into iso format date string.

        Convert date strings such as "2005", "2002Q3" and "1999M7" into iso
        formatted date strings "yyyy-mm-dd"
        """
        try:
            if "Q" in date_str:
                year, quarter = date_str.split("Q")
                return datetime.date_str(int(year), (int(quarter) * 3) - 2, 1)
            elif "M" in date_str:
                year, month = date_str.split("M")
                return datetime.date_str(int(year), int(month), 1)
            else:
                return datetime.date(int(date_str), 1, 1).isoformat()
        except ValueError:
            # some dates contain invalid date strings such as
            # "Last Known Value" or "1988-2000" and possible some more. See:
            # http://api.worldbank.org/countries/PRY/indicators/per_lm_ac.avt_q4_urb?date=1960%3A2016&format=json&per_page=10000  # noqa
            # http://api.worldbank.org/countries/all/indicators/DB_mw_19apprentice?format=json&mrv=10&gapfill=y  # noqa
            return datetime.date.today().isoformat()

    def as_orange_table(self, timeseries=False):
        data = self.as_list(timeseries)

        if data[0][0] == "Date":
            first_column = Orange.data.TimeVariable("Date")
            for row in data[1:]:
                row[0] = first_column.parse(self._get_iso_date(row[0]))
        elif data[0][0] == "Country":
            countries = [row[0] for row in data[1:]]
            first_column = Orange.data.DiscreteVariable(
                "Country", values=countries)
        else:
            logger.warning("Failed to create Orange table.")
            return

        logger.debug(
            "Generated Orange table with  %s data rows and %s columns.",
            len(data),
            len(data[0]) if data else 0,
        )
        domain_columns = [first_column] + [
            Orange.data.ContinuousVariable(column_name)
            for column_name in data[0][1:]
        ]

        domain = Orange.data.Domain(domain_columns)
        data = Orange.data.Table(domain, data[1:])
        return data


class IndicatorAPI(simple_wbd.IndicatorAPI):
    """Simple filter widget with filter callbacks.

    This is a simple widget with filter text, text area and okay button. The
    widget listens for return pressed or ok button click to call the callbacks
    with the entered filter text.
    """

    def __init__(self):
        super().__init__(IndicatorDataset)
