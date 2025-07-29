from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword
from NaxToPy.Core.Classes.ABQKeywords.N2PKeywordELSET import N2PKeywordELSET
from NaxToPy.Core.Classes.ABQEntities.N2PEntityShell import N2PEntityShell


class N2PKeywordSHELLSECTION(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def Elset(self) -> N2PKeywordELSET:
        """Set to which the property is applied"""
        return self._N2PKeyword__dictKeywordToN2P[self._N2PKeyword__info.Elset]

    @property
    def Material(self) -> str:
        """Material of the elements of the set. Return "COMPOSITE" for composite materials"""
        return self._N2PKeyword__info.Material

    @property
    def Name(self) -> str:
        """Name given to the section"""
        return self._N2PKeyword__info.Name

    @property
    def Thickness(self) -> float:
        """The sum of the thicknesses of the layers (COMPOSITE) or the material thickness (MATERIAL)"""
        return self._N2PKeyword__info.Thickness

    @property
    def IntegrationPoints(self) -> int:
        """Number of integration points"""
        return self._N2PKeyword__info.IntegrationPoints

    @property
    def IsComposite(self) -> bool:
        """True if the shell is composed of several layers"""
        return self._N2PKeyword__info.IsComposite

    @property
    def IsHomogeneous(self) -> bool:
        """True if the shell is composed of a single material"""
        return self._N2PKeyword__info.IsHomogeneous

    @property
    def LayerList(self) -> list:
        """List of shells that make up a composite shell"""
        output = []
        for shell in self._N2PKeyword__info.LayerList:
            if shell in self._N2PKeyword__dictEntityToN2P:
                output.append(self._N2PKeyword__dictEntityToN2P[shell])
            else:
                aux = N2PEntityShell(shell, self._N2PKeyword__dictKeywordToN2P, self._N2PKeyword__dictEntityToN2P)
                self._N2PKeyword__dictEntityToN2P[shell] = aux
                output.append(aux)

        return output
