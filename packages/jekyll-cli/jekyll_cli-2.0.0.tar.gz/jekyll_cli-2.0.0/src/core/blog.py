# -*- coding: UTF-8 -*-
import subprocess
from pathlib import Path
from typing import Literal

from core.models import Formatter, Item, ItemType, Result
from core.repository import BlogRepository
from settings import Mode


class Blog:

    def __init__(self, root: Path, mode: Mode):
        self.root = root
        self.mode = mode
        self.repo = BlogRepository(root, mode)

    @property
    def posts(self) -> list[Item]:
        return self.repo.posts

    @property
    def drafts(self) -> list[Item]:
        return self.repo.drafts

    def synchronize(self) -> Result[None]:
        try:
            self.repo.update_index()
            return Result.ok()
        except Exception as e:
            return Result.fail(e)

    def create(self, item: Item, formatter: Formatter) -> Result[Item]:
        try:
            if item in self:
                raise ValueError(f"Item {item.name} already exists")
            item = self.repo.add(item, formatter)
            return Result.ok(item)
        except Exception as e:
            return Result.fail(e)

    def remove(self, name: str) -> Result[None]:
        try:
            items = self.repo.posts + self.repo.drafts
            item = next((i for i in items if i.name == name), None)
            if item is None:
                raise ValueError(f"Item {name} not found")
            self.repo.remove(item)
            return Result.ok()
        except Exception as e:
            return Result.fail(e)

    def open(self, item: Item, editor: str | None = None) -> Result[None]:
        try:
            command = ["cmd.exe", "/c", "start", editor if editor else "", self.root / item.md_path]
            subprocess.run(command)
            return Result.ok()
        except Exception as e:
            return Result.fail(e)

    def find(self, name: str, subset: Literal["posts", "drafts", "all"]) -> Result[Item]:
        try:
            if subset == "posts":
                items = self.repo.posts
            elif subset == "drafts":
                items = self.repo.drafts
            else:
                items = self.repo.posts + self.repo.drafts

            item = next((i for i in items if i.name == name), None)
            if item is None:
                raise ValueError(f"Item {name} not found")
            return Result.ok(item)
        except Exception as e:
            return Result.fail(e)

    def rename(self, name: str, new_name: str) -> Result[None]:
        try:
            items = self.repo.posts + self.repo.drafts
            item = next((i for i in items if i.name == name), None)
            if item is None:
                raise ValueError(f"Item {name} not found")
            self.repo.rename(item, new_name)
            return Result.ok()
        except Exception as e:
            return Result.fail(e)

    def publish(self, name: str) -> Result[None]:
        try:
            items = self.repo.drafts
            item = next((i for i in items if i.name == name), None)
            if item is None:
                raise ValueError(f"Item {name} not found")
            if item.type == ItemType.Post:
                raise ValueError(f"Post {item} could not be published")
            self.repo.move(item, "_posts")
            return Result.ok()
        except Exception as e:
            return Result.fail(e)

    def unpublish(self, name: str) -> Result[None]:
        try:
            items = self.repo.posts
            item = next((i for i in items if i.name == name), None)
            if item is None:
                raise ValueError(f"Item {name} not found")
            if item.type == ItemType.Draft:
                raise ValueError(f"Draft {item} could not be unpublished")
            self.repo.move(item, "_drafts")
            return Result.ok()
        except Exception as e:
            return Result.fail(e)

    def __contains__(self, item: Item) -> bool:
        if not isinstance(item, Item):
            return False
        # name must be unique globally
        items = self.repo.posts + self.repo.drafts
        exist_item = next((i for i in items if i.name == item.name), None)
        return exist_item is not None
