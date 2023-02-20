Plotting of benchmarks
======================

After generating a CSV file with ``mdbenchmark analyze`` you can plot the results. In the following we describe how to use ``mdbenchmark plot``.

.. note::
   Make sure you wrote a CSV file using ``mdbenchmark analyze --save-csv``. Versions before ``2.0`` generated this file automatically, but this is
   no longer the default behavior.

Plotting a single CSV
---------------------

You can plot your benchmarks from a single CSV file, if you saved the data beforehand::

   mdbenchmark plot --csv data.csv

Plotting multiple CSV files
---------------------------

It is also possible to create one plot from multiple CSV files. To do this simply call the ``--csv`` option multiple times.::

   mdbenchmark plot --csv data1.csv --csv data2.csv

This will plot all data from the benchmark results found in the given files. These can be filtered using the options detailed below. All filters are applied to data in all CSV files collectively.

Output options and file formats
-------------------------------

You can set the output name for the generate plot using the ``--ouput-name`` option. If no name is given, the current date and time will be used as a file name. To generate a plot with the filename ``my_benchmark_plot``, simply run::

   mdbenchmark plot --output-name my_benchmark_plot

You can also specify a filetype with the ``--output-format`` option. If the option is not specified, a PNG file will be generated.
Supports file formats are ``png``, ``pdf``, ``svg`` and ``ps``. To set the file format to PDF, run::

   mdbenchmark plot --output-format pdf

Filter what to plot
-------------------

To filter your data from the given CSV file(s) you can use the following commands. These can be combined as you like.

Exclude CPU or GPU benchmarks from plots
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default both GPU and CPU data will be plotted. To create a plot without the GPU benchmarks run::

   mdbenchmark plot --no-gpu

To create a plot without CPU benchmarks run::

   mdbenchmark plot --no-cpu

Filter by MD engine
~~~~~~~~~~~~~~~~~~~

If you have run benchmarks for different MD engines, but want to only plot a subset of these, you can do so with the ``--module`` option. For example, if you wanted to plot all benchmarks for the two modules ``gromacs/2018.3`` and ``gromacs/2016.4``, run:: 

   mdbenchmark plot --module gromacs/2018.3 --module gromacs/2016.4

Filter by job template
~~~~~~~~~~~~~~~~~~~~~~

It is possible to filter your benchmarks by the job template that was used for any given benchmark with the ``--template`` option. To only plot benchmarks that were run with the ``draco`` job template, run::

   mdbenchmark plot --template draco

.. note::
   Both ``--template`` and ``--host`` may be used interchangeably. While some users might think of job templates as one specific template for their  cluster, others might think of them as a bundle of templates with different settings for the same cluster. Either view is correct, and thus we provide both options, but prefer ``--template``.

Changing axis labels from nodes to cores
----------------------------------------

To change the x-axis label from number of nodes to number of cores you can run::

   mdbenchmark plot --plot-cores

Hiding the optimal scaling
--------------------------

To create a plot without any optimal scaling graph, use the ``--no-fit`` option::

  mdbenchmark plot --no-fit

Changing font size
------------------

Font size can be adjusted with the ``--font-size`` option. The default is ``16pt``::

  mdbenchmark plot --font-size 16

Adjusting plot resolution (DPI)
-------------------------------

The plot resolution can be changed with the ``--dpi`` option. The default ist ``300``::

  mdbenchmark plot --dpi 300

Customizing ticks on the x-axis
-------------------------------

It is possible to change the frequence of ticks on the x-axis. To do this, call the ``--xtick-step`` option::

  mdbenchmark plot --xtick-step 1

The default value for ``--xtick-step`` depends on the data you want to plot:

- ``--xtick-step=1``, if you plot less than 19 benchmarks
- ``--xtick-step=2``, if you plot more than 18 benchmarks
- ``--xtick-step=3`` if you plot the number of cores and, more than 10 benchmarks or the first number of cores is bigger than 100

Removing the watermark
----------------------

By default a small watermark will be placed in the top left corner of every plot. To disable this, use the ``--no-watermark`` option::

  mdbenchmark plot --no-watermark

You are free to use your plots with and without the watermark, whereever you like, but we kindly ask you to cite our `latest DOI`_ from Zenodo. In this way, more people will notice MDBenchmark and start optimizing their use of high performance computing resources.

.. _latest DOI: https://zenodo.org/record/1156082
