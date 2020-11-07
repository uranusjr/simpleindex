from __future__ import annotations

import dataclasses
import pathlib
import typing

import httpx
import packaging_dists


class Response(typing.Protocol):
    status_code: int
    text: str


@dataclasses.dataclass()
class LocalResponse(Response):
    status_code: int
    text: str


Params = typing.Mapping[str, typing.Any]


@dataclasses.dataclass()
class Route:
    to: str

    async def get(self, canonical_name: str, params: Params) -> Response:
        raise NotImplementedError()


_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Links for {project}</title>
</head>
<body>
{anchors}
</body>
</html>
"""


def _iter_anchors(root: pathlib.Path, project: str) -> typing.Iterator[str]:
    """Create anchor tags from directory listing.

    Files are served at "{prefix}/{project}/{filename}". Entries that do not
    look like a distribution file and match the given project are ignored.
    """
    for path in root.iterdir():
        try:
            dist = packaging_dists.parse(path.name)
        except packaging_dists.InvalidDistribution:
            continue
        if dist.project != project:
            continue
        yield f'<a href="./{path.name}">{path.name}</a>'


@dataclasses.dataclass()
class PathRoute(Route):
    async def get(self, canonical_name: str, params: Params) -> Response:
        path = pathlib.Path(self.to.format(**params))
        if path.is_file():
            return LocalResponse(status_code=200, text=path.read_text())
        if path.is_dir():
            html = _HTML_TEMPLATE.format(
                project=canonical_name,
                anchors="\n".join(_iter_anchors(path, canonical_name)),
            )
            return LocalResponse(status_code=200, text=html)
        return LocalResponse(status_code=404, text="no such file or directory")


@dataclasses.dataclass()
class URLRoute(Route):
    async def get(self, canonical_name: str, params: Params) -> Response:
        url = self.to.format(**params)
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
        return resp
