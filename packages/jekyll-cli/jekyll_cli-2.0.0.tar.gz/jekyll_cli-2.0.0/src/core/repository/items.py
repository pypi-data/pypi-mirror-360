# -*- coding: UTF-8 -*-
from pathlib import Path

from core.models import BlogItems, Item
from core.utils import is_dir_item, is_file_item, load_item
from settings import Mode


def get_from_root(root: Path, mode: Mode) -> BlogItems:
    def get_from_sub_dir(sub_dir: str) -> list[Item]:
        parent_dir = root / sub_dir
        filter_item = is_file_item if mode == Mode.File else is_dir_item
        item_paths = [f for f in parent_dir.iterdir() if filter_item(f)]
        items = [load_item(f, root) for f in item_paths]
        return items

    posts = get_from_sub_dir("_posts")
    drafts = get_from_sub_dir("_drafts")
    return BlogItems(posts=posts, drafts=drafts)


def get_from_index(mode: Mode) -> BlogItems:
    index_abs_path = Path().home() / ".jekyll-cli" / f"index-{mode}.json"
    content = index_abs_path.read_text(encoding="utf-8")
    return BlogItems.model_validate_json(content)


def get_items(root: Path | None = None, mode: Mode | None = None) -> BlogItems:
    try:
        if not root or not mode:
            return BlogItems()
        index_file = Path().home() / ".jekyll-cli" / f"index-{mode}.json"
        if not index_file.is_file():
            items = get_from_root(root, mode)
            content = items.model_dump_json(indent=2)
            index_file.write_text(content, encoding="utf-8")
        items = get_from_index(mode)
        return items
    except Exception:
        return BlogItems()
