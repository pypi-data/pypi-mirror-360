from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword
from NaxToPy.Core.Classes.ABQEntities.N2PEntityNode import N2PEntityNode


class N2PKeywordNSET(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def Name(self) -> str:
        """Set name. In Abaqus Keywords Reference, the parameter is called ELSET and it is required"""
        return self._N2PKeyword__info.NSET

    @property
    def Instance(self) -> str:
        """If the set is defined under an instance, it shows in this parameter.

        Set this parameter equal to the name of the part instance that contains the elements listed on the data line.
        This parameter can be used only at the assembly level and is intended to be used as a shortcut to the naming
        convention. It can be used only in a model defined in terms of an assembly of part instances."""
        return self._N2PKeyword__info.INSTANCE

    @property
    def Generate(self) -> bool:
        """Parameter generate (defines the data structure)

        If this parameter is included, each data line should give a first element, ; a last element, ; and the increment
        in element numbers between these elements, i. Then, all elements going from  to  in steps of i will be added to the set. i must be an integer such that  is a whole number (not a fraction)."""
        return self._N2PKeyword__info.GENERATE

    @property
    def NodeList(self) -> list[N2PEntityNode, ]:
        """List of nodes of the set

        If the set has an Instance defined, the nodes of that instance.
        If the set has no Instance, the nodes of the instances of the Keyword.Part
        """
        return [self._N2PKeyword__dictEntityToN2P[node] for node in self._N2PKeyword__info.NodeList]
