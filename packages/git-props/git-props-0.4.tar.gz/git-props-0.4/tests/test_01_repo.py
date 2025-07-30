"""Test module gitprops.repo
"""

import contextlib
import logging
import pytest
from gitprops.repo import GitError
from gitprops.version import Version

logger = logging.getLogger(__name__)

@contextlib.contextmanager
def log_invocations(request, repo, max_call=None):
    name = request.node.nodeid.split("::", 1)[1]
    pre_count = repo.invocation_count
    logger.debug("%s: git invocations before the test: %d", name, pre_count)
    yield
    post_count = repo.invocation_count
    logger.debug("%s: git invocations after the test: %d", name, post_count)
    if max_call:
        assert post_count - pre_count <= max_call


def test_repo_commit(request, repo_case):
    repo = repo_case.repo
    with log_invocations(request, repo, max_call=1):
        if repo_case.commit is not None:
            assert repo.get_commit() == repo_case.commit
        else:
            with pytest.raises(GitError):
                repo.get_commit()

def test_repo_last_version(request, repo_case):
    repo = repo_case.repo
    with log_invocations(request, repo, max_call=repo_case.version_git_calls):
        if repo_case.tag is None:
            assert repo.get_last_version_tag() is None
        else:
            assert Version(repo.get_last_version_tag()) == repo_case.tag

def test_repo_dirty(request, repo_case):
    repo = repo_case.repo
    with log_invocations(request, repo, max_call=1):
        assert repo.is_dirty() == repo_case.dirty

def test_repo_version_meta(request, repo_case):
    repo = repo_case.repo
    max_call = repo_case.version_git_calls + 3
    with log_invocations(request, repo, max_call=max_call):
        meta = repo.get_version_meta()
        assert meta.version == repo_case.tag
        assert meta.count == repo_case.count
        assert meta.node == repo_case.node
        assert meta.dirty == repo_case.dirty

def test_repo_date(request, repo_case):
    repo = repo_case.repo
    with log_invocations(request, repo, max_call=2):
        assert repo.get_date() == repo_case.date
