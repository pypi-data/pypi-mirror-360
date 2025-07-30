Changelog
=========


.. _changes-0_4_0:

0.4 (2025-07-06)
~~~~~~~~~~~~~~~~

Bug fixes and minor changes
---------------------------

+ `#12`_, `#13`_: fix severe performance issues on repos with many
  tags.
+ `#14`_: Minor updates in the tool chain.

.. _#12: https://github.com/RKrahl/git-props/issues/12
.. _#13: https://github.com/RKrahl/git-props/pull/13
.. _#14: https://github.com/RKrahl/git-props/pull/14


.. _changes-0_3_0:

0.3 (2024-02-07)
~~~~~~~~~~~~~~~~

Incompatible changes
--------------------

+ `#11`_: Rename :meth:`gitprops.GitRepo.get_last_version_tag` to
  :meth:`gitprops.GitRepo.get_version_tag`.  This method now takes an
  optional argument, indicating the commit to return.

Bug fixes and minor changes
---------------------------

+ `#10`_, `#11`_: fail to detect last version tag if the corresponding
  commit has multiple version tags.

.. _#10: https://github.com/RKrahl/git-props/issues/10
.. _#11: https://github.com/RKrahl/git-props/pull/11


.. _changes-0_2_0:

0.2 (2024-01-01)
~~~~~~~~~~~~~~~~

New features
------------

+ `#2`_, `#6`_: Add a command line interface.

Bug fixes and minor changes
---------------------------

+ `#7`_, `#8`_: package level functions :func:`gitprops.get_version`,
  :func:`gitprops.get_last_release` and :func:`gitprops.get_date`
  raise :exc:`LookupError` when the git executable is not found.

Internal changes
----------------

+ `#1`_, `#5`_: Drop `setuptools_scm` in favour of `git-props`.

+ `#3`_, `#9`_: Review test suite.

.. _#1: https://github.com/RKrahl/git-props/issues/1
.. _#2: https://github.com/RKrahl/git-props/issues/2
.. _#3: https://github.com/RKrahl/git-props/issues/3
.. _#5: https://github.com/RKrahl/git-props/pull/5
.. _#6: https://github.com/RKrahl/git-props/pull/6
.. _#7: https://github.com/RKrahl/git-props/issues/7
.. _#8: https://github.com/RKrahl/git-props/pull/8
.. _#9: https://github.com/RKrahl/git-props/pull/9


.. _changes-0_1_0:

0.1 (2023-12-28)
~~~~~~~~~~~~~~~~

Initial release.
