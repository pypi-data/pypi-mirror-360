from os import getcwd
from pathlib import Path
from typing import Union

from invoke.collection import Collection
from invoke.tasks import task


def create_py_tasks(fp_root: Union[str, Path, None] = None) -> Collection:
    fp_root = Path(fp_root) if fp_root is not None else Path(getcwd())
    if fp_root.is_file():
        fp_root = fp_root.parent

    @task
    def version(_):
        """
        Print the version from Git
        """
        from wowool.build.git import get_version

        print(get_version(fp_root))

    @task
    def test(
        _,
        verbosity: int = 2,
        failfast: bool = True,
        list: bool = False,
        expression: str = "",
        xclude: str = "",
    ):
        """
        Run the Python unit-tests
        """
        from wowool.build.pytest import list_unittest_tests, run_unittest_tests

        (
            list_unittest_tests(
                fp_root,
                pattern_include=expression,
                pattern_exclude=xclude,
            )
            if list
            else run_unittest_tests(
                fp_root,
                verbosity=verbosity,
                failfast=failfast,
                pattern_include=expression,
                pattern_exclude=xclude,
            )
        )

    @task
    def clean(_):
        """
        Clean the Python package build
        """
        from wowool.build.pydist import clean_package_build

        clean_package_build(fp_root)

    @task(pre=[clean])
    def build(_, no_deps: bool = True):
        """
        Build the Python package
        """
        from wowool.build.pydist import build_wheel_package

        build_wheel_package(fp_root, no_deps)

    @task(aliases=("mep",))
    def make_entry_points(_):
        """
        Make entry points to the Python CLIs
        """
        from wowool.build.pydist import make_environment_entry_points

        make_environment_entry_points(fp_root)

    @task
    def upload(_, expression="wowool*"):
        """
        Upload the Python package to pypi
        """
        from wowool.build.pypi import upload_pypi

        upload_pypi(fp_root, expression=expression)

    @task
    def upload_pypi(_, expression: str = "wowool*", repository: str | None = None, test_pypy: bool = False):
        """Uploading the Python package to pypi"""
        from wowool.build.pypi import upload_pypi

        upload_pypi(fp_root, expression=expression, repository=repository, test_pypy=test_pypy)

    @task(aliases=("gld",))
    def generate_long_description(_):
        """
        Generate the long description for the Python package
        """
        from wowool.build.long_description import generate_long_description

        generate_long_description(fp_root)

    @task
    def samples(_):
        """
        run the samples
        """
        from wowool.build.samples import samples

        samples(fp_root)

    @task
    def build_docs(_, markdown: bool = False, upload: bool = False):
        from wowool.build.docstrings.extract_docstrings import extract_docstrings

        extract_docstrings(fp_root, markdown=markdown, upload=upload)

    return Collection(
        version,
        test,
        clean,
        build,
        make_entry_points,
        upload,
        upload_pypi,
        generate_long_description,
        samples,
        build_docs,
    )


# Allow both default Invoke namespaces to be available for import
ns = create_py_tasks()
namespace = ns
