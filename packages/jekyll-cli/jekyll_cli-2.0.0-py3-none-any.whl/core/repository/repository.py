# -*- coding: UTF-8 -*-
from pathlib import Path
from typing import Literal

from core.models import BlogItems, Formatter, Item
from core.repository.directory_dao import DirectoryDao
from core.repository.file_dao import FileDao
from core.repository.items import get_from_root, get_items
from settings import Mode


class BlogRepository:

    def __init__(self, root: Path, mode: Mode):
        self.root = root
        self.mode = mode
        self.__items: BlogItems | None = None
        if mode == Mode.File:
            self.dao = FileDao(root=root)
        elif mode == Mode.Directory:
            self.dao = DirectoryDao(root=root)
        else:
            raise NotImplementedError

    def update_index(self):
        items = get_from_root(self.root, self.mode)
        index_file = Path.home() / ".jekyll-cli" / f"index-{self.mode}.json"
        content = items.model_dump_json(indent=2)
        index_file.write_text(content, encoding="utf-8")

    def __get_items(self) -> BlogItems:
        if self.__items is None:
            self.__items = get_items(self.root, self.mode)
        return self.__items

    @property
    def posts(self) -> list[Item]:
        return list(self.__get_items().posts)

    @property
    def drafts(self) -> list[Item]:
        return list(self.__get_items().drafts)

    def add(self, item: Item, formatter: Formatter) -> Item:
        item = self.dao.add(item, formatter)
        self.update_index()
        return item

    def remove(self, item: Item):
        self.dao.remove(item)
        self.update_index()

    def rename(self, item: Item, new_name: str):
        self.dao.rename(item, new_name)
        self.update_index()

    def move(self, item: Item, sub_dir: Literal["_posts", "_drafts"]):
        self.dao.move(item, sub_dir)
        self.update_index()
