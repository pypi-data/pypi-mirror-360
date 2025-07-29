from logging import getLogger, DEBUG
from os import chmod, getcwd, stat
from pathlib import Path
from shutil import rmtree
from stat import S_IEXEC
from subprocess import run
from sys import path as sys_path, prefix
from typing import Optional

logger = getLogger(__name__)
logger_cmd = getLogger("wowool.cmd")


def make_environment_entry_points(fp: Path):
    """
    Create the console scripts from the entry points defined in setup.py

    :param fp: Path to the folder holding setup.py
    """
    egg_dirs = [fp for fp in fp.glob("*.egg-info")]
    if not egg_dirs:
        raise RuntimeError("Missing *.egg-info directories")
    for egg_dir in egg_dirs:
        entry_points = egg_dir / "entry_points.txt"
        from configparser import ConfigParser

        configur = ConfigParser()
        configur.read(entry_points)
        try:
            console_scripts = configur["console_scripts"]
        except KeyError:
            raise RuntimeError("No console scripts defined in setup.py")
        for cs in console_scripts:
            fn_cs = Path(f"{prefix}/bin/{cs}")
            print(f"Added entry point {cs} as alias to {fn_cs}")
            (imp, func) = console_scripts[cs].split(":")
            sys_path.append(f"{Path(__file__).parent.parent.resolve()}/core-build-py")
            template = rf"""#!{prefix}/bin/python
import re
import sys
sys.path.append("{fp}")
for p in {sys_path}:
    sys.path.append(p)
from {imp} import {func}
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit({func}())
"""
            with open(fn_cs, "w") as fh:
                fh.write(template)
            st = stat(fn_cs)
            chmod(fn_cs, st.st_mode | S_IEXEC)


def get_install_requires(fp: Optional[Path] = None):
    """
    Return the contents of the install_requires*.txt files in the given path

    :param fp: Path containing the install_requires*.txt files. If not set, the
               current working directory is used
    """

    def is_valid(requirement: str) -> bool:
        return len(requirement) != 0 and not requirement.startswith("#")

    fp = fp if fp is not None else Path(getcwd())
    install_requires = []
    for fn in fp.glob("install_requires*.txt"):
        requirements = filter(is_valid, [line.strip() for line in open(fn).readlines()])
        install_requires.extend(requirements)
    return install_requires


def resolve_template(template, __globals, __locals):
    return eval("f'''" + template + "'''", __globals, __locals)


def build_wheel_package(fp: Path, no_deps: bool = True, build_isolation: bool = False):
    """
    Build a wheel package

    :param fp: Folder holding the requirement files
    """
    template_pyproject_fn = fp / "pyproject_template.toml"
    if template_pyproject_fn.exists():
        from wowool.build.git import get_version

        pyproject_fn = fp / "pyproject.toml"
        data = template_pyproject_fn.read_text()
        version = get_version(fp)
        dependencies = get_install_requires(fp)
        package_name: str = fp.name
        if package_name.startswith("comp-"):
            package_name = package_name[5:]
        if package_name.endswith("-py"):
            package_name = package_name[:-3]
        print(f"Package name is {package_name}")
        resolve_data = resolve_template(data, globals(), locals())
        pyproject_fn.write_text(resolve_data)

    options = []
    if not build_isolation:
        options.append("--no-isolation")
    # cmd = f"python -m pip wheel {' '.join(options)} -w dist ."
    cmd = f"python -m build --wheel {' '.join(options)} ."
    print(f"CMD: {cmd}")
    run(cmd, shell=True, check=True, cwd=fp)


def clean_package_build(fp: Path):
    """
    Clean the package build
    """
    for dir in [
        "build",
        "dist",
        "var",
    ] + list(fp.glob("*.egg-info")):
        rmtree(fp / dir, ignore_errors=True)
