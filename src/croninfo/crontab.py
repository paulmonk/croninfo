from __future__ import annotations

import calendar
import dataclasses
import datetime as dt
from typing import ClassVar, Iterator

# Definitions based on spec here:
# https://www.freebsd.org/cgi/man.cgi?crontab%285%29
# @reboot and @every_second have been omitted.
CRON_MACROS = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
    "@every_minute": "*/1 * * * *",
}


@dataclasses.dataclass(frozen=True)
class CronPart:
    """
    Definition of a Crontab part.
    """

    # Friendly name for Part.
    name: ClassVar[str]

    # Each Cron part has a specific min/max range that is valid for it's part.
    min_value: ClassVar[int]
    max_value: ClassVar[int]

    # A cron part can have word aliases which convert to integers. E.G Months
    aliases: ClassVar[dict[str, int]]

    # Parsed value of the cron expression.
    values: list[int]

    @classmethod
    def __init_subclass__(
        cls,
        *,
        name: str,
        min_value: int,
        max_value: int,
        aliases: dict[str, int] | None = None,
    ):
        cls.name = name
        cls.min_value = min_value
        cls.max_value = max_value
        cls.aliases = aliases or {}

    def __iter__(self) -> Iterator[int]:
        return iter(self.values)

    def __str__(self) -> str:
        return str(self.values)

    @classmethod
    def from_expr(cls, expr: str):  # type: ignore
        """
        Parses crontab expression part based on rules provided (min-value, max-value, aliases etc...)

        *   any value
        ,   value list separator
        -   range of values
        /   step values
        """
        values = cls._parse(expr=expr)
        return cls(values=values)

    @classmethod
    def _parse(cls, *, expr: str, step: int = 1) -> list[int]:
        # Expressions can be delimited by commas.
        if "," in expr:
            # "parse" needs to be recursed to capture all possible values.
            values = {
                x
                for sub_expr in expr.split(",", maxsplit=2)
                for x in cls._parse(expr=sub_expr, step=step)
            }
            return list(values)

        # Wildcard, need to return all possible values
        elif expr == "*":
            # +1 as range arg are 0-based and we need result to be 1-based.
            return list(range(cls.min_value, cls.max_value + 1, step))

        # Single numeric value
        elif expr.isnumeric():
            return [cls._try_parse_int(expr)]

        # Step values
        # The rhs of an expression containing a / is the "step" value,
        # i.e `*/8` means every 8 minutes
        elif "/" in expr:
            try:
                lhs, rhs = expr.split("/", maxsplit=2)
            except ValueError:
                raise ValueError(
                    f"{cls.name} value must not contain more than one step parameter (/)"
                )

            rhs_step = cls._try_parse_int(rhs)
            return cls._parse(expr=lhs, step=rhs_step)

        # Expressions here represent two values
        elif "-" in expr:
            try:
                range_start, range_end = expr.split("-", maxsplit=2)
            except ValueError:
                raise ValueError(
                    f"{cls.name} value must not contain more than one range parameter (-)"
                )

            # x-y. x must be less than y, valid this.
            start = cls._try_parse_int(range_start)
            end = cls._try_parse_int(range_end)
            if start > end:
                raise ValueError(
                    f"{cls.name} range start value must not be > than end value"
                )
            return list(
                # +1 as range arg are 0-based and we need result to be 1-based.
                range(
                    start,
                    end + 1,
                    step,
                )
            )
        # Parse any remaining values. Will catch aliases here.
        else:
            return [cls._try_parse_int(expr)]

    @classmethod
    def _try_parse_int(cls, value: str | int) -> int:
        x = value

        # Check if the value is an alias that needs to be mapped.
        if isinstance(value, str):
            try:
                # Case should not matter for matches.
                x = cls.aliases[value.upper()]
            except KeyError:
                pass

        # Check value is a valid integer.
        try:
            x = int(x)
        except ValueError:
            raise ValueError(f"{cls.name} value must be of type int")

        if not (cls.min_value <= x <= cls.max_value):
            raise ValueError(
                f"{cls.name} value must be in range of "
                f"[{cls.min_value}, {cls.max_value}]"
            )
        return x


@dataclasses.dataclass(frozen=True)
class CronPartMinute(CronPart, name="Minute", min_value=0, max_value=59):
    """
    Crontab expression minute part.
    """


@dataclasses.dataclass(frozen=True)
class CronPartHour(CronPart, name="Hour", min_value=0, max_value=23):
    """
    Crontab expression hour part.
    """


@dataclasses.dataclass(frozen=True)
class CronPartMonthday(CronPart, name="Monthday", min_value=1, max_value=31):
    """
    Crontab expression day part.
    """


@dataclasses.dataclass(frozen=True)
class CronPartMonth(
    CronPart,
    name="Month",
    min_value=1,
    max_value=12,
    aliases={
        "JAN": 1,
        "FEB": 2,
        "MAR": 3,
        "APR": 4,
        "MAY": 5,
        "JUN": 6,
        "JUL": 7,
        "AUG": 8,
        "SEP": 9,
        "OCT": 10,
        "NOV": 11,
        "DEC": 12,
    },
):
    """
    Crontab expression month part.
    """


@dataclasses.dataclass(frozen=True)
class CronPartWeekday(
    CronPart,
    name="Weekday",
    min_value=1,
    max_value=7,
    aliases={
        "MON": 1,
        "TUE": 2,
        "WED": 3,
        "THU": 4,
        "FRI": 5,
        "SAT": 6,
        "SUN": 7,
        # Spec is 0 or 7 support is Sunday.
        # This ensures that we only output one option if both provided.
        "0": 7,
    },
):
    """
    Crontab expression weekday part.
    """


@dataclasses.dataclass(frozen=True)
class Crontab:
    """
    Crontab Expression class to store the results of a parsed
    cron expression (incl command).

    Cron expression part values are expanded to be complete list. E.G.
    */15 = 0 15 30 45
    """

    minute: CronPartMinute
    hour: CronPartHour
    monthday: CronPartMonthday
    month: CronPartMonth
    weekday: CronPartWeekday
    tz: dt.tzinfo
    command: str

    def __str__(self) -> str:
        return " ".join(
            [
                f"minute={self.minute}",
                f"hour={self.hour}",
                f"monthday={self.monthday}",
                f"month={self.month}",
                f"weekday={self.weekday}",
                f"tz={self.tz}",
                f"command={self.command}",
            ]
        )

    @classmethod
    def from_parse(
        cls,
        *,
        expr: str,
        tz: dt.tzinfo,
        now: dt.datetime | None = None,
    ) -> Crontab:
        """
        Parses Crontab expression which also includes the command to run.
        """
        # Resolve macros (@weekly, @daily etc) to equivalent cron expressions.
        # Split the expression to see if it contains a macro in the first indices.
        # This would be the case if a macro and command was passsed in like "@annually /usr/bin/find"
        x = expr.split()
        try:
            macro_val = CRON_MACROS[x[0]]
            value = f"{macro_val} {x[1]}"
        except KeyError:
            value = expr

        # 5 for cron schedule + 1 for cron command = 6
        fields_len_constraint = 6
        fields = value.split()
        fields_len = len(fields)
        if fields_len != fields_len_constraint:
            raise ValueError(
                f"{cls.__qualname__} expression must be of {fields_len_constraint} fields, "
                f"Received: {fields_len}"
            )

        fields_iter = iter(fields)
        now = (now or dt.datetime.now(tz=tz)).astimezone(tz)

        return cls(
            minute=CronPartMinute.from_expr(next(fields_iter)),
            hour=CronPartHour.from_expr(next(fields_iter)),
            monthday=CronPartMonthday.from_expr(next(fields_iter)),
            month=CronPartMonth.from_expr(next(fields_iter)),
            weekday=CronPartWeekday.from_expr(next(fields_iter)),
            command=str(next(fields_iter)),
            tz=now.tzinfo or tz,
        )

    @property
    def next_scheduled_run(self) -> dt.datetime:
        return next(self.iter())

    def iter(self, start: dt.datetime | None = None) -> Iterator[dt.datetime]:
        """
        Yields future schedules for this crontab expression.
        """
        anchor = start.astimezone(self.tz) if start else dt.datetime.now(tz=self.tz)
        anchor_date = anchor.date()

        for day_date in self._generate_future_dates(anchor_date):
            is_start_day = day_date == anchor_date

            for valid_hour in self.hour:
                is_start_hour = is_start_day and valid_hour == anchor.hour

                # If today is the date the job should start but the hour has
                # passed we need to skip
                if is_start_day and valid_hour < anchor.hour:
                    continue

                for valid_minute in self.minute:
                    # If today is the date the job and the hour it should start
                    # but the minute has passed we need to skip.
                    if is_start_hour and valid_minute < anchor.minute:
                        continue

                    yield dt.datetime(
                        year=day_date.year,
                        month=day_date.month,
                        day=day_date.day,
                        hour=valid_hour,
                        minute=valid_minute,
                        tzinfo=self.tz,
                    )

    def _generate_future_dates(self, start: dt.date | None = None) -> Iterator[dt.date]:
        """
        Yields future dates for the crontab expression based on the
        month, monthday and weekdays parts.
        """
        cal = calendar.Calendar()
        anchor = start if start else dt.date.today()

        # Cap generation at year 2099, this will give us good buffer.
        while anchor.year < 2099:
            for valid_month in self.month:
                # Check if the month is lower the current month.
                # If so we need to skip because it will be in the past.
                if valid_month < anchor.month:
                    continue

                for day_no, weekday_no in cal.itermonthdays2(anchor.year, valid_month):
                    # itermonthdays yields all days required to get a full week,
                    # but those outside the current month are 0 so we should ignore
                    # those.
                    if day_no == 0:
                        continue

                    # It is the same month, but the day is in the past so we should skip.
                    if valid_month == anchor.month and day_no < anchor.day:
                        continue

                    # Check if this weekday is valid.
                    # In the calendar module, dates are 0-based. Monday == 0 and Sunday == 6.
                    # Our approach is 1-based so we need to add 1 to the value to lookup correctly
                    if weekday_no + 1 not in self.weekday:
                        continue

                    # Check if this monthday is valid.
                    if day_no not in self.monthday:
                        continue

                    # Success! Valid date.
                    yield dt.date(year=anchor.year, month=valid_month, day=day_no)

            # After exhausting each month for the current anchor year, we need
            # to start again from a new year.
            anchor = dt.date(year=anchor.year + 1, month=1, day=1)
