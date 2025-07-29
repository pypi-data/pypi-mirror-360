import argparse
import ast
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument("--dir", required=True)
args = parser.parse_args()


print(f"Directory: {args.dir}")  # noqa: T201

PACKAGE_DIR = pathlib.Path(args.dir)
INIT_FILE = PACKAGE_DIR / "__init__.py"


def get_public_functions_from_file(py_file: pathlib.Path) -> list[str]:
    """Return public function names from a Python file."""
    source = py_file.read_text()
    tree = ast.parse(source)
    return [node.name for node in tree.body if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")]


def get_module_name(py_file: pathlib.Path) -> str:
    """Return module name relative to PACKAGE_DIR, without .py"""  # noqa: D400, D415
    return py_file.stem


def generate_init() -> None:
    all_entries = []
    import_lines = []

    for py_file in PACKAGE_DIR.glob("*.py"):
        if py_file.name == "__init__.py" or py_file.name.startswith("_"):
            continue

        module_name = get_module_name(py_file)
        public_funcs = get_public_functions_from_file(py_file)
        print(f"Found {len(public_funcs)} public functions in {py_file.name}: {public_funcs}")  # noqa: T201
        public_funcs.sort()

        if public_funcs:
            import_lines.append(f"from .{module_name} import {', '.join(public_funcs)}")
            all_entries.extend(public_funcs)

    import_lines.sort()
    all_entries = sorted(set(all_entries))
    content = "\n".join(import_lines) + "\n\n__all__ = " + repr(all_entries) + "\n"
    content = content.replace("'", '"')  # Ensure double quotes for consistency
    INIT_FILE.write_text(content)
    print(f"Generated {INIT_FILE} with {len(all_entries)} functions.")  # noqa: T201


if __name__ == "__main__":
    generate_init()
