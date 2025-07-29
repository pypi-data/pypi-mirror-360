"""Tests for EyalLang parser functionality."""

import pytest

from eyal_lang.parser import EyalLangInterpreter, EyalLangParser


@pytest.fixture(name="parser")
def parser_fixture() -> EyalLangParser:
    """Create a parser instance for tests."""
    return EyalLangParser()


@pytest.fixture(name="interpreter")
def interpreter_fixture() -> EyalLangInterpreter:
    """Create an interpreter instance for tests."""
    return EyalLangInterpreter()


def test_parse_say_command(parser: EyalLangParser) -> None:
    """Test parsing 'say' commands."""
    parsed, error = parser.parse_line("say hello world")
    assert error is None
    assert parsed is not None
    assert parsed["type"] == "say"
    assert parsed["params"] == ("hello world",)


def test_parse_say_command_with_quotes(parser: EyalLangParser) -> None:
    """Test parsing 'say' commands with quoted strings."""
    parsed, error = parser.parse_line('say "hello world"')
    assert error is None
    assert parsed is not None
    assert parsed["type"] == "say"
    assert parsed["params"] == ('"hello world"',)


def test_parse_set_command(parser: EyalLangParser) -> None:
    """Test parsing 'set' commands."""
    parsed, error = parser.parse_line('set name to "Eyal"')
    assert error is None
    assert parsed is not None
    assert parsed["type"] == "set"
    assert parsed["params"] == ("name", '"Eyal"')


def test_parse_set_command_with_number(parser: EyalLangParser) -> None:
    """Test parsing 'set' commands with numeric values."""
    parsed, error = parser.parse_line("set age to 25")
    assert error is None
    assert parsed is not None
    assert parsed["type"] == "set"
    assert parsed["params"] == ("age", "25")


def test_parse_comment(parser: EyalLangParser) -> None:
    """Test parsing comments."""
    parsed, error = parser.parse_line("# This is a comment")
    assert error is None
    assert parsed is not None
    assert parsed["type"] == "comment"
    assert parsed["content"] == "This is a comment"


def test_parse_empty_line(parser: EyalLangParser) -> None:
    """Test parsing empty lines."""
    parsed, error = parser.parse_line("")
    assert parsed is None
    assert error is None


def test_parse_whitespace_only(parser: EyalLangParser) -> None:
    """Test parsing whitespace-only lines."""
    parsed, error = parser.parse_line("   \t  \n  ")
    assert parsed is None
    assert error is None


def test_parse_unknown_command(parser: EyalLangParser) -> None:
    """Test parsing unknown commands."""
    parsed, error = parser.parse_line("unknown command")
    assert parsed is None
    assert error is not None
    assert "Unknown command" in error
    assert "Available commands" in error


def test_parse_say_without_message(parser: EyalLangParser) -> None:
    """Test parsing 'say' without a message."""
    parsed, error = parser.parse_line("say")
    assert parsed is None
    assert error is not None
    assert "suggestions" in error.lower()


def test_parse_set_without_to(parser: EyalLangParser) -> None:
    """Test parsing 'set' without 'to'."""
    parsed, error = parser.parse_line('set name "Eyal"')
    assert parsed is None
    assert error is not None
    assert "suggestions" in error.lower()


def test_line_number_in_error(parser: EyalLangParser) -> None:
    """Test that line numbers are included in error messages."""
    _parsed, error = parser.parse_line("unknown", line_number=5)
    assert error is not None
    assert "line 6" in error  # line_number + 1


def test_case_insensitive_parsing(parser: EyalLangParser) -> None:
    """Test that parsing is case insensitive."""
    parsed, error = parser.parse_line("SAY hello world")
    assert error is None
    assert parsed is not None
    assert parsed["type"] == "say"

    parsed, error = parser.parse_line("SET name TO value")
    assert error is None
    assert parsed is not None
    assert parsed["type"] == "set"


def test_translate_say_command(parser: EyalLangParser) -> None:
    """Test translating 'say' commands to Python."""
    parsed, _ = parser.parse_line("say hello world")
    assert parsed is not None
    result = parser.translate_to_python(parsed)
    assert result == 'print("hello world")'


def test_translate_say_command_with_quotes(parser: EyalLangParser) -> None:
    """Test translating 'say' commands with quoted strings."""
    parsed, _ = parser.parse_line('say "hello world"')
    assert parsed is not None
    result = parser.translate_to_python(parsed)
    assert result == 'print("hello world")'


def test_translate_set_command(parser: EyalLangParser) -> None:
    """Test translating 'set' commands to Python."""
    parsed, _ = parser.parse_line('set name to "Eyal"')
    assert parsed is not None
    result = parser.translate_to_python(parsed)
    assert result == 'name = "Eyal"'


def test_translate_set_command_with_number(parser: EyalLangParser) -> None:
    """Test translating 'set' commands with numeric values."""
    parsed, _ = parser.parse_line("set age to 25")
    assert parsed is not None
    result = parser.translate_to_python(parsed)
    assert result == "age = 25"


def test_translate_comment(parser: EyalLangParser) -> None:
    """Test translating comments to Python."""
    parsed, _ = parser.parse_line("# This is a comment")
    assert parsed is not None
    result = parser.translate_to_python(parsed)
    assert result == "# This is a comment"


def test_interpret_say_command(interpreter: EyalLangInterpreter) -> None:
    """Test interpreting 'say' commands."""
    result = interpreter.interpret("say hello world")
    assert result == 'print("hello world")'


def test_interpret_set_command(interpreter: EyalLangInterpreter) -> None:
    """Test interpreting 'set' commands."""
    result = interpreter.interpret('set name to "Eyal"')
    assert result == 'name = "Eyal"'


def test_interpret_comment(interpreter: EyalLangInterpreter) -> None:
    """Test interpreting comments."""
    result = interpreter.interpret("# This is a comment")
    assert result == "# This is a comment"


def test_interpret_empty_line(interpreter: EyalLangInterpreter) -> None:
    """Test interpreting empty lines."""
    result = interpreter.interpret("")
    assert result == ""


def test_interpret_whitespace_only(interpreter: EyalLangInterpreter) -> None:
    """Test interpreting whitespace-only lines."""
    result = interpreter.interpret("   \t  \n  ")
    assert result == ""


def test_interpret_unknown_command(interpreter: EyalLangInterpreter) -> None:
    """Test interpreting unknown commands."""
    result = interpreter.interpret("unknown command")
    assert result.startswith("❌ Error")


def test_interpret_batch_valid_commands(interpreter: EyalLangInterpreter) -> None:
    """Test interpreting multiple valid commands."""
    directives = ["say hello", 'set name to "Eyal"', "# comment"]
    results = interpreter.interpret_batch(directives)
    expected = ['print("hello")', 'name = "Eyal"', "# comment"]
    assert results == expected


def test_interpret_batch_with_error(interpreter: EyalLangInterpreter) -> None:
    """Test interpreting batch with an error."""
    directives = ["say hello", "unknown command", 'set name to "Eyal"']
    results = interpreter.interpret_batch(directives)
    assert results[0] == 'print("hello")'
    assert results[1].startswith("❌ Error")
    assert results[2] == 'name = "Eyal"'


def test_interpret_batch_empty_lines(interpreter: EyalLangInterpreter) -> None:
    """Test interpreting batch with empty lines."""
    directives = ["say hello", "", "   ", "# comment", 'set name to "Eyal"']
    results = interpreter.interpret_batch(directives)
    expected = ['print("hello")', "", "", "# comment", 'name = "Eyal"']
    assert results == expected
