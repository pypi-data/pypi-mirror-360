from argparse import ArgumentParser
import docstring_parser
import ast
from pathlib import Path
import json
import sys
from dataclasses import dataclass, field, asdict
from logging import getLogger
from collections import defaultdict
from re import sub, compile

logger = getLogger(__name__)


def parse_arguments():
    """
    Parses the command line arguments.
    """
    parser = ArgumentParser(prog="extract docstrings")
    parser.add_argument("-f", "--file", nargs="+", required=True, help="the json files to process.")
    parser.add_argument("-p", "--prefix", required=False, help="prefix when resolving links", default="{{url}}#")
    parser.add_argument("-o", "--output", required=False, help="output file to write the JSON result")
    return parser.parse_args()


@dataclass
class LinkInfo:
    id: str
    filename: Path


def load_files(files: list[Path], prefix: str, root: Path | None = None) -> dict:
    data = {}
    for file in files:
        fn = file.relative_to(root) if root else file
        module = json.loads(file.read_text())
        for item in module.get("classes", []):
            id = f"{prefix}{item['id']}"
            li = LinkInfo(id=id, filename=fn.with_suffix(".md"))
            data[item["name"]] = li
            data[id] = li
    return data


def substitute_links(text: str, data: dict) -> str:
    """
    Substitute class names in backticks with their full qualified names.

    Args:
        text (str): The text to process
        data (dict): Dictionary mapping class names to their full qualified names

    Returns:
        str: Text with substituted links
    """
    if not text:
        return text

    # Create pattern to match class names in backticks
    keys = [f"`{key}`" for key in data.keys() if key]
    if not keys:
        return text

    pattern = compile(r"|".join(keys))

    def replace_match(match):
        matched_text = match.group(0)
        # Remove backticks from the matched text to get the class name
        class_name = matched_text.strip("`")
        # Get the full qualified name(s) for this class
        li = data.get(class_name)
        if not li:
            return matched_text
        full_name = li.id
        if "{{markdown_filename}}" in full_name:
            full_name = full_name.replace("{{markdown_filename}}", str(li.filename).replace("/", "_"))

        return f"[{matched_text}]({full_name})"

    return sub(pattern, replace_match, text)


def resolve_links(files: list[Path], output: Path, prefix: str = "{{url}}#", root: Path | None = None):

    data = load_files(files, prefix, root)
    # for key, values in data.items():
    #     print(f"  {key}: {values}")

    # Process each file and substitute links
    for file in files:
        # print(f"\nProcessing file: {file}")
        module = json.loads(file.read_text())

        # Process classes and their methods
        if "classes" in module:
            for class_info in module["classes"]:
                # Process methods
                if "methods" in class_info:
                    for method in class_info["methods"]:
                        if "long_description" in method and method["long_description"]:
                            original = method["long_description"]
                            substituted = substitute_links(original, data)
                            if original != substituted:
                                print(f"    Method {method['name']}: substituted links")
                                method["long_description"] = substituted

                        if "short_description" in method and method["short_description"]:
                            original = method["short_description"]
                            substituted = substitute_links(original, data)
                            if original != substituted:
                                method["short_description"] = substituted

        # Process module-level methods
        if "methods" in module:
            for method in module["methods"]:
                if "long_description" in method and method["long_description"]:
                    original = method["long_description"]
                    substituted = substitute_links(original, data)
                    if original != substituted:
                        print(f"    Function {method['name']}: substituted links")
                        method["long_description"] = substituted

                if "short_description" in method and method["short_description"]:
                    original = method["short_description"]
                    substituted = substitute_links(original, data)
                    if original != substituted:
                        method["short_description"] = substituted

        # Write the updated module
        if output:
            ofn = file.relative_to(root) if root else file
            ofn = str(ofn).replace("/", "_")
            output_file = Path(output) / ofn
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(json.dumps(module, indent=2))
            print(f"Resolved: {output_file}")
        else:
            print(f"    Updated JSON:\n{json.dumps(module, indent=2)}")


def main():
    args = parse_arguments()
    args.file = [Path(f) for f in args.file]
    resolve_links(args.file, args.output, args.prefix)


if __name__ == "__main__":
    main()
