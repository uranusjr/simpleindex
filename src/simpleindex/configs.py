from __future__ import annotations

import dataclasses
import functools
import importlib.metadata
import pathlib
import typing

import pydantic
import toml

from .routes import Route


@functools.lru_cache(maxsize=None)
def _get_route_source_choices() -> typing.Dict[str, typing.Type[Route]]:
    entry_points = importlib.metadata.entry_points()
    return {
        ep.name: ep.load()
        for ep in entry_points.get("simpleindex.routes", [])
    }


def _validate_route_source(v: typing.Union[str, _RouteSource]) -> _RouteSource:
    if isinstance(v, _RouteSource):
        return v
    try:
        return _RouteSource(name=v, value=_get_route_source_choices()[v])
    except KeyError:
        raise ValueError(v)


@dataclasses.dataclass()
class _RouteSource:
    name: str
    value: typing.Type[Route]

    @classmethod
    def __get_validators__(cls):
        yield _validate_route_source


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
