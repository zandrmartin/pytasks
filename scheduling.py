import calendar
import datetime
import settings


class SchedulingError(Exception):
    pass


def parse_due_date(_d, start=datetime.date.today()):
    """Create a datetime.date object from a given string."""
    d = _d.lower()

    if d == 'today':
        return datetime.date.today()

    if d == 'tomorrow':
        return datetime.date.today() + datetime.timedelta(days=1)

    if d.title() in calendar.day_name:
        day = getattr(calendar, d.upper())

        if day > start.weekday():
            diff = day - start.weekday()
        else:
            diff = (7 - start.weekday()) + day

        return start + datetime.timedelta(days=diff)

    if d.isdigit():
        new_date = start.replace(day=int(d))

        if new_date < start:
            return new_date.replace(month=new_date.month + 1)

        return new_date

    try:
        return datetime.datetime.strptime(d, settings.date_format).date()
    except ValueError:
        pass

    raise SchedulingError(f'{_d} is not a valid date specification.')


def next_scheduled(schedule, start=datetime.date.today()):
    """Create a datetime.date object from a given schedule and start date."""
    err = f'{schedule} is not a valid schedule specification.'

    if ' ' in schedule:
        pieces = schedule.split()
        try:
            number = int(pieces[0])
        except ValueError:
            raise SchedulingError(err)

        frequency = pieces[1].lower()

        if 'day' in frequency:
            return start + datetime.timedelta(days=number)

        if 'week' in frequency:
            return start + datetime.timedelta(days=number * 7)

        if 'month' in frequency:
            return start.replace(month=start.month + number)

        if 'year' in frequency:
            return start.replace(year=start.year + number)

    if 'weekday' in schedule.lower():
        schedule = 'monday,tuesday,wednesday,thursday,friday'

    if any(d.lower() in schedule.lower() for d in calendar.day_name):
        return min(parse_due_date(d, start) for d in schedule.split(','))

    raise SchedulingError(err)
