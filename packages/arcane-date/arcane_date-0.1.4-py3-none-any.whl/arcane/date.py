from datetime import datetime, timedelta, date
import math
from typing import Iterator


def format_date(date: str) -> datetime:
    """
    Format string to datetime object
    :raises ValueError if date is not of valid format
    """
    if date == 'today':
        return datetime.today()
    if date == 'yesterday':
        return (datetime.today() - timedelta(days=1))
    if 'daysAgo' in date:
        try:
            nb_days = int(date.replace('daysAgo', '').strip())
            return (datetime.today() - timedelta(nb_days))
        except (ValueError, TypeError) as err:
            raise ValueError(f'Number of days must be int', {err}) from err
    elif '-' in date:
        try:
            return datetime.strptime(date, '%Y-%m-%d')
        except (ValueError, TypeError) as err:
            raise ValueError(f'Datetime is not of format "%Y-%m-%d", {err}') from err
    else:
        raise ValueError(f'Datetime is not of format "%Y-%m-%d", "today", "yesterday" or "X daysAgo". value "{date}" is not supported yet.')


def daterange(start_date: date, end_date: date):
    """
    Create an iterator over date between start date and end data. Both dates are included.

    """

    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def get_period_range(start_date: datetime, end_date: datetime, period_length: int = 30) -> Iterator[tuple[datetime, datetime]]:
    """Create n chunks of period_length days each, starting at start_date and ending at end_date

    Args:
        start_date (datetime): The starting date of the range
        end_date (datetime): The ending date of the range
        period_length (int, optional): The size of each each period. Defaults to 30.

    Yields:
        Iterator[tuple[datetime, datetime]]: An iterator of tuples of the form (period_start, period_end)
    """
    nb_days = (end_date - start_date).days + 1
    nb_of_period = max(math.ceil(nb_days / period_length), 1)
    for i in range(nb_of_period):
        period_end = start_date + timedelta(days=(i + 1) * period_length - 1)
        if period_end > end_date:
            period_end = end_date
        yield start_date + timedelta(days=i * period_length), period_end
