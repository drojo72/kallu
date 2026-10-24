from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from kellu.common import paths
from kellu.common.errors import SecurityError


def test_defaults_follow_xdg_layout(fake_home: Path) -> None:
    assert paths.config_dir() == fake_home / ".config" / "kellu"
    assert paths.state_dir() == fake_home / ".local" / "state" / "kellu"
    assert paths.cache_dir() == fake_home / ".cache" / "kellu"


def test_absolute_xdg_variable_is_honored(
    fake_home: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    custom = tmp_path / "custom"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(custom))
    assert paths.config_dir() == custom / "kellu"


def test_relative_xdg_variable_is_ignored(fake_home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", "relative/dir")
    assert paths.state_dir() == fake_home / ".local" / "state" / "kellu"


def test_resolving_paths_does_not_create_anything(fake_home: Path) -> None:
    paths.config_dir()
    paths.state_dir()
    paths.cache_dir()
    assert list(fake_home.iterdir()) == []


def test_ensure_private_dir_creates_mode_0700(fake_home: Path) -> None:
    target = fake_home / "state"
    paths.ensure_private_dir(target)
    assert stat.S_IMODE(target.stat().st_mode) == 0o700


def test_ensure_private_dir_tightens_loose_permissions(fake_home: Path) -> None:
    target = fake_home / "loose"
    target.mkdir()
    target.chmod(0o755)
    paths.ensure_private_dir(target)
    assert stat.S_IMODE(target.stat().st_mode) == 0o700


def test_ensure_private_dir_rejects_symlink(fake_home: Path) -> None:
    real = fake_home / "real"
    real.mkdir()
    link = fake_home / "link"
    os.symlink(real, link)
    with pytest.raises(SecurityError):
        paths.ensure_private_dir(link)
