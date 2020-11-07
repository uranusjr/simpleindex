from __future__ import annotations

import enum
import pathlib
import typing

import pydantic
import toml

from .routes import HTTPRoute, PathRoute, Route


class _RouteSource(enum.Enum):
    http = HTTPRoute
    path = PathRoute

    @classmethod
    def __validate(cls, v: typing.Union[str, _RouteSource]) -> _RouteSource:
        if isinstance(v, _RouteSource):
            return v
        try:
            return cls.__members__[v]
        except KeyError:
            raise ValueError(v)

    @classmethod
    def __get_validators__(cls):
        yield cls.__validate


class _Route(pydantic.BaseModel):
    source: _RouteSource
    to: str

    def derive(self, root: pathlib.Path) -> Route:
        return self.source.value(root=root, to=self.to)


class Configuration(pydantic.BaseModel):
    routes: typing.Mapping[str, _Route]
    server: typing.Mapping[str, typing.Any]


def parse(path: pathlib.Path) -> Configuration:
    with path.open(encoding="utf-8") as f:
        data = toml.load(f)
    return Configuration(**data)
