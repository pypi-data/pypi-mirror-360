"""Mix-in class providing runtime helpers for new aliases."""
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
        """Create aliases for an existing attribute at runtime.

        Parameters
        ----------
        target : str
            Existing attribute name to alias.
        *aliases : str
            One or more alias names.
        overwrite : bool, optional
            Overwrite existing attributes of the same name when ``True``;
            otherwise a ``ValueError`` is raised. Defaults to ``False``.
        strict : bool, optional
            Verify that ``target`` exists and is callable when ``True``.
            Defaults to ``True``.

        Examples
        --------
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

