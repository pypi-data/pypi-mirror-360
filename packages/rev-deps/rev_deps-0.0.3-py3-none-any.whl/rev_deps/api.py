from typing import Iterator
from . import core


def get_rev_deps(project: str) -> Iterator[str]:
    yield from core._rev_deps(project) 