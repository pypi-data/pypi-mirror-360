# -*- coding: UTF-8 -*-
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ItemType(StrEnum):
    Post = "post"
    Draft = "draft"


class Formatter(BaseModel):
    model_config = ConfigDict(extra="allow")

    layout: Annotated[str, Field(frozen=True)] = "post"
    title: str | None = None
    categories: list[str] = []
    tags: list[str] = []


class Item(BaseModel):
    name: str
    type: ItemType
    path: Annotated[Path | None, Field(description="item relative path")] = None
    md_path: Annotated[Path | None, Field(description="markdown relative path")] = None

    @property
    def parent(self) -> Path | None:
        return self.path.parent if self.path else None

    @property
    def info(self) -> dict[str, str]:
        return {
            "name": self.name,
            "type": self.type.name,
            "path": str(self.path),
            "markdown path": str(self.md_path),
        }

    def __str__(self):
        return self.name


class BlogItems(BaseModel):
    posts: list[Item] = []
    drafts: list[Item] = []

    @classmethod
    @field_validator("posts")
    def __check_posts(cls, posts: list[Item]) -> list[Item]:
        if not all(item.type == ItemType.Post for item in posts):
            raise ValueError("posts are not valid")
        return posts

    @classmethod
    @field_validator("drafts")
    def __check_drafts(cls, drafts: list[Item]) -> list[Item]:
        if not all(item.type == ItemType.Draft for item in drafts):
            raise ValueError("drafts are not valid")
        return drafts

    @property
    def articles(self) -> list[Item]:
        return self.posts + self.drafts
