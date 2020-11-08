# PEP 503 Simple Repository from routing rules

Install simpleindex ([pipx](https://pipxproject.github.io/pipx/) is recommended):

```
$ pipx install simpleindex
```

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
