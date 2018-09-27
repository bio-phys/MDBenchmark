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
(and also show of to your friends)! The plot below shows the performance of an
molecular dynamics system on up to five nodes with and without GPUs.

.. image:: https://raw.githubusercontent.com/bio-phys/MDBenchmark/master/runtimes.png


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

    Generate and run benchmark jobs for GROMACS simulations.

  Options:
    --version  Show the version and exit.
    --help     Show this message and exit.

  Commands:
    analyze   analyze finished benchmark.
    generate  Generate benchmark queuing jobs.
    plot      Generate plots from csv files
    submit    Start benchmark simulations.

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

Assuming you want to benchmark GROMACS version 2016.4 and your TPR file is
called ``protein.tpr``, run the following command::

  mdbenchmark generate --name protein --module gromacs/2016.4

To run benchmarks on GPUs simply add the ``--gpu`` flag::

  mdbenchmark generate --name protein --module gromacs/2016.4 --gpu

Benchmark submission
--------------------

After you generated your benchmarks, you can submit them at once::

  mdbenchmark submit

Benchmark analysis
------------------

As soon as the benchmarks have been submitted you can run the analysis via
``mdbenchmark analysis``. When at least one system has finished, the script will
produce a ``.csv`` output file or a plot for direct usage (via the ``--plot``
option).

**Note:** The plotting function currently only allows to plot a CPU and GPU
benchmark from the *same* module. This will be fixed in an upcoming version. If
you want to compare different modules with each other, either use the
``--directory`` option to generate separate plots or create your own plot from
the provided CSV file.

.. code::

    $ mdbenchmark analyze
                       gromacs  nodes  ns/day  run time [min]    gpu        host  ncores
    0  gromacs/5.1.4-plumed2.3      1  10.878              15  False       draco      32
    1  gromacs/5.1.4-plumed2.3      2   21.38              15  False       draco      64
    2  gromacs/5.1.4-plumed2.3      3  34.033              15  False       draco      96
    3  gromacs/5.1.4-plumed2.3      4  40.274              15  False       draco     128
    4  gromacs/5.1.4-plumed2.3      5   51.71              15  False       draco     160


Contributing
============

Contributions to the project are welcome! Information on how to contribute to
the project can be found in `CONTRIBUTING.md`_ and `DEVELOPER.rst`_.

.. _documentation: https://mdbenchmark.readthedocs.io/en/latest/
.. _CONTRIBUTING.md: https://github.com/bio-phys/MDBenchmark/blob/master/.github/CONTRIBUTING.md
.. _DEVELOPER.rst: https://github.com/bio-phys/MDBenchmark/blob/master/DEVELOPER.rst
