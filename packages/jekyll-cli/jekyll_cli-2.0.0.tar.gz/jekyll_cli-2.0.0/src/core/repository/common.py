# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from core.models import Formatter, Item


class DaoOperation(ABC):

    @abstractmethod
    def add(self, item: Item, formatter: Formatter):
        ...


    @abstractmethod
    def remove(self, item: Item):
        ...


    @abstractmethod
    def rename(self, item: Item, new_name: str):
        ...

    @abstractmethod
    def move(self, item: Item, sub_dir: Literal["_posts", "_drafts"]):
        ...


class BaseDao(DaoOperation, BaseModel, ABC):
    root: Path
