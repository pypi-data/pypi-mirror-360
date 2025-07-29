"""Tests for EyalLang interpreter functionality."""

import tempfile
from pathlib import Path

import pytest

from eyal_lang.interpreter import translate_file, translate_line, translate_lines


def test_translate_say_command() -> None:
    """Test translating 'say' commands."""
    result = translate_line("say hello world")
    assert result == 'print("hello world")'


def test_translate_say_command_with_quotes() -> None:
    """Test translating 'say' commands with quoted strings."""
    result = translate_line('say "hello world"')
    assert result == 'print("hello world")'


def test_translate_set_command() -> None:
    """Test translating 'set' commands."""
    result = translate_line('set name to "Eyal"')
    assert result == 'name = "Eyal"'


def test_translate_set_command_with_number() -> None:
    """Test translating 'set' commands with numeric values."""
    result = translate_line("set age to 25")
    assert result == "age = 25"


def test_translate_comment() -> None:
    """Test translating comments."""
    result = translate_line("# This is a comment")
    assert result == "# This is a comment"


def test_translate_empty_line() -> None:
    """Test translating empty lines."""
    result = translate_line("")
    assert result == ""


def test_translate_whitespace_only() -> None:
    """Test translating whitespace-only lines."""
    result = translate_line("   \t  \n  ")
    assert result == ""


def test_translate_unknown_command_raises_error() -> None:
    """Test that unknown commands raise ValueError."""
    with pytest.raises(ValueError, match="❌ Error"):
        translate_line("unknown command")


def test_translate_say_without_message_raises_error() -> None:
    """Test that 'say' without message raises error."""
    with pytest.raises(ValueError, match="❌ Error"):
        translate_line("say")


def test_translate_set_without_to_raises_error() -> None:
    """Test that 'set' without 'to' raises error."""
    with pytest.raises(ValueError, match="❌ Error"):
        translate_line('set name "Eyal"')


def test_translate_valid_commands() -> None:
    """Test translating multiple valid commands."""
    lines = ["say hello", 'set name to "Eyal"', "# comment"]
    results = translate_lines(lines)
    expected = ['print("hello")', 'name = "Eyal"', "# comment"]
    assert results == expected


def test_translate_with_empty_lines() -> None:
    """Test translating lines with empty lines."""
    lines = ["say hello", "", "   ", "# comment", 'set name to "Eyal"']
    results = translate_lines(lines)
    expected = ['print("hello")', "", "", "# comment", 'name = "Eyal"']
    assert results == expected


def test_translate_with_error_raises_exception() -> None:
    """Test that errors in batch raise ValueError."""
    lines = ["say hello", "unknown command", 'set name to "Eyal"']
    with pytest.raises(ValueError, match="Line 2"):
        translate_lines(lines)


def test_translate_empty_list() -> None:
    """Test translating empty list."""
    results = translate_lines([])
    assert not results


def test_translate_valid_file() -> None:
    """Test translating a valid EyalLang file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".eyal", delete=False) as f:
        f.write("say hello world\n")
        f.write('set name to "Eyal"\n')
        f.write("# This is a comment\n")
        f.write("say goodbye\n")
        file_path = f.name

    try:
        results = translate_file(file_path)
        expected = [
            'print("hello world")',
            'name = "Eyal"',
            'print("goodbye")',
        ]
        assert results == expected
    finally:
        Path(file_path).unlink()


def test_translate_file_with_empty_lines() -> None:
    """Test translating file with empty lines."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".eyal", delete=False) as f:
        f.write("say hello\n")
        f.write("\n")
        f.write("   \n")
        f.write("# comment\n")
        f.write('set name to "Eyal"\n')
        file_path = f.name

    try:
        results = translate_file(file_path)
        expected = [
            'print("hello")',
            'name = "Eyal"',
        ]
        assert results == expected
    finally:
        Path(file_path).unlink()


def test_translate_file_with_error_raises_exception() -> None:
    """Test that file with errors raises ValueError."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".eyal", delete=False) as f:
        f.write("say hello\n")
        f.write("unknown command\n")
        f.write('set name to "Eyal"\n')
        file_path = f.name

    try:
        with pytest.raises(ValueError, match="Line 2"):
            translate_file(file_path)
    finally:
        Path(file_path).unlink()


def test_translate_nonexistent_file_raises_exception() -> None:
    """Test that nonexistent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="File.*not found"):
        translate_file("nonexistent.eyal")


def test_translate_empty_file() -> None:
    """Test translating an empty file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".eyal", delete=False) as f:
        file_path = f.name

    try:
        results = translate_file(file_path)
        assert not results
    finally:
        Path(file_path).unlink()


def test_translate_file_with_only_comments() -> None:
    """Test translating file with only comments."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".eyal", delete=False) as f:
        f.write("# Comment 1\n")
        f.write("# Comment 2\n")
        f.write("# Comment 3\n")
        file_path = f.name

    try:
        results = translate_file(file_path)
        assert not results
    finally:
        Path(file_path).unlink()


def test_translate_file_with_only_empty_lines() -> None:
    """Test translating file with only empty lines."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".eyal", delete=False) as f:
        f.write("\n")
        f.write("   \n")
        f.write("\t\n")
        file_path = f.name

    try:
        results = translate_file(file_path)
        assert not results
    finally:
        Path(file_path).unlink()
