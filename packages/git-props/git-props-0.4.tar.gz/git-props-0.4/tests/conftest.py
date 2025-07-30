from collections import namedtuple
import datetime
from pathlib import Path
import shutil
import tarfile
import tempfile
import yaml
import pytest
import gitprops
from gitprops.repo import GitRepo

testdir = Path(__file__).resolve().parent
testdatadir = testdir / "data"
_cleanup = True

class CountingGitRepo(GitRepo):
    """A git repo that counts the number of git invocations.
    """

    def __init__(self, root="."):
        self._invocation_count = 0
        super().__init__(root=root)

    def _exec(self, cmd):
        self._invocation_count += 1
        return super()._exec(cmd)

    @property
    def invocation_count(self):
        return self._invocation_count

CaseTuple = namedtuple('CaseTuple', [
    'repo', 'branch', 'dirty',
    'tag', 'count', 'node', 'commit', 'version', 'date', 'marks',
    'version_git_calls',
])
class Case(CaseTuple):
    def __new__(cls, **kwargs):
        today = datetime.date.today()
        subst = dict(kwargs, today=today, today_str=today.strftime("%Y%m%d"))
        if kwargs.get('date') == 'today':
            kwargs['date'] = subst['today']
        if kwargs.get('version'):
            kwargs['version'] = kwargs['version'] % subst
        return super().__new__(cls, **kwargs)
    @property
    def name(self):
        parts = [self.repo]
        if self.branch:
            parts.append(self.branch)
        if self.dirty:
            parts.append('dirty')
        return '-'.join(parts)

def get_testdata(fname):
    fname = testdatadir / fname
    assert fname.is_file()
    return fname

def get_test_cases():
    casefile = get_testdata("caselist.yaml")
    with open(casefile, "rt") as f:
        for c in yaml.unsafe_load(f):
            case = Case(**c)
            marks = case.marks if case.marks else ()
            id = case.name
            yield pytest.param(case, id=id, marks=marks)

def get_test_repo(base, case):
    repo_archive = get_testdata("%s.tar.bz2" % case.repo)
    repo_dir = base / case.name
    tmp_dir = Path(tempfile.mkdtemp(dir=base))
    with tarfile.open(repo_archive, "r") as tarf:
        try:
            tarf.extraction_filter = tarfile.fully_trusted_filter
        except AttributeError:
            pass
        tarf.extractall(path=tmp_dir)
    (tmp_dir / case.repo).rename(repo_dir)
    tmp_dir.rmdir()
    repo = CountingGitRepo(repo_dir)
    if case.branch:
        repo._exec("git checkout %s" % case.branch)
    if case.dirty:
        (repo_dir / "_taint").touch(exist_ok=False)
        repo._exec("git add _taint")
    return repo


@pytest.fixture(scope="module")
def tmpdir():
    path = Path(tempfile.mkdtemp(prefix="git-props-test-"))
    yield path
    if _cleanup:
        shutil.rmtree(path)

@pytest.fixture(scope="module", params=get_test_cases())
def repo_case(tmpdir, request):
    case = request.param
    return case._replace(repo=get_test_repo(tmpdir, case))


def pytest_addoption(parser):
    parser.addoption("--no-cleanup", action="store_true", default=False,
                     help="do not clean up temporary data after the test.")

def pytest_configure(config):
    global _cleanup
    _cleanup = not config.getoption("--no-cleanup")

def pytest_report_header(config):
    """Add information on the package version used in the tests.
    """
    modpath = Path(gitprops.__file__).resolve().parent
    return [ "gitprops: %s" % (gitprops.__version__),
             "          %s" % (modpath)]
