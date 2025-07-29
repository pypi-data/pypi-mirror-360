from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword
from NaxToPy.Core.Classes.ABQEntities.N2PEntityNode import N2PEntityNode


class N2PKeywordNODE(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def NodeList(self) -> list[N2PEntityNode]:
        """List of nodes within the keyword"""
        return [self._N2PKeyword__dictEntityToN2P[node] for node in self._N2PKeyword__info.NodeList]
