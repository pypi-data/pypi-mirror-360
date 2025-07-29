from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword


class N2PKeywordDENSITY(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def Density(self) -> float:
        """Mass density [ML^-3]"""
        return self._N2PKeyword__info.Density

    @property
    def Temperature(self) -> float:
        """Temperature (optional)"""
        return self._N2PKeyword__info.Temperature

    @property
    def FieldVariables(self) -> list[float]:
        """Field variables (optional)"""
        return list(self._N2PKeyword__info.FieldVariables)
