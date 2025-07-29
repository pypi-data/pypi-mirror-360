from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword


class N2PKeywordKINEMATIC(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def FreedomDegrees(self) -> list[str, ]:
        """Degrees of freedom of the constraint.

        Format: 123456 for degrees 1-6 constrained; 134 for degrees 1, 3 and 4..."""
        return list(self._N2PKeyword__info.FreedomDegrees)
