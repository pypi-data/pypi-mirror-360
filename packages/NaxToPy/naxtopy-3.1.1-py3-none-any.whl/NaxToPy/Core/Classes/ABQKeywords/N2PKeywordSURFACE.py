from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword
from NaxToPy.Core.Classes.ABQEntities.N2PEntity import N2PEntity


class N2PKeywordSURFACE(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def Name(self) -> object:
        """Surface Name"""
        return self._N2PKeyword__info.Name

    @property
    def Type(self) -> object:
        """ABQEntities type (elements, nodes, segments...)"""
        return self._N2PKeyword__info.Type

    @property
    def EntityList(self) -> list[N2PEntity, ]:
        """List of entities (based on Type)"""
        return [self._N2PKeyword__dictEntityToN2P[i] for i in self._N2PKeyword__info.EntityList]
