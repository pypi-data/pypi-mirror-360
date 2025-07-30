import re
import tomllib
import nbformat

REGEX = r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"


def read_script_metadata(source: str) -> dict | None:
    """Read script metadata from python source

    See https://peps.python.org/pep-0723/#reference-implementation
    """
    name = "script"
    matches = list(
        filter(lambda m: m.group("type") == name, re.finditer(REGEX, source))
    )
    if len(matches) > 1:
        raise ValueError(f"Multiple {name} blocks found")
    elif len(matches) == 1:
        content = "".join(
            line[2:] if line.startswith("# ") else line[1:]
            for line in matches[0].group("content").splitlines(keepends=True)
        )
        return tomllib.loads(content)
    else:
        return None


def read_ipynb_script_metadata(file: str) -> dict | None:
    """Read script metadata from ipynb file

    Metadata must be in a code cell. Cannot be split across multiple cells. Only one metadata block is allowed.
    """
    with open(file, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    code_cells = (cell for cell in notebook.cells if cell.cell_type == "code")
    script_metadata_blocks = [
        metadata
        for cell in code_cells
        if (metadata := read_script_metadata(cell.source)) is not None
    ]

    if len(script_metadata_blocks) > 1:
        raise ValueError("Multiple script blocks found")
    elif len(script_metadata_blocks) == 1:
        script_metadata = script_metadata_blocks[0]
    else:
        script_metadata = None

    return script_metadata
