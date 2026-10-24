from __future__ import annotations

from collections.abc import Callable

from kellu import doctor


def _all_present(binary: str) -> str:
    return f"/usr/bin/{binary}"


def _only(*present: str) -> Callable[[str], str | None]:
    return lambda binary: f"/usr/bin/{binary}" if binary in present else None


def test_all_tools_present_passes() -> None:
    lines: list[str] = []
    assert doctor.run(which=_all_present, out=lines.append) == 0
    assert any("secret-tool" in line for line in lines)


def test_missing_required_tool_fails() -> None:
    assert doctor.run(which=lambda _b: None, out=lambda _s: None) == 1


def test_missing_optional_tool_only_warns() -> None:
    lines: list[str] = []
    assert doctor.run(which=_only("secret-tool"), out=lines.append) == 0
    assert any(line.startswith("[warn]") and "bwrap" in line for line in lines)


def test_checks_are_marked_required_or_optional() -> None:
    by_name = {c.name: c for c in doctor.collect_checks(_all_present)}
    assert by_name["secret-tool"].required
    assert not by_name["bwrap"].required
