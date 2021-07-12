# PEP 503 Simple Repository from routing rules

simpleindex helps set up a PEP 503 "proxy server" that re-routes requests to
each project to its "real" repository source, to prevent multiple indexes being
mixed together, creating [dependency confusion] vulnarabilities.

[dependency confusion]: https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610


## Installation

Install simpleindex with [pipx](https://pypa.github.io/pipx/):

```
$ pipx install simpleindex
```

Or use pip to install into an existing virtual environment:

```
$ pip install simpleindex
```


## Basic configuration

Generate distributions:

```
$ tree .
.
├── configuration.toml
├── uranusjr-core
│   ├── uranusjr_core-1.0.py3.none-any.whl
│   └── uranusjr_core-2.0.py3.none-any.whl
└── uranusjr-web
    └── uranusjr_web-2.0.py3.none-any.whl
```

Write a configuration:

```toml
# ./configuration.toml

# Serve local files for packages with prefix "uranusjr-".
[routes."uranusjr-{subproject}"]
source = "path"
to = "./uranusjr-{subproject}"

# Otherwise use PyPI.
[routes."{project}"]
source = "http"
to = "https://pypi.org/simple/{project}/"

[server]
host = "127.0.0.1"
port = 8000
```

Run the server:

```
$ simpleindex /path/to/configuration.toml
```

Install projects:

```
$ python -m pip install -i http://127.0.0.1:8000 uranusjr-web
```


## Custom route types

`simpleindex` can be made aware of new route types via the `simpleindex.routes` [entry point] group.

[entry point]: https://setuptools.readthedocs.io/en/latest/userguide/entry_point.html#advertising-behavior

A new route type should subclass `simpleindex.routes.Route`, and implement behaviour to respond to HTTP requests.

The `Route` instance has two attributes:

* `root`: A `pathlib.Path` pointing to the directory containing the configuration file current being served.
* `to`: The `to` string in the configuratio block.

For example, here's how you might want to implement Amazon S3 support:

```python
# simpleindex_s3.py

from simpleindex.routes import Response, Route

class AmazonS3Route(Route):
    async def get_page(self, params: dict[str, Any]) -> Response:
        # "params" is a mapping of parameters captured from the URL.
        s3_bucket = self.to.format(**params)
        list_of_files = _list_s3_files(s3_bucket)
        html = _create_html_for_files(list_of_files)
        return Response(status_code=200, content=html, media_type="text/html")
```

`Response` accepts an optional argument `headers` if you want to add additional response headers.

Now add the class to the entry point group:

```ini
# setup.cfg

[options.entry_points]
simpleindex.routes =
    s3 = simpleindex_s3:AmazonS3Route
```

You'll be able to use `source = "s3"` in the a `routes` block after installing the package:

```
$ pipx inject simpleindex simpleindex-s3
```
