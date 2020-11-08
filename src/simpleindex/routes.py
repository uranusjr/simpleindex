from __future__ import annotations

import dataclasses
import pathlib
import typing

import packaging_dists


@dataclasses.dataclass()
class Response:
    text: str = ""
    status_code: int = 200
    media_type: str = "text/plain"
    headers: typing.Optional[typing.Mapping[str, str]] = None


@dataclasses.dataclass()
class Route:
    root: pathlib.Path
    to: str

    async def get(self, params: typing.Mapping[str, typing.Any]) -> Response:
        raise NotImplementedError()


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


def _iter_anchors(root: pathlib.Path) -> typing.Iterator[str]:
    """Create anchor tags from directory listing.

    Files are served at "{prefix}/{project}/{filename}". Entries that do not
    look like a distribution file are ignored.
    """
    for path in root.iterdir():
        try:
            packaging_dists.parse(path.name)
        except packaging_dists.InvalidDistribution:
            continue
        yield f'<a href="./{path.name}">{path.name}</a>'


@dataclasses.dataclass()
class PathRoute(Route):
    async def get(self, params: typing.Mapping[str, typing.Any]) -> Response:
        path = self.root.joinpath(self.to.format(**params))
        if path.is_file():
            return Response(text=path.read_text(), media_type="text/html")
        if path.is_dir():
            html = _HTML.format(anchors="\n".join(_iter_anchors(path)))
            return Response(text=html, media_type="text/html")
        return Response(status_code=404, text="not found")


@dataclasses.dataclass()
class HTTPRoute(Route):
    async def get(self, params: typing.Mapping[str, typing.Any]) -> Response:
        url = self.to.format(**params)
        return Response(status_code=302, headers={"Location": url})
