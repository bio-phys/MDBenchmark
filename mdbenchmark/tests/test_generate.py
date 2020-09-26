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
import os

import datreant as dtr
import pytest
from click import exceptions

from mdbenchmark import cli
from mdbenchmark.cli.generate import NAMD_WARNING
from mdbenchmark.cli.validators import (
    print_known_hosts,
    validate_cpu_gpu_flags,
    validate_hosts,
    validate_module,
    validate_name,
    validate_number_of_nodes,
)
from mdbenchmark.mdengines import SUPPORTED_ENGINES

DIR_STRUCTURE = {
    "applications": {
        "gromacs": ["2016.4", "5.1.4-plumed2.3", "2018.1"],
        "namd": ["123", "456"],
        "amber": ["13", "14", "15"],
    },
    "visualization": {"vmd": ["1.9.3", "1.9.4"]},
}

NAMD_WARNING_FORMATTED = "WARNING " + NAMD_WARNING.format("--gpu") + "\n"


@pytest.fixture
def ctx_mock():
    """Mock a context object for python click."""

    class MockCtx(object):
        resilient_parsing = False
        color = None

        def exit(self):
            return

    return MockCtx()


@pytest.mark.parametrize(
    "module, extensions",
    [("gromacs/2016", ["tpr"]), ("namd/11", ["namd", "pdb", "psf"])],
)
def test_generate(cli_runner, module, extensions, tmpdir):
    """Test that we can generate benchmarks for all supported MD engines w/o module validation."""
    with tmpdir.as_cwd():
        for ext in extensions:
            open("protein.{}".format(ext), "a").close()

        result = cli_runner.invoke(
            cli,
            [
                "generate",
                "--module={}".format(module),
                "--host=draco",
                "--max-nodes=4",
                "--gpu",
                "--no-cpu",
                "--name=protein",
                "--yes",
            ],
        )

        expected_output = (
            "+---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n"
            "| Name    | Module       | Nodes   |   Time (min) | GPUs?   | Host   |   # ranks |   # threads | Hyperthreading?   |   # Simulations |\n"
            "|---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------|\n"
            "| protein | gromacs/2016 | 1-4     |           15 | True    | draco  |        40 |           1 | False             |               1 |\n"
            "+---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n\n"
        )

        if "namd" in module:
            expected_output = (
                "+---------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n"
                "| Name    | Module   | Nodes   |   Time (min) | GPUs?   | Host   |   # ranks |   # threads | Hyperthreading?   |   # Simulations |\n"
                "|---------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------|\n"
                "| protein | namd/11  | 1-4     |           15 | True    | draco  |        40 |           1 | False             |               1 |\n"
                "+---------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n\n"
            )

        start_of_message = "WARNING Cannot locate modules available on this host. Not performing module name validation.\n\n"
        end_of_message = (
            "We will generate 4 benchmarks.\n"
            "Finished! You can submit the jobs with mdbenchmark submit.\n"
        )
        output = start_of_message + "".join(expected_output) + end_of_message
        if "namd" in module:
            output = NAMD_WARNING_FORMATTED + output

        assert result.exit_code == 0
        assert result.output == output


@pytest.mark.parametrize(
    "module, extensions",
    [("gromacs/2016", ["tpr"]), ("namd/11", ["namd", "pdb", "psf"])],
)
def test_generate_with_cpu_gpu(
    cli_runner, module, extensions, tmpdir,
):
    """Test that we can generate benchmarks for CPUs and GPUs at once."""
    with tmpdir.as_cwd():
        for ext in extensions:
            open("protein.{}".format(ext), "a").close()

        result = cli_runner.invoke(
            cli,
            [
                "generate",
                "--module={}".format(module),
                "--template=draco",
                "--max-nodes=4",
                "--gpu",
                "--name=protein",
                "--yes",
            ],
        )

        expected_output = (
            "+---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n"
            "| Name    | Module       | Nodes   |   Time (min) | GPUs?   | Host   |   # ranks |   # threads | Hyperthreading?   |   # Simulations |\n"
            "|---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------|\n"
            "| protein | gromacs/2016 | 1-4     |           15 | False   | draco  |        40 |           1 | False             |               1 |\n"
            "| protein | gromacs/2016 | 1-4     |           15 | True    | draco  |        40 |           1 | False             |               1 |\n"
            "+---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n\n"
        )

        if "namd" in module:
            expected_output = (
                "+---------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n"
                "| Name    | Module   | Nodes   |   Time (min) | GPUs?   | Host   |   # ranks |   # threads | Hyperthreading?   |   # Simulations |\n"
                "|---------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------|\n"
                "| protein | namd/11  | 1-4     |           15 | False   | draco  |        40 |           1 | False             |               1 |\n"
                "| protein | namd/11  | 1-4     |           15 | True    | draco  |        40 |           1 | False             |               1 |\n"
                "+---------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n\n"
            )

        start_of_message = "WARNING Cannot locate modules available on this host. Not performing module name validation.\n\n"
        end_of_message = (
            "We will generate 8 benchmarks.\n"
            "Finished! You can submit the jobs with mdbenchmark submit.\n"
        )
        output = start_of_message + "".join(expected_output) + end_of_message
        if "namd" in module:
            output = NAMD_WARNING_FORMATTED + output

        assert result.exit_code == 0
        assert result.output == output


@pytest.mark.parametrize(
    "module, extensions",
    [("gromacs/2016", ["tpr"]), ("namd/11", ["namd", "pdb", "psf"])],
)
def test_generate_with_validation(cli_runner, module, monkeypatch, extensions, tmpdir):
    with tmpdir.as_cwd():
        for ext in extensions:
            open("protein.{}".format(ext), "a").close()

        # monkeypatch the output of the available modules
        monkeypatch.setattr(
            "mdbenchmark.mdengines.get_available_modules",
            lambda: {"gromacs": ["2016"], "namd": ["11"]},
        )

        result = cli_runner.invoke(
            cli,
            [
                "generate",
                "--module={}".format(module),
                "--template=draco",
                "--max-nodes=4",
                "--gpu",
                "--no-cpu",
                "--name=protein",
                "--yes",
            ],
        )

        expected_output = (
            "\n"
            "+---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n"
            "| Name    | Module       | Nodes   |   Time (min) | GPUs?   | Host   |   # ranks |   # threads | Hyperthreading?   |   # Simulations |\n"
            "|---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------|\n"
            "| protein | gromacs/2016 | 1-4     |           15 | True    | draco  |        40 |           1 | False             |               1 |\n"
            "+---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n\n"
        )

        if "namd" in module:
            expected_output = (
                "+---------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n"
                "| Name    | Module   | Nodes   |   Time (min) | GPUs?   | Host   |   # ranks |   # threads | Hyperthreading?   |   # Simulations |\n"
                "|---------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------|\n"
                "| protein | namd/11  | 1-4     |           15 | True    | draco  |        40 |           1 | False             |               1 |\n"
                "+---------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n\n"
            )

        end_of_message = (
            "We will generate 4 benchmarks.\n"
            "Finished! You can submit the jobs with mdbenchmark submit.\n"
        )
        output = "".join(expected_output) + end_of_message
        if "namd" in module:
            output = NAMD_WARNING_FORMATTED + "\n" + output

        assert result.exit_code == 0
        assert result.output == output


@pytest.mark.parametrize(
    "module, extensions",
    [("gromacs/2016", ["tpr"]), ("namd/11", ["namd", "pdb", "psf"])],
)
def test_generate_skip_validation(cli_runner, module, extensions, monkeypatch, tmpdir):
    """Test that we can skip the validation during benchmark generation."""
    with tmpdir.as_cwd():
        for ext in extensions:
            open("protein.{}".format(ext), "a").close()

        # monkeypatch the output of the available modules
        monkeypatch.setattr(
            "mdbenchmark.mdengines.get_available_modules",
            lambda: {"gromacs": ["2016"], "namd": ["11"]},
        )

        result = cli_runner.invoke(
            cli,
            [
                "generate",
                f"--module={module}",
                "--host=draco",
                "--max-nodes=4",
                "--gpu",
                "--no-cpu",
                "--name=protein",
                "--skip-validation",
                "--yes",
            ],
        )

        expected_output = (
            "+---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n"
            "| Name    | Module       | Nodes   |   Time (min) | GPUs?   | Host   |   # ranks |   # threads | Hyperthreading?   |   # Simulations |\n"
            "|---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------|\n"
            "| protein | gromacs/2016 | 1-4     |           15 | True    | draco  |        40 |           1 | False             |               1 |\n"
            "+---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n\n"
        )

        if "namd" in module:
            expected_output = (
                "+---------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n"
                "| Name    | Module   | Nodes   |   Time (min) | GPUs?   | Host   |   # ranks |   # threads | Hyperthreading?   |   # Simulations |\n"
                "|---------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------|\n"
                "| protein | namd/11  | 1-4     |           15 | True    | draco  |        40 |           1 | False             |               1 |\n"
                "+---------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n\n"
            )

        end_of_message = (
            "We will generate 4 benchmarks.\n"
            "Finished! You can submit the jobs with mdbenchmark submit.\n"
        )
        output = (
            "WARNING Not performing module name validation.\n\n"
            + "".join(expected_output)
            + end_of_message
        )
        if "namd" in module:
            output = NAMD_WARNING_FORMATTED + output

        assert result.exit_code == 0
        assert result.output == output


def test_generate_unsupported_engine(cli_runner, monkeypatch, tmpdir):
    """Make sure we throw the correct error, when passed an unsupported MD engine."""
    with tmpdir.as_cwd():
        for k, v in DIR_STRUCTURE.items():
            for k2, v2 in v.items():
                os.makedirs(os.path.join(k, k2))
                for v3 in v2:
                    open(os.path.join(k, k2, v3), "a").close()

        # Prepare path variable that we are going to monkeypatch for
        # `mdengines.get_available_modules`
        dirs = ":".join([os.path.join(os.getcwd(), x) for x in os.listdir(os.getcwd())])
        monkeypatch.setenv("MODULEPATH", dirs)

        supported_engines = ", ".join(sorted([x for x in SUPPORTED_ENGINES]))
        output = (
            "ERROR There is currently no support for 'doesnotexist'. "
            "Supported MD engines are: {}.\n".format(supported_engines)
        )
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                "--module=doesnotexist/version",
                "--host=draco",
                "--name=protein",
                "--yes",
            ],
        )
        assert result.exit_code == 1
        assert result.output == output


def test_generate_console_messages(cli_runner, monkeypatch, tmpdir):
    """Test that the CLI for generate prints all error messages as expected."""
    with tmpdir.as_cwd():
        # monkeypatch the output of the available modules
        monkeypatch.setattr(
            "mdbenchmark.mdengines.get_available_modules", lambda: {"gromacs": ["2016"]}
        )

        # Test that we get an error when not supplying a file name
        result = cli_runner.invoke(
            cli, ["generate", "--module=gromacs/2016", "--host=draco", "--yes"]
        )
        output = (
            "Usage: cli generate [OPTIONS]\n\nError: Invalid value for "
            '"-n" / "--name": Please specifiy the name of your input files.'
        )

        # Test error message if the TPR file does not exist
        result = cli_runner.invoke(
            cli,
            ["generate", "--module=gromacs/2016", "--host=draco", "--name=md", "--yes"],
        )
        output = (
            "ERROR File md.tpr does not exist, but is needed for GROMACS benchmarks.\n"
        )

        assert result.exit_code == 1
        assert result.output == output

        with open("protein.tpr", "w") as fh:
            fh.write("This is a dummy tpr!")

        # Test that the minimal number of nodes must be bigger than the maximal number
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                "--module=gromacs/2016",
                "--host=draco",
                "--name=protein",
                "--min-nodes=6",
                "--max-nodes=4",
                "--yes",
            ],
        )
        output = (
            "Usage: cli generate [OPTIONS]\n\nError: Invalid value for "
            '"--min-nodes": The minimal number of nodes needs to be smaller '
            "than the maximal number.\n"
        )
        assert result.exit_code == 2
        assert result.output == output

        # Test error message if we pass an invalid template name
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                "--module=gromacs/2016",
                "--host=minerva",
                "--name=protein",
                "--yes",
            ],
        )
        output = (
            "Could not find template for host 'minerva'.\n"
            "Available host templates:\n"
            "cobra\n"
            "draco\n"
            "hydra\n"
        )
        assert result.exit_code == 0
        assert result.output == output

        # Test error message if we do not pass any module name
        result = cli_runner.invoke(
            cli, ["generate", "--host=draco", "--name=protein", "--yes"]
        )
        output = (
            "Usage: cli generate [OPTIONS]\n\nError: Invalid value for "
            '"-m" / "--module": Please specify which MD engine module '
            "to use for the benchmarks.\n"
        )
        assert result.exit_code == 2
        assert result.output == output


def test_generate_namd_experimental_warning(cli_runner, monkeypatch, tmpdir):
    """Test that we print the NAMD experimental warning."""
    with tmpdir.as_cwd():
        for f in ["md.namd", "md.psf", "md.pdb"]:
            open(f, "a").close()

        # monkeypatch the output of the available modules
        monkeypatch.setattr(
            "mdbenchmark.mdengines.get_available_modules", lambda: {"namd": ["123"]}
        )

        result = cli_runner.invoke(
            cli, ["generate", "--module=namd/123", "--host=draco", "--name=md", "--yes"]
        )
        output1 = (
            "WARNING NAMD support is experimental. "
            "All input files must be in the current directory. "
            "Parameter paths must be absolute. Only crude file checks are performed! "
            "If you use the --gpu option make sure you use the GPU compatible NAMD module!\n"
            "\n"
        )
        expected_output = (
            "+--------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n",
            "| Name   | Module   | Nodes   |   Time (min) | GPUs?   | Host   |   # ranks |   # threads | Hyperthreading?   |   # Simulations |\n",
            "|--------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------|\n",
            "| md     | namd/123 | 1-5     |           15 | False   | draco  |        40 |           1 | False             |               1 |\n",
            "+--------+----------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n\n",
        )

        output2 = (
            "We will generate 5 benchmarks.\n"
            "Finished! You can submit the jobs with mdbenchmark submit.\n"
        )
        output = output1 + "".join(expected_output) + output2

        assert result.exit_code == 0
        assert result.output == output


def test_print_known_hosts(ctx_mock, capsys):
    """Test that the print_known_hosts function works as expected."""
    print_known_hosts(ctx_mock, None, True)
    out, _ = capsys.readouterr()

    assert out == "Available host templates:\ncobra\ndraco\nhydra\n"


def test_validate_generate_name(ctx_mock):
    """Test that the validate_generate_name function works as expected."""

    # Make sure we raise an exception if no name is given
    with pytest.raises(exceptions.BadParameter) as error:
        validate_name(ctx_mock, None)

    # Test the exception message
    assert str(error.value) == "Please specify the base name of your input files."

    # Make sure we return the module name, if we were given a name.
    assert validate_name(ctx_mock, None, "md") == "md"


def test_validate_generate_module(ctx_mock):
    """Test that the validate_generate_module function works as expected."""

    # Make sure we raise an exception if no module name was given
    with pytest.raises(exceptions.BadParameter) as error:
        validate_module(ctx_mock, None)

    # Test the exception message
    assert (
        str(error.value)
        == "Please specify which MD engine module to use for the benchmarks."
    )

    # Make sure we return the value again
    assert validate_module(ctx_mock, None, "gromacs/123") == "gromacs/123"


def test_validate_cpu_gpu_flags():
    """Test that the validate_cpu_gpu_flags function works as expected."""

    with pytest.raises(exceptions.BadParameter) as error:
        validate_cpu_gpu_flags(cpu=False, gpu=False)

    assert (
        str(error.value)
        == "You must select either CPUs or GPUs to run the benchmarks on."
    )

    assert validate_cpu_gpu_flags(cpu=True, gpu=False) is None
    assert validate_cpu_gpu_flags(cpu=False, gpu=True) is None
    assert validate_cpu_gpu_flags(cpu=True, gpu=True) is None


def test_validate_generate_number_of_nodes():
    """Test that the validate_generate_number_of_nodes function works as expected."""

    with pytest.raises(exceptions.BadParameter) as error:
        validate_number_of_nodes(min_nodes=6, max_nodes=5)

    assert (
        str(error.value)
        == "The minimal number of nodes needs to be smaller than the maximal number."
    )

    assert validate_number_of_nodes(min_nodes=1, max_nodes=6) is None


def test_validate_generate_host(ctx_mock):
    """Test that the validate_generate_host function works as expected."""

    # Test error without any hostname
    with pytest.raises(exceptions.BadParameter) as error:
        validate_hosts(ctx_mock, None)
    assert (
        str(error.value) == "Could not guess host. Please provide a value explicitly."
    )

    # Test error with non-existent hostname
    # TODO: We need to wrap this into a function!
    assert validate_hosts(ctx_mock, None, host="hercules") is None

    # Test success of existent hostname
    assert validate_hosts(ctx_mock, None, host="draco") == "draco"


def test_generate_prompt_yes(cli_runner, tmpdir):
    """Test whether promt answer yes works."""
    with tmpdir.as_cwd():
        open("protein.tpr", "a").close()

        result = cli_runner.invoke(
            cli,
            [
                "generate",
                "--module=gromacs/2016",
                "--host=draco",
                "--max-nodes=4",
                "--gpu",
                "--no-cpu",
                "--name=protein",
            ],
            input="y\n",
        )
        output1 = (
            "WARNING Cannot locate modules available on this host. Not performing module name validation.\n"
            "\n"
        )
        expected_output = (
            "+---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n"
            "| Name    | Module       | Nodes   |   Time (min) | GPUs?   | Host   |   # ranks |   # threads | Hyperthreading?   |   # Simulations |\n"
            "|---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------|\n"
            "| protein | gromacs/2016 | 1-4     |           15 | True    | draco  |        40 |           1 | False             |               1 |\n"
            "+---------+--------------+---------+--------------+---------+--------+-----------+-------------+-------------------+-----------------+\n\n",
        )

        output2 = (
            "We will generate 4 benchmarks. Continue? [y/N]: y\n"
            "Finished! You can submit the jobs with mdbenchmark submit.\n"
        )
        output = output1 + "".join(expected_output) + output2

        assert result.exit_code == 0
        assert result.output == output


def test_generate_test_prompt_no(cli_runner, tmpdir):
    """Test whether promt answer no works."""
    with tmpdir.as_cwd():
        open("protein.tpr", "a").close()

        result = cli_runner.invoke(
            cli,
            [
                "generate",
                "--module=gromacs/2016",
                "--host=draco",
                "--max-nodes=4",
                "--gpu",
                "--no-cpu",
                "--name=protein",
            ],
            input="n\n",
        )

        bundle = dtr.discover()
        assert result.exit_code == 1
        assert len(bundle) == 0
