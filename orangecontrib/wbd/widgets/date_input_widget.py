"""Simple date input widget."""
from PyQt4 import QtGui


class DateInputWidget(QtGui.QWidget):
    """Date input widget with date string validation.

    This Widget is meant for date input for World bank data style dates and
    date ranges. It also includes validation for dates.

    Allowed date types are year only, year with quarter, and year with month.
    Ranges are defined with two year parameters separated with a colon. The
    date order in the specified range does not matter.
    Examples:
        2010
        2006Q3
        2000M11
        2005:2011 (equals 2011:2005)
        2006Q1:2006Q3 (equals 2006Q3:2006Q1)
    """

    def __init__(self):
        super().__init__()
        layout = QtGui.QHBoxLayout()

        filter_label = QtGui.QLabel("Date")
        self.date_text = QtGui.QLineEdit(self, text="2001:2016")
        layout.addWidget(filter_label)
        layout.addWidget(self.date_text)

        self.setLayout(layout)

    def get_date_string(self):
        """Get inputted date string.

        This needs some validation.

        Returns:
            String representing a date or a date range.
        """
        return self.date_text.text()
