from pathlib import Path
from logging import getLogger

logger = getLogger(__name__)


def generate_long_description(fp: Path) -> None:
    """
    generate_long_description file .md
    """
    from re import sub, DOTALL, MULTILINE

    this_dir = fp
    docs_dir = this_dir / "docs/long_description"
    if not docs_dir.exists():
        raise FileNotFoundError(f"Directory {docs_dir} does not exist.")
    long_description = ""
    portal_doc_data_link_fn = docs_dir / "portal_doc.lnk"
    if portal_doc_data_link_fn.exists():
        print(f"- Adding portal doc data link: {portal_doc_data_link_fn}")
        portal_doc_data_link = portal_doc_data_link_fn.read_text().strip()
        portal_doc = this_dir / portal_doc_data_link
        if not portal_doc.exists():
            raise FileNotFoundError(f"File {portal_doc} does not exist.")
        portal_doc_data = portal_doc.read_text()

        portal_doc_data = sub(
            r"<div class=.*?<img src=\"markdown/docs/apps/(.*?)\.png\".*?</div>.*?</div>",
            r"![\1](https://www.wowool.com/markdown/docs/apps/\1.png)",
            portal_doc_data,
            flags=DOTALL | MULTILINE,
        )

        portal_doc_data += sub(r"## Examples.*?(?=^## |\Z)", "", portal_doc_data, flags=DOTALL | MULTILINE)
        portal_doc_data = portal_doc_data.replace("(docs/apps", "(https://www.wowool.com/docs/apps")
        long_description += portal_doc_data

    long_description_sdk_fn = docs_dir / "long_description_sdk.md"
    if long_description_sdk_fn.exists():
        print(f"- Adding : {long_description_sdk_fn}")
        long_description += long_description_sdk_fn.read_text()

    long_description_samples_fn = docs_dir / "long_description_samples.md"
    if long_description_samples_fn.exists():
        long_description_samples = long_description_samples_fn.read_text()
        print(f"- Adding : {long_description_samples_fn}")
        long_description += long_description_samples
        samples_dir = this_dir / "samples"
        if samples_dir.exists():
            for sample_md_fn in samples_dir.glob("*.md"):
                if sample_md_fn.stem.endswith("-output"):
                    continue
                print(f"- Adding : {sample_md_fn}")
                sample_description = sample_md_fn.read_text()
                sample_py = sample_md_fn.with_suffix(".py")
                sample_data = sample_py.read_text()
                long_description += "\n"
                long_description += sample_description
                long_description += f"\n\n```python\n{sample_data}\n```\n"
                output_fn = sample_md_fn.parent / f"{sample_md_fn.stem}-output.md"
                if output_fn.exists():
                    print(f"- Adding : {output_fn}")
                    output_data = output_fn.read_text()
                    long_description += "\n"
                    long_description += output_data
                    long_description += "\n"

        else:
            print(f"- Warning: No samples directory found in {samples_dir}")

    license_fn = this_dir / ".." / "wowool-license" / "public" / "docs" / "pypi_license.md"
    if license_fn.exists():
        print(f"- Adding : {license_fn}")
        license_data = license_fn.read_text()
        long_description += "\n\n"
        long_description += license_data
    else:
        print(f"- Warning: No license file found in {license_fn}")

    long_description_fn = this_dir / "long_description.md"
    print(f"- Writing : {long_description_fn}")
    long_description_fn.write_text(long_description)
