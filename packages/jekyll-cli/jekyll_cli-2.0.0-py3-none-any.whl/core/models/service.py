# -*- coding: UTF-8 -*-
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool
    data: T | None = None
    error: Exception | None = None

    @classmethod
    def ok(cls, data: T | None = None) -> Result[T]:
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: Exception | str) -> Result[T]:
        if isinstance(error, str):
            error = Exception(error)
        return cls(success=False, error=error)

    def unwrap(self) -> T:
        if not self.success:
            raise self.error
        return self.data

    def __str__(self):
        return str(self.data) if self.success else str(self.error)
