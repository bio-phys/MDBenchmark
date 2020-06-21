import itertools

import pytest

from mdbenchmark.versions import VersionCategories, VersionFactory

CATEGORIES = {
    "VERSION_2": ["name", "started", "module", "host", "time", "gpu", "nodes"],
    "VERSION_3": [
        "name",
        "started",
        "module",
        "host",
        "time",
        "gpu",
        "nodes",
        "version",
    ],
}

IMPLEMENTED_VERSION_CLASSES = [cls for cls in VersionCategories.__subclasses__()]


def test_init_raises_exception():
    with pytest.raises(ValueError) as err:
        VersionFactory()

    assert "must be set" in str(err.value)


@pytest.mark.parametrize("version", ("2", "3"))
def test_version(version):
    obj = VersionFactory(version=version)
    assert obj.version == version


@pytest.mark.parametrize("version", ("2", "3"))
def test_guess_version(version):
    obj = VersionFactory(categories=CATEGORIES[f"VERSION_{version}"])
    assert obj.version == version


def test_version_class_zero_does_not_exist():
    obj = VersionFactory(version="0")
    assert obj.version_class is None


@pytest.mark.parametrize(
    "attribute",
    (
        "version",
        "consolidate_categories",
        "generate_categories",
        "generate_mapping",
        "generate_printing",
        "analyze_categories",
        "analyze_printing",
        "analyze_sort",
        "category_mapping",
    ),
)
def test_not_implemented(attribute):
    obj = VersionCategories()
    assert getattr(obj, attribute) == NotImplemented
