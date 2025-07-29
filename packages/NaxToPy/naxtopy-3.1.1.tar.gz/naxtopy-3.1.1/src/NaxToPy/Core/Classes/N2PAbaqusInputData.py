"""This module contains classes related with a Abaqus Input File (.inp files). The parent classes are similar but not
the same as the Nastran Input File. Child classes of N2PKeyword are based on Abaqus Keywords Reference Guide."""
from __future__ import annotations  # For compatibility with Python 3.9 or higher
from typing import Literal, overload

from NaxToPy.Core.Errors.N2PLog import N2PLog
from NaxToPy.Core.Classes.N2PNastranInputData import N2PInputData
from NaxToPy.Core.Classes.ABQKeywords import *
from NaxToPy.Core.Classes.ABQEntities import *


class N2PAbaqusInputData:
    """
    Class with the complete data of an Abaqus MEF input file (text file usually with the extension .inp).
    """

    __slots__ = (
        "__inputfiledata",
        "__listcomments",
        "__dictionary_files_ids",
        "__listbulkdatakeywords",
        "__dictKeywordToN2P",
        "__dictEntityToN2P", 
    )

    def __init__(self, inputfiledata):
        self.__inputfiledata = inputfiledata
        self.__listcomments = []
        self.__dictionary_files_ids = {value: key for key, value in self.DictionaryIDsFiles.items()}
        self.__listbulkdatakeywords = []
        self.__dictKeywordToN2P: dict[object, N2PKeyword] = dict()
        self.__dictEntityToN2P: dict[object, N2PEntity] = dict()

        # Loop over all Keywords of C#
        for keyword in inputfiledata.ListBulkDataKeywords:
            # A N2PKeyword is instance to the proper child using the dictionary CONSTRUCTABQDICT
            n2pkeyword = CONSTRUCTABQDICT[keyword.KeywordType.ToString()](keyword, self.__dictKeywordToN2P, self.__dictEntityToN2P)
            self.__listbulkdatakeywords.append(n2pkeyword)
            # The Keyword of C# is saved as key and the N2PKeyword of Python as value
            self.__dictKeywordToN2P[keyword] = n2pkeyword

        # Dictionary comprehension where the key is a Entity of C# and the value a N2PEntity (a N2PEntityNode firstly)
        self.__dictEntityToN2P.update(
            {entitynode: N2PEntityNode(entitynode, self.__dictKeywordToN2P, self.__dictEntityToN2P)
             for entitynode in inputfiledata.StructuredInfo.ModelNodes})

        # Dictionary comprehension where the key is a Entity of C# and the value a N2PEntity (a N2PEntityNode secondly)
        self.__dictEntityToN2P.update(
            {entityelement: N2PEntityElement(entityelement, self.__dictKeywordToN2P, self.__dictEntityToN2P)
             for entityelement in inputfiledata.StructuredInfo.ModelElements})

    # Método para optener los objetos N2PCard del Input File -----------------------------------------------------------
    @property
    def ListBulkDataKeywords(self) -> list[N2PKeyword, ...]:
        """
        List with the N2PCard objects of the input FEM file. It has all bulk data cards of the model.
        """
        return self.__listbulkdatakeywords
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el diccionaro de IDs a FilePaths -------------------------------------------------------------
    @property
    def DictionaryIDsFiles(self) -> dict:
        """
        Dictionary with ID (`int`) as keys and FilePaths (`string`) as values.
        """
        return dict(self.__inputfiledata.DictionaryIDsFiles)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el diccionario de FilePaths a IDs ------------------------------------------------------------
    @property
    def DictionaryFilesIDs(self) -> dict:
        """
        Dictionary FilePaths (`string`) as keys and with ID (`int`) as values.
        """
        return dict(self.__dictionary_files_ids)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el tipo de Input File ------------------------------------------------------------------------
    @property
    def TypeOfFile(self) -> str:
        """
        Type of Input File.
        """
        return "ABAQUS"
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener la lista de comentarios en el Input File -----------------------------------------------------
    @property
    def ListComments(self) -> list[N2PInputData, ]:
        """
        List with all the comments in the FEM Input File.
        """
        if self.__listcomments:
            return self.__listcomments
        else:
            self.__listcomments = [N2PInputData(i) for i in self.__inputfiledata.StructuredInfo.ModelComments]
            return self.__listcomments
    # ------------------------------------------------------------------------------------------------------------------

    def get_keywords_by_type(self, field: KeyWordType) -> list[N2PKeyword,]:
        """
        Method that returns a list with the :class:`N2PKeyword` objects of the input FEM file asked. They can be uppercase or lowecase indistinctly.

        Args:
            field: str

        Returns:
            list[N2PKeyword, ]
        """
        if not isinstance(field, str):
            Exception(N2PLog.Critical.C201())
        elif field.upper() not in CONSTRUCTABQDICT:
            N2PLog.Error.E205()
            return []
        else:
            return [self.__dictKeywordToN2P[keyword] for keyword in self.__inputfiledata.GetKeywordsByType(field)]
    
    @overload
    def get_entity_by_key_and_id(self, entitytype: EntityType, entitityid: int, part: str) -> N2PEntity: ...
    @overload
    def get_entity_by_key_and_id(self, entitytype: EntityType, entitityid: int) -> list[N2PEntity, ]: ...
    # Actual implementation
    def get_entity_by_key_and_id(self, entitytype, entitityid, part=None):
        """
        Method that returns a list with the :class:`N2PEntities` objects of the input FEM file asked. There can be 
        several Entities with the same ID and EntityType as they can belong to different part. If the part is given,
        only a :class:`N2PEntity` will be returned.

        Args:
            entitytype: str
            entitityid: int
            part: str (optional)

        Returns:
            N2PEntity || list[N2PEntity, ]
        """
        if not isinstance(entitytype, str):
            Exception(N2PLog.Critical.C201())
        elif not isinstance(entitityid, int):
            Exception(N2PLog.Critical.C201())
        elif part:
            entity_error = self.__inputfiledata.GetEntitiesByTypeAndId(entitytype, entitityid, part)
            if entity_error.Item2 == 0:
                return self.__dictEntityToN2P[entity_error.Item1]
            elif entity_error.Item2 == -1:
                N2PLog.Error.E205(entitytype)
            elif entity_error.Item2 == -2:
                N2PLog.Error.E241(part)
            elif entity_error.Item2 == -3:
                N2PLog.Error.E242(part, entitityid)
            return None
        else: 
            return [self.__dictEntityToN2P[entitytype]
                    for entitytype in self.__inputfiledata.GetEntitiesByTypeAndId(entitytype, entitityid)]

    def rebuild_file(self, folder: str) -> None:
        """
        Method that writes the solver input file with the same file structure that was read in the folder is specified.

        Args:
            folder: str -> Path of the folder where the file or files will be writen
        """
        self.__inputfiledata.RebuildFile(folder)


CONSTRUCTABQDICT = {"BEAMSECTION": N2PKeywordBEAMSECTION,
                    "DENSITY": N2PKeywordDENSITY,
                    "COUPLING": N2PKeywordCOUPLING,
                    "DISTRIBUTING": N2PKeywordDISTRIBUTING,
                    "DISTRIBUTINGCOUPLING": N2PKeywordDISTRIBUTINGCOUPLING,
                    "ELASTIC": N2PKeywordELASTIC,
                    "ELEMENT": N2PKeywordELEMENT,
                    "ELSET": N2PKeywordELSET,
                    "ENDINSTANCE": N2PKeywordENDINSTANCE,
                    "ENDPART": N2PKeywordENDPART,
                    "INSTANCE": N2PKeywordINSTANCE,
                    "KINEMATIC": N2PKeywordKINEMATIC,
                    "KINEMATICCOUPLING": N2PKeywordKINEMATICCOUPLING,
                    "MATERIAL": N2PKeywordMATERIAL,
                    "NODE": N2PKeywordNODE,
                    "NSET": N2PKeywordNSET,
                    "ORIENTATION": N2PKeywordORIENTATION,
                    "PART": N2PKeywordPART,
                    "PLASTIC": N2PKeywordPLASTIC,
                    "SHELLSECTION": N2PKeywordSHELLSECTION,
                    "SOLIDSECTION": N2PKeywordSOLIDSECTION,
                    "SURFACE": N2PKeywordSURFACE,
                    "UNSUPPORTED": N2PKeyword}

KeyWordType = Literal["BEAMSECTION",
                      "DENSITY",
                      "COUPLING",
                      "DISTRIBUTING",
                      "DISTRIBUTINGCOUPLING",
                      "ELASTIC",
                      "ELEMENT",
                      "ELSET",
                      "ENDINSTANCE",
                      "ENDPART",
                      "INSTANCE",
                      "KINEMATIC",
                      "KINEMATICCOUPLING",
                      "MATERIAL",
                      "NODE",
                      "NSET",
                      "ORIENTATION",
                      "PART",
                      "PLASTIC",
                      "SHELLSECTION",
                      "SOLIDSECTION",
                      "SURFACE",
                      "UNSUPPORTED"]

EntityType = Literal["NODE", "ELEMENT"]
