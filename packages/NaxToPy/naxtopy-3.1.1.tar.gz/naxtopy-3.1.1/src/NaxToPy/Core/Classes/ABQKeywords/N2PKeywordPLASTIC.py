from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword


class N2PKeywordPLASTIC(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def PlasticComponents(self) -> list[dict]:
        """Properties of the material. One dictionary for each defined point"""
        return [dict(aux) for aux in self._N2PKeyword__info.PlasticComponents]

    @property
    def PlasticHardening(self) -> str:
        """Material hardening type (isotropic, kinematic...)"""
        return self._N2PKeyword__info.PlasticHardening

    @property
    def ScaleStress(self) -> str:
        """Factor by which the yield stress is set to be scaled."""
        return self._N2PKeyword__info.ScaleStress
