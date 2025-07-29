from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword


class N2PEntity:
    """Class created to add information under a Keyword. There is not a similar concept in Abaqus. It is used to define
    nodes, elements and shells."""

    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        self.__info = info
        self.__dictKeywordToN2P = dictKeywordToN2P
        self.__dictEntityToN2P = dictEntityToN2P

    @property
    def KeywordParent(self) -> N2PKeyword:
        """Keyword the entity belongs to. It always belongs to a keyword"""
        return self.__dictKeywordToN2P[self.__info.KeywordParent]

    @property
    def KeywordIndex(self) -> int:
        """Identification number of the Keyword ot belongs"""
        return self.__info.KeywordIndex

    @property
    def Part(self) -> str:
        """The part of an entity is always the part of the KeywordParent"""
        return self.KeywordParent.Part
