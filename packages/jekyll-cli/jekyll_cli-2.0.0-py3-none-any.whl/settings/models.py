# -*- coding: UTF-8 -*-
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, field_serializer, field_validator


class Mode(StrEnum):
    File = "file"
    Directory = "directory"


class GenerateSettings(BaseModel):
    draft: bool = False
    port: int = 4000


class AppSettings(BaseModel):
    root: Path | None = None
    mode: Mode
    editor: str | None = None
    generate: GenerateSettings = GenerateSettings()

    @field_serializer("root")
    def serialize_root(self, root: Path | None, _):
        return str(root) if root else None

    @field_validator("root", mode="before")
    @classmethod
    def validate_root(cls, value: Any, _) -> Path | None:
        if value is None:
            return None
        path = Path(str(value)).expanduser().resolve()
        if not path.is_dir():
            raise ValueError(f"Path {path} is not a directory")
        post_dir = path / "_posts"
        if not post_dir.is_dir():
            raise ValueError(f"Posts directory does not exist in this directory")
        draft_dir = path / "_drafts"
        if not draft_dir.is_dir():
            raise ValueError(f"Draft directory does not exist in this directory")
        return path

    @field_validator("mode", mode="before")
    @classmethod
    def validate_mode(cls, value: Any, _) -> str:
        if value is None:
            raise ValueError(f"mode is required")
        if not isinstance(value, str):
            raise ValueError(f"mode is not a string")
        value = value.lower()
        if value not in [Mode.File, Mode.Directory]:
            raise ValueError(f"mode is not a valid mode")
        return value
