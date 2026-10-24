from __future__ import annotations

import pytest

from kellu import __version__
from kellu.cli import EXIT_NOT_IMPLEMENTED, EXIT_OK, main


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_no_command_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == EXIT_OK
    assert "usage:" in capsys.readouterr().out


@pytest.mark.parametrize("command", ["keys", "tools", "lsp"])
def test_planned_commands_report_not_implemented(
    command: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([command]) == EXIT_NOT_IMPLEMENTED
    assert "not implemented yet" in capsys.readouterr().err


def test_unknown_command_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["nope"])
    assert exc.value.code == 2
