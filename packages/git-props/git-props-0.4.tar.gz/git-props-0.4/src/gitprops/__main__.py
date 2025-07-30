"""Command line interface
"""

import argparse
import inspect
from pathlib import Path
import sys
from . import get_version, get_last_release, get_date

python = Path(sys.executable).name
package = inspect.getmodule(inspect.stack()[0].frame).__package__

argparser = argparse.ArgumentParser(prog=("%s -m %s" % (python, package)))
argparser.add_argument('--repo', type=Path, default="",
                       help="Repository path")
argparser.add_argument('query', nargs='?',
                       choices=('version', 'release', 'date'),
                       help="type of information requested")
args = argparser.parse_args()

if args.query is None:
    print("Release: %s" % get_last_release(args.repo))
    print("Version: %s" % get_version(args.repo))
    print("Date:    %s" % get_date(args.repo))
elif args.query == 'version':
    print(str(get_version(args.repo)))
elif args.query == 'release':
    print(str(get_last_release(args.repo)))
elif args.query == 'date':
    print(str(get_date(args.repo)))
else:
    assert False
