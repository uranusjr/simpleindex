import argparse
import itertools
import pathlib
import typing

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from uvicorn import run as run_uvicorn

from . import configs, routes


def _build_routes(key: str, route: routes.Route) -> typing.List[Route]:
    async def page(request: Request):
        response = await route.get_page(request.path_params)
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.media_type,
            headers=response.headers,
        )

    async def dist(request: Request):
        params = request.path_params
        filename = params.pop(filename_param)
        response = await route.get_file(params, filename)
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.media_type,
            headers=response.headers,
        )

    filename_param = "__simpleindex_match_filename__"
    return [
        Route(f"/{key}/", page),
        Route(f"/{key}/{{{filename_param}}}", dist),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config",
        type=pathlib.Path,
        help="Path to configuration file",
    )
    ns = parser.parse_args()

    configuration = configs.parse(ns.config)

    routes = itertools.chain.from_iterable(
        _build_routes(key, route.derive(ns.config.parent))
        for key, route in configuration.routes.items()
    )
    app = Starlette(routes=list(routes))

    options = {k.replace("-", "_"): v for k, v in configuration.server.items()}
    run_uvicorn(app, **options)


if __name__ == "__main__":
    main()
