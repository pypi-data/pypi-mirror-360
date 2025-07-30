from os import environ
from pathlib import Path
from subprocess import run


from wowool.build.exceptions import UploadError


def _check_not_dirty(fn: Path):
    if "dirty" in fn.name:
        raise UploadError(f"Attempted to upload a dirty version: {fn}")


def upload_pypi(fp: Path, expression: str = "*", repository: str | None = None, test_pypy: bool = False):
    """
    Upload a Python package to pypi
    """
    if test_pypy:
        repository = "https://test.pypi.org/legacy/"
        environ["TWINE_USERNAME"] = environ.get("TWINE_TEST_USERNAME", "__token__")
        password = environ.get("TWINE_TEST_PASSWORD")
        if password is None:
            raise UploadError("TWINE_TEST_PASSWORD not set")
        environ["TWINE_PASSWORD"] = password
    else:
        repository = environ.get("TWINE_REPOSITORY", repository)
    fp_dist = fp / "dist"
    for fn in fp_dist.glob(expression):
        _check_not_dirty(fn)
        repository_option = f"--repository-url {repository}" if repository else ""
        cmd = f"python -m twine upload {repository_option} dist/{fn.name}"
        try:
            print(f"cmd: {cmd} {fn=} {fp_dist=}")
            run(cmd, shell=True, check=True, cwd=str(fp))
        except Exception as error:
            raise UploadError(f"PyPi Twine upload failed: {error}")
