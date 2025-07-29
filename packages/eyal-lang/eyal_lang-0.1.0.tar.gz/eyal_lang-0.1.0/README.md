# EyalLang Core

[![CI](https://github.com/Eyal-Lang/eyal-lang/actions/workflows/ci.yml/badge.svg)](https://github.com/Eyal-Lang/eyal-lang/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/eyal-lang.svg)](https://badge.fury.io/py/eyal-lang)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

💡 A simple, rule-based DSL that interprets Eyal-style directives to Python code.

## Features

- **Simple Syntax**: Direct commands without boilerplate
- **Fast & Reliable**: No external dependencies or API calls
- **Predictable**: Deterministic interpretation to Python
- **Extensible**: Easy to add new commands and syntax
- **Lightweight**: Uses only Python standard library
- **Great Error Reporting**: Helpful error messages with suggestions
- **Fail Fast**: Stops execution on first error

## Quick Start

### 1. No Dependencies Required!
```bash
# Just clone and run - no pip install needed!
git clone <your-repo>
cd eyal-lang
```

### 2. Basic Usage

```python
from eyal_lang import translate_line, translate_file, translate_lines

# Interpret a single directive
result = translate_line("say hello world")
print(result)  # Output: print("hello world")

# Interpret multiple directives
lines = ["say hello world", "set name to 'Eyal'"]
python_code = translate_lines(lines)
print(python_code)  # Output: ['print("hello world")', "name = 'Eyal'"]

# Interpret an entire file
python_code = translate_file("examples/hello.eyal")
```

## CLI Usage

### Interpret a File
```bash
python -m eyal_lang --file examples/hello.eyal
```

### Interactive Mode
```bash
python -m eyal_lang
# Then type EyalLang directives interactively
```

### Single Line Interpretation
```bash
python -m eyal_lang --line "say hello world"
```

### Save Output to File
```bash
python -m eyal_lang --file examples/hello.eyal --output hello.py
```

## Development

### Setup Development Environment
```bash
# Install with development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Code Quality Tools
The project uses pre-commit hooks to ensure code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security analysis

### Running Quality Checks
```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run individual tools
black .
isort .
flake8 .
mypy .
bandit -r .
```

## EyalLang Syntax Reference

### Output Commands
```eyal
say hello world          # print("hello world")
```

### Variables
```eyal
set name to "Eyal"       # name = "Eyal"
set count to 42          # count = 42
set result to a + b      # result = a + b
```

### Comments
```eyal
# This is a comment
```

## Project Structure

```
eyal-lang/
├── eyal_lang/           # Core package
│   ├── __init__.py      # Package exports
│   ├── __main__.py      # CLI entry point
│   ├── interpreter.py   # High-level API
│   └── parser.py        # Rule-based parser
├── examples/
│   ├── hello.eyal      # Basic output example
│   ├── simple.eyal     # Variables example
│   ├── calculator.eyal # Math operations
│   └── greeting.eyal   # String handling
├── .pre-commit-config.yaml  # Pre-commit hooks
├── pyproject.toml      # Build configuration
├── LICENSE            # MIT license
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## API Reference

### `translate_line(eyal_directive: str) -> str`
Interpret a single EyalLang directive to Python code.

**Raises**: `ValueError` if the directive cannot be parsed

### `translate_lines(eyal_lines: List[str]) -> List[str]`
Interpret multiple EyalLang directives to Python code.

**Raises**: `ValueError` if any line fails to parse

### `translate_file(file_path: str) -> List[str]`
Interpret an entire EyalLang file to Python code.

**Raises**: `FileNotFoundError` if the file doesn't exist, `ValueError` if any line fails to parse

### `EyalLangInterpreter`
Rule-based interpreter class.

## Example Interpretations

### Basic Output (hello.eyal)
```eyal
# Hello World in EyalLang
say hello world
say welcome to EyalLang
```

Interprets to:
```python
print("hello world")
print("welcome to EyalLang")
```

### Variables (simple.eyal)
```eyal
# Simple Variables Example
set name to "Eyal"
set greeting to "Hello"
say greeting name
say nice to meet you
```

Interprets to:
```python
name = "Eyal"
greeting = "Hello"
print("greeting name")
print("nice to meet you")
```

### Calculator (calculator.eyal)
```eyal
# Calculator Example
set a to 10
set b to 5
set sum to a + b
set product to a * b
say the sum is sum
say the product is product
```

Interprets to:
```python
a = 10
b = 5
sum = a + b
product = a * b
print("the sum is sum")
print("the product is product")
```

### Greeting (greeting.eyal)
```eyal
# Greeting Example
set first_name to "Alice"
set last_name to "Smith"
set time_of_day to "morning"
say good time_of_day first_name
say welcome to our program
```

Interprets to:
```python
first_name = "Alice"
last_name = "Smith"
time_of_day = "morning"
print("good time_of_day first_name")
print("welcome to our program")
```

## Error Handling

The interpreter stops execution on the first error and provides detailed error messages:

```python
# This will raise ValueError and stop execution
try:
    result = translate_line("invalid command")
except ValueError as e:
    print(e)
    # Output: ❌ Error on line 1: Unknown command 'invalid command'
    # 💡 Suggestions:
    #   'say' needs a message. Try: 'say hello world'
    # 📚 Available commands:
    #   say hello world - say <message> - prints a message
    #   set name to "Eyal" - set <variable> to <value> - creates a variable
```

### CLI Error Handling
```bash
# File interpretation stops on first error
python -m eyal_lang --file invalid.eyal
# ❌ Error: Line 2: ❌ Error on line 2: Unknown command 'invalid command'

# Interactive mode shows errors but continues
python -m eyal_lang
eyal> invalid command
❌ Error: ❌ Error on line 1: Unknown command 'invalid command'
eyal> say hello
🐍 print("hello")
```

## Integration Examples

### Flask API
```python
from flask import Flask, request, jsonify
from eyal_lang import translate_lines

app = Flask(__name__)

@app.route("/api/interpret", methods=["POST"])
def interpret():
    try:
        data = request.get_json()
        lines = data.get("lines", [])
        interpretations = translate_lines(lines)
        return jsonify({"output": interpretations})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
```

### Custom Interpreter
```python
from eyal_lang import EyalLangInterpreter

interpreter = EyalLangInterpreter()
try:
    result = interpreter.interpret("say hello world")
    print(result)
except Exception as e:
    print(f"Error: {e}")
```

## Advantages of Rule-Based Approach

- ⚡ **Instant**: No model loading or API calls
- 🎯 **Predictable**: Same input always produces same output
- 🔧 **Debuggable**: Clear error messages for invalid syntax
- 💰 **Free**: No external dependencies or costs
- 🚀 **Fast**: Immediate interpretation
- 📚 **Learnable**: Clear syntax rules to follow
- 🛠️ **Extensible**: Easy to add new commands
- 🛑 **Fail Fast**: Stops on first error for better debugging
- 🎯 **Simple**: No boilerplate, direct commands

## Publishing to PyPI

The project uses GitHub Actions to automatically publish to PyPI. To set this up:

1. **Create PyPI API Token**:
   - Go to [PyPI Account Settings](https://pypi.org/manage/account/)
   - Create an API token with "Entire account" scope
   - Copy the token

2. **Add GitHub Secret**:
   - Go to your GitHub repository settings
   - Navigate to "Secrets and variables" → "Actions"
   - Add a new secret named `PYPI_API_TOKEN` with your PyPI token

3. **Publishing**:
   - **PyPI**: Publishes when you create a release or push a tag (e.g., `v1.0.0`)

4. **Create a Release**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   Then create a release on GitHub with the same tag.

## License

MIT License - Feel free to use and modify!
