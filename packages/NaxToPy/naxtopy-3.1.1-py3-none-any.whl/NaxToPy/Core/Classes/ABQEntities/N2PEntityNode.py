from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQEntities.N2PEntity import N2PEntity


class N2PEntityNode(N2PEntity):

    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)
        
    @property
    def ID(self) -> int:
        """Node identification number"""
        return self._N2PEntity__info.ID

    @property
    def X1(self) -> float:
        """First coordinate"""
        return self._N2PEntity__info.ID

    @property
    def X2(self) -> float:
        """Second coordinate"""
        return self._N2PEntity__info.ID

    @property
    def X3(self) -> float:
        """Third coordinate"""
        return self._N2PEntity__info.ID

    @property
    def DirectionCosine1(self) -> float:
        """First direction cosine of the normal at the node (Optional)"""
        return self._N2PEntity__info.DirectionCosine1

    @property
    def DirectionCosine2(self) -> float:
        """ Second direction cosine of the normal at the node (Optional)
        For nodes entered a cylindrical or spherical system, this entry is an angle given in degrees."""
        return self._N2PEntity__info.DirectionCosine2

    @property
    def DirectionCosine3(self) -> float:
        """ Third direction cosine of the normal at the node (Optional)
        For nodes entered a spherical system, this entry is an angle given in degrees."""
        return self._N2PEntity__info.DirectionCosine3
