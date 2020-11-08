import argparse
import pathlib

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.routing import Route
from uvicorn import run as run_uvicorn

from . import configs, routes


def _resolve_path(v: str) -> pathlib.Path:
    return pathlib.Path(v).resolve()


def _build_page_route(key: str, route: routes.Route) -> Route:
    async def view(request: Request):
        response = await route.get(request.path_params)
        return HTMLResponse(
            content=response.text,
            status_code=response.status_code,
        )

    return Route(f"/{key}/", view)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config",
        type=_resolve_path,
        help="Path to configuration file",
    )
    ns = parser.parse_args()

    configuration = configs.parse(ns.config)

    web_routes = [
        _build_page_route(key, route.derive(ns.config.parent))
        for key, route in configuration.routes.items()
    ]
    app = Starlette(routes=web_routes)

    options = {k.replace("-", "_"): v for k, v in configuration.server.items()}
    run_uvicorn(app, **options)


if __name__ == "__main__":
    main()
