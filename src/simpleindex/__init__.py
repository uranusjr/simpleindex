"""PEP 503 Simple Repository index by declaring routing rules."""

import typing

__all__ = [
    "__version__",
    "run",
]

__version__ = "0.6.1"


def run(args: typing.Optional[typing.List[str]] = None) -> None:
    from .__main__ import run

    return run(args)
