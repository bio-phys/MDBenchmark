# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDBenchmark
# Copyright (c) 2017-2020 The MDBenchmark development team and contributors
# (see the file AUTHORS for the full list of names)
#
# MDBenchmark is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MDBenchmark is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MDBenchmark.  If not, see <http://www.gnu.org/licenses/>.
import os.path

import click
import pandas as pd

from mdbenchmark import console, mdengines, utils
from mdbenchmark.cli.validators import (
    validate_cpu_gpu_flags,
    validate_number_of_nodes,
    validate_number_of_simulations,
)
from mdbenchmark.mdengines.utils import write_benchmark
from mdbenchmark.models import Processor
from mdbenchmark.utils import (
    consolidate_dataframe,
    construct_generate_data,
    map_columns,
    print_dataframe,
    validate_required_files,
)
from mdbenchmark.versions import Version3Categories

NAMD_WARNING = (
    "NAMD support is experimental. "
    "All input files must be in the current directory. "
    "Parameter paths must be absolute. Only crude file checks are performed! "
    "If you use the {} option make sure you use the GPU compatible NAMD module!"
)


def do_generate(
    name,
    cpu,
    gpu,
    module,
    host,
    min_nodes,
    max_nodes,
    time,
    skip_validation,
    job_name,
    yes,
    physical_cores,
    logical_cores,
    number_of_ranks,
    enable_hyperthreading,
    multidir,
):
    """Generate a bunch of benchmarks."""

    # Instantiate the version we are going to use
    benchmark_version = Version3Categories()

    # Validate the CPU and GPU flags
    validate_cpu_gpu_flags(cpu, gpu)

    # Validate the number of nodes
    validate_number_of_nodes(min_nodes=min_nodes, max_nodes=max_nodes)

    if logical_cores < physical_cores:
        console.error(
            "The number of logical cores cannot be smaller than the number of physical cores."
        )

    if physical_cores and not logical_cores:
        console.warn("Assuming logical_cores = 2 * physical_cores")
        logical_cores = 2 * physical_cores

    if physical_cores and logical_cores:
        processor = Processor(
            physical_cores=physical_cores, logical_cores=logical_cores
        )
    else:
        processor = Processor()

    # Hyperthreading check
    if enable_hyperthreading and not processor.supports_hyperthreading:
        console.error("The processor of this machine does not support hyperthreading.")

    if not number_of_ranks:
        number_of_ranks = (processor.physical_cores,)

    # Validate number of simulations
    validate_number_of_simulations(multidir, min_nodes, max_nodes, number_of_ranks)

    # Grab the template name for the host. This should always work because
    # click does the validation for us
    template = utils.retrieve_host_template(host)

    # Warn the user that NAMD support is still experimental.
    if any(["namd" in m for m in module]):
        console.warn(NAMD_WARNING, "--gpu")

    # Stop if we cannot find any modules. If the user specified multiple
    # modules, we will continue with only the valid ones.
    modules = mdengines.normalize_modules(module, skip_validation)
    if not modules:
        console.error("No requested modules available!")

    # Check if all needed files exist. Throw an error if they do not.
    validate_required_files(name=name, modules=modules)

    # Validate that we can use the number of ranks and threads.
    # We can continue, if no ValueError is thrown
    for ranks in number_of_ranks:
        try:
            processor.get_ranks_and_threads(
                ranks, with_hyperthreading=enable_hyperthreading
            )
        except ValueError as e:
            console.error(e)

    # Create all benchmark combinations and put them into a DataFrame
    data = construct_generate_data(
        name,
        job_name,
        modules,
        host,
        template,
        cpu,
        gpu,
        time,
        min_nodes,
        max_nodes,
        processor,
        number_of_ranks,
        enable_hyperthreading,
        multidir,
    )
    df = pd.DataFrame(data, columns=benchmark_version.generate_categories)

    # Consolidate the data by grouping on the number of nodes and print to the
    # user as an overview.
    consolidated_df = consolidate_dataframe(
        df, columns=benchmark_version.consolidate_categories
    )
    print_dataframe(
        consolidated_df[benchmark_version.generate_printing],
        columns=map_columns(
            map_dict=benchmark_version.category_mapping,
            columns=benchmark_version.generate_printing,
        ),
    )

    # Save the number of benchmarks for later printing
    number_of_benchmarks = df.shape[0]
    # Ask the user for confirmation to generate files.
    # If the user defined `--yes`, we will skip the confirmation immediately.
    if yes:
        console.info(
            "We will generate {} "
            + "{benchmark}.".format(
                benchmark="benchmark" if number_of_benchmarks == 1 else "benchmarks"
            ),
            number_of_benchmarks,
        )
    elif not click.confirm(
        "We will generate {} benchmarks. Continue?".format(number_of_benchmarks)
    ):
        console.error("Exiting. No benchmarks were generated.")

    # Generate the benchmarks
    with click.progressbar(
        df.iterrows(),
        length=number_of_benchmarks,
        show_pos=True,
        label="Generating benchmarks",
    ) as bar:
        for _, row in bar:
            relative_path, file_basename = os.path.split(row["name"])
            mappings = benchmark_version.generate_mapping
            kwargs = {"name": file_basename, "relative_path": relative_path}
            for key, value in mappings.items():
                kwargs[value] = row[key]

            write_benchmark(**kwargs)

    # Finish up by telling the user how to submit the benchmarks
    console.info(
        "Finished! You can submit the jobs with {}.", "mdbenchmark submit",
    )
