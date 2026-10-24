"""XDG base-directory resolution and private directory creation.

Resolving a path never touches the filesystem. Directories are created only by
:func:`ensure_private_dir`, and only when a caller explicitly asks for it.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

from kellu.__app__ import APP_NAME
from kellu.common.errors import SecurityError

PRIVATE_DIR_MODE = 0o700


def _xdg_base(env_var: str, default_relative: str) -> Path:
    """Return an XDG base directory.

    The XDG specification says relative values must be ignored.
    """
    raw = os.environ.get(env_var, "")
    if raw and os.path.isabs(raw):
        return Path(raw)
    return Path.home() / default_relative


def config_dir() -> Path:
    """Providers, routing, scopes, sandbox policy."""
    return _xdg_base("XDG_CONFIG_HOME", ".config") / APP_NAME


def state_dir() -> Path:
    """Session logs and history."""
    return _xdg_base("XDG_STATE_HOME", ".local/state") / APP_NAME


def cache_dir() -> Path:
    """Disposable caches."""
    return _xdg_base("XDG_CACHE_HOME", ".cache") / APP_NAME


def ensure_private_dir(path: Path) -> Path:
    """Create ``path`` with mode 0700 if needed and verify it is safe to use.

    Raises:
        SecurityError: ``path`` is a symlink or not a directory, or is owned by another user.
        OSError: the directory cannot be created.
    """
    path.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIR_MODE)
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise SecurityError(f"{path} must be a real directory, not a symlink or a file")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise SecurityError(f"{path} is owned by another user")
    if stat.S_IMODE(info.st_mode) != PRIVATE_DIR_MODE:
        path.chmod(PRIVATE_DIR_MODE)
    return path
