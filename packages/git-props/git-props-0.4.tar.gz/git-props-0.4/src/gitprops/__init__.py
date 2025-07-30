"""Determine some properties from a git repository

A simple Python package to determine some properties from a git
repository.
"""

from pathlib import Path
from ._meta import version as __version__
from .repo import GitError, GitRepo
from .version import Version


_repo_cache = dict()
def _get_repo(root):
    root = Path(root).resolve()
    if root not in _repo_cache:
        try:
            _repo_cache[root] = GitRepo(root)
        except FileNotFoundError as exc:
            raise LookupError() from exc
    return _repo_cache[root]


def get_version(root="."):
    try:
        repo = _get_repo(root)
        meta = repo.get_version_meta()
        return Version.build_version(**(meta._asdict()))
    except GitError as exc:
        raise LookupError() from exc

def get_last_release(root="."):
    try:
        repo = _get_repo(root)
        tag = repo.get_last_version_tag()
        if tag is None:
            return None
        else:
            return Version(tag)
    except GitError as exc:
        raise LookupError() from exc

def get_date(root="."):
    try:
        repo = _get_repo(root)
        return repo.get_date()
    except GitError as exc:
        raise LookupError() from exc
