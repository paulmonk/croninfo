from __future__ import annotations

import datetime as dt
import sys

import pytest
import time_machine

from croninfo.cli import __version__, cli

# Backports is required for Python versions <3.9
if sys.version_info >= (3, 9):
    import zoneinfo
else:
    from backports import zoneinfo


@pytest.mark.parametrize(
    "expr, expected",
    [
        pytest.param(
            ["@every_minute /usr/bin/find"],
            """
            ╭─ Cron Expression ────────────────────────────────────────────────────────────╮
            │ Minute               0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 │
            │ 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46   │
            │ 47 48 49 50 51 52 53 54 55 56 57 58 59                                       │
            │ Hour                 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 │
            │ 22 23                                                                        │
            │ Day of Month         1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21   │
            │ 22 23 24 25 26 27 28 29 30 31                                                │
            │ Month                1 2 3 4 5 6 7 8 9 10 11 12                              │
            │ Day of Week          1 2 3 4 5 6 7                                           │
            │ TZ                   UTC                                                     │
            │ Command              /usr/bin/find                                           │
            │ Next Scheduled Run   2022-01-01T01:01:00+00:00 (in less than 60 seconds)     │
            ╰─ @every_minute /usr/bin/find ────────────────────────────────────────────────╯
            """,
            id="Less than 60 Seconds",
        ),
        pytest.param(
            ["@weekly /usr/bin/find"],
            """
            ╭─ Cron Expression ────────────────────────────────────────────────────────────╮
            │ Minute               0                                                       │
            │ Hour                 0                                                       │
            │ Day of Month         1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21   │
            │ 22 23 24 25 26 27 28 29 30 31                                                │
            │ Month                1 2 3 4 5 6 7 8 9 10 11 12                              │
            │ Day of Week          7                                                       │
            │ TZ                   UTC                                                     │
            │ Command              /usr/bin/find                                           │
            │ Next Scheduled Run   2022-01-02T00:00:00+00:00 (in 22 hours, 58 minutes and  │
            │ 58 seconds)                                                                  │
            ╰─ @weekly /usr/bin/find ──────────────────────────────────────────────────────╯
            """,
            id="Hours, Minutes, Seconds",
        ),
        pytest.param(
            ["*/2 * * * * /usr/bin/find"],
            """
            ╭─ Cron Expression ────────────────────────────────────────────────────────────╮
            │ Minute               0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 36 38  │
            │ 40 42 44 46 48 50 52 54 56 58                                                │
            │ Hour                 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 │
            │ 22 23                                                                        │
            │ Day of Month         1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21   │
            │ 22 23 24 25 26 27 28 29 30 31                                                │
            │ Month                1 2 3 4 5 6 7 8 9 10 11 12                              │
            │ Day of Week          1 2 3 4 5 6 7                                           │
            │ TZ                   UTC                                                     │
            │ Command              /usr/bin/find                                           │
            │ Next Scheduled Run   2022-01-01T01:02:00+00:00 (in 58 seconds)               │
            ╰─ */2 * * * * /usr/bin/find ──────────────────────────────────────────────────╯
            """,
            id="Seconds only",
        ),
        pytest.param(
            ["18-25 6-8,10-12 * JAN-DEC/2 SUN,TUE-fri /usr/bin/find"],
            """
            ╭─ Cron Expression ────────────────────────────────────────────────────────────╮
            │ Minute               18 19 20 21 22 23 24 25                                 │
            │ Hour                 6 7 8 10 11 12                                          │
            │ Day of Month         1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21   │
            │ 22 23 24 25 26 27 28 29 30 31                                                │
            │ Month                1 3 5 7 9 11                                            │
            │ Day of Week          2 3 4 5 7                                               │
            │ TZ                   UTC                                                     │
            │ Command              /usr/bin/find                                           │
            │ Next Scheduled Run   2022-01-02T06:18:00+00:00 (in 1 day, 5 hours, 16        │
            │ minutes and 58 seconds)                                                      │
            ╰─ 18-25 6-8,10-12 * JAN-DEC/2 SUN,TUE-fri /usr/bin/find ──────────────────────╯
            """,
            id="Day",
        ),
        pytest.param(
            ["18-25 1-2 1 JAN-DEC/2 SUN,TUE-fri /usr/bin/find"],
            """
            ╭─ Cron Expression ────────────────────────────────────────────────────────────╮
            │ Minute               18 19 20 21 22 23 24 25                                 │
            │ Hour                 1 2                                                     │
            │ Day of Month         1                                                       │
            │ Month                1 3 5 7 9 11                                            │
            │ Day of Week          2 3 4 5 7                                               │
            │ TZ                   UTC                                                     │
            │ Command              /usr/bin/find                                           │
            │ Next Scheduled Run   2022-03-01T01:18:00+00:00 (in 59 days, 16 minutes and   │
            │ 58 seconds)                                                                  │
            ╰─ 18-25 1-2 1 JAN-DEC/2 SUN,TUE-fri /usr/bin/find ────────────────────────────╯
            """,
            id="Days and No Hour",
        ),
    ],
)
@time_machine.travel(
    dt.datetime(
        year=2022, month=1, day=1, hour=1, minute=1, second=1, tzinfo=dt.timezone.utc
    )
)
def test_parse_command__output(expr, expected, typer_runner):
    """
    Given any type of valid cron expression and tz args input expect the output
    to be correct and formatted as desired.
    """
    cmds = ["parse"]
    cmds.extend(expr)
    result = typer_runner(cli, cmds)

    assert 0 == result.exit_code
    result.assert_cli_output(expected)


@pytest.mark.parametrize(
    "expr, expected, tzinfo",
    [
        pytest.param(
            ["*/15 0 1,15 * 1-5 /usr/bin/find"],
            """
            ╭─ Cron Expression ────────────────────────────────────────────────────────────╮
            │ Minute               0 15 30 45                                              │
            │ Hour                 0                                                       │
            │ Day of Month         1 15                                                    │
            │ Month                1 2 3 4 5 6 7 8 9 10 11 12                              │
            │ Day of Week          1 2 3 4 5                                               │
            │ TZ                   UTC                                                     │
            │ Command              /usr/bin/find                                           │
            │ Next Scheduled Run   2022-02-01T00:00:00+00:00 (in 30 days, 22 hours, 58     │
            │ minutes and 58 seconds)                                                      │
            ╰─ */15 0 1,15 * 1-5 /usr/bin/find ────────────────────────────────────────────╯
            """,
            zoneinfo.ZoneInfo("Europe/London"),
            id="Test UTC Opt Default",
        ),
        pytest.param(
            ["*/15 0 1,15 * 1-5 /usr/bin/find", "--tz-type", "utc"],
            """
            ╭─ Cron Expression ────────────────────────────────────────────────────────────╮
            │ Minute               0 15 30 45                                              │
            │ Hour                 0                                                       │
            │ Day of Month         1 15                                                    │
            │ Month                1 2 3 4 5 6 7 8 9 10 11 12                              │
            │ Day of Week          1 2 3 4 5                                               │
            │ TZ                   UTC                                                     │
            │ Command              /usr/bin/find                                           │
            │ Next Scheduled Run   2022-02-01T00:00:00+00:00 (in 30 days, 22 hours, 58     │
            │ minutes and 58 seconds)                                                      │
            ╰─ */15 0 1,15 * 1-5 /usr/bin/find ────────────────────────────────────────────╯
            """,
            zoneinfo.ZoneInfo("Europe/London"),
            id="Test UTC Opt",
        ),
        pytest.param(
            ["*/15 0 1,15 * 1-5 /usr/bin/find", "--tz-type", "local"],
            """
            ╭─ Cron Expression ────────────────────────────────────────────────────────────╮
            │ Minute               0 15 30 45                                              │
            │ Hour                 0                                                       │
            │ Day of Month         1 15                                                    │
            │ Month                1 2 3 4 5 6 7 8 9 10 11 12                              │
            │ Day of Week          1 2 3 4 5                                               │
            │ TZ                   Europe/London                                           │
            │ Command              /usr/bin/find                                           │
            │ Next Scheduled Run   2022-02-01T00:00:00+00:00 (in 30 days, 22 hours, 58     │
            │ minutes and 58 seconds)                                                      │
            ╰─ */15 0 1,15 * 1-5 /usr/bin/find ────────────────────────────────────────────╯
            """,
            zoneinfo.ZoneInfo("Europe/London"),
            id="Test Local Opt - London",
        ),
        pytest.param(
            ["*/15 0 1,15 * 1-5 /usr/bin/find", "--tz-type", "local"],
            """
            ╭─ Cron Expression ────────────────────────────────────────────────────────────╮
            │ Minute               0 15 30 45                                              │
            │ Hour                 0                                                       │
            │ Day of Month         1 15                                                    │
            │ Month                1 2 3 4 5 6 7 8 9 10 11 12                              │
            │ Day of Week          1 2 3 4 5                                               │
            │ TZ                   Europe/Berlin                                           │
            │ Command              /usr/bin/find                                           │
            │ Next Scheduled Run   2022-02-01T00:00:00+01:00 (in 30 days, 21 hours, 58     │
            │ minutes and 58 seconds)                                                      │
            ╰─ */15 0 1,15 * 1-5 /usr/bin/find ────────────────────────────────────────────╯
            """,
            zoneinfo.ZoneInfo("Europe/Berlin"),
            id="Test Local Opt - Berlin",
        ),
    ],
)
@time_machine.travel(
    dt.datetime(
        year=2022,
        month=1,
        day=1,
        hour=1,
        minute=1,
        second=1,
        tzinfo=dt.timezone.utc,
    )
)
def test_parse_command__opts_output(expr, expected, tzinfo, typer_runner, mocker):
    """
    Given any type of valid cron expression and tz args input expect the output
    to be correct and formatted as desired.
    """
    cmds = ["parse"]
    cmds.extend(expr)

    # Ensure tzlocal always picks up the expected tzinfo being passed.
    mocker.patch("croninfo.cli.tzlocal.get_localzone", return_value=tzinfo)

    result = typer_runner(cli, cmds)

    assert 0 == result.exit_code
    result.assert_cli_output(expected)


@pytest.mark.parametrize(
    "expr",
    [
        (["blah"]),
        (["*/15 0 1,15 * /usr/bin/find"]),
    ],
)
def test_parse_command__invalid_expressions(expr, typer_runner):
    """
    Given any type of invalid cron expression input expect an error to be
    returned.
    """
    cmds = ["parse"]
    cmds.extend(expr)
    result = typer_runner(cli, cmds)

    assert 1 == result.exit_code


@pytest.mark.parametrize(
    "expr, expected",
    [
        (
            ["*/15 0 1,15 * 1-5 /usr/bin/find", "--tz-type", "London"],
            "Invalid value for '--tz-type': 'London' is not one of 'local', 'utc'",
        ),
        (
            ["*/15 0 1,15 * 1-12 /usr/bin/test", "--tz-type", "Berlin"],
            "Invalid value for '--tz-type': 'Berlin' is not one of 'local', 'utc'",
        ),
    ],
)
def test_parse_command__invalid_opts(expr, expected, typer_runner):
    """
    Given any type of invalid cron expression input expect an error to be
    returned.
    """
    cmds = ["parse"]
    cmds.extend(expr)
    result = typer_runner(cli, cmds)

    assert 2 == result.exit_code
    assert expected in str(result.stdout)


def test_version_arg(typer_runner):
    """
    The --version output returns the expected version.
    """
    result = typer_runner(cli, "--version")

    assert 0 == result.exit_code
    result.assert_cli_output(f"Version: {__version__}")


def test_version_arg__is_eager(typer_runner):
    """
    The --version arg should be eager and supersede any commands if supplied.
    """
    result = typer_runner(cli, ["--version", "parse", "blah"])

    assert 0 == result.exit_code
    result.assert_cli_output(f"Version: {__version__}")
