"""Package initialization and built-in ``alias`` management."""

import builtins as _bt

from .decorator import alias
from .mixin import AliasMixin as Aliases


def install() -> None:
    """Inject :func:`alias` into :mod:`builtins` if not already present."""

    if not hasattr(_bt, "alias"):
        _bt.alias = alias


def uninstall() -> None:
    """Remove :func:`alias` from :mod:`builtins` when installed."""

    if getattr(_bt, "alias", None) is alias:
        delattr(_bt, "alias")


# Backwards compatibility – automatically expose ``alias`` on import
install()


__all__ = ["Aliases", "alias", "install", "uninstall"]
