"""Test toplevel function at package level.
"""

import pytest
from gitprops import get_version, get_last_release, get_date


def test_get_version(repo_case):
    version = get_version(root=repo_case.repo.root)
    assert version == repo_case.version

def test_get_last_release(repo_case):
    version = get_last_release(root=repo_case.repo.root)
    assert version == repo_case.tag

def test_get_date(repo_case):
    date = get_date(root=repo_case.repo.root)
    assert date == repo_case.date
