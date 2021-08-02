from datetime import datetime


def month_delta(date, delta):
    """
    function to return the date changed by delta month (+/-)
    :param date: date to start from
    :param delta: integer (+/-) to change the month
    :return: date changed by month
    """
    m, y = (date.month + delta) % 12, date.year + (date.month + delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day, [31,
                       29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])

    return date.replace(day=d, month=m, year=y)


def first(iterable, condition=lambda x: True):
    """
    Returns the first item in the `iterable` that
    satisfies the `condition`.

    If the condition is not given, returns the first item of
    the iterable.

    Raises `StopIteration` if no item satysfing the condition is found.

    >>> first( (1,2,3), condition=lambda x: x % 2 == 0)
    2
    >>> first(range(3, 100))
    3
    >>> first( () )
    Traceback (most recent call last):
    ...
    StopIteration
    """

    return next(x for x in iterable if condition(x))


class ChartDataset:
    """
    chart that holds one data set along with some styling data
    """

    def __init__(self, name, color, solid):
        self.name = name
        self.color = color
        self.solid = solid
        self.data = []
        self.delta = [] # absolute, to previous month


class ChartMarker:
    """
    class that holds one marker on the chart
    """

    def __init__(self, app_name, timeline_index, marker):
        self.app_name = app_name
        self.timeline_index = timeline_index
        self.marker = marker


class MonthYear:
    """
    class that holds the chart data ready to be displayed
    """

    def __init__(self):
        self.month = 0
        self.year = 0

    def __init__(self, month, year):
        self.month = month
        self.year = year

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, MonthYear):
            return self.month == other.month and self.year == other.year
        return False


class ChartData:
    """
    class that holds the chart data ready to be displayed
    """

    def __init__(self):
        self.timeline = []
        self.datasets = []
        self.markers = []

    def named(self, name):
        for dataset_item in self.datasets:
            if dataset_item.name == name:
                return dataset_item

        return None


def prev_two_month(date_value=datetime.today()):
    if date_value.month == 1:
        return date_value.replace(month=11, year=date_value.year - 1)
    elif date_value.month == 2:
        return date_value.replace(month=12, year=date_value.year - 1)
    else:
        try:
            return date_value.replace(month=date_value.month - 2)
        except ValueError:
            return prev_two_month(date_value=date_value.replace(day=date_value.day - 1))
