"""Test errors calling toplevel function at package level.
"""

import subprocess
import pytest
from gitprops import get_version, get_last_release, get_date

_orig_subprocess_run = subprocess.run

def git_fail_run(cmd, **kwargs):
    """A mockup version of subprocess.run that raises FileNotFoundError
    whenever the first argument in cmd is 'git'.
    """
    if cmd[0] == "git":
        raise FileNotFoundError(2, "No such file or directory: 'git'")
    else:
        return _orig_subprocess_run(cmd, **kwargs)

def test_nogit_error_get_version(monkeypatch):
    """Test the error condition that the git executable is not found.
    """
    monkeypatch.setattr(subprocess, "run", git_fail_run)
    with pytest.raises(LookupError):
        get_version()

def test_nogit_error_get_last_release(monkeypatch):
    """Test the error condition that the git executable is not found.
    """
    monkeypatch.setattr(subprocess, "run", git_fail_run)
    with pytest.raises(LookupError):
        get_last_release()

def test_nogit_error_get_date(monkeypatch):
    """Test the error condition that the git executable is not found.
    """
    monkeypatch.setattr(subprocess, "run", git_fail_run)
    with pytest.raises(LookupError):
        get_date()

def test_norepo_error_get_version(monkeypatch):
    """Test the error condition that there is no git repository.
    """
    with pytest.raises(LookupError):
        get_version(root='/')

def test_norepo_error_get_last_release(monkeypatch):
    """Test the error condition that there is no git repository.
    """
    with pytest.raises(LookupError):
        get_last_release(root='/')

def test_norepo_error_get_date(monkeypatch):
    """Test the error condition that there is no git repository.
    """
    with pytest.raises(LookupError):
        get_date(root='/')
