v1.2.2 (2025-07-07)
===================

Bugfixes
--------

- Fix bug where draft CHANGELOG did not render when running `ddt changelog`. (`#5 <https://bitbucket.org/dkistdc/dkist-dev-tools/pull-requests/5>`__)


v1.2.1 (2025-06-26)
===================

Documentation
-------------

- Update README to show how to get access to `towncrier` binaries when installing `dkist-dev-tools` with `pipx`


v1.2.0 (2025-06-23)
===================

Features
--------

- Add ability to check changelog compliance with the `check changelog` subcommand. (`#4 <https://bitbucket.org/dkistdc/dkist-dev-tools/pull-requests/4>`__)
- Add `changelog` subcommand that automatically renders the CHANGELOG (and maybe SCIENCE_CHANGELOG) with towncrier. (`#4 <https://bitbucket.org/dkistdc/dkist-dev-tools/pull-requests/4>`__)


Misc
----

- Add code coverage badge to README.rst. (`#3 <https://bitbucket.org/dkistdc/dkist-dev-tools/pull-requests/3>`__)


v1.1.0 (2025-03-13)
===================

Features
--------

- Check that a repo freeze is being done on a repo that should be frozen. (This check can be turned off). (`#2 <https://bitbucket.org/dkistdc/dkist-dev-tools/pull-requests/2>`__)


v1.0.0 (2025-02-05)
===================

Features
--------

- Add tools for freezing dependencies of instrument repos and checking that the freeze happened. (`#1 <https://bitbucket.org/dkistdc/dkist-dev-tools/pull-requests/1>`__)
