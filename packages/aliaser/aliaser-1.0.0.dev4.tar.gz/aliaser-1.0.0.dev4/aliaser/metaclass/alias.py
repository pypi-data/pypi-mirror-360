"""


Author: 
    Inspyre Softworks

Project:
    aliaser

File: 
    aliaser/metaclass/alias.py
 

Description:
    

"""


class AliasMeta(type):
    """Metaclass that injects method aliases declared via ``@alias``."""

    def __new__(mcls, name, bases, ns):
        cls = super().__new__(mcls, name, bases, ns)

        for attr_name, attr_val in list(vars(cls).items()):
            # ❶ Get any _aliases directly on the attribute …
            aliases = getattr(attr_val, "_aliases", None)

            # ❷ … or, if it’s a property/descriptor, look at its fget
            if aliases is None and isinstance(attr_val, property):
                aliases = getattr(attr_val.fget, "_aliases", None)

            if not aliases:
                continue

            for alias_name in aliases:
                if hasattr(cls, alias_name):
                    raise ValueError(
                        f"Cannot create alias '{alias_name}' – already defined on {name}"
                    )
                setattr(cls, alias_name, attr_val)   # ← same descriptor, no wrapper

        return cls
