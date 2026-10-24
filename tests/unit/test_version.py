from __future__ import annotations

import kellu
from kellu import __app__


def test_version_is_single_sourced() -> None:
    assert kellu.__version__ == __app__.__version__
