"""Test module gitprops.version
"""

import datetime
import packaging.version
import pytest
from gitprops.version import Version


@pytest.mark.parametrize(("vstr", "checks"), [
    ("4.11.1", [
        (lambda v: v == "4.11.1", True),
        (lambda v: v < "4.11.1", False),
        (lambda v: v > "4.11.1", False),
        (lambda v: v < "5.0.0", True),
        (lambda v: v > "4.11.0", True),
        (lambda v: v > "4.9.3", True),
        (lambda v: v == Version("4.11.1"), True),
    ]),
    ("5.0.0a1", [
        (lambda v: v == "5.0.0", False),
        (lambda v: v < "5.0.0", True),
        (lambda v: v > "4.11.1", True),
        (lambda v: v == "5.0.0a1", True),
        (lambda v: v < "5.0.0a2", True),
        (lambda v: v < "5.0.0b1", True),
    ]),
])
def test_version(vstr, checks):
    """Test class Version.
    """
    version = Version(vstr)
    for check, res in checks:
        assert check(version) == res

def test_version_set():
    s = set()
    s.add(Version("1.0"))
    s.add(Version("1.0.1"))
    assert len(s) == 2
    s.add(Version("1.0.0"))
    assert len(s) == 2
    assert Version("1") in s
    assert Version("1.0") in s
    assert Version("1.0.0") in s
    assert Version("1.0.1") in s
    assert Version("1.0.0.0") in s

@pytest.mark.parametrize(("version, count, node, dirty, expected"), [
    pytest.param(None, 0, None, False,
                 '0.1.dev0', id='0.0'),
    pytest.param(None, 0, None, True,
                 '0.1.dev0+d%(today)s', id='0.0+d'),
    pytest.param(None, 5, 'g784361a', False,
                 '0.1.dev5+g784361a', id='0.0.dev5'),
    pytest.param(None, 5, 'g784361a', True,
                 '0.1.dev5+g784361a.d%(today)s', id='0.0.dev5+d'),
    pytest.param(Version('1.0'), 0, 'g784361a', False,
                 '1.0', id='1.0'),
    pytest.param(Version('1.0'), 0, 'g784361a', True,
                 '1.0+d%(today)s', id='1.0+d'),
    pytest.param(Version('1.0'), 5, 'g784361a', False,
                 '1.1.dev5+g784361a', id='1.0.dev5'),
    pytest.param(Version('1.0'), 5, 'g784361a', True,
                 '1.1.dev5+g784361a.d%(today)s', id='1.0.dev5+d'),
    pytest.param(Version('1.0.0'), 5, 'g784361a', False,
                 '1.0.1.dev5+g784361a', id='1.0.0.dev5'),
    pytest.param(Version('1.0.0a1'), 5, 'g784361a', False,
                 '1.0.0a2.dev5+g784361a', id='1.0.0a1.dev5'),
    pytest.param(Version('1.0.0b2'), 5, 'g784361a', False,
                 '1.0.0b3.dev5+g784361a', id='1.0.0b2.dev5'),
    pytest.param(Version('1.0.0rc1'), 5, 'g784361a', False,
                 '1.0.0rc2.dev5+g784361a', id='1.0.0rc1.dev5'),
    pytest.param(Version('1.0.0.post1'), 5, 'g784361a', False,
                 '1.0.1.dev5+g784361a', id='1.0.0.dev5+p'),
    pytest.param(Version('1.0.0+abc'), 5, 'g784361a', False,
                 '1.0.1.dev5+g784361a', id='1.0.0.dev5+l'),
])
def test_build_version(version, count, node, dirty, expected):
    subst = {'today': datetime.date.today().strftime("%Y%m%d")}
    expected = expected % subst
    new_ver = Version.build_version(version, count, node, dirty)
    assert new_ver == expected
