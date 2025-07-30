from pathlib import Path
from subprocess import run
import sys
import os
from re import compile as re_compile
from re import sub as re_sub


def samples(repo: Path, pattern: str = ""):
    """
    Check the samples
    """
    from pathlib import Path
    import difflib
    from wowool.native.core.engine import Engine
    from wowool.native.core.engine import default_engine

    matcher = re_compile(f".*{pattern}")

    sys.path.append(str(repo))
    if "PYTHONPATH" in os.environ:
        os.environ["PYTHONPATH"] = f"{str(repo)}:{os.environ.get('PYTHONPATH', '')}"
    else:
        os.environ["PYTHONPATH"] = str(repo)
    engine: Engine = default_engine()
    language_info = engine.language_info
    if not language_info:
        raise RuntimeError("No language information available")
    language_info["lid"] = {}
    language_info["none"] = {}

    def get_language(fn: Path):
        return str(fn.name).split("-")[0]

    samples_dir = repo / "samples"

    files = sorted([fn for fn in samples_dir.glob("**/*.py") if not (str(fn).endswith("_setup.py") or str(fn).endswith("_cleanup.py"))])

    for fn in files:
        if not matcher.match(str(fn)):
            continue
        language = get_language(fn)
        if language not in language_info:
            print(f"Warning: Skipping '{fn.name}': language '{language}' not available")
            continue

        fn_setup = Path(str(fn).replace(".py", "_setup.py"))
        if fn_setup.exists():
            run(f"python {fn_setup}", check=True, shell=True, cwd=fn.parent)

        print(f"Running sample: {fn}")
        result = run(f"python {fn}", capture_output=True, shell=True, cwd=fn.parent)

        fn_cleanup = Path(str(fn).replace(".py", "_cleanup.py"))
        if fn_cleanup.exists():
            run(f"python {fn_cleanup}", check=True, shell=True, cwd=fn.parent)

        if result.returncode != 0:
            print(f"Error running {fn}: {result.stderr.decode()}")
            continue

        fn_skip_file = fn.with_suffix(".skip")
        if fn_skip_file.exists():
            print(f"Skipping comparison for {fn} as .skip file exists")
            continue

        result_stdout = result.stdout.decode()
        result_stdout = re_sub("""(@dev\\d*|@[0-9\\.]+[\\d]+)""", "", result_stdout)
        # print(f"Sample {fn} output:\n{result_stdout}")

        fn_ref = Path(str(fn).replace(".py", "-output.txt"))
        if fn_ref.exists():
            lines = [line for line in difflib.unified_diff(fn_ref.read_text(), result_stdout)]
            if 0 != len(lines):
                print("Unexpected output:")
                print(result_stdout)
                exit(-1)
        else:
            print(f"Reference file {fn_ref} does not exist, skipping comparison")
            print(f"stdout: {result_stdout}")
            fn_ref = Path(str(fn).replace(".py", "-output-result.txt"))
            fn_ref.write_text(result_stdout)
