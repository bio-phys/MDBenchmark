from mdbenchmark import console


class VersionCategories:
    version = NotImplemented
    consolidate_categories = NotImplemented
    generate_categories = NotImplemented
    generate_mapping = NotImplemented
    generate_printing = NotImplemented
    analyze_categories = NotImplemented
    analyze_printing = NotImplemented
    analyze_sort = NotImplemented
    category_mapping = NotImplemented

    def __getattr__(self, attr):
        return self.__getattribute__(attr)


class Version2Categories(VersionCategories):
    version = "2"
    consolidate_categories = [
        "module",
        "host",
        "gpu",
    ]
    analyze_categories = [
        "module",
        "nodes",
        "ns/day",
        "time",
        "gpu",
        "host",
        "ncores",
        "number_of_ranks",
        "number_of_threads",
        "hyperthreading",
        "version",
    ]
    analyze_printing = [
        "module",
        "nodes",
        "ns/day",
        "time",
        "gpu",
        "host",
        "ncores",
        "number_of_ranks",
        "number_of_threads",
        "hyperthreading",
    ]
    analyze_sort = ["module", "gpu", "nodes"]
    generate_printing = [
        "name",
        "module",
        "nodes",
        "time",
        "gpu",
        "host",
        "number_of_ranks",
        "number_of_threads",
        "hyperthreading",
    ]
    submit_categories = [
        "module",
        "nodes",
        "time",
        "gpu",
        "host",
        "ncores",
        "number_of_ranks",
        "number_of_threads",
        "hyperthreading",
        "version",
    ]
    category_mapping = {
        "name": "Name",
        "engine": "Engine",
        "module": "Module",
        "nodes": "Nodes",
        "ns/day": "Performances (ns/day)",
        "time": "Time (min)",
        "gpu": "GPUs?",
        "host": "Host",
        "ncores": "# cores",
        "number_of_ranks": "# ranks",
        "number_of_threads": "# threads",
        "hyperthreading": "Hyperthreading?",
        "job_name": "Job name",
        "submitted": "Submitted?",
    }


class Version3Categories(VersionCategories):
    version = "3"
    consolidate_categories = [
        "module",
        "host",
        "use_gpu",
        "number_of_ranks",
        "hyperthreading",
        "multidir",
    ]
    generate_categories = [
        "name",
        "job_name",
        "base_directory",
        "host",
        "engine",
        "module",
        "nodes",
        "time",
        "use_gpu",
        "template",
        "number_of_ranks",
        "number_of_threads",
        "hyperthreading",
        "multidir",
    ]
    generate_mapping = {
        "engine": "engine",
        "base_directory": "base_directory",
        "template": "template",
        "nodes": "nodes",
        "use_gpu": "gpu",
        "module": "module",
        "job_name": "job_name",
        "host": "host",
        "time": "time",
        "number_of_ranks": "number_of_ranks",
        "number_of_threads": "number_of_threads",
        "hyperthreading": "hyperthreading",
        "multidir": "multidir",
    }
    generate_printing = [
        "name",
        "module",
        "nodes",
        "time",
        "use_gpu",
        "host",
        "number_of_ranks",
        "number_of_threads",
        "hyperthreading",
        "multidir",
    ]
    analyze_categories = [
        "module",
        "nodes",
        "performance",
        "time",
        "use_gpu",
        "host",
        "ncores",
        "number_of_ranks",
        "number_of_threads",
        "hyperthreading",
        "version",
    ]
    analyze_printing = [
        "module",
        "nodes",
        "performance",
        "time",
        "use_gpu",
        "host",
        "ncores",
        "number_of_ranks",
        "number_of_threads",
        "hyperthreading",
    ]
    analyze_sort = ["module", "number_of_ranks", "hyperthreading", "use_gpu", "nodes"]
    submit_categories = [
        "module",
        "nodes",
        "time",
        "use_gpu",
        "host",
        "ncores",
        "number_of_ranks",
        "number_of_threads",
        "hyperthreading",
        "version",
    ]
    category_mapping = {
        "name": "Name",
        "engine": "Engine",
        "module": "Module",
        "nodes": "Nodes",
        "performance": "Performances (ns/day)",
        "time": "Time (min)",
        "use_gpu": "GPUs?",
        "host": "Host",
        "ncores": "# cores",
        "number_of_ranks": "# ranks",
        "number_of_threads": "# threads",
        "hyperthreading": "Hyperthreading?",
        "job_name": "Job name",
        "submitted": "Submitted?",
        "multidir": "# sims",
    }


VERSIONS = [Version2Categories(), Version3Categories()]


class VersionFactory:
    """Factory class that provides access to categories needed at different lifecycles.

    It tries to determine the version given some categories or uses an initial version value."""

    def __init__(self, categories=None, version=None):
        if categories is None and version is None:
            raise ValueError("Either `categories` or `version` must be set.")

        if categories is not None:
            self._guess_version(categories)

        if version is not None:
            self.version = version

    def _guess_version(self, categories):
        console.info("Setting up...")
        try:
            if "module" in categories and "version" in categories:
                # Versions >=3 have both a "module" and "version" key
                self.version = "3"
            elif "module" in categories:
                # Version 2 uses "module", but has no "version" key
                self.version = "2"
            else:
                # We found a version that is not enumerated above
                self.version = "next"
        except TypeError:
            # If we point datreant to an empty or non-existent directory, it
            # will throw an error. Catch it and set some default version.
            self.version = "3"

    @property
    def version_class(self):
        matches = [cls for cls in VERSIONS if cls.version == self.version]

        if len(matches) == 0:
            return None

        return matches[0]
