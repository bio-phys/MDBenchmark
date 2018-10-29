============================================
  Benchmark molecular dynamics simulations
============================================

.. image:: https://img.shields.io/pypi/v/mdbenchmark.svg
    :target: https://pypi.python.org/pypi/mdbenchmark

.. image:: https://anaconda.org/conda-forge/mdbenchmark/badges/version.svg
    :target: https://anaconda.org/conda-forge/mdbenchmark

.. image:: https://img.shields.io/pypi/l/mdbenchmark.svg
    :target: https://pypi.python.org/pypi/mdbenchmark

.. image:: https://travis-ci.org/bio-phys/MDBenchmark.svg?branch=develop
    :target: https://travis-ci.org/bio-phys/MDBenchmark

.. image:: https://readthedocs.org/projects/mdbenchmark/badge/?version=latest&style=flat
    :target: https://mdbenchmark.readthedocs.io/en/latest/

.. image:: https://codecov.io/gh/bio-phys/MDBenchmark/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/bio-phys/MDBenchmark

.. image:: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square
    :target: http://makeapullrequest.com

.. image:: https://zenodo.org/badge/112506401.svg
    :target: https://zenodo.org/badge/latestdoi/112506401

---------------

**MDBenchmark** — quickly generate, start and analyze benchmarks for your molecular dynamics simulations.

MDBenchmark is a tool to squeeze the maximum out of your limited computing
resources. It tries to make it as easy as possible to set up systems on varying
numbers of nodes and compare their performances to each other.

You can also create a plot to get a quick overview of the possible performance
(and also show of to your friends)! The plot below shows the performance of a
molecular dynamics system on up to five nodes with and without GPUs.

.. image:: https://raw.githubusercontent.com/bio-phys/MDBenchmark/master/docs/_static/runtimes.png


Installation
============

You can install ``mdbenchmark`` via ``pip``, ``conda`` or ``pipenv``:

pip
---

.. code::

   pip install mdbenchmark

conda
-----

.. code::

   conda install -c conda-forge mdbenchmark

pipenv
------

.. code::

   pipenv install mdbenchmark

After installation MDBenchmark is accessible on your command-line via ``mdbenchmark``::

    $ mdbenchmark
    Usage: mdbenchmark [OPTIONS] COMMAND [ARGS]...

    Generate, run and analyze benchmarks of molecular dynamics simulations.

    Options:
    --version  Show the version and exit.
    --help     Show this message and exit.

    Commands:
    analyze   Analyze benchmarks and print the performance...
    generate  Generate benchmarks for molecular dynamics...
    plot      Generate plots showing the benchmark...
    submit    Submit benchmarks to queuing system.

Features
========

- Generates benchmarks for GROMACS and NAMD simulations (contributions for other MD engines are welcome!).
- Automatically detects the queuing system on your high-performance cluster and submits jobs accordingly.
- Grabs performance from the output logs and creates a fancy plot.
- Benchmarks systems on CPUs and/or GPUs.

Short usage reference
=====================

The following shows a short usage reference for MDBenchmark. Please consult the
`documentation`_ for a complete guide.

Benchmark generation
--------------------

Assuming you want to benchmark GROMACS version 2018.3 and your TPR file is
called ``protein.tpr``, run the following command::

  mdbenchmark generate --name protein --module gromacs/2018.3

To run benchmarks on GPUs simply add the ``--gpu`` flag::

  mdbenchmark generate --name protein --module gromacs/2018.3 --gpu

Benchmark submission
--------------------

After you generated your benchmarks, you can submit them at once::

  mdbenchmark submit

Benchmark analysis
------------------

As soon as the benchmarks have been submitted you can run the analysis via
``mdbenchmark analyze``. Systems that have not finished yet will be marked with a question mark (``?``). You can save the performance results to a CSV file and subsequently create a plot from the data::

    # Print performance results to console and save them to a file called results.csv 
    mdbenchmark analyze --save-csv results.csv
    
    # Create a plot from the results present in the file results.csv
    mdbenchmark plot --csv results.csv

Contributing
============

Contributions to the project are welcome! Information on how to contribute to
the project can be found in `CONTRIBUTING.md`_ and `DEVELOPER.rst`_.

.. _documentation: https://mdbenchmark.readthedocs.io/en/latest/
.. _CONTRIBUTING.md: https://github.com/bio-phys/MDBenchmark/blob/master/.github/CONTRIBUTING.md
.. _DEVELOPER.rst: https://github.com/bio-phys/MDBenchmark/blob/master/DEVELOPER.rst
