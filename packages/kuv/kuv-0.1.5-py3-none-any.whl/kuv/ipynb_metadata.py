import re

import nbformat

REGEX = r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"

def find_script_metadata_blocks(source: str) -> list[str]:
    """Read script metadata from python source

    See https://peps.python.org/pep-0723/#reference-implementation
    """
    name = "script"
    matches = filter(lambda m: m.group("type") == name, re.finditer(REGEX, source))
    return list(m.string for m in matches)

def get_ipynb_script_metadata(file:str) -> str | None:
    """Get script metadata from ipynb file

    Metadata must be in a code cell. Cannot be split across multiple cells. Only one metadata block is allowed per notebook.
    """
    with open(file, "r", encoding="utf-8") as f:
        notebook = nbformat.read(f, as_version=4)

    code_cells = (cell for cell in notebook.cells if cell.cell_type == "code")

    script_metadata_blocks = [
        block
        for cell in code_cells
        for block in find_script_metadata_blocks(cell.source)
    ]

    if len(script_metadata_blocks) == 0:
        return None
    elif len(script_metadata_blocks) == 1:
        return script_metadata_blocks[0]
    else:
        raise ValueError("Multiple script blocks found")
