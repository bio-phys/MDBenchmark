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
import os

import pytest

from mdbenchmark import cli
from mdbenchmark.ext.click_test import cli_runner
from mdbenchmark.mdengines import (
    detect_md_engine,
    get_available_modules,
    normalize_modules,
    prepare_module_name,
    validate_module_name,
)

DIR_STRUCTURE = {
    "applications": {
        "gromacs": ["2016.4", "5.1.4-plumed2.3", "2018.1"],
        "namd": ["123", "456"],
        "amber": ["13", "14", "15"],
    },
    "visualization": {"vmd": ["1.9.3", "1.9.4"]},
}


def test_prepare_module_name(capsys):
    """Test that prepare_module_name works as expected."""
    # Fail state
    with pytest.raises(SystemExit) as e:
        prepare_module_name("gromacs-2016.4")
        assert e.type == SystemExit
        assert e.code == 1

    out, err = capsys.readouterr()
    assert out == "ERROR We were not able to determine the module name.\n"

    # Second fail state
    with pytest.raises(SystemExit) as e:
        prepare_module_name("whatever", skip_validation=True)
        assert e.type == SystemExit
        assert e.code == 1

    out, err = capsys.readouterr()
    assert (
        out == "ERROR Although you are using the --skip-validation option, you have to "
        "provide a valid MD engine name, e.g., gromacs/dummy or namd/dummy.\n"
    )

    assert prepare_module_name("gromacs/2016.4")


@pytest.mark.parametrize(
    "arg, out",
    (
        ("gromacs/2016.3", "mdbenchmark.mdengines.gromacs"),
        ("namd/123", "mdbenchmark.mdengines.namd"),
        ("NAMD/123", "mdbenchmark.mdengines.namd"),
        ("NamD/123", "mdbenchmark.mdengines.namd"),
        ("GROMACS/123", "mdbenchmark.mdengines.gromacs"),
        ("GRomacS/123", "mdbenchmark.mdengines.gromacs"),
    ),
)
def test_detect_md_engine_supported(arg, out):
    """Test that we only accept supported MD engines."""
    engine = detect_md_engine(arg)
    assert engine.__name__ == out


def test_detect_md_engine_unkown():
    """Test that we return None for unkown engines"""
    engine = detect_md_engine("someengine/123")
    assert engine is None


def test_normalize_modules(capsys, monkeypatch, tmpdir):
    """Test that normalize modules works as expected."""
    # Test the warning when we skip the validation
    normalize_modules(modules=["gromacs/2016.4"], skip_validation=True)
    out, err = capsys.readouterr()
    assert out == "WARNING Not performing module name validation.\n"

    # Test the warning when we do not skip the validation
    normalize_modules(modules=["gromacs/2016.4"], skip_validation=False)
    out, err = capsys.readouterr()
    assert (
        out == "WARNING Cannot locate modules available on this host. "
        "Not performing module name validation.\n"
    )

    with tmpdir.as_cwd():
        for k, v in DIR_STRUCTURE.items():
            for k2, v2 in v.items():
                os.makedirs(os.path.join(k, k2))
                for v3 in v2:
                    open(os.path.join(k, k2, v3), "a").close()

        # Prepare path variable that we are going to monkeypatch for
        # `get_available_modules`
        dirs = ":".join([os.path.join(os.getcwd(), x) for x in os.listdir(os.getcwd())])
        monkeypatch.setenv("MODULEPATH", dirs)

        output = (
            "WARNING We have problems finding all of your requested modules on this host.\n"
            "We were not able to find the following modules for MD engine gromacs: "
            "doesnotexist.\n"
            "Available modules are:\n"
            "gromacs/2016.4\n"
            "gromacs/2018.1\n"
            "gromacs/5.1.4-plumed2.3\n\n"
        )

        normalize_modules(modules=["gromacs/doesnotexist"], skip_validation=False)
        out, err = capsys.readouterr()
        assert out == output


def test_validation(capsys, monkeypatch, tmpdir):
    """Test that we retrieve the correct module versions.

       Names are retrieved from a given path and the module names and versions
       are validated.
    """
    with tmpdir.as_cwd():
        for k, v in DIR_STRUCTURE.items():
            for k2, v2 in v.items():
                os.makedirs(os.path.join(k, k2))
                for v3 in v2:
                    open(os.path.join(k, k2, v3), "a").close()

        # Prepare path variable that we are going to monkeypatch for
        # `get_available_modules`
        dirs = ":".join([os.path.join(os.getcwd(), x) for x in os.listdir(os.getcwd())])
        monkeypatch.setenv("MODULEPATH", dirs)
        modules = get_available_modules()

        # Assert that the correct modules and their versions are returned.
        assert set(modules["gromacs"]) == set(["2016.4", "5.1.4-plumed2.3", "2018.1"])
        assert set(modules["namd"]) == set(["123", "456"])

        # Make sure we return a boolean if the module is available or not.
        assert not validate_module_name("gromacs/123", modules)
        assert validate_module_name("gromacs/2018.1", modules)

        output = "ERROR We were not able to determine the module name.\n"
        with pytest.raises(SystemExit) as e:
            validate_module_name("wrong=format")
            out, err = capsys.readouterr()

            assert e.type == SystemExit
            assert e.code == 1
            assert out == output


def test_generate_validation(cli_runner, tmpdir, monkeypatch):
    # Test that we get a warning, if the MD engine is unsupported.
    result = cli_runner.invoke(
        cli, ["generate", "--module=somehpc/123", "--host=draco", "--name=protein"]
    )
    output = (
        "ERROR There is currently no support for 'somehpc'. "
        "Supported MD engines are: gromacs, namd.\n"
    )

    # assert result.exit_code == 1
    assert result.output == output

    with tmpdir.as_cwd():
        for f in ["protein.tpr", "protein.namd", "protein.pdb", "protein.psf"]:
            with open(f, "w") as fh:
                fh.write("This is a dummy file.")
        for k, v in DIR_STRUCTURE.items():
            for k2, v2 in v.items():
                os.makedirs(os.path.join(k, k2))
                for v3 in v2:
                    open(os.path.join(k, k2, v3), "a").close()

        # Prepare path variable that we are going to monkeypatch for
        # `validate.get_available_modules`
        dirs = ":".join([os.path.join(os.getcwd(), x) for x in os.listdir(os.getcwd())])
        monkeypatch.setenv("MODULEPATH", dirs)

        # Test that we get a warning if we cannot find the requested modules.
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                "--module=gromacs/doesnotexist",
                "--host=draco",
                "--name=protein",
            ],
        )
        output = (
            "WARNING We have problems finding all of your requested modules on this host.\n"
            "We were not able to find the following modules for MD engine gromacs: "
            "doesnotexist.\n"
            "Available modules are:\n"
            "gromacs/2016.4\n"
            "gromacs/2018.1\n"
            "gromacs/5.1.4-plumed2.3\n"
            "\n"
            "ERROR No requested modules available!\n"
        )

        assert result.exit_code == 1
        assert result.output == output

        # Test that the warning also works when specifying several MD engines.
        # Test that we get a warning if we cannot find the requested modules.
        result = cli_runner.invoke(
            cli,
            [
                "generate",
                "--module=gromacs/doesnotexist",
                "--module=namd/abc",
                "--host=draco",
                "--name=protein",
            ],
        )
        output = (
            "WARNING NAMD support is experimental. "
            "All input files must be in the current directory. "
            "Parameter paths must be absolute. Only crude file checks are performed! "
            "If you use the --gpu option make sure you use the GPU compatible NAMD module!\n"
            "WARNING We have problems finding all of your requested modules on this host.\n"
            "We were not able to find the following modules for MD engine gromacs: "
            "doesnotexist.\n"
            "Available modules are:\n"
            "gromacs/2016.4\n"
            "gromacs/2018.1\n"
            "gromacs/5.1.4-plumed2.3\n"
            "We were not able to find the following modules for MD engine namd: abc.\n"
            "Available modules are:\n"
            "namd/123\n"
            "namd/456\n"
            "\n"
            "ERROR No requested modules available!\n"
        )

        assert result.exit_code == 1
        assert result.output == output
