from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword
from NaxToPy.Core.Classes.ABQKeywords.N2PKeywordELSET import N2PKeywordELSET
from NaxToPy.Core.Classes.ABQKeywords.N2PKeywordORIENTATION import N2PKeywordORIENTATION


class N2PKeywordSOLIDSECTION(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def Elset(self) -> N2PKeywordELSET:
        """Set to which the property is applied"""
        return self._N2PKeyword__info.Elset

    @property
    def Material(self) -> str:
        """Material of the elements of the set"""
        return self._N2PKeyword__info.Material

    @property
    def Orientation(self) -> N2PKeywordORIENTATION:
        """Section orientation"""
        return self._N2PKeyword__dictKeywordToN2P[self._N2PKeyword__info.Orientation]

    @property
    def Name(self) -> str:
        """Name given to the section"""
        return self._N2PKeyword__info.Name
