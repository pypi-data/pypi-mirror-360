from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword
from NaxToPy.Core.Classes.ABQKeywords.N2PKeywordELSET import N2PKeywordELSET


class N2PKeywordELEMENT(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

        # When an ELEMENT keyword is used, an ELSET with all that elements is generated if a Name is used
    @property
    def ElementList(self) -> list:
        """List of elements within the keyword"""
        return [self._N2PKeyword__dictEntityToN2P[element] for element in self._N2PKeyword__info.ElementList]

    @property
    def ElementType(self) -> str:
        """String with the type of the element"""
        return self._N2PKeyword__info.ElementType
