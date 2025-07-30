"""


Author: 
    Inspyre Softworks

Project:
    aliaser

File: 
    aliaser/mixin.py
 

Description:
    

"""
from .metaclass import AliasMeta


class AliasMixin(metaclass=AliasMeta):
    """Opt-in mix-in that adds a runtime helper for new aliases."""

    @classmethod
    def add_alias(
        cls,
        target: str,
        *aliases: str,
        overwrite: bool = False,
        strict: bool = True,
    ) -> None:
        """
        Dynamically add aliases **after** the class has been created.

        Parameters:
            target (str):
                The existing attribute name to alias.
            *aliases (str):
                One or more alias names.
            overwrite: bool, default=False
                If ``True`` an existing attribute of the same name is
                overwritten; otherwise, a ``ValueError`` is raised.
            strict: bool, default=True
                If ``True`` verifies that *target* exists and is callable.

        Example Usage:
            >>> class Greeter(AliasMixin):
            ...     def hello(self):
            ...         print("Hi!")
            ...
            >>> Greeter.add_alias('hello', 'hi', 'sup')
        """
        if strict and not hasattr(cls, target):
            raise ValueError(f"{cls.__name__}.{target} doesn't exist")

        func = getattr(cls, target)

        if strict and not callable(func):
            raise ValueError(f"Attribute {target!r} is not callable")

        for name in aliases:
            if hasattr(cls, name) and not overwrite:
                raise ValueError(f"Attribute {name!r} already exists")
            setattr(cls, name, func)

