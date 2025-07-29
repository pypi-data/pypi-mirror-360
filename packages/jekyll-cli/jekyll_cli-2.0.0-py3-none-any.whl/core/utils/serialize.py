# -*- coding: UTF-8 -*-
import re
from pathlib import Path

from ruamel.yaml import YAML

from core.models import Formatter, Item, ItemType


def __load_formatter(formatter: str) -> Formatter:
    formatter = YAML().load(formatter) if formatter else {}
    if "tags" in formatter and isinstance(formatter["tags"], str):
        formatter["tags"] = formatter["tags"].split(" ")
    if "categories" in formatter and isinstance(formatter["categories"], str):
        formatter["categories"] = formatter["categories"].split(" ")
    formatter = Formatter(**formatter)
    return formatter


def load_item(item_abs_path: Path, root: Path) -> Item:
    if item_abs_path.is_file() and item_abs_path.suffix == ".md":
        md_abs_path = item_abs_path
    elif item_abs_path.is_dir():
        # 取第一个md
        md_abs_path = next(item_abs_path.glob("*.md"), None)
    else:
        md_abs_path = None

    if md_abs_path is None:
        raise ValueError("md_path is not found")

    if item_abs_path.parent.name == "_drafts":
        item_type = ItemType.Draft
    elif item_abs_path.parent.name == "_posts":
        item_type = ItemType.Post
    else:
        raise ValueError("Unexpected item type")

    name = item_abs_path.stem
    if item_type == ItemType.Post and (match := re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", name)):
        name = match.group(1)

    item = Item(
        name=name,
        type=item_type,
        path=item_abs_path.relative_to(root),
        md_path=md_abs_path.relative_to(root),
    )
    return item
