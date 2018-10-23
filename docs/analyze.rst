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

This will print a summary of the simulations you ran to the terminal. You can do this anytime
you like and check the status of your simulations even if they haven't completed yet.
The printed results look like this::

  +--------------------------+---------+----------+------------------+-------+--------+----------+
  | module                   |   nodes |   ns/day |   run time [min] | gpu   | host   |   ncores |
  |--------------------------+---------+----------+------------------+-------+--------+----------|
  | gromacs/2016.4-plumed2.3 |       1 |   99.102 |               15 | True  | draco  |       24 |
  | gromacs/2016.4-plumed2.3 |       2 |  161.454 |               15 | True  | draco  |       48 |
  | gromacs/2016.4-plumed2.3 |       3 |        ? |               15 | True  | draco  |       72 |
  | gromacs/2016.4-plumed2.3 |       4 |  181.614 |               15 | True  | draco  |       96 |
  +--------------------------+---------+----------+------------------+-------+--------+----------+

The results above showcases that MDBenchmark displays jobs that have not
finished, started or crashed with a question mark (?).

Saving a CSV file
-----------------
Once your runs have completed you can write an output CSV file for further processing and
plotting.
You can define the name of the output CSV file with the ``-s`` or ``--save-csv`` option::

  mdbenchmark analyze --output-name my_benchmark_results.csv

Narrow down results to a specific benchmark
-------------------------------------------

Similar to the submission of benchmarks, you can use the ``--directory`` option
to narrow down the performance analysis to a specific path of benchmarks or a
single benchmark::

  mdbenchmark analyze --directory draco_gromacs/2018.2

  .. warning::

   The following section is for users still using versions older than 2.0.
   We advise all users to switch to a newer version as the new ``mdbenchmark plot`` functionality
   greatly increases usability and fixes many existing issues with plotting.
   This will be discontinued in future versions.

Plotting of benchmark results
-----------------------------

MDBenchmark provides a quick and simple way to plot the results of the
benchmarks, giving you a ``.pdf`` file as output. To generate a plot simply use
the ``--plot`` option::

  mdbenchmark analyze --plot


Plot the number of cores
------------------------

You can customize the top of your plot with the ``--ncores`` option. It accepts
an integer value, referring to the number of cores per node. If the option is
not given, MDBenchmark will try to read this information from the log file.
