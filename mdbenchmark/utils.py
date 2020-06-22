# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDBenchmark
# Copyright (c) 2017-2018 The MDBenchmark development team and contributors
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
import datetime as dt
import multiprocessing as mp
import os
import socket
import sys

import click
import datreant as dtr
import pandas as pd
import xdg
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader
from tabulate import tabulate

from mdbenchmark import console, mdengines
from mdbenchmark.ext.cadishi import _cat_proc_cpuinfo_grep_query_sort_uniq
from mdbenchmark.mdengines import detect_md_engine, utils

# Order where to look for host templates: HOME -> etc -> package
# home
_loaders = [FileSystemLoader(os.path.join(xdg.XDG_CONFIG_HOME, "MDBenchmark"))]
# allow custom folder for templates. Useful for environment modules
_mdbenchmark_env = os.getenv("MDBENCHMARK_TEMPLATES")
if _mdbenchmark_env is not None:
    _loaders.append(FileSystemLoader(_mdbenchmark_env))
# global
_loaders.extend(
    [FileSystemLoader(os.path.join(d, "MDBenchmark")) for d in xdg.XDG_CONFIG_DIRS]
)
# from package
_loaders.append(PackageLoader("mdbenchmark", "templates"))
ENV = Environment(loader=ChoiceLoader(_loaders))


def get_possible_hosts():
    return ENV.list_templates()


def print_possible_hosts():
    all_hosts = get_possible_hosts()
    console.info("Available host templates:")
    for host in all_hosts:
        console.info(host)


def guess_host():
    hostname = socket.gethostname()
    known_hosts = get_possible_hosts()
    for host in known_hosts:
        if host in hostname:
            return host

    return None


def retrieve_host_template(host=None):
    """Lookup the template name.

    Parameter
    ---------
    host : str
    Name of the host template to lookup

    Returns
    -------
    template
    """
    return ENV.get_template(host)


def guess_ncores():
    """Guess the number of physical CPU cores.

    We inspect `/proc/cpuinfo` to grab the actual number."""
    total_cores = None
    if sys.platform.startswith("linux"):
        nsocket = len(_cat_proc_cpuinfo_grep_query_sort_uniq("physical id"))
        ncores = len(_cat_proc_cpuinfo_grep_query_sort_uniq("core id"))
        total_cores = ncores * nsocket
    elif sys.platform == "darwin":
        # assumes we have an INTEL CPU with hyper-threading. As of 2017 this is
        # true for all officially supported Apple models.
        total_cores = mp.cpu_count() // 2
    if total_cores is None:
        console.warn(
            "Could not guess number of physical cores. "
            "Assuming there is only 1 core per node."
        )
        total_cores = 1
    return total_cores


def validate_required_files(name, modules):
    for module in modules:
        # Here we detect the MD engine (supported: GROMACS and NAMD).
        engine = mdengines.detect_md_engine(module)
        engine.check_input_file_exists(name)


def construct_directory_name(template, module, gpu):
    return "{template}_{module}{gpu}".format(
        template=template, module=module, gpu="_gpu" if gpu else ""
    )


def construct_generate_data(
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
):
    data = []
    for module in modules:
        # Here we detect the MD engine (supported: GROMACS and NAMD).
        engine = mdengines.detect_md_engine(module)

        # Iterate over CPUs or GPUs
        gpu_cpu = {"cpu": cpu, "gpu": gpu}
        for key, value in sorted(gpu_cpu.items()):
            # Skip the current processing unit
            if not value:
                continue

            # Generate directory name and string representation for the user.
            # Also set the `gpu` variable for later use.
            gpu = True if key == "gpu" else False
            directory = construct_directory_name(template.name, module, gpu)

            # Set up the path to the new directory as `datreant.Tree`
            base_directory = dtr.Tree(directory)

            # Do the main iteration over nodes and ranks
            for nodes in range(min_nodes, max_nodes + 1):
                for _ranks in number_of_ranks:
                    ranks, threads = processor.get_ranks_and_threads(
                        _ranks, with_hyperthreading=enable_hyperthreading
                    )

                    # Append the data to our list
                    data.append(
                        [
                            name,
                            job_name,
                            base_directory,
                            host,
                            engine,
                            module,
                            nodes,
                            time,
                            gpu,
                            template,
                            ranks,
                            threads,
                            enable_hyperthreading,
                        ]
                    )

    return data


def generate_output_name(extension):
    """ generate a unique filename based on the date and time for a given extension.
    """
    date_time = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = "{}.{}".format(date_time, extension)
    return out


def parse_bundle(bundle, columns, sort_values_by, discard_performance=False):
    """Generates a DataFrame from a datreant.Bundle."""
    data = []

    with click.progressbar(
        bundle, length=len(bundle), label="Analyzing benchmarks", show_pos=True
    ) as bar:
        for treant in bar:
            module = treant.categories["module"]
            engine = detect_md_engine(module)
            row = utils.analyze_benchmark(engine=engine, benchmark=treant)

            version = 2
            if "version" in treant.categories:
                version = 3
            row += [version]

            if discard_performance:
                row = row[:2] + row[3:]

            data.append(row)

    df = pd.DataFrame(data, columns=columns)

    # Exit if no data is available
    if df.empty:
        console.error("There is no data for the given path.")

    # Sort values by `nodes`
    df = df.sort_values(sort_values_by).reset_index(drop=True)

    return df


def map_columns(map_dict, columns):
    return [map_dict[key] for key in columns]


def consolidate_dataframe(df, columns):
    """Return a shortened version of a DataFrame, grouping the nodes."""
    new_columns = df.columns
    agg = {column: "first" for column in new_columns if column not in columns}
    agg["nodes"] = format_interval_groups
    new_df = df.groupby(columns, as_index=False).agg(agg)
    return new_df[new_columns]


def print_dataframe(df, columns):
    """Print a nicely formatted shortened DataFrame."""
    table = df.copy()
    table.columns = columns
    table = tabulate(table, headers="keys", tablefmt="psql", showindex=False)
    console.info(table, newlines=True)


def group_consecutives(values, step=1):
    """Return list of consecutive lists of numbers from vals (number list).
    This list hast to be at least ordered such that N+1 > N.
    Adapted from code found on stack overflow.
    Question Thread:
    https://stackoverflow.com/questions/7352684/
    Solved by:
    https://stackoverflow.com/users/308066/dkamins
    """

    run = []
    result = [run]
    expected = None
    for value in values:
        if (value == expected) or (expected is None):
            run.append(value)
        else:
            run = [value]
            result.append(run)
        expected = value + step

    return result


def format_interval_groups(nodes):
    output = []
    groups = group_consecutives(nodes)

    for group in groups:
        if len(group) == 1:
            output.append(group[0])
        else:
            output.append(str(group[0]) + "-" + str(group[-1]))

    return ", ".join(str(node) for node in output)
