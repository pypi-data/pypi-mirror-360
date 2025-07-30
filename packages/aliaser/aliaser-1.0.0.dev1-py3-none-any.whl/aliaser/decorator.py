"""


Author: 
    Inspyre Softworks

Project:
    aliaser

File: 
    aliaser/decorator.py
 

Description:
    

"""
from __future__ import annotations
from types import FunctionType
from typing import Callable, Iterable, Hashable


def alias(*names: Hashable) -> Callable[[FunctionType], FunctionType]:
    """
    Parameters:
        *names: str
            One or more alternate attribute names that should behave
            exactly like the decorated method.

    Returns:
        The original function, annotated with ``_aliases`` so the metaclass
        can wire things up later.
    """
    if not names:
        raise ValueError("At least one alias must be provided")

    def decorator(func: FunctionType) -> FunctionType:
        # Stash aliases on the function for the metaclass to pick up
        setattr(func, "_aliases", tuple(str(n) for n in names))
        return func

    return decorator


__all__ = ("alias",)
