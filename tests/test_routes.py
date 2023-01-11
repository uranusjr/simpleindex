import pathlib

import mousebender.simple
import pytest

from simpleindex.routes import HTTPRoute, PathRoute


@pytest.mark.asyncio
async def test_path_route_directory(tmp_path):
    """An HTML document is built from a local directory."""
    directory = tmp_path.joinpath("my-package")
    directory.mkdir()

    project_files = [
        "my-package-1.0.tar.gz",
        "my_package-1.0-py2.py3-none-any.whl",
    ]
    for name in project_files:
        directory.joinpath(name).touch()

    route = PathRoute(root=tmp_path, to="{project}")
    resp = await route.get_page({"project": "my-package"})
    assert resp.status_code == 200

    links = mousebender.simple.parse_archive_links(resp.content)
    assert [link.filename for link in links] == project_files
    assert [link.url for link in links] == [f"./{n}" for n in project_files]


@pytest.mark.asyncio
async def test_path_route_file(tmp_path):
    """A local file route simply serves the file as-is."""
    html_file = tmp_path.joinpath("project.html")
    html_file.write_text("<body>test content</body>")

    route = PathRoute(root=tmp_path, to="{project}.html")
    resp = await route.get_page({"project": "project"})
    assert resp.status_code == 200
    assert resp.content.decode() == "<body>test content</body>"


@pytest.mark.asyncio
async def test_path_route_invalid(tmp_path):
    """404 is returned if the path does not point to a file or directory."""
    route = PathRoute(root=tmp_path, to="does-not-exist")
    resp = await route.get_page({})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_http_route():
    route = HTTPRoute(
        root=pathlib.Path("does-not-matter"),
        to="http://example.com/simple/{project}/",
    )
    resp = await route.get_page({"project": "package"})
    assert resp.status_code == 302
