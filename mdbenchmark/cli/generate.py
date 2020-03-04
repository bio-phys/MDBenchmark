# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDBenchmark
# Copyright (c) 2017-2019 The MDBenchmark development team and contributors
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
import datreant as dtr
import pandas as pd

from mdbenchmark import console, mdengines, utils
from mdbenchmark.cli.validators import validate_cpu_gpu_flags, validate_number_of_nodes
from mdbenchmark.mdengines.utils import write_benchmark
from mdbenchmark.utils import ConsolidateDataFrame, DataFrameFromBundle, PrintDataFrame

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
):
    """Generate a bunch of benchmarks."""
    # Validate the CPU and GPU flags
    validate_cpu_gpu_flags(cpu, gpu)

    # Validate the number of nodes
    validate_number_of_nodes(min_nodes=min_nodes, max_nodes=max_nodes)

    # Grab the template name for the host. This should always work because
    # click does the validation for us
    template = utils.retrieve_host_template(host)

    # Warn the user that NAMD support is still experimental.
    if any(["namd" in m for m in module]):
        console.warn(NAMD_WARNING, "--gpu")

    module = mdengines.normalize_modules(module, skip_validation)

    # If several modules were given and we only cannot find one of them, we
    # continue.
    if not module:
        console.error("No requested modules available!")

    df_overview = pd.DataFrame(
        columns=[
            "name",
            "job_name",
            "base_directory",
            "template",
            "engine",
            "module",
            "nodes",
            "run time [min]",
            "gpu",
            "host",
        ]
    )

    i = 1
    for m in module:
        # Here we detect the MD engine (supported: GROMACS and NAMD).
        engine = mdengines.detect_md_engine(m)

        # Check if all needed files exist. Throw an error if they do not.
        engine.check_input_file_exists(name)

        gpu_cpu = {"cpu": cpu, "gpu": gpu}
        for pu, state in sorted(gpu_cpu.items()):
            if not state:
                continue

            directory = "{}_{}".format(host, m)
            gpu = False
            gpu_string = ""
            if pu == "gpu":
                gpu = True
                directory += "_gpu"
                gpu_string = " with GPUs"

            console.info("Creating benchmark system for {}.", m + gpu_string)

            base_directory = dtr.Tree(directory)

            for nodes in range(min_nodes, max_nodes + 1):
                df_overview.loc[i] = [
                    name,
                    job_name,
                    base_directory,
                    template,
                    engine,
                    m,
                    nodes,
                    time,
                    gpu,
                    host,
                ]
                i += 1

    console.info("{}", "Benchmark Summary:")

    df_short = ConsolidateDataFrame(df_overview)
    PrintDataFrame(df_short)

    if yes:
        console.info("Generating the above benchmarks.")
    elif not click.confirm("The above benchmarks will be generated. Continue?"):
        console.error("Exiting. No benchmarks generated.")

    for _, row in df_overview.iterrows():
        relative_path, file_basename = os.path.split(row["name"])
        write_benchmark(
            engine=row["engine"],
            base_directory=row["base_directory"],
            template=row["template"],
            nodes=row["nodes"],
            gpu=row["gpu"],
            module=row["module"],
            name=file_basename,
            relative_path=relative_path,
            job_name=row["job_name"],
            host=row["host"],
            time=row["run time [min]"],
        )

    # Provide some output for the user
    console.info(
        "Finished generating all benchmarks.\n" "You can now submit the jobs with {}.",
        "mdbenchmark submit",
    )
