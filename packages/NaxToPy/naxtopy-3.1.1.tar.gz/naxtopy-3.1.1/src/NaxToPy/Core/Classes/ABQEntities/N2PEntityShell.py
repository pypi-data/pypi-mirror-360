from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword
from NaxToPy.Core.Classes.ABQEntities.N2PEntity import N2PEntity


class N2PEntityShell(N2PEntity):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def Name(self) -> str:
        """Name of the layer"""
        return self._N2PEntity__info.Name

    @property
    def Thickness(self) -> float:
        """Shell thickness"""
        return self._N2PEntity__info.Thickness

    @property
    def IntegrationPoints(self) -> int:
        """Number of integration points to be used through the shell section. Default: five for Simpson's rule and 3 for Gauss quadrature """
        return self._N2PEntity__info.IntegrationPoints

    @property
    def Material(self) -> N2PKeyword:
        """Node identification number"""
        return self._N2PEntity__dictKeywordToN2P[self._N2PEntity__info.Material]

    @property
    def Orientation(self) -> N2PKeyword:
        """Node identification number"""
        return self._N2PEntity__dictKeywordToN2P.get(self._N2PEntity__info.Orientation)
