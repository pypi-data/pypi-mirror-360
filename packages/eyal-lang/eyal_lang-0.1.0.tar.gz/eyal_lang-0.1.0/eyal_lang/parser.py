"""
Simple rule-based EyalLang parser with great error reporting and easy extensibility.
"""

import re
from typing import Any


class EyalLangParser:
    """Simple parser for EyalLang with clear error reporting."""

    def __init__(self) -> None:
        """Initialize with core EyalLang commands."""
        # Core command patterns - easy to extend
        self.commands: dict[str, dict[str, str]] = {
            # Output
            "say": {
                "pattern": r"^say\s+(.+)$",
                "description": "say <message> - prints a message",
                "example": "say hello world",
            },
            # Variables
            "set": {
                "pattern": r"^set\s+(\w+)\s+to\s+(.+)$",
                "description": "set <variable> to <value> - creates a variable",
                "example": 'set name to "Eyal"',
            },
            # Comments
            "comment": {
                "pattern": r"^#(.+)$",
                "description": "# <comment> - adds a comment",
                "example": "# This is a comment",
            },
        }

        # Compile patterns for performance
        self.compiled_patterns: dict[str, re.Pattern[str]] = {}
        for cmd_name, cmd_info in self.commands.items():
            self.compiled_patterns[cmd_name] = re.compile(cmd_info["pattern"], re.IGNORECASE)

    def parse_line(
        self, line: str, line_number: int = 0
    ) -> tuple[dict[str, Any] | None, str | None]:
        """
        Parse a single EyalLang line with detailed error reporting.

        Args:
            line: The EyalLang directive to parse
            line_number: Line number for error reporting

        Returns:
            Tuple of (parsed_command, error_message)
        """
        original_line = line
        line = line.strip()

        # Skip empty lines
        if not line:
            return None, None

        # Check for comments first
        if line.startswith("#"):
            return {
                "type": "comment",
                "content": line[1:].strip(),
                "original": original_line,
                "line_number": line_number,
            }, None

        # Try to match each command
        for cmd_name, _cmd_info in self.commands.items():
            if cmd_name == "comment":
                continue  # Already handled

            match = self.compiled_patterns[cmd_name].match(line)
            if match:
                return {
                    "type": cmd_name,
                    "params": match.groups(),
                    "original": original_line,
                    "line_number": line_number,
                }, None

        # No match found - generate helpful error
        error_msg = self._generate_error_message(line, line_number)
        return None, error_msg

    def _generate_error_message(self, line: str, line_number: int) -> str:
        """Generate a helpful error message with suggestions."""
        suggestions = []

        # Check for common mistakes
        if line.lower().startswith("say") and len(line.split()) < 2:
            suggestions.append("'say' needs a message. Try: 'say hello world'")
        elif line.lower().startswith("set") and "to" not in line.lower():
            suggestions.append("'set' needs 'to'. Try: 'set name to \"value\"'")

        # Add available commands
        available_commands = []
        for cmd_name, cmd_info in self.commands.items():
            if cmd_name != "comment":
                available_commands.append(f"  {cmd_info['example']} - {cmd_info['description']}")

        error_parts = [f"❌ Error on line {line_number + 1}: Unknown command '{line}'"]

        if suggestions:
            error_parts.append("💡 Suggestions:")
            error_parts.extend([f"  {s}" for s in suggestions])

        error_parts.append("📚 Available commands:")
        error_parts.extend(available_commands)

        return "\n".join(error_parts)

    def translate_to_python(self, parsed_command: dict[str, Any]) -> str:
        """
        Translate a parsed EyalLang command to Python code.

        Args:
            parsed_command: The parsed command dictionary

        Returns:
            Python code as string
        """
        command_type = parsed_command["type"]
        params = parsed_command.get("params", [])

        if command_type == "comment":
            return f"# {parsed_command['content']}"

        if command_type == "say":
            message = params[0].strip()
            # Handle quotes properly
            if message.startswith('"') and message.endswith('"'):
                return f"print({message})"
            return f'print("{message}")'

        if command_type == "set":
            var_name = params[0]
            value = params[1].strip()
            return f"{var_name} = {value}"

        return f"# Unknown command type: {command_type}"


class EyalLangInterpreter:
    """Simple interpreter for EyalLang directives."""

    def __init__(self) -> None:
        """Initialize the interpreter."""
        self.parser = EyalLangParser()

    def interpret(self, eyal_directive: str) -> str:
        """
        Interpret a single EyalLang directive to Python code.

        Args:
            eyal_directive: The EyalLang directive to interpret

        Returns:
            Interpreted Python code as string
        """
        if not eyal_directive.strip():
            return ""

        parsed, error = self.parser.parse_line(eyal_directive)
        if error:
            return error
        if parsed:
            return self.parser.translate_to_python(parsed)
        return ""

    def interpret_batch(self, directives: list[str]) -> list[str]:
        """
        Interpret multiple EyalLang directives to Python code.

        Args:
            directives: List of EyalLang directives

        Returns:
            List of interpreted Python code strings
        """
        results = []
        for i, directive in enumerate(directives):
            parsed, error = self.parser.parse_line(directive, i)
            if error:
                results.append(error)
            elif parsed:
                results.append(self.parser.translate_to_python(parsed))
            else:
                results.append("")
        return results
