2.0.1 (2020-03-04)
==================

Features
--------

- Add GPUs to cobra template. (`#142 <https://github.com/bio-phys/MDBenchmark/issues/142>`_)
- Lower startup time of the CLI. (`#153 <https://github.com/bio-phys/MDBenchmark/issues/153>`_)


Bugfixes
--------

- Already submitted benchmarks are now hidden in the summary of ``mdbenchmark submit``. (`#139 <https://github.com/bio-phys/MDBenchmark/issues/139>`_)
- Plotting will now work, even when some benchmarks are unfinished. (`#140 <https://github.com/bio-phys/MDBenchmark/issues/140>`_)
- Restarting benchmarks with ``mdbenchmark submit --force`` works again. (`#141 <https://github.com/bio-phys/MDBenchmark/issues/141>`_)


Misc
----

- Use ``poetry`` to manage Python dependencies and the project in general. (`#155 <https://github.com/bio-phys/MDBenchmark/issues/155>`_)


2.0.0 (2018-10-29)
==================

Features
--------

- Updated plotting interface. ``mdbenchmark analyze --plot`` is not deprecated. Use ``mdbenchmark plot`` instead.

  The new workflow for plotting data is as follows:

  1) Use ``mdbenchmark analyze --save-csv results.csv`` to generate a CSV output file.
  2) Use ``mdbenchmark plot --csv results.csv`` to plot the data.

  Consult ``mdbenchmark <command> --help`` for options to filter your data accordingly. (`#52 <https://github.com/bio-phys/MDBenchmark/issues/52>`_)
- ``mdbenchmark generate`` now accepts ``--cpu`` / ``--no-cpu`` and ``--gpu`` / ``--no-gpu``. The default is ``--cpu`` and ``--no-gpu``. (`#69 <https://github.com/bio-phys/MDBenchmark/issues/69>`_)
- Added user prompts to ``mdbenchmark generate`` and ``mdbenchmark submit``. (`#90 <https://github.com/bio-phys/MDBenchmark/issues/90>`_)
- Added ``--yes`` flag to ``mdbenchmark generate`` and ``mdbenchmark submit`` to bypass user prompt. (`#90 <https://github.com/bio-phys/MDBenchmark/issues/90>`_)
- Added ``-nc`` and ``-ng`` options to ``mdbenchmark generate``. These are short hand for ``--no-cpu`` and ``--no-gpu``, respectively. (`#93 <https://github.com/bio-phys/MDBenchmark/issues/93>`_)
- Added template for MPCDF cluster ``cobra``. (`#104 <https://github.com/bio-phys/MDBenchmark/issues/104>`_)
- Added ``--template`` and ``-t`` option to ``mdbenchmark generate``, to specify a job template. The ``--host`` option still works. (`#106 <https://github.com/bio-phys/MDBenchmark/issues/106>`_)
- Standarize the CLI options across all ``mdbenchmark`` calls. (`#107 <https://github.com/bio-phys/MDBenchmark/issues/107>`_)
- Added ``mdbenchmark plot --dpi`` option to change the plot DPI. (`#108 <https://github.com/bio-phys/MDBenchmark/issues/108>`_)
- Added ``mdbenchmark plot --font-size`` to change the plot font size. (`#108 <https://github.com/bio-phys/MDBenchmark/issues/108>`_)
- Linear scaling fit can now be hidden with ``--no-fit``. (`#108 <https://github.com/bio-phys/MDBenchmark/issues/108>`_)
- Updated ``ylim``, ``xtick``  and ``ytick`` defaults. The steps for ``xtick`` can be overwritten with ``mdbenchmark plot --xtick-step``. (`#108 <https://github.com/bio-phys/MDBenchmark/issues/108>`_)
- Added a watermark in the top left corner for every plot. Can be easiliy disabled with ``mdbenchmark plot --no-watermark``. (`#108 <https://github.com/bio-phys/MDBenchmark/issues/108>`_)
- ``mdbenchmark analyze`` no longer writes CSV files by default. ``--save-csv`` flag added to write csv files. (`#119 <https://github.com/bio-phys/MDBenchmark/issues/119>`_)
- Added ``mdbenchmark generate --job-name`` to change the job name submitted to the queuing system. (`#125 <https://github.com/bio-phys/MDBenchmark/issues/125>`_)


Bugfixes
--------

- Fixed a bug where benchmark creation with files ending in ``.namd`` did not work. (`#124 <https://github.com/bio-phys/MDBenchmark/issues/124>`_)
- Fixed a bug where benchmark creation would fail when the input file was not in the current directory. (`#124 <https://github.com/bio-phys/MDBenchmark/issues/124>`_)


Misc
----

- Replaced ``mdsynthesis`` with ``datreant`` and upgraded to the new ``datreant>=1.0`` format. (`#110 <https://github.com/bio-phys/MDBenchmark/issues/110>`_)


1.3.3 (2018-09-24)
==================

Bugfixes
--------

- Fixed a bug where the user was unable to call ``mdbenchmark analyze --plot``. (`#86 <https://github.com/bio-phys/MDBenchmark/issues/86>`_)


1.3.2 (2018-07-20)
==================

Bugfixes
--------

- We now print all rows when running ``mdbenchmark analyze``. (`#68 <https://github.com/bio-phys/MDBenchmark/issues/68>`_)
- Suppress UserWarning caused by ``MDAnalysis==0.18``. (`#71 <https://github.com/bio-phys/MDBenchmark/issues/71>`_)


Misc
----

- Added new error message when running ``mdbenchmark generate [...] --skip-validation`` without providing a supported MD engine. (`#74 <https://github.com/bio-phys/MDBenchmark/issues/74>`_)


1.3.1 (2018-05-17)
==================

Bugfixes
--------

- Module name validation is now performed case insensitive. (`#61 <https://github.com/bio-phys/MDBenchmark/issues/61>`_)


Misc
----
- Consolidate common functions from ``mdengines.gromacs`` and ``mdengines.namd`` into ``mdengines.utils``, removing code duplication. (`#57 <https://github.com/bio-phys/MDBenchmark/issues/57>`_)
- Refactor unit tests. Make everything more concise and use some more pytest functionality. (`#58 <https://github.com/bio-phys/MDBenchmark/issues/58>`_)


1.3.0 (2018-04-08)
==================

Features
--------

- Add functionality to perform benchmarks with NAMD. (`#29 <https://github.com/bio-phys/MDBenchmark/issues/29>`_)
- Consolidated internal API to output messages to the console. (`#42 <https://github.com/bio-phys/MDBenchmark/issues/42>`_)
- Module name is now validated against available modules on host. Can be
  skipped with ``--skip-validation``. (`#49 <https://github.com/bio-phys/MDBenchmark/issues/49>`_)


Bugfixes
--------

- The option ``--min-nodes`` needs to be bigger than ``--max-nodes``. (`#46 <https://github.com/bio-phys/MDBenchmark/issues/46>`_)
- Fixed edge-case in input filename parsing. (`#54 <https://github.com/bio-phys/MDBenchmark/issues/54>`_)


Misc
----

- Fixed display of the number of benchmarks to-be generated. (`#46 <https://github.com/bio-phys/MDBenchmark/issues/46>`_)


1.2.0 (2018-02-19)
==================

Features
--------

- Added ``Makefile`` to the project. Updated default strings. (`#36 <https://github.com/bio-phys/MDBenchmark/issues/36>`_)
- GROMACS .tpr files can now be referenced with and without the file extension. (`#32 <https://github.com/bio-phys/MDBenchmark/issues/32>`_)


Bugfixes
--------

- Fixed crash during analyze, if some simulations have not started/finished yet. (`#26 <https://github.com/bio-phys/MDBenchmark/issues/26>`_)
- Suppress FutureWarning caused by ``h5py``. (`#35 <https://github.com/bio-phys/MDBenchmark/issues/35>`_)

Improved Documentation
----------------------

- Update and add more unit tests. (`#36 <https://github.com/bio-phys/MDBenchmark/issues/36>`_)


1.1.1 (2018-01-20)
==================

Misc
----
- Show benchmark png on PyPI.


1.1.0 (2018-01-19)
==================

Features
--------

- Enable to run on macOS. (`#10 <https://github.com/bio-phys/MDBenchmark/issues/10>`_)
- Read number of cores from simulation log. (`#19 <https://github.com/bio-phys/MDBenchmark/issues/19>`_)


Bugfixes
--------

- Ensure MPI environment is loaded on draco after a purge. (`#17 <https://github.com/bio-phys/MDBenchmark/issues/17>`_)


Improved Documentation
----------------------

- Fix readme usage docs for the module argument. (`#20 <https://github.com/bio-phys/MDBenchmark/issues/20>`_)


1.0.1 (2017-12-03)
==================

Misc
----

- Fixup ``MANIFEST.in``. (`#9 <https://github.com/bio-phys/MDBenchmark/issues/9>`_)


1.0.0 (2017-12-03)
==================

Initial release.
