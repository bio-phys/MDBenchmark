Defining host templates
=======================

You can create your own host templates in addition to the ones shipped with the
MDBenchmark. We use the ``jinja2`` Python package for these host templates.
Please refer to the `official Jinja2 documentation <http://jinja.pocoo.org/>`_
for further information on formatting and functionality.

To be detected automatically, a template file must have the same filename as
returned by the UNIX command ``hostname``. If this is not the case, you can
point MDBenchmark to a specific template by providing its name via the
``--host`` option.

Assuming you created a new host template in your home directory ``~/.config/MDBenchmark/my_custom_hostfile``::

    mdbenchmark generate --host my_custom_hostfile

Sun Grid Engine (SGE)
---------------------

This example shows a HPC running SGE with 30 CPUs per node.

.. code::

  #!/bin/bash
  ### join stdout and stderr
  #$ -j y
  ### change to currend work dir
  #$ -cwd
  #$ -N {{ job_name }}
  # Number of nodes and MPI tasks per node:
  #$ -pe impi_hydra {{ 30 * n_nodes }}
  #$ -l h_rt={{ formatted_time }}

  module unload gromacs
  module load {{ module }}
  module load impi
  module load cuda

  # The below configuration was kindly provided by Dr. Klaus Reuter
  # --- edit the following two lines to configure your job ---
  {% if hyperthreading %}
  USE_HT=1                                # use hyperthreading, 0 (off) or 1 (on)
  {%- else %}
  USE_HT=0                                # use hyperthreading, 0 (off) or 1 (on)
  {%- endif %
  N_TASKS_PER_HOST={{ number_of_ranks }}  # number of MPI tasks to be started per node


  # --- no need to touch the lines below ---
  N_SLOTS_TOTAL=$NSLOTS
  N_TASKS_TOTAL=$((N_TASKS_PER_HOST*NHOSTS))
  N_SLOTS_PER_HOST=$((NSLOTS/NHOSTS))
  N_THREADS_PER_PROCESS=$((N_SLOTS_PER_HOST/N_TASKS_PER_HOST))
  N_THREADS_PER_PROCESS=$(((1+USE_HT)*N_THREADS_PER_PROCESS))
  export OMP_NUM_THREADS=$N_THREADS_PER_PROCESS
  if [ $USE_HT ]; then
      export OMP_PLACES=threads
  else
      export OMP_PLACES=cores
  fi

  # Edit again below, as you see fit

  # Run gromacs/{{ version }} for {{ time - 5 }} minutes
  mpiexec -n $N_TASKS_TOTAL -ppn $N_TASKS_PER_HOST mdrun_mpi -ntomp $N_THREADS_PER_PROCESS -v -maxh {{ time / 60 }} -resethway -noconfout -deffnm {{ name }}

Slurm
-----

The following showcases the job template for the MPCDF cluster ``draco`` using
Slurm.

.. code::

  #!/bin/bash -l
  # Standard output and error:
  #SBATCH -o ./{{ job_name }}.out.%j
  #SBATCH -e ./{{ job_name }}.err.%j
  # Initial working directory:
  #SBATCH -D ./
  # Job Name:
  #SBATCH -J {{ job_name }}
  #
  # Queue (Partition):
  {%- if gpu %}
  #SBATCH --partition=gpu
  #SBATCH --constraint='gpu'
  {%- else %}
  {%- if time is lessthan 30 or time is equalto 30 %}
  #SBATCH --partition=express
  {%- elif time is greaterthan 30 and time is lessthan 240 or time is equalto 240 %}
  #SBATCH --partition=short
  {%- else %}
  #SBATCH --partition=general
  {%- endif %}
  {%- endif %}
  #
  # Request {{ n_nodes }} node(s)
  #SBATCH --nodes={{ n_nodes }}
  # Set the number of tasks per node (=MPI ranks)
  #SBATCH --ntasks-per-node={{ number_of_ranks }}
  # Set the number of threads per rank (=OpenMP threads)
  #SBATCH --cpus-per-task={{ number_of_threads }}
  {% if hyperthreading %}
  # Enable hyperthreading
  #SBATCH --ntasks-per-core=2
  {%- endif %}
  # Wall clock limit:
  #SBATCH --time={{ formatted_time }}

  module purge
  module load impi
  module load cuda
  module load {{ module }}

  export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
  {% if hyperthreading %}
  export OMP_PLACES=threads
  export SLURM_HINT=multithread
  {%- else %}
  export OMP_PLACES=cores
  {%- endif %}

  # Run {{ module }} for {{ time  }} minutes
  srun gmx_mpi mdrun -v -ntomp $OMP_NUM_THREADS -maxh {{ time / 60 }} -resethway -noconfout -deffnm {{ name }}

  # Running multiple simulations on a single node (multidir)
  # If you want to run multiple simulations on the same node, use the `multidir`
  # variable, like so:
  #
  # srun gmx_mpi mdrun -v -ntomp $OMP_NUM_THREADS -maxh {{ time / 60 }} -resethway -noconfout -deffnm {{ name }} {{ multidir }}
  #
  # MDBenchmark will set up the folder structure as required by GROMACS and
  # replace the variable.


LoadLeveler
-----------

Here is an example job template for the decomissioned MPG cluster ``hydra`` (LoadLeveler).

.. code::

    # @ shell=/bin/bash
    #
    # @ error = {{ job_name }}.err.$(jobid)
    # @ output = {{ job_name }}.out.$(jobid)
    # @ job_type = parallel
    # @ node_usage = not_shared
    # @ node = {{ n_nodes }}
    # @ tasks_per_node = {{ number_of_threads }}
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
    poe gmx_mpi mdrun -deffnm {{ name }} -maxh {{ time / 60 }} -resethway -noconfout

Options passed to job templates
-------------------------------

MDBenchmark passes the following variables to each template:

+-------------------+---------------------------------------------------------------------+
| Value             | Description                                                         |
+===================+=====================================================================+
| name              | Name of the TPR file                                                |
+-------------------+---------------------------------------------------------------------+
| job_name          | Job name as specified by the user, if not specified same as name    |
+-------------------+---------------------------------------------------------------------+
| gpu               | Boolean that is true, if GPUs are requested                         |
+-------------------+---------------------------------------------------------------------+
| module            | Name of the module to load                                          |
+-------------------+---------------------------------------------------------------------+
| n_nodes           | Maximal number of nodes to run on                                   |
+-------------------+---------------------------------------------------------------------+
| number_of_ranks   | The number of MPI ranks                                             |
+-------------------+---------------------------------------------------------------------+
| number_of_threads | The number of OpenMP threads                                        |
+-------------------+---------------------------------------------------------------------+
| hyperthreading    | Whether to use hyperthreading                                       |
+-------------------+---------------------------------------------------------------------+
| time              | Benchmark run time in minutes                                       |
+-------------------+---------------------------------------------------------------------+
| formatted_time    | Run time for the queuing system in human readable format (HH:MM:SS) |
+-------------------+---------------------------------------------------------------------+
| multidir          | Run multiple simulations on a single node (GROMACS only)            |
+-------------------+---------------------------------------------------------------------+

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

.. _xdg: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
