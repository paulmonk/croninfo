from __future__ import annotations

import datetime as dt

import pytest

from croninfo.crontab import Crontab


@pytest.mark.parametrize(
    "expr, expected",
    [
        (
            "* * * * * /usr/bin/find",
            "minute=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, "
            "22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, "
            "43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59] "
            "hour=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23] "
            "monthday=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, "
            "24, 25, 26, 27, 28, 29, 30, 31] "
            "month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] "
            "weekday=[1, 2, 3, 4, 5, 6, 7] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        (
            "0 0-23 */2 1,2-3,4-12/2 0,1,2 /usr/bin/find",
            "minute=[0] "
            "hour=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23] "
            "monthday=[1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31] "
            "month=[1, 2, 3, 4, 6, 8, 10, 12] "
            "weekday=[1, 2, 7] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        (
            "*/15 0 1,15 * 1-5 /usr/bin/find",
            "minute=[0, 15, 30, 45] "
            "hour=[0] "
            "monthday=[1, 15] "
            "month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] "
            "weekday=[1, 2, 3, 4, 5] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        (
            "*/30 0 * jan,FEB 1-5 /usr/bin/find",
            "minute=[0, 30] "
            "hour=[0] "
            "monthday=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, "
            "24, 25, 26, 27, 28, 29, 30, 31] "
            "month=[1, 2] "
            "weekday=[1, 2, 3, 4, 5] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        (
            "*/30 0 * 1 Mon-Sat /usr/bin/find",
            "minute=[0, 30] "
            "hour=[0] "
            "monthday=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, "
            "24, 25, 26, 27, 28, 29, 30, 31] "
            "month=[1] "
            "weekday=[1, 2, 3, 4, 5, 6] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        (
            "*/30 0 10 jan-4,8-12 1-5 /usr/bin/find",
            "minute=[0, 30] "
            "hour=[0] "
            "monthday=[10] "
            "month=[1, 2, 3, 4, 8, 9, 10, 11, 12] "
            "weekday=[1, 2, 3, 4, 5] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        # Macros
        (
            "@yearly /usr/bin/find",
            "minute=[0] "
            "hour=[0] "
            "monthday=[1] "
            "month=[1] "
            "weekday=[1, 2, 3, 4, 5, 6, 7] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        (
            "@annually /usr/bin/find",
            "minute=[0] "
            "hour=[0] "
            "monthday=[1] "
            "month=[1] "
            "weekday=[1, 2, 3, 4, 5, 6, 7] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        (
            "@monthly /usr/bin/find",
            "minute=[0] "
            "hour=[0] "
            "monthday=[1] "
            "month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] "
            "weekday=[1, 2, 3, 4, 5, 6, 7] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        (
            "@weekly /usr/bin/find",
            "minute=[0] "
            "hour=[0] "
            "monthday=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, "
            "24, 25, 26, 27, 28, 29, 30, 31] "
            "month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] "
            "weekday=[7] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        (
            "@daily /usr/bin/find",
            "minute=[0] "
            "hour=[0] "
            "monthday=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, "
            "24, 25, 26, 27, 28, 29, 30, 31] "
            "month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] "
            "weekday=[1, 2, 3, 4, 5, 6, 7] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        (
            "@midnight /usr/bin/find",
            "minute=[0] "
            "hour=[0] "
            "monthday=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, "
            "24, 25, 26, 27, 28, 29, 30, 31] "
            "month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] "
            "weekday=[1, 2, 3, 4, 5, 6, 7] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        (
            "@hourly /usr/bin/find",
            "minute=[0] "
            "hour=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23] "
            "monthday=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, "
            "24, 25, 26, 27, 28, 29, 30, 31] "
            "month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] "
            "weekday=[1, 2, 3, 4, 5, 6, 7] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
        (
            "@every_minute /usr/bin/find",
            "minute=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, "
            "22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, "
            "43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59] "
            "hour=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23] "
            "monthday=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, "
            "24, 25, 26, 27, 28, 29, 30, 31] "
            "month=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] "
            "weekday=[1, 2, 3, 4, 5, 6, 7] "
            "tz=UTC "
            "command=/usr/bin/find",
        ),
    ],
)
def test_crontab_parse__valid(expr, expected):
    """
    Given any type of valid cron expression input expect the output to be as desired.
    """
    crontab = Crontab.from_parse(expr=expr, tz=dt.timezone.utc)
    assert expected == str(crontab)


@pytest.mark.parametrize(
    "expr, exc, expected",
    [
        (
            "c * * * * /usr/bin/find",
            ValueError,
            "Minute value must be of type int",
        ),
        (
            "* 1-! * * * /usr/bin/find",
            ValueError,
            "Hour value must be of type int",
        ),
        (
            "* * 1-12/. * * /usr/bin/find",
            ValueError,
            "Monthday value must be of type int",
        ),
        (
            "*/* * * * * /usr/bin/find",
            ValueError,
            "Minute value must be of type int",
        ),
        (
            "*// * * * * /usr/bin/find",
            ValueError,
            r"Minute value must not contain more than one step parameter \(/\)",
        ),
        (
            "1-- * * * * /usr/bin/find",
            ValueError,
            r"Minute value must not contain more than one range parameter \(-\)",
        ),
        (
            "1,, * * * * /usr/bin/find",
            ValueError,
            "Minute value must be of type int",
        ),
        (
            "* 2-1 * * * /usr/bin/find",
            ValueError,
            "Hour range start value must not be > than end value",
        ),
        (
            "60 * * * * /usr/bin/find",
            ValueError,
            r"Minute value must be in range of \[0, 59\]",
        ),
        (
            "* 24 * * * /usr/bin/find",
            ValueError,
            r"Hour value must be in range of \[0, 23\]",
        ),
        (
            "* * 32 * * /usr/bin/find",
            ValueError,
            r"Monthday value must be in range of \[1, 31\]",
        ),
        (
            "* * * 13 * /usr/bin/find",
            ValueError,
            r"Month value must be in range of \[1, 12\]",
        ),
        (
            "* * * * 8 /usr/bin/find",
            ValueError,
            r"Weekday value must be in range of \[1, 7\]",
        ),
        (
            "* * 0 * * /usr/bin/find",
            ValueError,
            r"Monthday value must be in range of \[1, 31\]",
        ),
        (
            "* * * 0 * /usr/bin/find",
            ValueError,
            r"Month value must be in range of \[1, 12\]",
        ),
        (
            "* * * *",
            ValueError,
            r"Crontab expression must be of 6 fields, Received: 4",
        ),
    ],
)
def test_crontab_parse__invalid(expr, exc, expected):
    """
    Given any type of invalid cron expression input expect parser to raise a ValueError.
    """
    with pytest.raises(exc, match=expected):
        Crontab.from_parse(expr=expr, tz=dt.timezone.utc)
