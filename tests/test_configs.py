import importlib.resources

import pytest

from simpleindex.configs import _Route, _RouteSource, parse
from simpleindex.routes import HTTPRoute, PathRoute


def test_configuration_parse(tmp_path):
    with importlib.resources.path("examples", "annotated.toml") as path:
        conf = parse(path)
    assert conf.server == {"host": "127.0.0.1", "port": 8000}
    assert conf.routes == {
        "my-first-package": _Route(
            source=_RouteSource.path,
            to="./index/my-first-package",
        ),
        "my-second-package": _Route(
            source=_RouteSource.path,
            to="./index/my-second-package/index.html",
        ),
        "{project:str}": _Route(
            source=_RouteSource.http,
            to="https://pypi.org/{project}/",
        ),
    }


@pytest.mark.parametrize(
    "conf, result",
    [
        (
            _Route(source=_RouteSource.path, to="./index/my-first-package"),
            PathRoute(to="./index/my-first-package"),
        ),
        (
            _Route(source=_RouteSource.http, to="https://pypi.org/{project}/"),
            HTTPRoute(to="https://pypi.org/{project}/"),
        ),
    ],
)
def test_route_derivation(conf, result):
    assert conf.derive() == result
