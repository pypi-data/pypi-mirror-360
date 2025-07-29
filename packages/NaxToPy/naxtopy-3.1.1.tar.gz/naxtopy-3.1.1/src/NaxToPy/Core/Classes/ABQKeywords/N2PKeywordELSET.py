from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword
from NaxToPy.Core.Classes.ABQEntities.N2PEntityElement import N2PEntityElement


class N2PKeywordELSET(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def Name(self) -> str:
        """Set Name"""
        return self._N2PKeyword__info.ELSET

    @property
    def Instance(self) -> str:
        """If the set is defined under an instance, it shows the name of the instance. It is None otherwise."""
        return self._N2PKeyword__info.INSTANCE

    @property
    def Generate(self) -> bool:
        """Parameter generate (defines the data structure)"""
        return self._N2PKeyword__info.GENERATE

    @property
    def ElementList(self) -> list[N2PEntityElement]:
        """List of elements of the set"""
        return [self._N2PKeyword__dictEntityToN2P.get(element) for element in self._N2PKeyword__info.ElementList]
