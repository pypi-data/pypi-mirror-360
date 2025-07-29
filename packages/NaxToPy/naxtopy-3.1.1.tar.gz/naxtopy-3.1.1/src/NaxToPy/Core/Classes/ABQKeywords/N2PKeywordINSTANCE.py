from __future__ import annotations  # For compatibility with Python 3.9 or higher
import numpy as np

from NaxToPy.Core._AuxFunc._NetToPython import _nettonumpy
from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword


class N2PKeywordINSTANCE(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def Name(self) -> str:
        """Name of the instance"""
        return self._N2PKeyword__info.Name

    @property
    def TranslationComponents(self) -> np.ndarray:
        """x, y, z values of the translation of the instance"""
        return _nettonumpy(self._N2PKeyword__info.TranslationComponents)

    @property
    def RotationComponents(self) -> np.ndarray:
        """x1, y1, z1 components of the first node that defines the rotation axis;
        x2, y2, z2 components of the second node that defines the rotation axis;
        Angle of rotation"""
        return _nettonumpy(self._N2PKeyword__info.RotationComponents)
