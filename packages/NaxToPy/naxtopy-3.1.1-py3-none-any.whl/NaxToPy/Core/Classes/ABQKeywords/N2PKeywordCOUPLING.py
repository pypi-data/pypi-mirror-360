from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword
from NaxToPy.Core.Classes.ABQEntities.N2PEntityNode import N2PEntityNode
from NaxToPy.Core.Classes.ABQKeywords.N2PKeywordSURFACE import N2PKeywordSURFACE


class N2PKeywordCOUPLING(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def RefNode(self) -> N2PEntityNode:
        """Reference node of the coupling"""
        return self._N2PKeyword__info.RefNode

    @property
    def Surface(self) -> N2PKeywordSURFACE:
        """Surface defining the constrained nodes"""
        return self._N2PKeyword__dictKeywordToN2P[self._N2PKeyword__info.Surface]

    @property
    def ConstrainedSpareNodes(self) -> list[N2PEntityNode, ]:
        """Nodes defined in the coupling outside the surface"""
        return list(self._N2PKeyword__info.ConstrainedSpareNodes)

    @property
    def ConstrainedNodes(self) -> list[N2PEntityNode, ]:
        """All the nodes defined in the coupling"""
        return list(self._N2PKeyword__info.ConstrainedNodes)

    @property
    def Name(self) -> str:
        """Name of the Coupling"""
        return self._N2PKeyword__info.Name

    @property
    def FreedomDegrees(self) -> list[str]:
        """List with the degrees of freedom"""
        return self._N2PKeyword__info.FreedomDegrees
