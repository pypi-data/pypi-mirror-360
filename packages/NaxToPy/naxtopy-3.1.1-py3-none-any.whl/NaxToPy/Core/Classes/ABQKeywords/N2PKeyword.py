from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.N2PNastranInputData import N2PInputData


class N2PKeyword(N2PInputData):

    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info)
        self.__info = info
        self.__dictKeywordToN2P = dictKeywordToN2P
        self.__dictEntityToN2P = dictEntityToN2P

    @property
    def SuperKeyword(self) -> N2PKeyword:
        """Keyword that this one depends on"""
        return self._N2PKeyword__dictKeywordToN2P.get(self._N2PKeyword__info.SuperKeyword)

    @property
    def SubKeywords(self) -> list[N2PKeyword, ]:
        """Keywords that depend on this one"""
        if self._N2PKeyword__info.SubKeywords:
            return [self._N2PKeyword__dictKeywordToN2P.get(keyword) for keyword in self._N2PKeyword__info.SubKeywords]
        else:
            return []

    @property
    def Part(self) -> str:
        """Part of the keyword"""
        return self.__info.Part

    @property
    def KeywordType(self) -> str:
        return self.__info.KeywordType.ToString()

    @property
    def KeywordCode(self) -> str:
        """Keyword code: the first field read from a keyword"""
        return self.__info.KeywordCode

    @property
    def Parameters(self) -> dict:
        return dict(self.__info.Parameters)
