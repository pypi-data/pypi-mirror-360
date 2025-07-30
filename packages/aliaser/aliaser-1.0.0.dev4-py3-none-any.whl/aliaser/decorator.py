"""Utility decorator for exposing a method under multiple names."""
from __future__ import annotations
from types import FunctionType
from typing import Callable, Hashable


def alias(*names: Hashable) -> Callable[[FunctionType], FunctionType]:
    """Decorate a function with one or more alias names.

    Parameters
    ----------
    *names : str
        Alternate attribute names that should behave exactly like the
        decorated function.

    Returns
    -------
    Callable
        The original function annotated with ``_aliases`` so the metaclass
        can wire up the aliases later.
    """
    if not names:
        raise ValueError("At least one alias must be provided")

    def decorator(func: FunctionType) -> FunctionType:
        # Stash aliases on the function for the metaclass to pick up
        setattr(func, "_aliases", tuple(str(n) for n in names))
        return func

    return decorator


__all__ = ("alias",)
