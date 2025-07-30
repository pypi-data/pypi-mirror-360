"""Tests for the CLI."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

from trackdo import main
from trackdo._internal import debug


def test_main() -> None:
    """Basic CLI test."""
    assert main([]) == 0


def test_show_help(capsys: pytest.CaptureFixture) -> None:
    """Show help.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    result = main(["--help"])
    captured = capsys.readouterr()
    assert result == 0
    assert "trackdo" in captured.out  # Typer outputs help to stdout


def test_show_version(capsys: pytest.CaptureFixture) -> None:
    """Show version.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    result = main(["-V"])
    captured = capsys.readouterr()
    assert result == 0
    assert debug._get_version() in captured.out


def test_show_debug_info(capsys: pytest.CaptureFixture) -> None:
    """Show debug information.

    Parameters:
        capsys: Pytest fixture to capture output.
    """
    result = main(["--debug-info"])
    captured = capsys.readouterr().out.lower()
    assert result == 0
    assert "python" in captured
    assert "system" in captured
    assert "environment" in captured
    assert "packages" in captured
