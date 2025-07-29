"""
Main interpreter for EyalLang directives.
"""

from functools import lru_cache

from .parser import EyalLangInterpreter


@lru_cache(maxsize=1)
def _get_interpreter() -> EyalLangInterpreter:
    """Get or create the global interpreter instance."""
    return EyalLangInterpreter()


def translate_line(eyal_directive: str) -> str:
    """
    Interpret a single EyalLang directive to Python code.

    Args:
        eyal_directive: The EyalLang directive to interpret

    Returns:
        Interpreted Python code as string

    Raises:
        ValueError: If the directive cannot be parsed

    Example:
        >>> translate_line("start the magic")
        'def main():'
    """
    interpreter = _get_interpreter()
    result = interpreter.interpret(eyal_directive)

    # Check if result is an error message
    if result.startswith("❌ Error"):
        raise ValueError(result)

    return result


def translate_file(file_path: str) -> list[str]:
    """
    Interpret an entire EyalLang file to Python code.

    Args:
        file_path: Path to the .eyal file

    Returns:
        List of interpreted Python code lines

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If any line fails to parse

    Example:
        >>> translate_file("hello.eyal")
        ['def main():', '    print("Hello, world!")', 'main()']
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]

        # Filter out empty lines and comments
        directives = [line for line in lines if line and not line.startswith("#")]

        interpreter = _get_interpreter()
        results = interpreter.interpret_batch(directives)

        # Check for any errors and stop on first failure
        for i, result in enumerate(results):
            if result.startswith("❌ Error"):
                raise ValueError(f"Line {i + 1}: {result}")

        return results

    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_path}' not found") from None
    except Exception as e:  # pylint: disable=broad-exception-caught
        if isinstance(e, (ValueError, FileNotFoundError)):
            raise
        raise ValueError(f"Error processing file: {e}") from e


def translate_lines(eyal_lines: list[str]) -> list[str]:
    """
    Interpret multiple EyalLang directives to Python code.

    Args:
        eyal_lines: List of EyalLang directives

    Returns:
        List of interpreted Python code lines

    Raises:
        ValueError: If any line fails to parse

    Example:
        >>> translate_lines(["start the magic", "say hello", "end the magic"])
        ['def main():', '    print("hello")', 'main()']
    """
    interpreter = _get_interpreter()
    results = interpreter.interpret_batch(eyal_lines)

    # Check for any errors and stop on first failure
    for i, result in enumerate(results):
        if result.startswith("❌ Error"):
            raise ValueError(f"Line {i + 1}: {result}")

    return results
