# -*- coding: UTF-8 -*-
import re
import shutil
import subprocess
import time
from typing import Literal

from ruamel.yaml import YAML

from core.models import Formatter, Item, ItemType
from core.repository.common import BaseDao
from core.utils import assert_item_exists


class FileDao(BaseDao):

    def add(self, item: Item, formatter: Formatter) -> Item:
        md_filename = f"{item.name}.md"
        if item.type == ItemType.Post:
            md_filename = f"{time.strftime('%Y-%m-%d')}-{md_filename}"
        sub_dir = "_posts" if item.type == ItemType.Post else "_drafts"
        item_abs_path = self.root / sub_dir / md_filename

        if item.type == ItemType.Post:
            formatter.date = time.strftime("%Y-%m-%d %H:%M")
        item.path = item_abs_path.relative_to(self.root)
        item.md_path = item_abs_path.relative_to(self.root)

        yaml = YAML(typ="string")
        content = f"---\n{yaml.dump_to_string(formatter.model_dump())}\n---\n"
        item_abs_path.write_text(content, encoding="utf-8")
        return item


    def open(self, item: Item, editor: str | None = None):
        assert_item_exists(self.root, item)
        command = ["cmd.exe", "/c", "start", editor if editor else "", item.md_path]
        subprocess.run(command)


    def remove(self, item: Item):
        assert_item_exists(self.root, item)
        (self.root / item.path).unlink()


    def rename(self, item: Item, new_name: str):
        assert_item_exists(self.root, item)

        pattern = re.compile(r"(\d{4}-\d{2}-\d{2})-(.+)")
        if item.type == ItemType.Post and (match := pattern.match(item.md_path.stem)):
            new_stem = f"{match.group(1)}-{new_name}"
        else:
            new_stem = new_name

        md_path = self.root / item.md_path.with_stem(new_stem)
        if md_path.exists():
            raise ValueError("Item path already exists.")
        (self.root / item.md_path).rename(md_path)

    def move(self, item: Item, target_dir: Literal["_posts", "_drafts"]):
        assert_item_exists(self.root, item)
        dest_parent_abs_path = self.root / target_dir
        dest_item_abs_path = dest_parent_abs_path / item.path.relative_to(item.parent)
        dest_md_abs_path = dest_parent_abs_path / item.md_path.relative_to(item.parent)
        shutil.move(self.root / item.path, dest_item_abs_path)

        if target_dir == "_posts":
            new_filename = f"{time.strftime('%Y-%m-%d')}-{item.name}.md"
        elif target_dir == "_drafts":
            new_filename = f"{item.name}.md"
        else:
            raise NotImplementedError
        dest_md_abs_path.rename(dest_md_abs_path.with_name(new_filename))
