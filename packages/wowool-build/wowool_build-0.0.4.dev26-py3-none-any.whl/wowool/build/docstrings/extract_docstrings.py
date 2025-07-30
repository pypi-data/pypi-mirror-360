import json
from pathlib import Path
from wowool.build.docstrings.tojson import docstring_to_json
from wowool.build.docstrings.resolve_links import resolve_links
from wowool.build.docstrings.json_to_markdown import to_markdown
from shutil import rmtree
import tarfile
from wowool.build.git import upload_raw, ensure_latest_release, move_and_push_tag


def build_json(module, root, output):
    for fn in module["files"]:
        docstring_to_json(
            filename=fn,
            root=root,
            output=output,
            exclude=module["exclude"],
            remove_none_values=True,
        )


def build_resolve_links(build_folder, dist_folder, prefix: str):
    files = [Path(fn) for fn in build_folder.glob("**/*.json")]
    resolve_links(files=files, output=dist_folder, prefix=prefix, root=build_folder)


def build_markdown(dist_folder: Path, markdown_folder: Path):
    markdown_folder.mkdir(parents=True, exist_ok=True)
    files = [Path(fn) for fn in dist_folder.glob("**/*.json")]
    for fn in files:
        to_markdown(
            filename=fn,
            root=dist_folder,
            output=markdown_folder,
        )


def extract_docstrings(fp_root: str | Path, markdown: bool = False, upload: bool = False):
    """
    Extract docstrings from the Python package and save them to a file.

    Args:
        fp_root (str | Path): The root path of the Python package.
    """

    wowool_folder = Path(fp_root)
    wowool_folder = wowool_folder.resolve()
    build_folder = wowool_folder / "build-docstrings"
    build_json_folder = build_folder / "json"

    dist_folder = build_folder / "dist"

    dist_markdown = build_folder / "dist-markdown"
    markdown_folder = build_folder / "markdown"

    doc_config_filename = wowool_folder / "doc-config.json"
    if not doc_config_filename.exists():
        raise FileNotFoundError(f"Configuration file not found: {doc_config_filename}")
    doc_config = json.loads(doc_config_filename.read_text(encoding="utf-8"))
    doc_config["fp_root"] = str(wowool_folder)
    if "files" not in doc_config:
        doc_config["files"] = [Path(fn) for fn in wowool_folder.glob("wowool/**/*.py") if fn.is_file()]
    else:
        files = []
        for expression in doc_config["files"]:
            print("Searching for files with expression:", expression, wowool_folder)
            files.extend(list(wowool_folder.glob(expression)))
        doc_config["files"] = files
    print(doc_config)
    build_json(doc_config, wowool_folder, build_json_folder)
    # build_resolve_links(build_json_folder, dist_folder, prefix="{{url}}#")

    # rmtree(build_json_folder, ignore_errors=True)
    if markdown:
        build_resolve_links(build_json_folder, dist_markdown, prefix="{{markdown_filename}}#")
        build_markdown(dist_markdown, markdown_folder)

    tar_fn = build_folder / "docstrings-json.tar.gz"
    with tarfile.open(tar_fn, "w:gz") as tar:
        for file in build_json_folder.glob("**/*.json"):
            tar.add(file, arcname=file.relative_to(build_json_folder))
    print(f"Docstrings extracted to {build_folder / 'docstrings-json.tar.gz'}")
    if upload:
        repo = f"wowool/{wowool_folder.name}"
        version = "latest"

        try:
            move_and_push_tag("latest", fp_repo=wowool_folder, force=True)

            # Ensure the 'latest' release exists before uploading
            print(f"Ensuring 'latest' release exists for {repo}...")
            if not ensure_latest_release(repo):
                print(f"❌ Failed to ensure 'latest' release exists for {repo}")
                return

            upload_raw(
                repo,
                version=version,
                file_path=tar_fn,
                overwrite=True,
            )
        except Exception as e:
            print(f"❌ Error uploading to GitHub: {e}")
            print(f"📁 Docstrings are still available locally at: {tar_fn}")
            # Don't raise the exception - continue execution

    # tar_fn.unlink()
