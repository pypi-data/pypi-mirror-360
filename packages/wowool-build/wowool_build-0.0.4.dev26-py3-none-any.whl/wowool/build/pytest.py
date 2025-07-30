import ast
from difflib import unified_diff
from logging import getLogger
from os import environ, pathsep, sep
from pathlib import Path
import re
from subprocess import check_output, run
from typing import Callable, List, Optional
from unittest import TestLoader, TestResult, TestSuite, TextTestRunner, skipIf

from contextlib import contextmanager
from importlib import reload
from io import StringIO
import sys
from typing import Optional


logger = getLogger(__name__)


# Test environment
def is_ci_environment():
    return "CI" in environ and not environ["CI"].lower() in ("0", "false")


# Unit-test skip decorators
skipIfCI = skipIf(is_ci_environment(), "CI environment detected")
skipIfNotCI = skipIf(not is_ci_environment(), "CI environment not detected")


class UnittestError(RuntimeError):
    def __init__(self, result: TestResult):
        self.result = result
        message = f"Unit-test(s) failed: {len(result.errors)} errors and {len(result.failures)} failures"
        super(UnittestError, self).__init__(message)


def get_unittest_names(
    fp: Path,
    pattern_include: str = "",
    pattern_exclude: Optional[str] = "",
):
    names: List[str] = []
    files = [fn for fn in fp.glob("tests/**/test_*.py")]
    for filename in files:
        node = ast.parse(filename.read_text())
        offset = 0 if str(fp).endswith("/") else 1
        module_name = str(filename.with_suffix(""))[len(str(fp)) + offset :].replace(sep, ".")
        classes = [n for n in node.body if isinstance(n, ast.ClassDef)]

        for class_ in classes:
            methods = [n for n in class_.body if isinstance(n, ast.FunctionDef)]
            for method in methods:
                if method.name.startswith("test_"):
                    names.append(f"{module_name}.{class_.name}.{method.name}")

    matcher_include = re.compile(f".*{pattern_include}")
    names = [name for name in names if matcher_include.match(name)]
    if pattern_exclude:
        matcher_exclude = re.compile(f".*{pattern_exclude}")
        names = [name for name in names if not matcher_exclude.match(name)]
    return sorted(names)


def get_unittest_suite(
    fp: Path,
    pattern_include: str = "",
    pattern_exclude: Optional[str] = "",
) -> TestSuite:
    tests = get_unittest_names(fp, pattern_include, pattern_exclude)
    return TestLoader().loadTestsFromNames(tests)


def list_unittest_tests(fp: Path, printer: Callable[[str], None] = print, pattern_include: str = "", pattern_exclude: Optional[str] = ""):
    """
    List the unit tests found in the given directory

    :param fp: Search directory
    :param printer: Printer function that accepts a string
    """
    printer("\n".join(get_unittest_names(fp, pattern_include, pattern_exclude)))


def run_unittest_tests(
    fp: Path, verbosity: int, failfast: bool, pattern_include: str = "", pattern_exclude: Optional[str] = "", exit_on_error: bool = True
) -> TestResult:
    """
    Run the unittest tests found in the given directory

    :param fp: Search directory
    :param verbosity: Verbosity level
    :param failfast: Fail on first error
    :param pattern: Only run tests matching the given pattern
    :param exit_on_error: Exit directly in case of a failure, otherwise raise an error
    """

    suite = get_unittest_suite(fp, pattern_include, pattern_exclude)
    result = TextTestRunner(verbosity=verbosity, failfast=failfast).run(suite)
    if not result.wasSuccessful():
        if exit_on_error:
            exit(1)
        else:
            raise UnittestError(result)
    return result


def run_unittest_samples(fp: Path, pattern: str = ""):
    """
    Check the samples
    """
    matcher = re.compile(f".*{pattern}")
    pypath = f"{pathsep}{environ['PYTHONPATH']}" if "PYTHONPATH" in environ else ""
    environ["PYTHONPATH"] = f"{str(fp)}{pypath}"
    samples_dir = fp / "samples"
    files = sorted([fn for fn in samples_dir.glob("**/*.py") if not (str(fn).endswith("_setup.py") or str(fn).endswith("_cleanup.py"))])
    for fn in files:
        if matcher.match(str(fn)):
            print(f"Running sample: {fn}")

            fn_setup = Path(str(fn).replace(".py", "_setup.py"))
            if fn_setup.exists():
                run(f"python {fn_setup}", check=True, shell=True, cwd=fn.parent)

            out_data = check_output(f"python {fn}", shell=True, cwd=fn.parent).decode().strip()
            logger.debug(f"{fn} stdout:[{out_data}]")

            fn_ref = Path(str(fn).replace(".py", "_output.txt"))
            if fn_ref.exists():
                expected_data = fn_ref.read_text().strip()
                lines = [line for line in unified_diff(expected_data, out_data)]
                if 0 != len(lines):
                    raise RuntimeError(f"Unexpected output:\n[{expected_data}]\n!=\n[{out_data}]")

            fn_cleanup = Path(str(fn).replace(".py", "_cleanup.py"))
            if fn_cleanup.exists():
                run(f"python {fn_cleanup}", check=True, shell=True, cwd=fn.parent)


@contextmanager
def capture_stream(stream: str = "stdout"):
    stream_original = getattr(sys, stream)
    stream_captured = StringIO()
    setattr(sys, stream, stream_captured)
    reload(sys)
    try:
        yield stream_captured
    finally:
        sys.stdout = stream_original
        reload(sys)
