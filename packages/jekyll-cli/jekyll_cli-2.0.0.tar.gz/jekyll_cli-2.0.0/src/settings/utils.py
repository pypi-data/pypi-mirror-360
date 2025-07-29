# -*- coding: UTF-8 -*-
from pathlib import Path
from typing import Any

import tomlkit

from settings.models import AppSettings, Mode


def update_settings(app_settings: AppSettings):
    settings_file = Path().home() / ".jekyll-cli" / "settings.toml"
    app_settings = app_settings.model_dump(exclude_none=True)
    with settings_file.open("w", encoding="utf-8") as f:
        tomlkit.dump(app_settings, f)


def get_settings() -> AppSettings:
    settings_file = Path().home() / ".jekyll-cli" / "settings.toml"
    if not settings_file.exists():
        app_settings = AppSettings(mode=Mode.File)
        with settings_file.open("w", encoding="utf-8") as f:
            tomlkit.dump(app_settings.model_dump(exclude_none=True), f)
        return app_settings
    else:
        with settings_file.open("r", encoding="utf-8") as f:
            app_settings = tomlkit.load(f).unwrap()
            app_settings = AppSettings.model_validate(app_settings)
            return app_settings


def set_settings_by_path(s: AppSettings, path: str, value: Any) -> AppSettings:
    d = s.model_dump()
    keys = path.split(".")
    current = d

    # get target key
    # intermediate node type must be BaseModel
    for key in keys[:-1]:
        if not isinstance(current, dict):
            raise TypeError(f"Intermediate node type {type(current)} is not a dict")
        if key not in current:
            raise AttributeError(f"Missing \"{key}\"")
        current = current[key]

    # target node processing
    if keys[-1] not in current:
        raise AttributeError(f"Missing \"{keys[-1]}\"")
    current[keys[-1]] = value
    return AppSettings.model_validate(d)
