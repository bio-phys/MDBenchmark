Developer guide
###############

This document should guide you through the setup of your local developer
environment, as well as through the release process of a new version.

====================================
Setting up a development environment
====================================

Download code
-------------

First clone the repository to your local machine::

    $ git clone https://github.com/bio-phys/MDBenchmark.git

Create a virtual environment
----------------------------

If you are using ``conda``, you can easily create a `conda environment`_::

    $ conda create -n benchmark -c conda-forge mdsynthesis click
    $ source activate benchmark

Make sure to activate the environment, before trying to install the package.
Also you will need to always activate the environment before you can use the
package.

Install package
---------------

When developing python packages locally, it is advisable to install them with
the ``-e`` option. This way all changes to the code will be reflected
immediately in your local development environment::

    $ pip install -e .

=======================
Preparing pull requests
=======================

When working on some code, you are free to open a **work in progress**
(abbreviated: WIP) pull request. Others can then help you with design decisions
and point out problems with the code, while you are still working on it. This
way the development can happen in an iterative manner.

After you have finished all code for the pull request, make sure to add the
corresponding changelog files in ``./changelog/``. This
project uses ``towncrier`` to generate the ``CHANGELOG.rst`` found in the
project root.

Using ``towncrier``
-------------------

Every feature that has been added or every bug that has been fixed, requires a
separate file in the ``./changelog/`` directory (called fragments). Filenames
should start with the issue or pull request number and either end with
``.bugfix`` or ``.feature``. For some more possibilities, refer to the
`towncrier README`_.

For example, if you have opened up pull request #20 and fixed a bug in there,
the corresponding file should be named ``20.bugfix``. This file should contain a
one-line summary of what was done, as well as a reference to the issue or pull
request::

    Improved plotting functionality. Plots are even more fancy now. (PR #20)

Make sure to add every notable change into a separate fragment and commit all of
them into your pull request.

==================
Creating a Release
==================

To create a new release for PyPI and conda, you need to follow a few steps.

1. Update version
-----------------

Bump the version info in ``mdbenchmark/__init__.py``.

This project uses the `semantic versioning scheme`_.

2. Update ``CHANGELOG``
-----------------------

To update the ``CHANGELOG``, you first need to install the python package ``towncrier``::

    $ pip install towncrier

Next run ``towncrier``, which should grab all changelog files from
``./changelog/`` and add their contents to ``CHANGELOG.rst``::

    $ towncrier

You can also dry-run ``towncrier``, thus not making any changes::

    $ towncrier --draft

After ``towncrier`` has finished, the folder ``./changelog/`` should only
contain the file ``.invisible``. Also the file ``CHANGELOG.rst`` should have
been updated.

**Important:** Make sure that the version numbers inside
 ``mdbenchmark/__init__.py`` and ``CHANGELOG.rst`` match.

3. Generate dist files
----------------------

Next we need to actually build the project. The following steps were taken from
the official `python packaging guide`_.

First make sure that your ``wheel`` package is up-to-date::

    $ pip install --upgrade wheel

Next we can generate a source distribution package and universal wheel::

   $ python setup.py sdist bdist_wheel --universal

Check that the tarball inside ``./dist/`` includes all needed files (source
code, ``README.rst``, ``CHANGELOG.rst``, ``LICENSE``), !

4. Publish on GitHub
--------------------

Create a tag for the respective commit and mark it as a `release on GitHub`_::

    # Replace 1.x.x with the actual version.
    $ git commit -a version-1.x.x -m 'Version 1.x.x'
    $ git push origin version-1.x.x

5. Publishing to PyPI
---------------------

Make sure to have ``twine`` installed.

The upload should work via::

    $ twine upload dist/*

6. Publishing to ``conda-forge``
--------------------------------

After the PyPI upload, update the ``conda-forge`` recipe.

.. _conda environment: https://conda.io/docs/user-guide/tasks/manage-environments.html
.. _towncrier README: https://github.com/hawkowl/towncrier#news-fragments
.. _semantic versioning scheme: https://semver.org/
.. _python packaging guide: https://packaging.python.org/tutorials/distributing-packages/
.. _release on GitHub: https://github.com/bio-phys/MDBenchmark/releases/new
