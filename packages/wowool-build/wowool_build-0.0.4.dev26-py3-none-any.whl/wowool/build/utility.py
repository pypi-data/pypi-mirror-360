from contextlib import contextmanager
from os import chdir, getcwd
from pathlib import Path
from typing import Union


def ask(question, default: bool = True) -> bool:
    """
    Ask a simple yes/no question

    :param question: The question to present to the user
    :param default: The default answer to assume if no valid answer is provided
    """
    postfix = "Y/n" if default else "y/N"
    while True:
        answer = input(question + " [{}] ".format(postfix)).lower()
        if "" == answer:
            return default
        elif "y" == answer:
            return True
        elif "n" == answer:
            return False


@contextmanager
def in_cwd(fp: Union[Path, str]):
    """
    Temporarily change the working directory

    :param fp: The folder to change to
    """
    oldpwd = getcwd()
    chdir(str(fp))
    try:
        yield
    finally:
        chdir(oldpwd)
