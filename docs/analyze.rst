Analysis of benchmarks
======================

As soon as the benchmarks have been submitted you can request a summary of the
current performance. If a job has not yet finished, not yet started or crashed,
MDBenchmark notifies you and marks the affected benchmarks accordingly.

Retrieving the results
----------------------

The benchmark results can be retrieved immediately after they have been
submitted, even if the jobs have not yet started. To do this, simply run::

  mdbenchmark analyze

This will do two things for you:

1. Print the current performance results for all benchmarks found recursively in the current directory.
2. Save the above performance results to a ``.csv`` file.

The printed results look like this::

                         module  nodes  ns/day  run time [min]    gpu        host  ncores
    0  gromacs/2016.4-plumed2.3      1  10.878              15  False       draco      32
    1  gromacs/2016.4-plumed2.3      2   21.38              15  False       draco      64
    2  gromacs/2016.4-plumed2.3      3  34.033              15  False       draco      96
    3  gromacs/2016.4-plumed2.3      4       ?              15  False       draco       ?
    4  gromacs/2016.4-plumed2.3      5   51.71              15  False       draco     160

The results above showcases that MDBenchmark displays jobs that have not
finished, started or crashed with a question mark (?).

Defining a name for the CSV file
--------------------------------

You can define the name of the output CSV file with the ``-o`` or ``--output-name`` option::

  mdbenchmark analyze --output-name my_benchmark_results.csv

Narrow down results to a specific benchmark
-------------------------------------------

Similar to the submission of benchmarks, you can use the ``--directory`` option
to narrow down the performance analysis to a specific path of benchmarks or a
single benchmark::

  mdbenchmark analyze --directory draco_gromacs/2018.2

Plotting of benchmark results
-----------------------------

MDBenchmark provides a quick and simple way to plot the results of the
benchmarks, giving you a ``.pdf`` file as output. To generate a plot simply use
the ``--plot`` option::

  mdbenchmark analyze --plot

.. warning::

  The plotting function currently only allows to plot CPU and GPU benchmark from
  the same module, and also assumes that benchmarks were always performed with
  CPUs. This behavior will be fixed in a future release. If you want to compare
  different modules with each other, either use the ``--directory`` option to
  generate separate plots or create your own plot from the provided CSV file.

Plot the number of cores
------------------------

You can customize the top of your plot with the ``--ncores`` option. It accepts
an integer value, referring to the number of cores per node. If the option is
not given, MDBenchmark will try to read this information from the log file.
