"""Time management helper.

stephane.ploix@g-scop.grenoble-inp.fr
"""
from __future__ import annotations
import datetime
import time
from typing import Literal
import pytz
from statistics import mean
from tzlocal import get_localzone

REGULAR_DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'


def epochtimems_to_stringdate(epochtimems, date_format=REGULAR_DATETIME_FORMAT, timezone_str: str = None) -> str:
    """Transform an epoch time  into a string representation.

    :param epochtimems: epoch time in milliseconds
    :type epochtimems: int
    :return: string representation '%d/%m/%Y %H:%M:%S'
    :rtype: datetime.datetime
    """
    if timezone_str is None:
        timezone_str = str(get_localzone())
    dt = datetime.datetime.fromtimestamp(epochtimems // 1000)
    localized_dt = pytz.timezone(timezone_str).localize(dt, is_dst=True)
    return localized_dt.strftime(date_format)


def epochtimems_to_datetime(epochtimems, timezone_str: str = None) -> datetime.datetime:
    """Transform an epoch time into an internal datetime representation.

    :param epochtimems: epoch time in milliseconds
    :type epochtimems: int
    :return: internal datetime representation
    :rtype: datetime.datetime
    """
    if timezone_str is None:
        timezone_str = str(get_localzone())
    dt = datetime.datetime.fromtimestamp(epochtimems // 1000)
    localized_dt = pytz.timezone(timezone_str).localize(dt, is_dst=True)
    return localized_dt


def date_to_epochtimems(a_date: datetime) -> int:
    return datetime_to_epochtimems(a_date)


def datetime_to_epochtimems(a_datetime) -> int:
    """Transform a an internal datetime representation into a epoch time.

    :param a_datetime: internal datetime representation
    :type a_datetime: datetime to be converted
    :return: epoch time in milliseconds
    :rtype: int
    """
    if type(a_datetime) is datetime.date:
        a_datetime: datetime.datetime = datetime.datetime.combine(
            a_datetime, datetime.time(0))
    return a_datetime.timestamp() * 1000


def stringdate_to_epochtimems(stringdatetime, date_format=REGULAR_DATETIME_FORMAT, timezone_str: str = None) -> int:
    """Transform a date string representation into an epoch time.

    :param stringdatetime: date string representation '%d/%m/%Y %H:%M:%S'
    :type stringdatetime: str
    :return: epoch time in milliseconds
    :rtype: int
    """

    if timezone_str is None:
        timezone_str = str(get_localzone())
    dt = datetime.datetime.strptime(stringdatetime, date_format)
    localized_dt = pytz.timezone(timezone_str).localize(
        dt, is_dst=True)  # Changed is_dst to None for automatic detection
    return int(localized_dt.timestamp() * 1000)
    if timezone_str is None:
        timezone_str = str(get_localzone())
    dt = datetime.strptime(stringdatetime, date_format)
    localized_dt: datetime.datetime = pytz.timezone(
        timezone_str).localize(dt, is_dst=True)
    return int(localized_dt.timestamp() * 1000)


def stringdate_to_openmeteo_date(stringdate: str, timezone_str: str = None) -> str:
    if timezone_str is None:
        timezone_str = str(get_localzone())
    a_struct_time: datetime.struct_time = time.strptime(stringdate, '%d/%m/%Y')
    a_datetime = datetime.datetime(
        *a_struct_time[:6], tzinfo=pytz.timezone(timezone_str))
    return a_datetime.strftime('%Y-%m-%d')


def openmeteo_to_stringdate(openmeteo_date: str) -> str:
    """Transform an openmeteo date into a string representation.

    :param openmeteo_date: openmeteo date in format 'Y-m-d'
    :type openmeteo_date: str
    :return: string representation
    :rtype: str
    """
    year, month, day = openmeteo_date.split('-')
    return day + '/' + month + '/' + year


def openmeteo_to_stringdatetime(openmeteo_date) -> str:
    a_date, a_time = openmeteo_date.split('T')
    year, month, day = a_date.split('-')
    hour, minute = a_time.split(':')
    return day + '/' + month + '/' + year + ' ' + hour + ':' + minute + ':00'


def datetime_to_stringdate(a_datetime: datetime, date_format: str = REGULAR_DATETIME_FORMAT) -> str:
    """Transform a datetime representation into a datetime internal format.

    :param a_datetime: internal datetime representation
    :type a_datetime: datetime.datetime
    :return: stringdatetime: date string representation '%d/%m/%Y %H:%M:%S'
    :rtype: str
    """
    return a_datetime.strftime(date_format)


def stringdate_to_datetime(stringdatetime, date_format=REGULAR_DATETIME_FORMAT, timezone_str: str = None) -> datetime:
    """Transform a date string representation into an internal datetime representation.

    :param stringdatetime: date string representation '%d/%m/%Y %H:%M:%S'
    :type stringdatetime: str
    :return: internal datetime representation
    :rtype: datetime.datetime
    """
    if timezone_str is None:
        timezone_str = str(get_localzone())
    dt = datetime.datetime.strptime(stringdatetime, date_format)
    localized_dt: datetime.datetime = pytz.timezone(
        timezone_str).localize(dt, is_dst=True)
    return localized_dt


def stringdate_to_date(stringdate: str, date_format='%d/%m/%Y', timezone_str: str = None) -> datetime:
    """Transform a date string representation into an internal datetime representation.

    :param stringdatetime: date string representation '%d/%m/%Y'
    :type stringdatetime: str
    :return: internal datetime representation
    :rtype: datetime.datetime
    """
    if timezone_str is None:
        timezone_str = str(get_localzone())
    dt = datetime.datetime.strptime(stringdate, date_format)
    localized_dt: datetime.datetime = pytz.timezone(
        timezone_str).localize(dt, is_dst=True)
    return localized_dt.date()


def date_to_stringdate(a_date: datetime.date, date_format='%d/%m/%Y') -> str:
    a_datetime = datetime.datetime.combine(a_date, datetime.time(0))
    # a_datetime.replace(tzinfo=pytz.timezone(tz) if tz is not None else None)
    return a_datetime.strftime(date_format)


def epochtimems_to_timequantum(epochtimems, timequantum_duration_in_secondes) -> int:
    """Transform an epoch time into a rounded discrete epoch time according to a given time quantum (sampling period).

    :param epochtimems: epoch time in milliseconds
    :type epochtimems: int
    :param timequantum_duration_in_secondes: time quantum duration (sampling period) in seconds
    :type timequantum_duration_in_secondes: int
    :return: rounded discrete epoch time in milliseconds
    """
    return (epochtimems // (timequantum_duration_in_secondes * 1000)) * timequantum_duration_in_secondes * 1000


def datetime_with_day_delta(a_datetime: datetime.datetime, number_of_days: int = 0, date_format: str = REGULAR_DATETIME_FORMAT) -> str:
    """Compute a date from today minus a given day delta.

    :param number_of_days: number of day to remove to the current date, defaults to 0
    :type number_of_days: int, optional
    :param date_format: date format, defaults to '%d/%m/%Y %H:%M:%S'
    :type date_format: str, optional
    :return: the date in the past
    :rtype: datetime.datetime
    """
    return (a_datetime + datetime.timedelta(days=number_of_days)).strftime(date_format)


def current_stringdate(date_format=REGULAR_DATETIME_FORMAT) -> str:
    """Return the current date in string format.

    :param date_format: the string format, defaults to '%d/%m/%Y %H:%M:%S'
    :type date_format: str, optional
    :return: current date in string
    :rtype: str
    """
    return time.strftime(date_format, time.localtime())


def current_epochtimems() -> int:
    """Return current date in epoch time format.

    :return: epoch time number of milliseconds
    :rtype: int
    """
    return int(time.mktime(time.localtime()) * 1000)


def time_from_seconds_day_hours_minutes(duration_in_seconds: int) -> str:
    d = duration_in_seconds // (24 * 3600)
    h = (duration_in_seconds - 24 * d * 3600) // 3600
    m = (duration_in_seconds - 24 * d * 3600 - h * 3600) // 60
    s = (duration_in_seconds - 24 * d * 3600 - h * 3600 - m * 60) % 60

    return '%i days, %i hours, %i min, %i sec' % (d, h, m, s)


def dayify(datetime_data: list[float], datetimes: list[datetime.datetime], processing: str = 'average') -> tuple[list[float], list[datetime.date]]:
    """Convert a time series in datetimes to a time series in dates by merging data
    Merging can be: averaging data (average), summing data (summation), maximizing data (min), minimizing data (min), averaging only positive data and ignoring others (avgifpos)
    :param datetime_data: list of datetimes
    :type datetimes-data: list[float]
    :param datetimes: the datetimes of the series to process
    :type datetimes: list[datetime]
    :param processing: merge type among "average", "summation" or "avgifpos". Default to average
    :type processing:  str among "average"/"avg"/"mean", "summation"/"sum", "minimize"/"min", "maximize"/"max" or "avgifpos"
    """
    dates = list()
    daily_data = list()
    buffer = list()
    current_date = datetimes[0].date()
    for i, dt in enumerate(datetimes):
        if dt.date() != current_date or (i+1 == len(datetimes) and len(buffer) > 0):
            if processing in ('average', 'avg', 'mean'):
                if len(buffer) == 0:
                    daily_data.append(0)
                else:
                    daily_data.append(mean(buffer))
            elif processing in ('summation', 'sum'):
                daily_data.append(sum(buffer))
            elif processing in ('max', 'maximize'):
                daily_data.append(max(buffer))
            elif processing in ('min', 'minimize'):
                daily_data.append(min(buffer))
            elif processing == 'avgifpos':
                size = 0
                for v in buffer:
                    if v > 0:
                        size += 1
                if size > 0:
                    daily_data.append(sum(buffer)/size)
                else:
                    daily_data.append(0)
            elif processing == 'maximum':
                daily_data.append(max(buffer))
            else:
                raise ValueError('Unknown processing')
            dates.append(current_date)
            buffer = [datetime_data[i]]
            current_date = datetimes[i].date()
        else:
            buffer.append(datetime_data[i])
    return daily_data, dates


class TimeSeriesMerger:

    def __init__(self, datetimes: list[datetime.date] | list[datetime.datetime], values: list[float], group_by: str):

        self._datetimes: list[datetime.date] | list[datetime.datetime] = datetimes
        self.values: list[float] = values
        self.indices: list[tuple[int, int]] = [0]
        self.group_by = group_by
        if group_by != 'hour':
            sequence_types: dict[str, str] = {
                'day': '%d', 'week': '%V', 'month': '%m', 'year': '%Y'}
            sequence_type: str = sequence_types[group_by]

            sequence_id: list[int] = datetimes[0].strftime(sequence_type)
            for i in range(1, len(datetimes)):
                next_sequence_id = datetimes[i].strftime(sequence_type)
                if next_sequence_id != sequence_id:
                    self.indices.append(i)
                    sequence_id = next_sequence_id
            if self.indices[-1] != len(self._datetimes) - 1:
                self.indices.append(len(self._datetimes))

    def __call__(self, merge_function: str = 'avg') -> list[float]:
        if self.group_by == 'hour':
            return self.values
        merge_functions: dict[str, str] = {
            'avg': mean, 'mean': mean, 'min': min, 'max': max, 'sum': sum}
        merged_values = list()
        for k in range(1, len(self.indices)):
            group_value: float = merge_functions[merge_function](
                [self.values[i] if self.values[i] is not None else 0 for i in range(self.indices[k-1], self.indices[k])])
            for i in range(self.indices[k] - self.indices[k-1]):
                merged_values.append(group_value)
        return merged_values
