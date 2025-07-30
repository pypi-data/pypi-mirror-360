from argparse import ArgumentParser
import docstring_parser
import ast
from pathlib import Path
import json
import sys
from dataclasses import dataclass, field, asdict
from logging import getLogger
from re import compile

logger = getLogger(__name__)


@dataclass
class ParamInfo:
    arg: str
    description: str | None = None
    type: str | None = None
    default: str | None = None


@dataclass
class ReturnsInfo:
    description: str | None = None
    type: str | None = None


@dataclass
class RaisesInfo:
    type: str | None = None
    description: str | None = None


@dataclass
class MethodInfo:
    name: str
    id: str
    params: list[ParamInfo] | None = None
    returns: ReturnsInfo | None = None
    short_description: str | None = None
    long_description: str | None = None
    raises: list[RaisesInfo] | None = None
    examples: list[str] | None = None
    notes: list[str] | None = None


@dataclass
class DocStringInfo:
    name: str
    id: str
    params: list[ParamInfo] | None = None
    returns: ReturnsInfo | None = None
    short_description: str | None = None
    long_description: str | None = None
    raises: list[RaisesInfo] | None = None
    decorators: list[str] = field(default_factory=list)  # List of decorator names
    examples: list[str] | None = None
    notes: list[str] | None = None


@dataclass
class PropertyInfo:
    name: str
    id: str
    returns: ReturnsInfo | None = None
    short_description: str | None = None
    long_description: str | None = None
    raises: list[RaisesInfo] | None = None
    examples: list[str] | None = None
    notes: list[str] | None = None


@dataclass
class ClassInfo:
    name: str
    id: str
    short_description: str | None = None  # Short description of the class
    long_description: str | None = None  # Long description of the class
    examples: list[str] | None = None
    notes: list[str] | None = None
    bases: list[str] | None = None
    methods: list[MethodInfo] | None = None  # Will contain MethodInfo objects
    property_methods: list[PropertyInfo] | None = None  # Will contain MethodInfo objects for properties
    static_methods: list[MethodInfo] | None = None
    params: list[ParamInfo] | None = None


@dataclass
class ModuleInfo:
    module: str
    file: str
    methods: list[MethodInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)  # Will contain class info with MethodInfo objects


def parse_arguments():
    """
    Parses the command line arguments.
    """
    parser = ArgumentParser(prog="extract docstrings")
    parser.add_argument("-f", "--file", nargs="+", required=True, help="files to process.")
    parser.add_argument(
        "-r",
        "--root",
        required=False,
        help="root directory to use for relative module names (default: current directory)",
    )
    parser.add_argument("-o", "--output", required=False, help="output file to write the JSON result")
    parser.add_argument("-x", "--exclude", required=False, nargs="+", help="exclude the give id of methods and classes")
    parser.add_argument("-n", "--remove_none_values", action="store_true", help="remove None values from the output JSON")
    return parser.parse_args()


def make_id(
    module_info: ModuleInfo,
    item_name: str,
    class_name: str | None = None,
) -> str:
    """
    Create a unique ID for the item based on the module file and item name.
    The ID is a combination of the module file path (without extension) and the item name.
    """
    name = module_info.module.replace(".", "-")
    if class_name:
        value = f"{name}-{class_name}-{item_name}"
    else:
        value = f"{name}-{item_name}"
    # value = value.lower().replace("_", "-")
    return value


WARNINGS = compile(r"""\*\*.*:\*\*|\.\. code\-block::""")


def find_first_none_whitespace(line: str) -> int:
    """
    Find the index of the first non-whitespace character in a line.
    Returns -1 if the line is empty or contains only whitespace.
    """
    for i, char in enumerate(line):
        if not char.isspace():
            return i
    return 0xFFFF  # Return a large value if no non-whitespace character is found


def unindent_lines(lines: list[str]):
    """
    Unindents a list of lines by removing the common leading whitespace.
    """
    if not lines:
        return lines
    # Find the minimum indentation level
    min_indent = find_first_none_whitespace(lines[0])
    # Remove the minimum indentation from each line
    retval = [line[min_indent:] for line in lines]
    return retval


def parse_docstrings(module_info: ModuleInfo, object_id: str, item, docstring: str, root: Path | None = None) -> DocStringInfo:
    parsed = docstring_parser.parse(trim(docstring))

    if not parsed.short_description:
        logger.warning(
            f"{module_info.file} module={module_info.module} item={item.name} has no short description in docstring.\n{docstring}"
        )
    decorators = [decorator.id for decorator in item.decorator_list if isinstance(decorator, ast.Name)]
    # Create ParamInfo objects for each parameter
    params = None
    if "property" not in decorators:
        params = []
        for param in parsed.params:
            params.append(
                ParamInfo(
                    arg=param.arg_name,
                    description=param.description,
                    type=param.type_name,
                    default=param.default,
                )
            )

    # Create returns info
    returns = None
    if parsed.returns:
        if not parsed.returns.description:
            logger.warning(
                f"{module_info.file}:{module_info.module} {item.name}\n{docstring} has no short description in `Returns:` docstring."
            )

        if not parsed.returns.type_name:
            raise ValueError(
                f"{module_info.file}: Has no type in or invalid format\n(note: the has to be directly attached !)\n`Returns:`  {module_info.module} {item.name}\n{docstring}"
            )

        returns = ReturnsInfo(
            description=parsed.returns.description,
            type=parsed.returns.type_name,
        )

    # Extract examples and notes from the raw docstring
    examples = []
    notes = []

    # Parse the raw docstring to extract examples and notes
    raw_docstring = trim(docstring)
    lines = raw_docstring.split("\n")

    current_section = None
    current_content = []

    for line in lines:
        stripped = line.strip()

        # Detect section headers
        if stripped.lower().startswith("example:") or stripped.lower().startswith("examples:"):
            # Save previous section
            if current_section == "note" and current_content:
                notes.append("\n".join(unindent_lines(current_content)).strip())
            elif current_section == "example" and current_content:
                examples.append("\n".join(unindent_lines(current_content)).strip())

            current_section = "example"
            current_content = []
            # Add content after "Example:" if any
            example_content = stripped[stripped.lower().find(":") + 1 :].strip()
            if example_content:
                current_content.append(example_content)

        elif stripped.lower().startswith("note:") or stripped.lower().startswith("notes:"):
            # Save previous section
            if current_section == "note" and current_content:
                notes.append("\n".join(unindent_lines(current_content)).strip())
            elif current_section == "example" and current_content:
                examples.append("\n".join(unindent_lines(current_content)).strip())

            current_section = "note"
            current_content = []
            # Add content after "Note:" if any
            note_content = stripped[stripped.lower().find(":") + 1 :].strip()
            if note_content:
                current_content.append(note_content)

        elif stripped.lower().startswith(("args:", "arguments:", "parameters:", "returns:", "return:", "raises:", "yields:", "yield:")):
            # Save current section and stop parsing examples/notes
            if current_section == "note" and current_content:
                notes.append("\n".join(unindent_lines(current_content)).strip())
            elif current_section == "example" and current_content:
                examples.append("\n".join(unindent_lines(current_content)).strip())
            current_section = None
            current_content = []

        elif current_section in ["example", "note"] and stripped:

            if stripped.startswith("""---"""):
                if current_section == "note" and current_content:
                    notes.append("\n".join(unindent_lines(current_content)).strip())
                elif current_section == "example" and current_content:
                    examples.append("\n".join(unindent_lines(current_content)).strip())
                current_content = []
            else:
                current_content.append(line)

        elif current_section in ["example", "note"] and not stripped and current_content:
            # Empty line might continue the section or end it
            current_content.append("")

    # Save any remaining content
    if current_section == "note" and current_content:
        notes.append("\n".join(unindent_lines(current_content)).strip())
    elif current_section == "example" and current_content:
        examples.append("\n".join(unindent_lines(current_content)).strip())

    # Additional note extraction from meta sections (if available)
    if hasattr(parsed, "meta") and parsed.meta:
        for meta in parsed.meta:
            if meta.args and len(meta.args) > 0 and meta.args[0].lower() == "note":
                if meta.description not in notes:
                    notes.append(meta.description)

    if WARNINGS.findall(raw_docstring):
        fn = Path(module_info.file) if root is None else Path(root / module_info.file)
        logger.warning(
            f"{fn}:{item.lineno}:{item.end_lineno} {module_info.module=} {item.name} contains '.. code-block::' or **...** which is not supported. "
        )

    # Create raises info
    raises = None
    if parsed.raises:
        raises = [RaisesInfo(type=r.type_name, description=r.description) for r in parsed.raises]

    if not notes:
        notes = None
    if not examples:
        examples = None
    if not raises:
        raises = None
    if not params:
        params = None
    retval = DocStringInfo(
        name=item.name,
        id=object_id,
        params=params,
        returns=returns,
        short_description=parsed.short_description,
        long_description=parsed.long_description,
        raises=raises,
        decorators=decorators,
        examples=examples,
        notes=notes,
    )

    return retval


def _to_method(doc_str: DocStringInfo) -> MethodInfo:
    method = MethodInfo(
        name=doc_str.name,
        id=doc_str.id,
        params=doc_str.params,
        returns=doc_str.returns,
        short_description=doc_str.short_description,
        long_description=doc_str.long_description,
        raises=doc_str.raises or [],
        examples=doc_str.examples,
        notes=doc_str.notes,
    )
    return method


def _to_property(doc_str: DocStringInfo) -> PropertyInfo:
    property = PropertyInfo(
        name=doc_str.name,
        id=doc_str.id,
        returns=doc_str.returns,
        short_description=doc_str.short_description,
        long_description=doc_str.long_description,
        raises=doc_str.raises or [],
        examples=doc_str.examples,
        notes=doc_str.notes,
    )
    return property


def trim(docstring):
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return "\n".join(trimmed)


def get_module_name(filename: Path, root: Path | None = None):
    """
    Get the module name from a file path.
    If root is provided, it will be used to determine the relative path.
    """
    if root:
        filename = filename.relative_to(root)
    parts = list(filename.parts)
    if parts[0] == "/":
        # If the first part is a root directory, we can ignore it for module naming
        parts = parts[1:]
    if parts[-1] == "__init__.py":
        # If the file is __init__.py, return the parent directory as the module name
        parts = parts[:-1]  # Remove the __init__.py from the parts
    else:
        parts[-1] = Path(parts[-1]).stem  # Remove the filename part
    return ".".join(parts)  # Join the parent directories as the module name


def has_decorator(node, decorator_name):
    """
    Check if the given AST node has a specific decorator.
    """
    if not hasattr(node, "decorator_list"):
        return False
    return any(decorator.id == decorator_name for decorator in node.decorator_list if isinstance(decorator, ast.Name))


PRIVATE = compile("^_[a-zA-Z0-9][a-zA-Z0-9_]*$")  # Regex to match private names


def is_private(exclude_pattern, node, id: str | None = None):
    """
    Check if the given AST node is a private class or function.
    """
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        if exclude_pattern and id is not None:
            test = exclude_pattern.match(id)
            # print(f"Exclude pattern match: {exclude_pattern} {id} {test}")
            if test:
                logger.warning(f"Excluded: `{node.name}` is excluded by pattern `{exclude_pattern.pattern}`")
                return True

        value = PRIVATE.match(node.name) or has_decorator(node, "private")
        # print(f"Checking if {node.name} is private: {value}")
        return value
    return False


def _remove_none_values(obj):
    """Recursively remove keys with None values from dictionaries."""
    if isinstance(obj, dict):
        return {k: _remove_none_values(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [_remove_none_values(item) for item in obj if item is not None]
    else:
        return obj


def docstring_to_json(
    filename: Path, root: Path | None = None, output: Path | None = None, exclude: list[str] | None = None, remove_none_values: bool = True
):

    exclude_pattern = None
    if exclude is not None:
        exclude_pattern = compile(f"""^{"|".join(exclude)}$""")
    # Load the module to get its actual name
    module_name = get_module_name(filename, root)  # Default to filename without extension

    file_path = filename if root is None else filename.relative_to(root)
    data: str = Path(filename).read_text(encoding="utf-8")

    # Initialize ModuleInfo
    module_info = ModuleInfo(module=module_name, file=str(file_path))
    tree = ast.parse(data)
    logger.debug(f"Parsed AST: {module_name} , from {file_path}")

    # Process only top-level nodes to avoid duplicates
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if is_private(exclude_pattern, node):
                # Skip private classes
                continue
            # print(f"Function: {node.name}")
            docstring = ast.get_docstring(node)
            if docstring:
                # print(f"  Docstring: {docstring}")
                object_id = make_id(module_info, node.name)

                doc_string_info = parse_docstrings(module_info, object_id, node, docstring, root)
                module_info.methods.append(_to_method(doc_string_info))
                # print(f"Docstring:\n {json.dumps(doc_string_info, indent=2)}")
            # else:
            #     print(f"  Function: {node.name} - No docstring")
        # elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
        elif isinstance(node, ast.ClassDef):
            # print(f"Class: {node.name}")
            if is_private(exclude_pattern, node):
                # Skip private classes
                continue
            class_info = ClassInfo(name=node.name, id=make_id(module_info, node.name))
            docstring = ast.get_docstring(node)
            if docstring:
                object_id = make_id(module_info, node.name)
                doc_string_info = parse_docstrings(module_info, object_id, node, docstring, root)
                class_info.short_description = doc_string_info.short_description
                class_info.long_description = doc_string_info.long_description
                class_info.examples = doc_string_info.examples
                class_info.notes = doc_string_info.notes
                class_info.params = doc_string_info.params
            if node.bases:
                class_info.bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
            for item in node.body:

                if isinstance(item, ast.FunctionDef):

                    object_id = make_id(module_info, item.name, class_name=node.name)
                    # print(f"Method: {item.name} - ID: {object_id}")
                    if is_private(exclude_pattern, item, object_id):
                        # Skip private methods
                        continue

                    docstring = ast.get_docstring(item)
                    if docstring:
                        # print(f"  Method: {item.name} - {docstring}")

                        doc_string_info = parse_docstrings(module_info, object_id, item, docstring, root)
                        if "property" in doc_string_info.decorators:
                            if class_info.property_methods is None:
                                class_info.property_methods = []
                            class_info.property_methods.append(_to_property(doc_string_info))
                        elif "staticmethod" in doc_string_info.decorators:
                            if class_info.static_methods is None:
                                class_info.static_methods = []
                            class_info.static_methods.append(_to_method(doc_string_info))
                        else:
                            if class_info.methods is None:
                                class_info.methods = []
                            class_info.methods.append(_to_method(doc_string_info))
                        # print(f"Docstring:\n {json.dumps(doc_string_info, indent=2)}")
                # else:
                # print(f"  !!! Method: {item} - No docstring")
                #     print(f"  Method: {item.name} - No docstring")
            module_info.classes.append(class_info)
            class_info = None

    module_data = asdict(module_info)
    clean_data = _remove_none_values(module_data) if remove_none_values else module_data
    json_string = json.dumps(clean_data, indent=2)
    if output:
        dir = Path(output)
        filename = Path(filename)
        if root:
            filename = filename.relative_to(Path(root))
        else:
            filename = Path(filename)
        filename = dir / filename.with_suffix(".json")
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(json_string, encoding="utf-8")
        print(f"To Json: {filename}")
    else:

        logger.debug(f"Module Info as JSON:\n{json_string}")


def main():

    args = parse_arguments()
    args.file = [Path(f) for f in args.file]
    for fn in args.file:
        if not fn.exists():
            raise FileNotFoundError(f"File {fn} does not exist.")
        docstring_to_json(
            filename=fn,
            root=Path(args.root) if args.root else None,
            output=Path(args.output) if args.output else None,
            exclude=args.exclude if args.exclude else None,
            remove_none_values=args.remove_none_values,
        )


if __name__ == "__main__":
    main()
