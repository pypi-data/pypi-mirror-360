# -*- coding: UTF-8 -*-
from pathlib import Path

from core.models import Item


def assert_item_exists(root: Path, item: Item):
    if item.path is None or not (root / item.path).exists():
        raise ValueError('Item path is null.')
    if item.md_path is None or not (root / item.md_path).exists():
        raise ValueError('File path is null.')


def is_file_item(f: Path) -> bool:
    return f.is_file() and f.suffix == ".md"


def is_dir_item(f: Path) -> bool:
    if not f.is_dir():
        return False
    md_paths = list(f.glob("*.md"))
    return len(md_paths) == 1
