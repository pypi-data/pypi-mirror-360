"""Test command line interface.
"""

from itertools import zip_longest
import os
import re
import subprocess
import sys
import pytest


def test_cli_default(repo_case):
    """Calling gitprops with no arguments.
    """
    outline_re = re.compile(r"^(\S+):\s+(\S+)$")
    cmd = [sys.executable, "-m", "gitprops"]
    proc = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          cwd=repo_case.repo.root,
                          check=True,
                          env=dict(os.environ, LC_ALL='C'),
                          universal_newlines=True)
    outlines = proc.stdout.strip().split("\n")
    expectlines = (
        ('Release', str(repo_case.tag)),
        ('Version', str(repo_case.version)),
        ('Date', str(repo_case.date)),
    )
    for line, expect in zip_longest(outlines, expectlines):
        m = outline_re.match(line)
        assert m
        assert m.groups() == expect

def test_cli_repoarg(repo_case):
    """Same as above, but setting the repository using the --repo flag
    instead of changing the cwd.
    """
    outline_re = re.compile(r"^(\S+):\s+(\S+)$")
    cmd = [sys.executable, "-m", "gitprops",
           "--repo", str(repo_case.repo.root)]
    proc = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          check=True,
                          env=dict(os.environ, LC_ALL='C'),
                          universal_newlines=True)
    outlines = proc.stdout.strip().split("\n")
    expectlines = (
        ('Release', str(repo_case.tag)),
        ('Version', str(repo_case.version)),
        ('Date', str(repo_case.date)),
    )
    for line, expect in zip_longest(outlines, expectlines):
        m = outline_re.match(line)
        assert m
        assert m.groups() == expect

def test_cli_release(repo_case):
    """Request release using the query argument.
    """
    cmd = [sys.executable, "-m", "gitprops", "release"]
    proc = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          cwd=repo_case.repo.root,
                          check=True,
                          env=dict(os.environ, LC_ALL='C'),
                          universal_newlines=True)
    assert proc.stdout.strip() == str(repo_case.tag)

def test_cli_version(repo_case):
    """Request version using the query argument.
    """
    cmd = [sys.executable, "-m", "gitprops", "version"]
    proc = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          cwd=repo_case.repo.root,
                          check=True,
                          env=dict(os.environ, LC_ALL='C'),
                          universal_newlines=True)
    assert proc.stdout.strip() == str(repo_case.version)

def test_cli_date(repo_case):
    """Request date using the query argument.
    """
    cmd = [sys.executable, "-m", "gitprops", "date"]
    proc = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          cwd=repo_case.repo.root,
                          check=True,
                          env=dict(os.environ, LC_ALL='C'),
                          universal_newlines=True)
    assert proc.stdout.strip() == str(repo_case.date)
