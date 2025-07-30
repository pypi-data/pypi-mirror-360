"""Provide class Verson
"""

import datetime
import itertools
import packaging.version


class Version(packaging.version.Version):
    """Represent a version number.

    This class extends :class:`packaging.version.Version`:

    + add class method build_version(),
    + keep the original version string and expose it in
      :attr:`~gitprops.version.Version.orig_version`,
    + add a __hash__() method,
    + add comparison with strings.

    >>> version = Version('4.11.1')
    >>> version == '4.11.1'
    True
    >>> version < '4.9.3'
    False
    >>> version = Version('5.0.0a1')
    >>> str(version)
    '5.0.0a1'
    >>> version > '4.11.1'
    True
    >>> version < '5.0.0'
    True
    >>> version == '5.0.0a1'
    True
    >>> v = Version('v1.0')
    >>> str(v)
    '1.0'
    >>> v.orig_version
    'v1.0'
    >>> v = Version('v1.01')
    >>> str(v)
    '1.1'
    >>> v.orig_version
    'v1.01'

    """

    @classmethod
    def build_version(cls, version, count, node, dirty):
        """Build a new version based on repository metadata.
        """
        # Start from a copy of the last version
        if version:
            new_version = cls(str(version))
        else:
            new_version = cls('0.1.dev0')
        _ver = new_version._version
        repl = dict()
        if dirty:
            dirtytag = datetime.date.today().strftime("d%Y%m%d")
        if count:
            # local part is build from node and dirty, boldly overwriting
            # anything that may be set here
            if dirty:
                repl['local'] = (node, dirtytag)
            else:
                repl['local'] = (node,)
            # drop post part unconditionally
            repl['post'] = None
            if _ver.dev:
                # dev part is present: increment its numerical
                # component by count
                repl['dev'] = ('dev', _ver.dev[1]+count)
            else:
                # dev part is not present: add a dev part with count as
                # numerical component and increment either the pre or the
                # release part by one
                repl['dev'] = ('dev', count)
                if _ver.pre:
                    repl['pre'] = (_ver.pre[0], _ver.pre[1]+1)
                else:
                    repl['release'] = _ver.release[0:-1] + (_ver.release[-1]+1,)
        elif dirty:
            repl['local'] = (dirtytag,)
        # apply the accumulated replacements and return the new version
        if repl:
            new_version._version = _ver._replace(**repl)
            new_version = cls(str(new_version))
        return new_version

    def __init__(self, version):
        self._orig_version = version
        super().__init__(version)

    @property
    def orig_version(self):
        return self._orig_version

    def __hash__(self):
        # strip trailing zero segments from release
        release = tuple(
            reversed(list(
                itertools.dropwhile(
                    lambda x: x == 0,
                    reversed(self._version.release),
                )
            ))
        )
        return hash(self._version._replace(release=release))

    def __lt__(self, other):
        if isinstance(other, str):
            other = type(self)(other)
        return super().__lt__(other)

    def __le__(self, other):
        if isinstance(other, str):
            other = type(self)(other)
        return super().__le__(other)

    def __eq__(self, other):
        if isinstance(other, str):
            other = type(self)(other)
        return super().__eq__(other)

    def __ge__(self, other):
        if isinstance(other, str):
            other = type(self)(other)
        return super().__ge__(other)

    def __gt__(self, other):
        if isinstance(other, str):
            other = type(self)(other)
        return super().__gt__(other)

    def __ne__(self, other):
        if isinstance(other, str):
            other = type(self)(other)
        return super().__ne__(other)
