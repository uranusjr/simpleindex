import argparse
import itertools
import typing

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route
from uvicorn import run as run_uvicorn

from . import configs, routes


def _build_routes(key: str, route: routes.Route) -> typing.List[Route]:
    async def page(request: Request):
        return await route.get_page(request.path_params)

    async def dist(request: Request):
        params = request.path_params
        filename = params.pop(filename_param)
        return await route.get_file(params, filename)

    filename_param = "__simpleindex_match_filename__"
    return [
        Route(f"/{key}/", page),
        Route(f"/{key}/{{{filename_param}}}", dist),
    ]


def run(args: typing.Optional[typing.List[str]]) -> None:
    """Run the index server.

    :param args: CLI arguments to pass to the argument parser. If ``None`` is
        passed, ``sys.argv[1:]`` is used (the default argparse behavior).
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config",
        type=configs.Configuration.parse_arg,
        help="Path to configuration file",
    )
    ns = parser.parse_args(args)

    config_path, configuration = ns.config

    routes = itertools.chain.from_iterable(
        _build_routes(key, route.derive(config_path.parent))
        for key, route in configuration.routes.items()
    )
    app = Starlette(routes=list(routes))

    options = {k.replace("-", "_"): v for k, v in configuration.server.items()}
    run_uvicorn(app, **options)


if __name__ == "__main__":
    run(None)
