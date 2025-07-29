#!/usr/bin/env python3
"""
EyalLang CLI - Run EyalLang files and test the interpreter.
"""

import argparse
import sys

from . import translate_file, translate_line


def _run_single_line(line: str) -> None:
    """Run EyalLang in single line mode."""
    try:
        result = translate_line(line)
        print(f"Input: {line}")
        print(f"Output: {result}")
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def _run_file_mode(file_path: str, output_path: str | None = None) -> None:
    """Run EyalLang in file mode."""
    try:
        print(f"📖 Interpreting {file_path}...")
        python_code = translate_file(file_path)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(python_code))
            print(f"✅ Python code saved to {output_path}")
        else:
            print("🐍 Generated Python code:")
            for line in python_code:
                print(f"  {line}")

    except (ValueError, FileNotFoundError) as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def _run_interactive() -> None:
    """Run EyalLang in interactive mode."""
    print("🎯 EyalLang Interactive Mode")
    print("Type EyalLang directives (or 'quit' to exit):")

    while True:
        try:
            directive = input("eyal> ").strip()
            if directive.lower() in ["quit", "exit", "q"]:
                break
            if directive:
                try:
                    result = translate_line(directive)
                    print(f"🐍 {result}")
                except ValueError as e:
                    print(f"❌ Error: {e}")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


def main() -> None:
    """Main function to run the EyalLang CLI."""
    parser = argparse.ArgumentParser(description="EyalLang Interpreter")

    # Create mutual exclusive group for file and line
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--file", "-f", help="EyalLang file to interpret")
    group.add_argument("--line", "-l", help="Interpret a single line")

    # Output argument only makes sense with file mode
    parser.add_argument("--output", "-o", help="Output file for Python code (only with --file)")

    args = parser.parse_args()

    # Validate that output is only used with file
    if args.output and not args.file:
        print("❌ Error: --output can only be used with --file")
        sys.exit(1)

    # Single line interpretation
    if args.line:
        _run_single_line(args.line)
        return

    # File interpretation
    if args.file:
        _run_file_mode(args.file, args.output)
        return

    # Interactive mode (default when no arguments)
    _run_interactive()


if __name__ == "__main__":
    main()
