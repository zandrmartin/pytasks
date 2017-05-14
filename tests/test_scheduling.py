import datetime
import pytest

import scheduling


def test_parse_due_date(jan_3_2017):
    """Test the scheduling.parse_due_date() function."""

    # test "today"
    expected = datetime.date.today()
    result = scheduling.parse_due_date('today', jan_3_2017)
    assert result == expected

    # test "tomorrow"
    expected = datetime.date.today() + datetime.timedelta(days=1)
    result = scheduling.parse_due_date('tomorrow', jan_3_2017)
    assert result == expected

    # test "wednesday"
    expected = jan_3_2017.replace(day=4)
    result = scheduling.parse_due_date('wednesday', jan_3_2017)
    assert result == expected

    # test "monday"
    expected = jan_3_2017.replace(day=9)
    result = scheduling.parse_due_date('monday', jan_3_2017)
    assert result == expected

    # test "6" (Friday 1-6-2017)
    expected = jan_3_2017.replace(day=6)
    result = scheduling.parse_due_date('6', jan_3_2017)
    assert result == expected

    # test "1" (Wednesday 2-1-2017)
    expected = jan_3_2017.replace(month=2, day=1)
    result = scheduling.parse_due_date('1', jan_3_2017)
    assert result == expected

    # test YYYY-MM-DD formatted date (2020-07-05)
    expected = datetime.date(2020, 7, 5)
    result = scheduling.parse_due_date('2020-07-05', jan_3_2017)
    assert result == expected

    # test failure with invalid date
    with pytest.raises(scheduling.SchedulingError):
        scheduling.parse_due_date('foobar', jan_3_2017)


def test_next_scheduled(jan_3_2017):
    """Test the scheduling.next_scheduled() function."""

    # test "3 days"
    expected = jan_3_2017.replace(day=6)
    result = scheduling.next_scheduled('3 days', jan_3_2017)
    assert result == expected

    # test "4 weeks"
    expected = datetime.date(2017, 1, 31)
    result = scheduling.next_scheduled('4 weeks', jan_3_2017)
    assert result == expected

    # test "5 months"
    expected = jan_3_2017.replace(month=6)
    result = scheduling.next_scheduled('5 months', jan_3_2017)
    assert result == expected

    # test "2 years"
    expected = jan_3_2017.replace(year=2019)
    result = scheduling.next_scheduled('2 years', jan_3_2017)
    assert result == expected

    # test "thursday"
    expected = jan_3_2017.replace(day=5)
    result = scheduling.next_scheduled('thursday', jan_3_2017)
    assert result == expected

    # test "monday"
    expected = jan_3_2017.replace(day=9)
    result = scheduling.next_scheduled('monday', jan_3_2017)
    assert result == expected

    # test "weekdays"
    expected = jan_3_2017.replace(day=4)
    result = scheduling.next_scheduled('weekdays', jan_3_2017)
    assert result == expected

    # test "weekdays" from a Friday
    jan_6_2017 = jan_3_2017.replace(day=6)
    expected = jan_3_2017.replace(day=9)
    result = scheduling.next_scheduled('weekdays', jan_6_2017)
    assert result == expected

    # test failure with invalid schedule
    with pytest.raises(scheduling.SchedulingError):
        scheduling.next_scheduled('foobar', jan_3_2017)
