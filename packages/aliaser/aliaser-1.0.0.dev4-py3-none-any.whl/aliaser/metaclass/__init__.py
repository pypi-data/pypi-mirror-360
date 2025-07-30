from .alias import AliasMeta
from .multiton import MultitonMeta


class AliasMultitonMeta(AliasMeta, MultitonMeta):
    """
    Alias harvesting metaclass that combines the functionality of the AliasMeta and MultitonMeta metaclasses.

    See Also:
        - :class:`AliasMeta`,
        - :class:`MultitonMeta`
    """
    pass
