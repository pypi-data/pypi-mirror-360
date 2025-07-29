from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQEntities.N2PEntity import N2PEntity
from NaxToPy.Core.Classes.ABQEntities.N2PEntityNode import N2PEntityNode


class N2PEntityElement(N2PEntity):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def ID(self) -> int:
        """Element identification number"""
        return self._N2PEntity__info.ID

    @property
    def NodeArray(self) -> list[N2PEntityNode, ]:
        """Element identification number"""
        return [self._N2PEntity__dictEntityToN2P[node] for node in self._N2PEntity__info.NodeArray]
