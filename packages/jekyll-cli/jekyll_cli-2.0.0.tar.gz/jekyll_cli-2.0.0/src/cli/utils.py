# -*- coding: UTF-8 -*-
import ast
from typing import Any, Callable, List


def convert_literal(value: str) -> Any:
    try:
        value = ast.literal_eval(value)
        return value
    except Exception:
        return value


def complete_items(candidates: List[Any]) -> Callable[[str], List[str]]:
    def complete(incomplete: str) -> List[str]:
        return [str(candidate) for candidate in candidates if str(candidate).startswith(incomplete)]

    return complete
