Submission of benchmarks
========================

After all benchmark systems are generated, you can also use MDBenchmark to
submit these to the queuing system on your HPC. We currently support submission
to `Slurm`_, `SGE`_ and `LoadLeveler`_.

Submitting all generated benchmarks
-----------------------------------

To submit all generated benchmarks that are recursively found starting in the
current directory, use::

  mdbenchmark submit

Submitting specific benchmarks separately
-----------------------------------------

If you do not want to submit all benchmark systems at once, you can submit them
separately with the ``--directory`` option. Simply define the relative path to
the given directory::

  mdbenchmark submit --directory draco_gromacs/2016.4-plumed2.3

Force submitting jobs that were already submitted once
------------------------------------------------------

If your jobs were already submitted, but you want to resubmit them once more,
you can do so with the ``--force`` option::

  mdbenchmark submit --force

.. _Slurm: https://en.wikipedia.org/wiki/Slurm_Workload_Manager
.. _SGE: https://en.wikipedia.org/wiki/Oracle_Grid_Engine
.. _LoadLeveler: https://en.wikipedia.org/wiki/IBM_Tivoli_Workload_Scheduler
