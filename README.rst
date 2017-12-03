===================================
  MDBenchmark GROMACS simulations
===================================

.. image:: https://travis-ci.org/bio-phys/MDBenchmark.svg?branch=master
   :target: https://travis-ci.org/bio-phys/MDBenchmark
.. image:: https://codecov.io/gh/bio-phys/MDBenchmark/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/bio-phys/MDBenchmark

Quickly generate, start and analyze benchmarks for GROMACS simulations. Below is
an example of the scaling plots you can generate quickly with MDBenchmark.

.. image:: runtimes.png


Installation
============

You can install MDBenchmark via pip:

.. code::

    pip install mdbenchmark

If you are using conda:

.. code::

    conda install -c conda-forge mdbenchmark

Usage
=====

After installation, the ``mdbenchmark`` command should be available to you
globally. If you have installed the package in a virtual environment, make sure
to activate that first!

Generate 10 benchmarks for our system with the GROMACS module ``gromacs/5.1.4-plumed2.3``.

.. code::

    mdbenchmark generate --name protein --module 5.1.4-plumed2.3 --max-nodes 10

The naming of the GROMACS module assumes that you refer to the GROMACS module
you are using. On our clusters this is always ``gromacs/VERSION``.

To run benchmarks on GPUs add the ``--gpu`` flag:

.. code::

    mdbenchmark generate --name protein --module 5.1.4-plumed2.3 --max-nodes 10 --gpu

You can also create benchmarks for different versions off GROMACS:

.. code::

    mdbenchmark generate --name protein --module 5.1.4-plumed2.3 --module 2016.4-plumed2.3 --max-nodes 10 --gpu

After you generated all the benchmarks, you can start them at once:

.. code::

    mdbenchmark start

When the benchmark simulations have finished, you can run the analysis to
produce a ``CSV`` output file or a plot for direct usage (via ``--plot`` option).

.. code::

    mdbenchmark analyze

Defining Host Templates
=======================

It is possible to define your own host templates in addition to the ones shipped
with the package. A template file should have the same filename as the UNIX
command ``hostname`` returns to be detected automatically. You can also specify
the exact template you want to use with ``--host``.

Here is an example template from for the MPG cluster ``hydra``.

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

MDBenchmark provides the following values to a template

- **name**: name of benchmark
- **gpu**: boolean if GPUs are requested
- **module**: module to load
- **n_nodes**: number of nodes to run on
- **time**: program run-time in minutes
- **formatted_time**: queuing runtime in human readable format (HH:MM:SS)

To ensure correct termination of jobs ``formatted_time`` is 5 minutes longer
then ``time``.

MDBenchmark searches for user templates in the `xdg`_ config folders defined by
``XDG_CONFIG_HOME`` and ``XDG_CONFIG_DIRS`` which by default are
``$HOME/.config/MDBenchmark`` and ``/etc/xdg/MDBenchmark`` respectively. If the
variable ``MDBENCHMARK_TEMPLATES`` is set, the script will also search in that
directory.

MDBenchmark will first search in ``XDG_CONFIG_HOME`` and ``XDG_CONFIG_DIRS`` for a
suitable template file. This means it is possible to overwrite system-wide
installed templates or templates shipped with the package.

.. _xdg: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
