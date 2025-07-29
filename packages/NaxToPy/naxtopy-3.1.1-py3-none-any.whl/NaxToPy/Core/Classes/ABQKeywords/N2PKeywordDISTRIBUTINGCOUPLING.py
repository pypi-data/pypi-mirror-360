from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword


class N2PKeywordDISTRIBUTINGCOUPLING(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    # The method overrides the parent class method.
    @property
    def WeightingMethod(self) -> str:
        """Coupling method used to couple the displacement and rotation of the reference node to the average motion of
        the surface nodes within the influence radius.

        Default: UNIFORM (1.0)"""
        return self._N2PKeyword__info.WeightingMethod
