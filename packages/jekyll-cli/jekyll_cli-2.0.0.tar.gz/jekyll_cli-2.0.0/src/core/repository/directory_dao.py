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


class DirectoryDao(BaseDao):

    def add(self, item: Item, formatter: Formatter) -> Item:
        sub_dir = "_posts" if item.type == ItemType.Post else "_drafts"
        item_abs_path = self.root / sub_dir / item.name
        assets_abs_path = item_abs_path / "assets"
        md_filename = f"{item.name}.md"
        if item.type == ItemType.Post:
            md_filename = f"{time.strftime('%Y-%m-%d')}-{md_filename}"
        md_abs_path = item_abs_path / md_filename

        if item.type == ItemType.Post:
            formatter.date = time.strftime("%Y-%m-%d %H:%M")
        item.path = item_abs_path.relative_to(self.root)
        item.md_path = md_abs_path.relative_to(self.root)

        item_abs_path.mkdir(exist_ok=True)
        assets_abs_path.mkdir(exist_ok=True)

        yaml = YAML(typ="string")
        content = f"---\n{yaml.dump_to_string(formatter.model_dump())}\n---\n"
        md_abs_path.write_text(content, encoding="utf-8")
        return item


    def open(self, item: Item, editor: str | None = None):
        assert_item_exists(self.root, item)
        command = ["cmd.exe", "/c", "start", editor if editor else "", item.md_path]
        subprocess.run(command)


    def remove(self, item: Item):
        assert_item_exists(self.root, item)
        shutil.rmtree(self.root / item.path)


    def rename(self, item: Item, new_name: str):
        assert_item_exists(self.root, item)

        md_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})-(.+)\.md")
        if item.type == ItemType.Post and (match := md_pattern.match(item.md_path.name)):
            new_filename = f"{match.group(1)}-{new_name}.md"
        else:
            new_filename = f"{new_name}.md"

        md_abs_path = self.root / item.md_path.with_name(new_filename)
        item_abs_path = self.root / item.path.with_name(new_name)

        if item_abs_path.exists():
            raise ValueError("Item path already exists.")

        (self.root / item.md_path).rename(md_abs_path)
        (self.root / item.path).rename(item_abs_path)

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
