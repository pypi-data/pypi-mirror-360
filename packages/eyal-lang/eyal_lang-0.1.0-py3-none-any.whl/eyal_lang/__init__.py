"""
EyalLang - A playful DSL powered by Eyal-inspired directives and rule-based interpretation.
"""

from .interpreter import translate_file, translate_line, translate_lines
from .parser import EyalLangInterpreter, EyalLangParser

__version__ = "0.1.0"
__all__ = [
    "translate_line",
    "translate_file",
    "translate_lines",
    "EyalLangInterpreter",
    "EyalLangParser",
]
