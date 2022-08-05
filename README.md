# Croninfo

[![PyPi Version](https://img.shields.io/pypi/v/croninfo.svg?style=flat-square&logo=PyPi)](https://pypi.org/project/croninfo/)
[![PyPi License](https://img.shields.io/pypi/l/croninfo.svg?style=flat-square)](https://pypi.org/project/croninfo/)
[![CI
Tests](https://github.com/paulmonk/croninfo/workflows/CI%20Test/badge.svg)](https://github.com/paulmonk/croninfo/actions?query=workflow%3A%22CI+Test%22)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

**Croninfo** is a CLI which provides the functionality of parsing
cron expressions and rendering an output to ease with understanding the schedule
of the cron expression.

The Cron syntax supported is based on the [definition provided by FreeBSD](https://www.freebsd.org/cgi/man.cgi?crontab%285%29).

# Getting Started

**Python 3.7 to 3.10 supported**

To get started, install with pip:

```shell
$ python -m pip install croninfo
```

# Usage

## CLI

To CLI is provided with one command `parse` as can be seen below.
If any doubts you can run `croninfo --help` or `croninfo <command> --help`
for further details.

```shell
$ croninfo parse "10 0 1,15 * 1-3 /usr/bin/find"
╭─ Cron Expression ──────────────────────────────────────────────────────────────────────────────╮
│ Minute               10                                                                        │
│ Hour                 0                                                                         │
│ Day of Month         1 15                                                                      │
│ Month                1 2 3 4 5 6 7 8 9 10 11 12                                                │
│ Day of Week          1 2 3                                                                     │
│ TZ                   UTC                                                                       │
│ Command              /usr/bin/find                                                             │
│ Next Scheduled Run   2022-08-15T00:10:00+00:00 (in 10 days, 2 hours, 3 minutes and 25 seconds) │
╰─ 10 0 1,15 * 1-3 /usr/bin/find ────────────────────────────────────────────────────────────────╯
```

This will output with consideration to **UTC** by default but you can pass
`--tz-type local` to override to be your local timezone, E.G. `Europe/London`.
As shown below:

```shell
$ croninfo parse "10 0 1,15 * 1-3 /usr/bin/find" --tz-type local
╭─ Cron Expression ──────────────────────────────────────────────────────────────────────────────╮
│ Minute               10                                                                        │
│ Hour                 0                                                                         │
│ Day of Month         1 15                                                                      │
│ Month                1 2 3 4 5 6 7 8 9 10 11 12                                                │
│ Day of Week          1 2 3                                                                     │
│ TZ                   Europe/London                                                             │
│ Command              /usr/bin/find                                                             │
│ Next Scheduled Run   2022-08-15T00:10:00+01:00 (in 10 days, 1 hour, 2 minutes and 25 seconds)  │
╰─ 10 0 1,15 * 1-3 /usr/bin/find ────────────────────────────────────────────────────────────────╯
```

Alternatively, you can use the [**Official Croninfo Docker Image**](https://hub.docker.com/r/paulmonk/croninfo)
