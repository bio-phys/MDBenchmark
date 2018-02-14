===================================
  Benchmark GROMACS simulations
===================================

.. image:: https://img.shields.io/pypi/v/mdbenchmark.svg
    :target: https://pypi.python.org/pypi/mdbenchmark

.. image:: https://img.shields.io/pypi/l/mdbenchmark.svg
    :target: https://pypi.python.org/pypi/mdbenchmark

.. image:: https://travis-ci.org/bio-phys/MDBenchmark.svg?branch=master
    :target: https://travis-ci.org/bio-phys/MDBenchmark

.. image:: https://codecov.io/gh/bio-phys/MDBenchmark/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/bio-phys/MDBenchmark

.. image:: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square
    :target: http://makeapullrequest.com

.. image:: https://zenodo.org/badge/112506401.svg
   :target: https://zenodo.org/badge/latestdoi/112506401

---------------

**MDBenchmark** — quickly generate, start and analyze benchmarks for GROMACS simulations.

MDBenchmark is a tool to squeeze the maximum out of your limited computing
resources. It tries to make it as easy as possible to set up systems on varying
numbers of nodes and compare their performances to each other.

You can also create a plot to get a quick overview of the possible performance
(and also show of to your friends)! The plot below shows the performance of an
MD system on up to five nodes with and without GPUs.

.. image:: https://raw.githubusercontent.com/bio-phys/MDBenchmark/master/runtimes.png


Installation
============

You can install ``mdbenchmark`` via ``pip`` or ``conda``:

.. code::

    $ pip install mdbenchmark

.. code::

    $ conda install -c conda-forge mdbenchmark

Usage with a virtual environments
--------------------------------

We recommend to install the package inside a `conda environment`_. This can
easily be done with ``conda``. The following commands create an environment
called ``benchmark`` and then installs ``mdbenchmark`` and its dependencies.

.. code::

    $ conda create -n benchmark
    $ conda install -n benchmark -c conda-forge mdsynthesis click mdbenchmark

Before every usage of ``mdbenchmark``, you need to first activate the conda
environment. After doing this once, you can use the tool for the whole duration
of your shell session.

.. code::

   $ source activate benchmark
   # mdbenchmark should now be usable!
   $ mdbenchmark
   Usage: mdbenchmark [OPTIONS] COMMAND [ARGS]...

     Generate and run benchmark jobs for GROMACS simulations.

   Options:
     --version  Show the version and exit.
     --help     Show this message and exit.

   Commands:
     analyze   analyze finished benchmark.
     generate  Generate benchmark queuing jobs.
     submit    Start benchmark simulations.

Features
========

- Generates benchmarks for GROMACS systems (contributions for other MD systems are welcome!).
- Automatically detects the queuing system on your high-performance cluster and submits jobs accordingly.
- Grabs performance from GROMACS logs and creates a fancy plot.
- Can benchmark systems either with or without GPUs.

Usage
=====

After installation, the ``mdbenchmark`` command should be available to you
globally. If you have installed the package in a virtual environment, make sure
to activate that first!

Assuming your TPR files is called ``protein.tpr`` and want to run benchmarks
with the module ``gromacs/5.1.4-plumed2.3`` on up to ten nodes, use the
following command:

.. code::

    $ mdbenchmark generate --name protein --module gromacs/5.1.4-plumed2.3 --max-nodes 10

To run benchmarks on GPUs add the ``--gpu`` flag:

.. code::

    $ mdbenchmark generate --name protein --module gromacs/5.1.4-plumed2.3 --max-nodes 10 --gpu

You can also create benchmarks for different versions of GROMACS:

.. code::

    $ mdbenchmark generate --name protein --module gromacs/5.1.4-plumed2.3 --module gromacs/2016.4-plumed2.3 --max-nodes 10 --gpu

After you generated all benchmark systems, you can start them at once:

.. code::

    $ mdbenchmark start

As soon as the benchmark simulations have been submitted you can run the
analysis script via ``mdbenchmark analysis``. As soon as at least one system has
finished the script will produce a ``.csv`` output file or a plot for direct
usage (via the ``--plot`` option).

.. code::

    $ mdbenchmark analyze
                       gromacs  nodes  ns/day  run time [min]    gpu        host  ncores
    0  gromacs/5.1.4-plumed2.3      1  10.878              15  False       draco      32
    1  gromacs/5.1.4-plumed2.3      2   21.38              15  False       draco      64
    2  gromacs/5.1.4-plumed2.3      3  34.033              15  False       draco      96
    3  gromacs/5.1.4-plumed2.3      4  40.274              15  False       draco     128
    4  gromacs/5.1.4-plumed2.3      5   51.71              15  False       draco     160

Defining Host Templates
=======================

It is possible to define your own host templates in addition to the ones shipped
with the package. A template file should have the same filename as the UNIX
command ``hostname`` returns to be detected automatically. Otherwise you can
point MDBenchmark to a specific template by providing its name via the
``--host`` option.

Assuming you created a new host template in your home directory ``~/.config/MDBenchmark/my_custom_hostfile~~::

    $ mdbenchmark generate protein --host my_custom_hostfile --module gromacs/5.1.4-plumed2.3

Here is an example job template for the MPG cluster ``hydra``.

.. code::

    # @ shell=/bin/bash
    #
    # @ error = {{ name }}.err.$(jobid)
    # @ output = {{ name }}.out.$(jobid)
    # @ job_type = parallel
    # @ node_usage = not_shared
    # @ node = {{ n_nodes }}
    # @ tasks_per_node = 20
    {%- if gpu %}
    # @ requirements = (Feature=="gpu")
    {%- endif %}
    # @ resources = ConsumableCpus(1)
    # @ network.MPI = sn_all,not_shared,us
    # @ wall_clock_limit = {{ formatted_time }}
    # @ queue

    module purge
    module load {{ module }}

    # run {{ module }} for {{ time }} minutes
    poe gmx_mpi mdrun -deffnm {{ name }} -maxh {{ time / 60 }}

MDBenchmark passes the following variables to each template:

+----------------+---------------------------------------------------------------------+
| Value          | Description                                                         |
+================+=====================================================================+
| name           | Name of the TPR file                                                |
+----------------+---------------------------------------------------------------------+
| gpu            | Boolean that is true, if GPUs are requested                         |
+----------------+---------------------------------------------------------------------+
| module         | Name of the module to load                                          |
+----------------+---------------------------------------------------------------------+
| n_nodes        | Maximal number of nodes to run on                                   |
+----------------+---------------------------------------------------------------------+
| time           | Benchmark run time in minutes                                       |
+----------------+---------------------------------------------------------------------+
| formatted_time | Run time for the queuing system in human readable format (HH:MM:SS) |
+----------------+---------------------------------------------------------------------+

To ensure correct termination of jobs ``formatted_time`` is 5 minutes longer
than ``time``.

MDBenchmark will look for user templates in the `xdg`_ config folders defined by
the environment variables ``XDG_CONFIG_HOME`` and ``XDG_CONFIG_DIRS`` which by
default are set to ``$HOME/.config/MDBenchmark`` and ``/etc/xdg/MDBenchmark``,
respectively. If the variable ``MDBENCHMARK_TEMPLATES`` is set, the script will
also search in that directory.

MDBenchmark will first search in ``XDG_CONFIG_HOME`` and ``XDG_CONFIG_DIRS`` for
a suitable template file. This means it is possible to overwrite system-wide
installed templates or templates shipped with the package.

Contributing
============

Contributions to the project are welcome! Information on how to contribute to
the project can be found in `CONTRIBUTING.md`_ and `DEVELOPER.rst`_.

.. _conda environment: https://conda.io/docs/user-guide/tasks/manage-environments.html
.. _xdg: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
.. _CONTRIBUTING.md: https://github.com/bio-phys/MDBenchmark/blob/master/.github/CONTRIBUTING.md
.. _DEVELOPER.rst: https://github.com/bio-phys/MDBenchmark/blob/master/DEVELOPER.rst
