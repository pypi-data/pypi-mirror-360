"""


Author: 
    Inspyre Softworks

Project:
    aliaser

File: 
    aliaser/__init__.py
 

Description:
    

"""
import builtins as _bt
from .decorator import alias
from .mixin import AliasMixin as Aliases


# Avoid clobbering existing names
if not hasattr(_bt, "alias"):
    _bt.alias = alias


__all__ = ['Aliases']
