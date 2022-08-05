from __future__ import annotations

import datetime as dt
from enum import Enum

import typer
import tzlocal
from rich.console import Console
from rich.panel import Panel

from croninfo import __version__
from croninfo.crontab import Crontab

cli = typer.Typer()


class ParseTZOpts(str, Enum):
    LOCAL = "local"
    UTC = "utc"


@cli.command()
def parse(
    expression: str,
    tz_type: ParseTZOpts = typer.Option(  # noqa: B008
        ParseTZOpts.UTC.value, "--tz-type", case_sensitive=False
    ),
) -> None:
    """
    Accept the input of a Crontab expression, which is then parsed into a data structure.
    All datetime info is parsed in the timezone provided, defaults to UTC.
    """
    tz = (
        dt.timezone.utc
        if tz_type.value == ParseTZOpts.UTC.value
        else tzlocal.get_localzone()
    )
    crontab = Crontab.from_parse(expr=expression, tz=tz)

    # Determine next scheduled run of crontab.
    next_run = crontab.next_scheduled_run
    next_run_delta = next_run - dt.datetime.now(tz=crontab.tz)

    # Map of desired header name->value
    output_map = {
        "Minute": crontab.minute.values,
        "Hour": crontab.hour.values,
        "Day of Month": crontab.monthday.values,
        "Month": crontab.month.values,
        "Day of Week": crontab.weekday.values,
        "TZ": crontab.tz,
        "Command": crontab.command,
        "Next Scheduled Run": f"{next_run.isoformat()} (in {_format_friendly_timedelta(next_run_delta)})",
    }
    final_output = []
    for k, v in output_map.items():
        # 'Command' value is a string and we do not want the join iteration to apply to
        # strings which should still be outputted as the original value.
        result = v
        if isinstance(v, list):
            result = " ".join(str(x) for x in v if v)
        final_output.append(f"[bold]{k:<20}[/bold] {result}")

    panel = Panel(
        "\n".join(final_output),
        title="Cron Expression",
        title_align="left",
        subtitle=expression,
        subtitle_align="left",
        expand=False,
    )
    console = Console()
    console.print(panel, justify="left")


def _format_friendly_timedelta(delta: dt.timedelta) -> str:
    days = delta.days

    # In cases where delta days can be -1 short-circuit.
    # E.G. cron is scheduled to run every minute.
    if days < 0:
        return "less than 60 seconds"

    hours, _rem = divmod(delta.seconds, 3600)
    mins, secs = divmod(_rem, 60)

    # Avoid returns extra noise when specific fragments are not required.
    descriptor = "seconds" if secs > 1 else "second"
    pattern = f"{secs:.0f} {descriptor}"
    if mins > 0:
        descriptor = "minutes" if mins > 1 else "minute"
        pattern = f"{mins:.0f} {descriptor} and {pattern}"
    if hours > 0:
        descriptor = "hours" if hours > 1 else "hour"
        pattern = f"{hours:.0f} {descriptor}, {pattern}"
    if days > 0:
        descriptor = "days" if days > 1 else "day"
        pattern = f"{days} {descriptor}, {pattern}"
    return pattern


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"Version: {__version__}")
        raise typer.Exit()


@cli.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(  # noqa: B008
        None, "--version", callback=_version_callback, is_eager=True
    ),
) -> None:
    """
    A CLI tool which accepts a Crontab expression to be parsed with output.
    See "parse" command for more information.
    """
