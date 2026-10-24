"""Enforce the layer dependency rule from docs/ARCHITECTURE.md."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "kellu"

LOWER = {"common", "security", "sandbox", "providers", "projects"}
ALLOWED: dict[str, set[str]] = {
    "common": set(),
    "security": {"common"},
    "sandbox": {"common"},
    "providers": {"common"},
    "projects": {"common"},
    "tools": {"common", "security", "sandbox"},
    "core": LOWER | {"tools"},
    "frontends": LOWER | {"tools", "core"},
}
IGNORED = {"__app__"}  # identity module, importable from anywhere


def _imported_kellu_modules(py_file: Path) -> set[str]:
    """Return the second path component of every ``kellu.<x>`` import in the file."""
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.level == 0, f"{py_file}: relative imports are not allowed"
            if node.module == "kellu":
                found.update(alias.name for alias in node.names)
            elif node.module and node.module.startswith("kellu."):
                found.add(node.module.split(".")[1])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if parts[0] == "kellu" and len(parts) > 1:
                    found.add(parts[1])
    return found - IGNORED


@pytest.mark.parametrize("layer", sorted(ALLOWED))
def test_layer_only_imports_allowed_layers(layer: str) -> None:
    layer_dir = SRC / layer
    assert (layer_dir / "__init__.py").is_file(), f"layer {layer} must be a package"
    for py_file in layer_dir.rglob("*.py"):
        imported = _imported_kellu_modules(py_file) - {layer}
        forbidden = imported - ALLOWED[layer]
        assert not forbidden, f"{py_file.relative_to(SRC)} imports forbidden layers: {forbidden}"


def test_every_source_directory_is_a_declared_layer() -> None:
    dirs = {p.name for p in SRC.iterdir() if p.is_dir() and not p.name.startswith("__")}
    assert dirs == set(ALLOWED), f"undeclared or missing layers: {dirs ^ set(ALLOWED)}"
