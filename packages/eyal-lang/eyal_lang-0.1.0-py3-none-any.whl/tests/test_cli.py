"""Tests for EyalLang CLI functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from eyal_lang.__main__ import _run_file_mode, _run_single_line, main


def test_run_single_line_success(capsys: pytest.CaptureFixture[str]) -> None:
    """Test successful single line execution."""
    _run_single_line("say hello world")
    captured = capsys.readouterr()
    assert "Input: say hello world" in captured.out
    assert 'Output: print("hello world")' in captured.out


def test_run_single_line_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Test single line execution with error."""
    with pytest.raises(SystemExit):
        _run_single_line("unknown command")
    captured = capsys.readouterr()
    assert "❌ Error" in captured.out


def test_run_file_mode_success(capsys: pytest.CaptureFixture[str]) -> None:
    """Test successful file mode execution."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".eyal", delete=False) as f:
        f.write("say hello world\n")
        f.write('set name to "Eyal"\n')
        file_path = f.name

    try:
        _run_file_mode(file_path)
        captured = capsys.readouterr()
        assert "📖 Interpreting" in captured.out
        assert "🐍 Generated Python code:" in captured.out
        assert 'print("hello world")' in captured.out
        assert 'name = "Eyal"' in captured.out
    finally:
        Path(file_path).unlink()


def test_run_file_mode_with_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Test file mode execution with output file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".eyal", delete=False) as f:
        f.write("say hello world\n")
        file_path = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as output_f:
        output_path = output_f.name

    try:
        _run_file_mode(file_path, output_path)
        captured = capsys.readouterr()
        assert "✅ Python code saved to" in captured.out

        # Check output file content
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert 'print("hello world")' in content
    finally:
        Path(file_path).unlink()
        Path(output_path).unlink()


def test_run_file_mode_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Test file mode execution with error."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".eyal", delete=False) as f:
        f.write("unknown command\n")
        file_path = f.name

    try:
        with pytest.raises(SystemExit):
            _run_file_mode(file_path)
        captured = capsys.readouterr()
        assert "❌ Error" in captured.out
    finally:
        Path(file_path).unlink()


def test_run_file_mode_nonexistent_file(capsys: pytest.CaptureFixture[str]) -> None:
    """Test file mode execution with nonexistent file."""
    with pytest.raises(SystemExit):
        _run_file_mode("nonexistent.eyal")
    captured = capsys.readouterr()
    assert "❌ Error" in captured.out


def test_main_single_line_mode(capsys: pytest.CaptureFixture[str]) -> None:
    """Test main function with single line mode."""
    with patch("sys.argv", ["eyal-lang", "--line", "say hello"]):
        main()
    captured = capsys.readouterr()
    assert "Input: say hello" in captured.out
    assert 'Output: print("hello")' in captured.out


def test_main_file_mode(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """Test main function with file mode."""
    # Create a test file
    test_file = tmp_path / "test.eyal"
    test_file.write_text("say hello world\n")

    with patch("sys.argv", ["eyal-lang", "--file", str(test_file)]):
        main()
    captured = capsys.readouterr()
    assert "📖 Interpreting" in captured.out
    assert "🐍 Generated Python code:" in captured.out
    assert 'print("hello world")' in captured.out


def test_main_file_mode_with_output(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """Test main function with file mode and output."""
    # Create a test file
    test_file = tmp_path / "test.eyal"
    test_file.write_text("say hello world\n")

    output_path = tmp_path / "output.py"
    with patch(
        "sys.argv",
        ["eyal-lang", "--file", str(test_file), "--output", str(output_path)],
    ):
        main()
    captured = capsys.readouterr()
    assert "✅ Python code saved to" in captured.out

    # Check output file content
    assert 'print("hello world")' in output_path.read_text()


def test_main_mutual_exclusion_error() -> None:
    """Test main function with mutually exclusive arguments."""
    with patch("sys.argv", ["eyal-lang", "--file", "test.eyal", "--line", "say hello"]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        # argparse returns 2 for argument errors
        assert excinfo.value.code == 2


def test_main_output_without_file_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Test main function with output but no file."""
    with patch("sys.argv", ["eyal-lang", "--output", "output.py"]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        assert "❌ Error: --output can only be used with --file" in captured.out
