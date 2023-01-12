from __future__ import annotations

import contextlib
import dataclasses
import pathlib
import typing

import packaging.utils


@dataclasses.dataclass()
class Response:
    content: typing.Union[bytes, str] = b""
    status_code: int = 200
    media_type: str = "text/plain"
    headers: typing.Optional[typing.Mapping[str, str]] = None


Params = typing.Mapping[str, typing.Any]


@dataclasses.dataclass()
class Route:
    root: pathlib.Path
    to: str

    async def get_page(self, params: Params) -> Response:
        raise NotImplementedError()

    async def get_file(self, params: Params, filename: str) -> Response:
        return Response(status_code=404, content="not found")


_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>
{anchors}
</body>
</html>
"""


def _is_valid_dist_filename(filename: str) -> bool:
    with contextlib.suppress(
        packaging.utils.InvalidWheelFilename,
        packaging.utils.InvalidVersion,
    ):
        packaging.utils.parse_wheel_filename(filename)
        return True
    with contextlib.suppress(
        packaging.utils.InvalidSdistFilename,
        packaging.utils.InvalidVersion,
    ):
        packaging.utils.parse_sdist_filename(filename)
        return True
    return False


def _iter_anchors(root: pathlib.Path) -> typing.Iterator[str]:
    """Create anchor tags from directory listing.

    Files are served at "{prefix}/{project}/{filename}". Entries that do not
    look like a distribution file are ignored.
    """
    for path in root.iterdir():
        if not _is_valid_dist_filename(path.name):
            continue
        yield f'<a href="./{path.name}">{path.name}</a>'


class PathRoute(Route):
    async def get_page(self, params: Params) -> Response:
        path = self.root.joinpath(self.to.format(**params))
        if path.is_file():
            return Response(content=path.read_bytes(), media_type="text/html")
        if path.is_dir():
            html = _HTML.format(anchors="\n".join(_iter_anchors(path)))
            return Response(content=html, media_type="text/html")
        return Response(status_code=404, content="Not Found")

    async def get_file(self, params: Params, filename: str) -> Response:
        path = self.root.joinpath(self.to.format(**params))
        if not path.is_dir():
            return await super().get_file(params, filename)
        path = path.joinpath(filename)
        if not path.is_file():
            return await super().get_file(params, filename)
        if not _is_valid_dist_filename(path.name):
            return await super().get_file(params, filename)
        if filename.endswith(".tar.gz"):
            media_type = "application/x-tar"
        elif path.suffix in (".whl", ".zip"):
            media_type = "application/zip"
        else:
            media_type = "application/octet-stream"
        data = path.read_bytes()
        return Response(status_code=200, content=data, media_type=media_type)


class HTTPRoute(Route):
    async def get_page(self, params: Params) -> Response:
        url = self.to.format(**params)
        return Response(status_code=302, headers={"Location": url})
