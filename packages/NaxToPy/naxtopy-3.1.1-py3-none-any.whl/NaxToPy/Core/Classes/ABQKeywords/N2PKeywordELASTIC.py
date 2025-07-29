from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword


class N2PKeywordELASTIC(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def ElasticType(self) -> str:
        """Material type for elasticity (isotropic, orthotropic...)"""
        return self._N2PKeyword__info.ElasticType

    @property
    def ElasticComponents(self) -> dict[str, float]:
        """Components of the tensor"""
        return dict(self._N2PKeyword__info.ElasticComponents)
