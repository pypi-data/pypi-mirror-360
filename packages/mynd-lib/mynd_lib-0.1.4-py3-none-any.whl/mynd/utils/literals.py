"""Module for literal functionality."""

import ast


Primitive = int | str | float | bool | None


def literal_primitive(literal: str) -> Primitive | None:
    """Evaluate a string as a dtype."""
    try:
        evaluated: Primitive = ast.literal_eval(literal)
        return evaluated
    except ValueError:
        return None
