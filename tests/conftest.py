from __future__ import annotations

from functools import partial
from textwrap import dedent

import pytest
from typer.testing import CliRunner


def assert_cli_output(result, output):
    assert result.output.strip() == dedent(output).strip()


@pytest.fixture(scope="session")
def typer_runner():
    runner = CliRunner()

    def inner(cmd, *args, **kwargs):
        result = runner.invoke(cmd, *args, **kwargs)
        result.assert_cli_output = partial(assert_cli_output, result)
        return result

    return inner
