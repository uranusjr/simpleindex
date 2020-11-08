import importlib.resources
import pathlib

import pytest

from simpleindex.configs import _Route, parse
from simpleindex.routes import HTTPRoute, PathRoute


def test_configuration_parse(tmp_path):
    with importlib.resources.path("examples", "annotated.toml") as path:
        conf = parse(path)
    assert conf.server == {"host": "127.0.0.1", "port": 8000}
    assert conf.routes == {
        "my-first-package": _Route(
            source="path",
            to="./index/my-first-package",
        ),
        "my-second-package": _Route(
            source="path",
            to="./index/my-second-package/index.html",
        ),
        "{project}": _Route(
            source="http",
            to="https://pypi.org/simple/{project}/",
        ),
    }


@pytest.mark.parametrize(
    "conf, result",
    [
        (
            _Route(source="path", to="./index/my-first-package"),
            PathRoute(root=pathlib.Path(), to="./index/my-first-package"),
        ),
        (
            _Route(source="http", to="https://pypi.org/simple/{project}/"),
            HTTPRoute(
                root=pathlib.Path(),
                to="https://pypi.org/simple/{project}/",
            ),
        ),
    ],
)
def test_route_derivation(conf, result):
    assert conf.derive(root=pathlib.Path()) == result
