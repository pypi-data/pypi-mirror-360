# -*- coding: UTF-8 -*-
from pathlib import Path
from typing import Any, Literal

import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError, Validator
from rich.console import Console
from rich.table import Table


__console = Console()


def success(message: str):
    __console.print(f"[green]{message}[/green]")


def error(message: str):
    __console.print(f"[red]{message}[/red]")


def info(rich_text: str):
    __console.print(rich_text)


def error_exit(message: str):
    error(message)
    raise typer.Exit(code=1)


def print_list(items: list[Any], **table_config):
    if not items:
        return
    table = Table(**table_config)
    table.add_column()

    if len(items) == 1:
        table.add_row(f"[green][1][/] {items[0]}")
        __console.print(table)
        return

    table.add_column()
    for i in range(0, len(items), 2):
        item1 = f"[green][{i + 1}][/] {items[i]}"
        item2 = f"[green][{i + 2}][/] {items[i + 1]}" if i + 1 < len(items) else ""
        table.add_row(item1, item2)
    __console.print(table)


def print_dict(d: dict[str, Any], **table_config):
    table = Table(**table_config)
    table.add_column()
    table.add_column()
    for key, value in d.items():
        table.add_row(f"[cyan]{key.capitalize()}", str(value))
    __console.print(table)


def select(message: str, choices: list[Any] | dict[str, Any]) -> Any:
    if isinstance(choices, list):
        select_choices = choices
    elif isinstance(choices, dict):
        select_choices = [Choice(name=name, value=value) for name, value in choices.items()]
    else:
        raise ValueError("choices is not a list or dict.")
    return inquirer.select(
        message=message,
        choices=select_choices,
        vi_mode=True
    ).execute()


def check(message: str, choices: list[Any] | dict[str, Any]) -> Any:
    if isinstance(choices, list):
        select_choices = choices
    elif isinstance(choices, dict):
        select_choices = [Choice(name=name, value=value) for name, value in choices.items()]
    else:
        raise ValueError("choices is not a list or dict.")
    return inquirer.checkbox(
        message=message,
        choices=select_choices,
        vi_mode=True
    ).execute()


def confirm(message, default=False) -> bool:
    return inquirer.confirm(message, default=default).execute()


class __PathValidator(Validator):

    def validate(self, document: Document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Input cannot be empty",
                cursor_position=document.cursor_position,
            )
        path = Path(document.text).expanduser().resolve()
        if not path.is_dir():
            raise ValidationError(
                message="Input is not a valid directory",
                cursor_position=document.cursor_position,
            )
        post_dir = path / "_posts"
        if not post_dir.is_dir():
            raise ValidationError(
                message="Posts directory does not exist in this directory",
                cursor_position=document.cursor_position,
            )
        draft_dir = path / "_drafts"
        if not draft_dir.is_dir():
            raise ValidationError(
                message="Draft directory does not exist in this directory",
                cursor_position=document.cursor_position,
            )


def input_path(message: str, path_type: Literal["file", "directory"]) -> Path:
    only_files = (path_type == "file")
    only_directories = (path_type == "directory")
    return inquirer.filepath(
        message=message,
        vi_mode=True,
        only_files=only_files,
        only_directories=only_directories,
        multicolumn_complete=True,
        validate=__PathValidator(),
        filter=lambda path: Path(path).resolve()
    ).execute()


def input_text(message: str) -> str:
    return inquirer.text(message=message, vi_mode=True).execute()
