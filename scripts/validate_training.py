#!/usr/bin/env python
"""Static validation for the canonical training notebook."""
import ast
from pathlib import Path

import nbformat

path = Path(__file__).resolve().parents[1] / "fraudguard_training.ipynb"
notebook = nbformat.read(path, as_version=4)
errors = []
for index, cell in enumerate(notebook.cells):
    if cell.cell_type != "code":
        continue
    source = "\n".join(
        line for line in cell.source.splitlines()
        if not line.lstrip().startswith(("%", "!"))
    )
    try:
        ast.parse(source)
    except SyntaxError as exc:
        errors.append(f"cell {index}: {exc}")
if errors:
    raise SystemExit("\n".join(errors))
print(f"Notebook syntax OK: {path.name} ({len(notebook.cells)} cells)")
