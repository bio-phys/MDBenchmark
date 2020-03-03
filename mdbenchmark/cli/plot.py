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
import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import rcParams as mpl_rcParams
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from mdbenchmark import console
from mdbenchmark.utils import calc_slope_intercept, generate_output_name, lin_func

plt.switch_backend("agg")


def get_xsteps(size, min_x, plot_cores, xtick_step):
    """Return the step size needed for a reasonable xtick spacing.

    Default step size is 1. If benchmarks>=18 are plotted, the step size is
    increased to 2. If we are plotting the number of cores, we increase the
    step size to 3, if the number of benchmarks>10 or the number of
    cores/node>=100.

    The user setting `xtick_step` overrides all previous settings.
    """
    step = 1

    # Increase step size if we plot many nodes at once
    if size >= 18:
        step = 2
    # Make sure we fit all xticks for a reasonable number of cores
    if plot_cores and ((size > 10) or (min_x >= 100)):
        step = 3
    # Ignore all above logic and set value specified by user
    if xtick_step:
        step = xtick_step

    return step


def plot_projection(df, selection, color, ax=None):
    if ax is None:
        ax = plt.gca()
    slope, intercept = calc_slope_intercept(
        (df[selection].iloc[0], df["ns/day"].iloc[0]),
        (df[selection].iloc[1], df["ns/day"].iloc[1]),
    )
    xstep = df[selection].iloc[1] - df[selection].iloc[0]
    xmax = df[selection].iloc[-1] + xstep
    x = df[selection]
    x = pd.concat([pd.DataFrame({0: [0]}), x, pd.DataFrame({0: [xmax]})])
    # avoid a label and use values instead of pd.Series
    ax.plot(x, lin_func(x.values, slope, intercept), ls="--", color=color, alpha=0.5)
    return ax


def plot_line(df, selection, label, fit, ax=None):
    if ax is None:
        ax = plt.gca()

    p = ax.plot(selection, "ns/day", ".-", data=df, ms="10", label=label)
    color = p[0].get_color()

    if fit and (len(df[selection]) > 1):
        plot_projection(df=df, selection=selection, color=color, ax=ax)

    return ax


def plot_over_group(df, plot_cores, fit, ax=None):
    # plot all lines
    selection = "ncores" if plot_cores else "nodes"

    groupby = ["gpu", "module", "host"]
    gb = df.groupby(groupby)
    for key, df in gb:
        template = key[2]
        module = key[1]
        pu = "GPU" if key[0] else "CPU"

        label = "{template} - {module} on {pu}s".format(
            template=template, module=module, pu=pu
        )
        plot_line(df=df, selection=selection, ax=ax, fit=fit, label=label)

    # style axes
    xlabel = "cores" if plot_cores else "nodes"
    ax.set_xlabel("Number of {}".format(xlabel))
    ax.set_ylabel("Performance [ns/day]")

    # here I return the figure as well as the legend
    return ax


def filter_dataframe_for_plotting(df, host_name, module_name, gpu, cpu):
    # gpu/cpu can be plotted together or separately
    if gpu and cpu:
        # if no flags are given by the user or both are set everything is plotted
        console.info("Plotting GPU and CPU data.")
    elif gpu and not cpu:
        df = df[df.gpu]
        console.info("Plotting GPU data only.")
    elif cpu and not gpu:
        df = df[~df.gpu]
        console.info("Plotting CPU data only.")
    elif not cpu and not gpu:
        console.error("CPU and GPU not set. Nothing to plot. Exiting.")

    if df.empty:
        console.error("Your filtering led to an empty dataset. Exiting.")

    df_filtered_hosts = df[df["host"].isin(host_name)]
    df_unique_hosts = np.unique(df_filtered_hosts["host"])

    if df_unique_hosts.size != len(host_name):
        console.error(
            "Could not find all provided hosts. Available hosts are: {}".format(
                ", ".join(np.unique(df["host"]))
            )
        )

    if not host_name:
        console.info("Plotting all hosts in input file.")
    else:
        df = df_filtered_hosts
        console.info(
            "Data for the following hosts will be plotted: {}".format(
                ", ".join(df_unique_hosts)
            )
        )

    for module in module_name:
        if module in ["gromacs", "namd"]:
            console.info("Plotting all modules for engine '{}'.", module)
        elif module in df["module"].tolist():
            console.info("Plotting module '{}'.", module)
        elif module not in df["module"].tolist():
            console.error(
                "The module '{}' does not exist in your data. Exiting.", module
            )

    if not module_name:
        console.info("Plotting all modules in your input data.")
    # this should work but we need to check before whether any of the entered
    # names are faulty/don't exist
    if module_name:
        df = df[df["module"].str.contains("|".join(module_name))]

    if df.empty:
        console.error(
            "Your selections contained no benchmarking information. "
            "Are you sure all your selections are correct?"
        )

    return df


def do_plot(
    csv,
    output_name,
    output_format,
    template,
    module,
    gpu,
    cpu,
    plot_cores,
    fit,
    font_size,
    dpi,
    xtick_step,
    watermark,
):
    """Creates plots of benchmarks."""
    if not csv:
        raise click.BadParameter(
            "You must specify at least one CSV file.", param_hint='"--csv"'
        )

    df = pd.concat([pd.read_csv(c, index_col=0) for c in csv]).dropna()

    df = filter_dataframe_for_plotting(df, template, module, gpu, cpu)

    mpl_rcParams["font.size"] = font_size
    fig = Figure()
    FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax = plot_over_group(df=df, plot_cores=plot_cores, fit=fit, ax=ax)

    # Update xticks
    selection = "ncores" if plot_cores else "nodes"
    min_x = df[selection].min() if plot_cores else 1
    max_x = df[selection].max()
    xticks_steps = min_x
    xticks = np.arange(min_x, max_x + min_x, xticks_steps)
    step = get_xsteps(xticks.size, min_x, plot_cores, xtick_step)

    ax.set_xticks(xticks[::step])
    xdiff = min_x * 0.5 * step
    ax.set_xlim(min_x - xdiff, max_x + xdiff)

    # Update yticks
    max_y = df["ns/day"].max() or 50
    yticks_steps = ((max_y + 1) / 10).astype(int)
    yticks = np.arange(0, max_y + (max_y * 0.25), yticks_steps)
    ax.set_yticks(yticks)
    ax.set_ylim(0, max_y + (max_y * 0.25))

    # Add watermark
    if watermark:
        ax.text(0.025, 0.925, "MDBenchmark", transform=ax.transAxes, alpha=0.3)

    lgd = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.175))
    plt.tight_layout()

    if output_name is None and len(csv) == 1:
        csv_string = csv[0].split(".")[0]
        output_name = "{}.{}".format(csv_string, output_format)
    elif output_name is None and len(csv) != 1:
        output_name = generate_output_name(output_format)
    elif not output_name.endswith(".{}".format(output_format)):
        output_name = "{}.{}".format(output_name, output_format)
    # tight alone does not consider the legend if it is outside the plot.
    # therefore i add it manually as extra artist. This way we don't get problems
    # with the variability of individual lines which are to be plotted
    fig.savefig(
        output_name,
        type=output_format,
        bbox_extra_artists=(lgd,),
        bbox_inches="tight",
        dpi=dpi,
    )
    console.info("Your file was saved as '{}' in the working directory.", output_name)
