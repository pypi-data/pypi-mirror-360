"""Module with de definition of N2PModelInputData"""
import array
import System
from typing import Union, overload

from NaxToPy.Core.Errors.N2PLog import N2PLog

class _LazyList(list):
    """
    A lazy list connected to a LazyDict. The items are lazily instantiated
    from the LazyDict when accessed. It is immutable
    """
    def __init__(self, lazy_dict):
        super().__init__([None] * len(lazy_dict))  # Initialize list with placeholders
        self._lazy_dict = lazy_dict
        self.keys = list(lazy_dict.keys())  # Extract keys from the LazyDict

    def __getitem__(self, index):
        if not (0 <= index < len(self.keys)):
            raise IndexError("list index out of range")
        
        # Get the key corresponding to the index
        key = self.keys[index]
        value = super().__getitem__(index)

        if value is None:
            # Trigger the LazyDict to create the value
            value = self._lazy_dict[key]
            # Update the list with the created value
            super().__setitem__(index, value)

        return value

    def __setitem__(self, index, value):
        raise TypeError("ListBulkDataCards is immutable")

    def append(self, value):
        raise TypeError("ListBulkDataCards is immutable")

    def extend(self, iterable):
        raise TypeError("ListBulkDataCards is immutable")

    def insert(self, index, value):
        raise TypeError("ListBulkDataCards is immutable")

    def pop(self, index=-1):
        raise TypeError("ListBulkDataCards is immutable")

    def remove(self, value):
        raise TypeError("ListBulkDataCards is immutable")

    def clear(self):
        raise TypeError("ListBulkDataCards is immutable")
    
    def __iter__(self):
        for index in range(len(self.keys)):
            yield self[index]  # Trigger lazy evaluation for each item


class IndexTrackingList(list):
    """Class that is used as a list. It is used because it changes the setitem method of the list class to affect the
    csharp list where the information is actually safe"""
    def __init__(self, iterable=None, csobject=None):
        super().__init__(iterable or [])
        self._csobject = csobject

    def __setitem__(self, index, value):
        self._csobject[index] = value
        super().__setitem__(index, value)


class _N2PField:
    """Class defined only for Typing"""
    def ToReal(self):
        """Converts the Field object of a Table of a N2PCard into a float"""
        pass
    def ToCharacter(self):
        """Converts the Field object of a Table of a N2PCard into a str"""
        pass
    def ToInteger(self):
        """Converts the Field object of a Table of a N2PCard into a int"""
        pass


class N2PInputData:
    """General class for the information in an input file of Nastran
    """

    __slots__ = (
        "__inputdata"
    )

    def __init__(self, inputdata):
        self.__inputdata = inputdata

    @property
    def DataType(self) -> str:
        return self.__inputdata.DataType.ToString()

    @property
    def Lines(self) -> list[str]:
        return list(self.__inputdata.Lines)

    @property
    def FilePathId(self) -> int:
        return self.__inputdata.FilePathId

    # @property
    # def Children(self) -> list["N2PInputData"]:
    #     return list(self.__inputdata.Children)


class N2PCard(N2PInputData):
    """Class with the information of a bulk data card of an input file of Nastran.
    """

    def __init__(self, card):
        super().__init__(card)
        self.__card = card

    @property
    def Table(self) -> array.array:
        """2D Array with the information of each field of a card. This information is kept as an object.
        To actually obtain this information one of this methods should be used on a field:\n

            - ToCharacter()
            - ToReal()
            - ToInteger()

        WARNING: The user must know what type of data the filed is to use the correct method

        Example:
            >>> card_id = .Table[0,1].ToInteger()
        """
        return self.__card.Table

    @property
    def SuperElement(self) -> int:
        return self.__card.SuperElement

    @property
    def CardType(self) -> str:
        return self.__card.CardType.ToString()

    def get_field(self, i: int, j: int) -> _N2PField:
        """It returns an object with the information of a field of a card. To actually obtain this information one of
        this methods should be used on a field:\n

            - ToCharacter()
            - ToReal()
            - ToInteger()

        WARNING: The user must know what type of data the filed is to use the correct method

        Example:
            >>> card_id = .get_field(0, 1).ToInteger()
        """
        return self.__card.Table[i, j]


class N2PNastranInputData:
    """Class with the complete data of a MEF input file (text file).

    Note:
        The property :class:`N2PModelContent.ModelInputData` can be a :class:`N2PNastranInputData` if the input file is from
        Nastran (.bdf) or Opstitruct (.fem), or a :class:`N2PAbaqusInputData` (.inp) if is from Abaqus.

    Example:
        >>> model = n2p.load_model("my_nastran_input_file.bdf")
        >>> inputdata = model.ModelInputData  # This is a N2PNastranInputData
    """

    def __init__(self, dictcardscston2p: dict, inputfiledata):
        self.__dictcardscston2p = dictcardscston2p
        self.__inputfiledata = inputfiledata
        self.__listinstructions = []
        self.__listcomments = []
        self.__dictionary_files_ids = {value: key for key, value in self.DictionaryIDsFiles.items()}
        self.__lazylist = None

    @property
    def ListBulkDataCards(self) -> list[N2PCard]:
        """List with the N2PCard objects of the input FEM file. It has all bulk data cards of the model"""

        # We actually return a LazyList, conected to the LazyDict of cards. Only when a card is required is instantiated
        if self.__lazylist is None:
            self.__lazylist = _LazyList(self.__dictcardscston2p)

        return self.__lazylist

    @property
    def DictionaryIDsFiles(self) -> dict:
        """Dictionary with ID (`int`) as keys and FilePaths (`string`) as values."""
        return dict(self.__inputfiledata.DictionaryIDsFiles)

    @property
    def DictionaryFilesIDs(self) -> dict:
        """Dictionary FilePaths (`string`) as keys and with ID (`int`) as values."""
        return dict(self.__dictionary_files_ids)

    @property
    def TypeOfFile(self) -> str:
        """Type of file read. It may be "NASTRAN" or "OPTISTRUCT" ."""
        return self.__inputfiledata.TypeOfFile.ToString()

    @property
    def ListInstructions(self) -> list[N2PInputData]:
        """List with the instructions of the model. They are the commands above the BEGIN BULK: Executive Control
        Statements and Control Case Commands"""
        if self.__listinstructions:
            return self.__listinstructions
        else:
            self.__listinstructions = [N2PInputData(i) for i in self.__inputfiledata.StructuredInfo.ModelInstructions]
            return self.__listinstructions

    @property
    def ListComments(self) -> list[N2PInputData]:
        """List with all the comments in the FEM Input File"""
        if self.__listcomments:
            return self.__listcomments
        else:
            self.__listcomments = [N2PInputData(i) for i in self.__inputfiledata.StructuredInfo.ModelComments]
            return self.__listcomments

    def get_cards_by_field(self, fields: list[str, ], row: int = 0, col: int = 0) -> list[N2PCard, ]:
        """Method that returns a list with the N2PCard objects of the input FEM file that meet the condition.
        In other words, that field is equal to the string in the position defined. If no row or column is defined, the
        string will compare with the position (0,0) of the card, that is the name of the card.

        Args:
            fields: str | list[str]
            row: int (optional)
            col: int (optional)

        Returns:
            list[N2PCard, ]
        """
        if isinstance(fields, str):
            fields = [fields]
        array_strings = System.Array[System.String]([field.strip() for field in fields])

        return [self.__dictcardscston2p[card] for card in self.__inputfiledata.GetCardsByField(array_strings, row, col)]
    

    def rebuild_file(self, folder: str) -> None:
        """Method that writes the solver input file with the same file structure that was read in the folder is specified

        Args:
            folder: str -> Path of the folder where the file or files will be written.
        """
        self.__inputfiledata.RebuildFile(folder)


class N2PModelInputData(N2PNastranInputData):
    """Deprecated class. To maintain its functionality it works as the new class N2PNastranInputData"""
    def __init__(self, *args, **kwargs):
        N2PLog.Warning.W207()
        super().__init__(*args, **kwargs)


class CBAR(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCbar)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Unique element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """ Property identification number of a PBAR or PBARL entry. (Integer > 0 or blank*; Default = EID unless BAROR entry has nonzero entry in field 3.)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def GA(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integer > 0; GA ≠ GB)
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value

    @property
    def X1(self) -> float:
        """
           Components of orientation vector v, from GA, in the displacement coordinate system at GA(default), or in the basic coordinate system.See Remark 8. (Real)
           * Remark 8:
           OFFT is a character string code that describes how the offset and orientation vector components are to be interpreted.By default (string input is GGG or
           blank), the offset vectors are measured in the displacement coordinate systems at grid points A and B and the orientation vector is measured in the
           displacement coordinate system of grid point A.At user option, the offset vectors can be measured in an offset coordinate system relative to grid points
           A and B, and the orientation vector can be measured in the basic system as indicated in the following table:
           String    Orientation Vector     End A Offset     End B Offset
           GGG       Global                 Global           Global
           BGG       Basic                  Global           Global
           GGO       Global                 Global           Basic
           BGO       Basic                  Global           Basic
           GOG       Global                 Offset           Global
           BOG       Basic                  Offset           Global
           GOO       Global                 Offset           Basic
           BOO       Basic                  Offset           Basic
        """
        return self.__cardinfo.X1

    @X1.setter
    def X1(self, value: float) -> None:
        self.__cardinfo.X1 = value

    @property
    def X2(self) -> float:
        """
           X2
        """
        return self.__cardinfo.X2

    @X2.setter
    def X2(self, value: float) -> None:
        self.__cardinfo.X2 = value

    @property
    def X3(self) -> float:
        """
           X3
        """
        return self.__cardinfo.X3

    @X3.setter
    def X3(self, value: float) -> None:
        self.__cardinfo.X3 = value

    @property
    def G0(self) -> int:
        """
           Alternate method to supply the orientation vector v using grid point G0.The direction of v is from GA to G0.v is then translated to End A. (Integer > 0; G0 ≠ GA or GB)
        """
        return self.__cardinfo.G0

    @G0.setter
    def G0(self, value: int) -> None:
        self.__cardinfo.G0 = value

    @property
    def OFFT(self) -> str:
        """
           Offset vector interpretation flag. (character or blank) See Remark 8.
           * Remark 8:
           OFFT is a character string code that describes how the offset and orientation vector components are to be interpreted. By default, (string input is GGG or
           blank), the offset vectors are measured in the displacement coordinate systems at grid points A and B and the orientation vector is measured in the
           displacement coordinate system of grid point A.At user option, the offset vectors can be measured in an offset coordinate system relative to grid points
           A and B, and the orientation vector can be measured in the basic system as indicated in the following table:
           String    Orientation Vector     End A Offset     End B Offset
           GGG       Global                 Global           Global
           BGG       Basic                  Global           Global
           GGO       Global                 Global           Basic
           BGO       Basic                  Global           Basic
           GOG       Global                 Offset           Global
           BOG       Basic                  Offset           Global
           GOO       Global                 Offset           Basic
           BOO       Basic                  Offset           Basic
        """
        return self.__cardinfo.OFFT

    @OFFT.setter
    def OFFT(self, value: str) -> None:
        self.__cardinfo.OFFT = value

    @property
    def PA(self) -> int:
        """
           Pin flags for bar ends A and B, respectively. Used to remove connections between the grid point and selected degrees-offreedom of the bar.The degrees-of-freedom
           are defined in the element’s coordinate system (see Figure 8-8). The bar must have stiffness associated with the PA and PB degrees-of-freedom to be
           released by the pin flags. For example, if PA = 4 is specified, the PBAR entry must have a value for J, the torsional stiffness. (Up to 5 of the unique
           Integers 1 through 6 anywhere in the field with no embedded blanks; Integer > 0.) Pin flags combined with offsets are not allowed for SOL 600.
        """
        return self.__cardinfo.PA

    @PA.setter
    def PA(self, value: int) -> None:
        self.__cardinfo.PA = value

    @property
    def PB(self) -> int:
        """
           PB
        """
        return self.__cardinfo.PB

    @PB.setter
    def PB(self, value: int) -> None:
        self.__cardinfo.PB = value

    @property
    def W1A(self) -> float:
        """
           Components of offset vectors and, respectively (see Figure 8-8) in displacement coordinate systems(or in element system depending upon the content of the OFFT
           field), at points GA and GB, respectively. See Remark 7. and 8. (Real; Default = 0.0)
           * Remark 7:
           Offset vectors are treated like rigid elements and are therefore subject to the same limitations.
           • Offset vectors are not affected by thermal loads.
           • The specification of offset vectors is not recommended in solution sequences that compute differential stiffness because the offset vector
           remains parallel to its original orientation. (Differential stiffness is computed in buckling analysis provided in SOLs 103 and 107 through 112 with the
           STATSUB command; and also in nonlinear analysis provided in SOLs 106, 129, 153, and 159 with PARAM, LGDISP,1.)
           • BAR elements with offsets will give wrong buckling results.
           • Masses are not offset for shells.
           • The nonlinear solution in SOL 106 uses differential stiffness due for the iterations to reduce equilibrium errors.An error in the differential stiffness
           due to offsets may cause the iterations to converge slowly or to diverge. If the solution converges the answer is correct, even though there may be an
           error in the differential stiffness.However, the special capabilities in SOL 106 to get vibration and buckling modes will produce wrong answers if the
           differential stiffness is bad.
           • The internal “rigid elements” for offset BAR/BEAM elements are rotated in the nonlinear force calculations. Thus, if convergence is achieved, BAR/BEAM
           elements may be used in SOL 106 with LGDISP,1.
           * Remark 8:
           OFFT is a character string code that describes how the offset and orientation vector components are to be interpreted.By default (string input is GGG or
           blank), the offset vectors are measured in the displacement coordinate systems at grid points A and B and the orientation vector is measured in the
           displacement coordinate system of grid point A. At user option, the offset vectors can be measured in an offset coordinate system relative to grid points
           A and B, and the orientation vector can be measured in the basic system as indicated in the following table:
           String    Orientation Vector     End A Offset     End B Offset
           GGG       Global                 Global           Global
           BGG       Basic                  Global           Global
           GGO       Global                 Global           Basic
           BGO       Basic                  Global           Basic
           GOG       Global                 Offset           Global
           BOG       Basic                  Offset           Global
           GOO       Global                 Offset           Basic
           BOO       Basic                  Offset           Basic
        """
        return self.__cardinfo.W1A

    @W1A.setter
    def W1A(self, value: float) -> None:
        self.__cardinfo.W1A = value

    @property
    def W2A(self) -> float:
        """
           W2A
        """
        return self.__cardinfo.W2A

    @W2A.setter
    def W2A(self, value: float) -> None:
        self.__cardinfo.W2A = value

    @property
    def W3A(self) -> float:
        """
           W3A
        """
        return self.__cardinfo.W3A

    @W3A.setter
    def W3A(self, value: float) -> None:
        self.__cardinfo.W3A = value

    @property
    def W1B(self) -> float:
        """
           W1B
        """
        return self.__cardinfo.W1B

    @W1B.setter
    def W1B(self, value: float) -> None:
        self.__cardinfo.W1B = value

    @property
    def W2B(self) -> float:
        """
           W2B
        """
        return self.__cardinfo.W2B

    @W2B.setter
    def W2B(self, value: float) -> None:
        self.__cardinfo.W2B = value

    @property
    def W3B(self) -> float:
        """
           W3B
        """
        return self.__cardinfo.W3B

    @W3B.setter
    def W3B(self, value: float) -> None:
        self.__cardinfo.W3B = value


class CBEAM(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCbeam)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Unique element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of PBEAM, PBCOMP or PBEAML entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def GA(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integer > 0; GA ≠ GB)
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value

    @property
    def X1(self) -> float:
        """
           Components of orientation vector v, from GA, in the displacement coordinate system at GA(default), or in the basic coordinate system.See Remark 9. (Real)
           * Remark 9:
           If the element is a p-version element, BIT in field 9 contains the value of the built-in-twist measured in radians.Otherwise, OFFT in field 9 is a character
           string code that describes how the offset and orientation vector components are to be interpreted.By default (string input is GGG or blank), the offset
           vectors are measured in the displacement coordinate systems at grid points A and B and the orientation vector is measured in the displacement
           coordinate system of grid point A.At user option, the offset vectors can be measured in an offset system relative to grid points A and B, and the
           orientation vector can be measured in the basic system as indicated in the following table:
           String    Orientation Vector     End A Offset     End B Offset
           GGG       Global                 Global           Global
           BGG       Basic                  Global           Global
           GGO       Global                 Global           Offset
           BGO       Basic                  Global           Offset
           GOG       Global                 Offset           Global
           BOG       Basic                  Offset           Global
           GOO       Global                 Offset           Offset
           BOO       Basic                  Offset           Offset
        """
        return self.__cardinfo.X1

    @X1.setter
    def X1(self, value: float) -> None:
        self.__cardinfo.X1 = value

    @property
    def X2(self) -> float:
        """
           X2
        """
        return self.__cardinfo.X2

    @X2.setter
    def X2(self, value: float) -> None:
        self.__cardinfo.X2 = value

    @property
    def X3(self) -> float:
        """
           X3
        """
        return self.__cardinfo.X3

    @X3.setter
    def X3(self, value: float) -> None:
        self.__cardinfo.X3 = value

    @property
    def G0(self) -> int:
        """
           Alternate method to supply the orientation vector v using grid point G0.The direction of v is from GA to G0.v is then transferred to End A. (Integer > 0; G0 ≠ GA or GB)
        """
        return self.__cardinfo.G0

    @G0.setter
    def G0(self, value: int) -> None:
        self.__cardinfo.G0 = value

    @property
    def OFFT(self) -> str:
        """
           Offset vector interpretation flag. (character or blank) See Remark 9.
           * Remark 9:
           If the element is a p-version element, BIT in field 9 contains the value of the built-in-twist measured in radians.Otherwise, OFFT in field 9 is a character
           string code that describes how the offset and orientation vector components are to be interpreted.By default (string input is GGG or blank), the offset
           vectors are measured in the displacement coordinate systems at grid points A and B and the orientation vector is measured in the displacement
           coordinate system of grid point A.At user option, the offset vectors can be measured in an offset system relative to grid points A and B, and the
           orientation vector can be measured in the basic system as indicated in the following table:
           String    Orientation Vector     End A Offset     End B Offset
           GGG       Global                 Global           Global
           BGG       Basic                  Global           Global
           GGO       Global                 Global           Offset
           BGO       Basic                  Global           Offset
           GOG       Global                 Offset           Global
           BOG       Basic                  Offset           Global
           GOO       Global                 Offset           Offset
           BOO       Basic                  Offset           Offset
        """
        return self.__cardinfo.OFFT

    @OFFT.setter
    def OFFT(self, value: str) -> None:
        self.__cardinfo.OFFT = value

    @property
    def BIT(self) -> float:
        """
           Built-in twist of the cross-sectional axes about the beam axis at end B relative to end A.For beam p-elements only. (Real; Default = 0.0)
        """
        return self.__cardinfo.BIT

    @BIT.setter
    def BIT(self, value: float) -> None:
        self.__cardinfo.BIT = value

    @property
    def PA(self) -> int:
        """
           Pin flags for beam ends A and B, respectively. Used to remove connections between the grid point and selected degrees-offreedom of the bar. The degrees-of-freedom
           are defined in the element’s coordinate system (see Figure 8-12). The beam must have stiffness associated with the PA and PB degrees-of-freedom to be
           released by the pin flags.For example, if PA = 4 is specified, the PBEAM entry must have a value for J, the torsional stiffness. (Up to 5 of the unique
           Integers 1 through 6 anywhere in the field with no embedded blanks; Integer > 0.) Pin flags combined with offsets are not allowed for SOL 600.
        """
        return self.__cardinfo.PA

    @PA.setter
    def PA(self, value: int) -> None:
        self.__cardinfo.PA = value

    @property
    def PB(self) -> int:
        """
           PB
        """
        return self.__cardinfo.PB

    @PB.setter
    def PB(self, value: int) -> None:
        self.__cardinfo.PB = value

    @property
    def W1A(self) -> float:
        """
           Components of offset vectors and , respectively (see Figure 8-8) in displacement coordinate systems(or in element system depending upon the content of the OFFT
           field), at points GA and GB, respectively. See Remark 7. and 8. (Real; Default = 0.0)
           * Remark 7:
           Offset vectors are treated like rigid elements and are therefore subject to the same limitations.
           • Offset vectors are not affected by thermal loads.
           • The specification of offset vectors is not recommended in solution sequences that compute differential stiffness because the offset vector
           remains parallel to its original orientation. (Differential stiffness is computed in buckling analysis provided in SOLs 103 and 107 through 112 with the
           STATSUB command; and also in nonlinear analysis provided in SOLs 106, 129, 153, and 159 with PARAM, LGDISP,1.)
           • BAR elements with offsets will give wrong buckling results.
           • Masses are not offset for shells.
           • The nonlinear solution in SOL 106 uses differential stiffness due for the iterations to reduce equilibrium errors.An error in the differential stiffness
           due to offsets may cause the iterations to converge slowly or to diverge. If the solution converges the answer is correct, even though there may be an
           error in the differential stiffness.However, the special capabilities in SOL 106 to get vibration and buckling modes will produce wrong answers if the
           differential stiffness is bad.
           • The internal “rigid elements” for offset BAR/BEAM elements are rotated in the nonlinear force calculations.Thus, if convergence is achieved, BAR/BEAM
           elements may be used in SOL 106 with LGDISP,1.
           * Remark 8:
           OFFT is a character string code that describes how the offset and orientation vector components are to be interpreted.By default (string input is GGG or
           blank), the offset vectors are measured in the displacement coordinate systems at grid points A and B and the orientation vector is measured in the
           displacement coordinate system of grid point A.At user option, the offset vectors can be measured in an offset coordinate system relative to grid points
           A and B, and the orientation vector can be measured in the basic system as indicated in the following table:
           String    Orientation Vector     End A Offset     End B Offset
           GGG       Global                 Global           Global
           BGG       Basic                  Global           Global
           GGO       Global                 Global           Basic
           BGO       Basic                  Global           Basic
           GOG       Global                 Offset           Global
           BOG       Basic                  Offset           Global
           GOO       Global                 Offset           Basic
           BOO       Basic                  Offset           Basic
        """
        return self.__cardinfo.W1A

    @W1A.setter
    def W1A(self, value: float) -> None:
        self.__cardinfo.W1A = value

    @property
    def W2A(self) -> float:
        """
           W2A
        """
        return self.__cardinfo.W2A

    @W2A.setter
    def W2A(self, value: float) -> None:
        self.__cardinfo.W2A = value

    @property
    def W3A(self) -> float:
        """
           W3A
        """
        return self.__cardinfo.W3A

    @W3A.setter
    def W3A(self, value: float) -> None:
        self.__cardinfo.W3A = value

    @property
    def W1B(self) -> float:
        """
           W1B
        """
        return self.__cardinfo.W1B

    @W1B.setter
    def W1B(self, value: float) -> None:
        self.__cardinfo.W1B = value

    @property
    def W2B(self) -> float:
        """
           W2B
        """
        return self.__cardinfo.W2B

    @W2B.setter
    def W2B(self, value: float) -> None:
        self.__cardinfo.W2B = value

    @property
    def W3B(self) -> float:
        """
           W3B
        """
        return self.__cardinfo.W3B

    @W3B.setter
    def W3B(self, value: float) -> None:
        self.__cardinfo.W3B = value

    @property
    def SA(self) -> int:
        """
           Scalar or grid point identification numbers for the ends A and B, respectively.The degrees-of-freedom at these points are the warping variables dθ ⁄ dx.
           SA and SB cannot be specified for beam p-elements. (Integers > 0 or blank)
        """
        return self.__cardinfo.SA

    @SA.setter
    def SA(self, value: int) -> None:
        self.__cardinfo.SA = value

    @property
    def SB(self) -> int:
        """
           SB
        """
        return self.__cardinfo.SB

    @SB.setter
    def SB(self, value: int) -> None:
        self.__cardinfo.SB = value


class CBUSH(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCbush)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PBUSH entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def GA(self) -> int:
        """
           CardGrid point identification number of connection points. See Remark 6. (Integer > 0)
           * Remark 6:
           If the distance between GA and GB is less than .0001, or if GB is blank, then CID must be specified.GB blank implies that B is grounded.
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value

    @property
    def X1(self) -> float:
        """
           Components of orientation vector v, from GA, in the displacement coordinate system at GA. (Real)
        """
        return self.__cardinfo.X1

    @X1.setter
    def X1(self, value: float) -> None:
        self.__cardinfo.X1 = value

    @property
    def X2(self) -> float:
        """
           X2
        """
        return self.__cardinfo.X2

    @X2.setter
    def X2(self, value: float) -> None:
        self.__cardinfo.X2 = value

    @property
    def X3(self) -> float:
        """
           X3
        """
        return self.__cardinfo.X3

    @X3.setter
    def X3(self, value: float) -> None:
        self.__cardinfo.X3 = value

    @property
    def G0(self) -> int:
        """
           Alternate method to supply vector v using grid point GO. Direction of v is from GA to GO. v is then transferred to End A.See Remark 3. (Integer > 0)
           * Remark 3:
           CID > 0 overrides GO and Xi. Then the element x-axis is along T1, the element y-axis is along T2, and the element z-axis is along T3 of the CID
           coordinate system.If the CID refers to a cylindrical coordinate system or as pherical coordinate system, then grid GA is used to locate the system. If for
           cylindrical or spherical coordinate, GA falls on the z-axis used to define them, it is recommended that another CID be selectfced to define the element x-axis.
        """
        return self.__cardinfo.G0

    @G0.setter
    def G0(self, value: int) -> None:
        self.__cardinfo.G0 = value

    @property
    def CID(self) -> int:
        """
           Element coordinate system identification. A 0 means the basic coordinate system.If CID is blank, then the element coordinate system is determined from
           GO or Xi.See Figure 8-19 and Remark 3. (Integer > 0 or blank)
           * Remark 3:
           CID > 0 overrides GO and Xi. Then the element x-axis is along T1, the element y-axis is along T2, and the element z-axis is along T3 of the CID
           coordinate system.If the CID refers to a cylindrical coordinate system or as pherical coordinate system, then grid GA is used to locate the system. If for
           cylindrical or spherical coordinate, GA falls on the z-axis used to define them, it is recommended that another CID be selectfced to define the element x-axis.
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value

    @property
    def S(self) -> float:
        """
           Location of spring damper. See Figure 8-19. (0.0 < Real < 1.0; Default = 0.5)
        """
        return self.__cardinfo.S

    @S.setter
    def S(self, value: float) -> None:
        self.__cardinfo.S = value

    @property
    def OCID(self) -> int:
        """
           Coordinate system identification of spring-damper offset. See Remark 9. (Integer > -1; Default = -1, which means the offset point lies on the line
           between GA and GB according to Figure 8-19)
           * Remark 9:
           If OCID = -1 or blank (default) then S is used and S1, S2, S3 are ignored. If OCID > 0, then S is ignored and S1, S2, S3 are used.
        """
        return self.__cardinfo.OCID

    @OCID.setter
    def OCID(self, value: int) -> None:
        self.__cardinfo.OCID = value

    @property
    def S1(self) -> float:
        """
           Components of spring-damper offset in the OCID coordinate system if OCID > 0. See Figure 8-20 and Remark 9. (Real)
           * Remark 9:
           If OCID = -1 or blank (default) then S is used and S1, S2, S3 are ignored. If OCID > 0, then S is ignored and S1, S2, S3 are used.
        """
        return self.__cardinfo.S1

    @S1.setter
    def S1(self, value: float) -> None:
        self.__cardinfo.S1 = value

    @property
    def S2(self) -> float:
        """
           S2
        """
        return self.__cardinfo.S2

    @S2.setter
    def S2(self, value: float) -> None:
        self.__cardinfo.S2 = value

    @property
    def S3(self) -> float:
        """
           S3
        """
        return self.__cardinfo.S3

    @S3.setter
    def S3(self, value: float) -> None:
        self.__cardinfo.S3 = value


class CELAS1(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCelas1)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Unique element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PELAS entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           Geometric grid point identification number. (Integer >= 0)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def C1(self) -> int:
        """
           Component number. (0 < Integer < 6; blank or zero if scalar point.)
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: int) -> None:
        self.__cardinfo.C1 = value

    @property
    def C2(self) -> int:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: int) -> None:
        self.__cardinfo.C2 = value


class CELAS2(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCelas2)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Unique element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           <para>PID: <see cref="CardCelas2"/> does not have an associate property. Returns <see cref="uint.MaxValue"/></para>
           <para>Implemented to use the interface <see cref="ICardElement"/></para>
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def K(self) -> float:
        """
           Stiffness of the scalar spring. (Real)
        """
        return self.__cardinfo.K

    @K.setter
    def K(self, value: float) -> None:
        self.__cardinfo.K = value

    @property
    def G1(self) -> int:
        """
           Geometric grid point identification number. (Integer >= 0)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def C1(self) -> int:
        """
           Component number. (0 < Integer < 6; blank or zero if scalar point.)
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: int) -> None:
        self.__cardinfo.C1 = value

    @property
    def C2(self) -> int:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: int) -> None:
        self.__cardinfo.C2 = value

    @property
    def GE(self) -> float:
        """
           Damping coefficient. See Remarks 6. and 8. (Real)
           * Remark 6:
           If PARAM,W4 is not specified, GE is ignored in transient analysis. See “Parameters” on page 631.
           * Remark 8:
           To obtain the damping coefficient GE, multiply the critical damping ratio C ⁄ C0 by 2.0.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def S(self) -> float:
        """
           Stress coefficient (Real).
        """
        return self.__cardinfo.S

    @S.setter
    def S(self, value: float) -> None:
        self.__cardinfo.S = value


class CELAS3(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCelas3)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Unique element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PELAS entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def S1(self) -> int:
        """
           Scalar point identification numbers. (Integer >= 0)
        """
        return self.__cardinfo.S1

    @S1.setter
    def S1(self, value: int) -> None:
        self.__cardinfo.S1 = value

    @property
    def S2(self) -> int:
        """
           S2
        """
        return self.__cardinfo.S2

    @S2.setter
    def S2(self, value: int) -> None:
        self.__cardinfo.S2 = value


class CELAS4(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCelas4)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Unique element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           <para>PID: <see cref="CardCelas4"/> does not have an associate property. Returns <see cref="uint.MaxValue"/></para>
           <para>Implemented to use the interface <see cref="ICardElement"/></para>
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def K(self) -> float:
        """
           Stiffness of the scalar spring. (Real)
        """
        return self.__cardinfo.K

    @K.setter
    def K(self, value: float) -> None:
        self.__cardinfo.K = value

    @property
    def S1(self) -> int:
        """
           Scalar point identification numbers. (Integer >= 0; S1 ≠ S2)
        """
        return self.__cardinfo.S1

    @S1.setter
    def S1(self, value: int) -> None:
        self.__cardinfo.S1 = value

    @property
    def S2(self) -> int:
        """
           S2
        """
        return self.__cardinfo.S2

    @S2.setter
    def S2(self, value: int) -> None:
        self.__cardinfo.S2 = value


class CFAST(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCfast)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PFAST entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def TYPE(self) -> str:
        """
           Specifies the surface patch definition: (Character)
           If TYPE = ‘PROP’, the surface patch connectivity between patch A and patch B is defined with two PSHELL(or PCOMP) properties with property ids given by
           IDA and IDB.See Remark 1. and Figure 8-22.
           If TYPE = ‘ELEM’, the surface patch connectivity between patch A and patch B is defined with two shell element ids given by IDA and IDB.See Remark 1. and
           Figure 8-22.
           * Remark 1:
           The CardCfast defines a flexible connection between two surface patches. Depending on the location for the piercing points GA and GB, and the size of the diameter
           D(see PFAST), the number of unique physical grids per patch ranges from a possibility of 3 to 16 grids. (Currently there is a limitation that there can be only
           a total of 16 unique grids in the upper patch and only a total of 16 unique grids in the lower patch.Thus, for example, a patch can not hook up to
           four CQUAD8 elements with midside nodes and no nodes in common between each CQUAD8 as that would total to 32 unique grids for the patch.)
        """
        return self.__cardinfo.TYPE

    @TYPE.setter
    def TYPE(self, value: str) -> None:
        self.__cardinfo.TYPE = value

    @property
    def IDA(self) -> int:
        """
           Property id (for PROP option) or Element id (for ELEM option) defining patches A and B. IDA ≠ IDB (Integer > 0)
        """
        return self.__cardinfo.IDA

    @IDA.setter
    def IDA(self, value: int) -> None:
        self.__cardinfo.IDA = value

    @property
    def IDB(self) -> int:
        """
           IDB
        """
        return self.__cardinfo.IDB

    @IDB.setter
    def IDB(self, value: int) -> None:
        self.__cardinfo.IDB = value

    @property
    def GS(self) -> int:
        """
           CardGrid point defining the location of the fastener. See Remark 2. (Integer > 0 or blank)
           * Remark 2:
           GS defines the approximate location of the fastener in space. GS is projected onto the surface patches A and B.The resulting piercing points GA and GB
           define the axis of the fastener.GS does not have to lie on the surfaces of the patches.GS must be able to project normals to the two patches. GA can be
           specified in lieu of GS, in which case GS will be ignored. If neither GS nor GA is specified, then (XS, YS, ZS) in basic must be specified.
           If both GA and GB are specified, they must lie on or at least have projections onto surface patches A and B respectively. The locations will then be
           corrected so that they lie on the surface patches A and B within machine precision. The length of the fastener is the final distance between GA and GB.
           If the length is zero, the normal to patch A is used to define the axis of the fastener.
           Diagnostic printouts, checkout runs and control of search and projection parameters are requested on the SWLDPRM Bulk Data entry.
        """
        return self.__cardinfo.GS

    @GS.setter
    def GS(self, value: int) -> None:
        self.__cardinfo.GS = value

    @property
    def GA(self) -> int:
        """
           CardGrid ids of piecing points on patches A and B. See Remark 2. (Integer > 0 or blank)
           * Remark 2:
           GS defines the approximate location of the fastener in space. GS is projected onto the surface patches A and B.The resulting piercing points GA and GB
           define the axis of the fastener.GS does not have to lie on the surfaces of the patches.GS must be able to project normals to the two patches. GA can be
           specified in lieu of GS, in which case GS will be ignored. If neither GS nor GA is specified, then (XS, YS, ZS) in basic must be specified.
           If both GA and GB are specified, they must lie on or at least have projections onto surface patches A and B respectively. The locations will then be
           corrected so that they lie on the surface patches A and B within machine precision. The length of the fastener is the final distance between GA and GB.
           If the length is zero, the normal to patch A is used to define the axis of the fastener.
           Diagnostic printouts, checkout runs and control of search and projection parameters are requested on the SWLDPRM Bulk Data entry.
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value

    @property
    def XS(self) -> float:
        """
           Location of the fastener in basic. Required if neither GS nor GA is defined.See Remark 2. (Real or blank)
           * Remark 2:
           GS defines the approximate location of the fastener in space. GS is projected onto the surface patches A and B.The resulting piercing points GA and GB
           define the axis of the fastener.GS does not have to lie on the surfaces of the patches.GS must be able to project normals to the two patches. GA can be
           specified in lieu of GS, in which case GS will be ignored. If neither GS nor GA is specified, then (XS, YS, ZS) in basic must be specified.
           If both GA and GB are specified, they must lie on or at least have projections onto surface patches A and B respectively. The locations will then be
           corrected so that they lie on the surface patches A and B within machine precision. The length of the fastener is the final distance between GA and GB.
           If the length is zero, the normal to patch A is used to define the axis of the fastener.
           Diagnostic printouts, checkout runs and control of search and projection parameters are requested on the SWLDPRM Bulk Data entry.
        """
        return self.__cardinfo.XS

    @XS.setter
    def XS(self, value: float) -> None:
        self.__cardinfo.XS = value

    @property
    def YS(self) -> float:
        """
           YS
        """
        return self.__cardinfo.YS

    @YS.setter
    def YS(self, value: float) -> None:
        self.__cardinfo.YS = value

    @property
    def ZS(self) -> float:
        """
           ZS
        """
        return self.__cardinfo.ZS

    @ZS.setter
    def ZS(self, value: float) -> None:
        self.__cardinfo.ZS = value


class CHEXANAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardChexaNas)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100000000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSOLID or PLSOLID entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value

    @property
    def G11(self) -> int:
        """
           G11
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: int) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> int:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: int) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> int:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: int) -> None:
        self.__cardinfo.G13 = value

    @property
    def G14(self) -> int:
        """
           G14
        """
        return self.__cardinfo.G14

    @G14.setter
    def G14(self, value: int) -> None:
        self.__cardinfo.G14 = value

    @property
    def G15(self) -> int:
        """
           G15
        """
        return self.__cardinfo.G15

    @G15.setter
    def G15(self, value: int) -> None:
        self.__cardinfo.G15 = value

    @property
    def G16(self) -> int:
        """
           G16
        """
        return self.__cardinfo.G16

    @G16.setter
    def G16(self, value: int) -> None:
        self.__cardinfo.G16 = value

    @property
    def G17(self) -> int:
        """
           G17
        """
        return self.__cardinfo.G17

    @G17.setter
    def G17(self, value: int) -> None:
        self.__cardinfo.G17 = value

    @property
    def G18(self) -> int:
        """
           G18
        """
        return self.__cardinfo.G18

    @G18.setter
    def G18(self, value: int) -> None:
        self.__cardinfo.G18 = value

    @property
    def G19(self) -> int:
        """
           G19
        """
        return self.__cardinfo.G19

    @G19.setter
    def G19(self, value: int) -> None:
        self.__cardinfo.G19 = value

    @property
    def G20(self) -> int:
        """
           G20
        """
        return self.__cardinfo.G20

    @G20.setter
    def G20(self, value: int) -> None:
        self.__cardinfo.G20 = value


class CHEXAOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardChexaOpt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100000000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSOLID or PLSOLID entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value

    @property
    def G11(self) -> int:
        """
           G11
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: int) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> int:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: int) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> int:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: int) -> None:
        self.__cardinfo.G13 = value

    @property
    def G14(self) -> int:
        """
           G14
        """
        return self.__cardinfo.G14

    @G14.setter
    def G14(self, value: int) -> None:
        self.__cardinfo.G14 = value

    @property
    def G15(self) -> int:
        """
           G15
        """
        return self.__cardinfo.G15

    @G15.setter
    def G15(self, value: int) -> None:
        self.__cardinfo.G15 = value

    @property
    def G16(self) -> int:
        """
           G16
        """
        return self.__cardinfo.G16

    @G16.setter
    def G16(self, value: int) -> None:
        self.__cardinfo.G16 = value

    @property
    def G17(self) -> int:
        """
           G17
        """
        return self.__cardinfo.G17

    @G17.setter
    def G17(self, value: int) -> None:
        self.__cardinfo.G17 = value

    @property
    def G18(self) -> int:
        """
           G18
        """
        return self.__cardinfo.G18

    @G18.setter
    def G18(self, value: int) -> None:
        self.__cardinfo.G18 = value

    @property
    def G19(self) -> int:
        """
           G19
        """
        return self.__cardinfo.G19

    @G19.setter
    def G19(self, value: int) -> None:
        self.__cardinfo.G19 = value

    @property
    def G20(self) -> int:
        """
           G20
        """
        return self.__cardinfo.G20

    @G20.setter
    def G20(self, value: int) -> None:
        self.__cardinfo.G20 = value

    @property
    def CORDM(self) -> str:
        """
           Flag indicating that the following field(s) reference data to determine the material coordinate system.
        """
        return self.__cardinfo.CORDM

    @CORDM.setter
    def CORDM(self, value: str) -> None:
        self.__cardinfo.CORDM = value

    @property
    def CID(self) -> int:
        """
           Material coordinate system identification number. Default = 0 (Integer ≥ -1)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value

    @property
    def THETA(self) -> float:
        """
           Angle of rotation of the elemental X-axis and Y-axis about the elemental Z-axis. The new coordinate system formed after this rotational transformation
           represents the material system (the PHI field can further transform the material system). Note: For positive THETA, the elemental X-axis is rotated
           towards the elemental Y-axis. Default = blank (Real)
        """
        return self.__cardinfo.THETA

    @THETA.setter
    def THETA(self, value: float) -> None:
        self.__cardinfo.THETA = value

    @property
    def PHI(self) -> float:
        """
           This angle is applied on the new coordinate system derived after transformation with THETA. Angle of rotation of the elemental Z-axis and new X-axis
           about the new Y-axis.The new coordinate system formed after this rotational transformation represents the material system.
           Note: For positive PHI, the new X-axis is rotated towards the elemental Z-axis. Default = blank (Real)
        """
        return self.__cardinfo.PHI

    @PHI.setter
    def PHI(self, value: float) -> None:
        self.__cardinfo.PHI = value


class CONM2(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardConm2)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           <para>PID: <see cref="CardConm2"/> does not have an associate property. Returns <see cref="uint.MaxValue"/></para>
           <para>Implemented to use the interface <see cref="ICardElement"/></para>
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G(self) -> int:
        """
           CardGrid point identification number. (Integer > 0)
        """
        return self.__cardinfo.G

    @G.setter
    def G(self, value: int) -> None:
        self.__cardinfo.G = value

    @property
    def CID(self) -> int:
        """
           Coordinate system identification number.For CID of -1; see X1, X2, X3 low. (Integer > -1; Default = 0)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value

    @property
    def M(self) -> float:
        """
           Mass value. (Real)
        """
        return self.__cardinfo.M

    @M.setter
    def M(self, value: float) -> None:
        self.__cardinfo.M = value

    @property
    def X1(self) -> float:
        """
           Offset distances from the grid point to the center of gravity of the mass in the coordinate system defined in field 4, unless CID = -1, in which
           case X1, X2, X3 are the coordinates, not offsets, of the center of gravity of the mass in the basic coordinate system. (Real)
        """
        return self.__cardinfo.X1

    @X1.setter
    def X1(self, value: float) -> None:
        self.__cardinfo.X1 = value

    @property
    def X2(self) -> float:
        """
           X2
        """
        return self.__cardinfo.X2

    @X2.setter
    def X2(self, value: float) -> None:
        self.__cardinfo.X2 = value

    @property
    def X3(self) -> float:
        """
           X3
        """
        return self.__cardinfo.X3

    @X3.setter
    def X3(self, value: float) -> None:
        self.__cardinfo.X3 = value

    @property
    def I11(self) -> float:
        """
           Mass moments of inertia measured at the mass center of gravity in the coordinate system defined by field 4. If CID = -1, the basic coordinate
           system is implied. (For I11, I22, and I33; Real > 0.0; for I21, I31, and I32; Real)
        """
        return self.__cardinfo.I11

    @I11.setter
    def I11(self, value: float) -> None:
        self.__cardinfo.I11 = value

    @property
    def I21(self) -> float:
        """
           I21
        """
        return self.__cardinfo.I21

    @I21.setter
    def I21(self, value: float) -> None:
        self.__cardinfo.I21 = value

    @property
    def I22(self) -> float:
        """
           I22
        """
        return self.__cardinfo.I22

    @I22.setter
    def I22(self, value: float) -> None:
        self.__cardinfo.I22 = value

    @property
    def I31(self) -> float:
        """
           I31
        """
        return self.__cardinfo.I31

    @I31.setter
    def I31(self, value: float) -> None:
        self.__cardinfo.I31 = value

    @property
    def I32(self) -> float:
        """
           I32
        """
        return self.__cardinfo.I32

    @I32.setter
    def I32(self, value: float) -> None:
        self.__cardinfo.I32 = value

    @property
    def I33(self) -> float:
        """
           I33
        """
        return self.__cardinfo.I33

    @I33.setter
    def I33(self, value: float) -> None:
        self.__cardinfo.I33 = value


class CORD1C(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCord1c)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def CIDA(self) -> int:
        """
           Coordinate system identification number. (Integer > 0)
        """
        return self.__cardinfo.CIDA

    @CIDA.setter
    def CIDA(self, value: int) -> None:
        self.__cardinfo.CIDA = value

    @property
    def CIDB(self) -> int:
        """
           CIDB
        """
        return self.__cardinfo.CIDB

    @CIDB.setter
    def CIDB(self, value: int) -> None:
        self.__cardinfo.CIDB = value

    @property
    def G1A(self) -> int:
        """
           CardGrid point identification numbers. (Integer > 0; G1A ≠ G2A ≠ G3AG1B ≠ G2B ≠ G3B;)
        """
        return self.__cardinfo.G1A

    @G1A.setter
    def G1A(self, value: int) -> None:
        self.__cardinfo.G1A = value

    @property
    def G2A(self) -> int:
        """
           G2A
        """
        return self.__cardinfo.G2A

    @G2A.setter
    def G2A(self, value: int) -> None:
        self.__cardinfo.G2A = value

    @property
    def G3A(self) -> int:
        """
           G3A
        """
        return self.__cardinfo.G3A

    @G3A.setter
    def G3A(self, value: int) -> None:
        self.__cardinfo.G3A = value

    @property
    def G1B(self) -> int:
        """
           G1B
        """
        return self.__cardinfo.G1B

    @G1B.setter
    def G1B(self, value: int) -> None:
        self.__cardinfo.G1B = value

    @property
    def G2B(self) -> int:
        """
           G2B
        """
        return self.__cardinfo.G2B

    @G2B.setter
    def G2B(self, value: int) -> None:
        self.__cardinfo.G2B = value

    @property
    def G3B(self) -> int:
        """
           G3B
        """
        return self.__cardinfo.G3B

    @G3B.setter
    def G3B(self, value: int) -> None:
        self.__cardinfo.G3B = value


class CORD1R(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCord1r)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def CIDA(self) -> int:
        """
           Coordinate system identification number. (Integer > 0)
        """
        return self.__cardinfo.CIDA

    @CIDA.setter
    def CIDA(self, value: int) -> None:
        self.__cardinfo.CIDA = value

    @property
    def CIDB(self) -> int:
        """
           CIDB
        """
        return self.__cardinfo.CIDB

    @CIDB.setter
    def CIDB(self, value: int) -> None:
        self.__cardinfo.CIDB = value

    @property
    def G1A(self) -> int:
        """
           CardGrid point identification numbers. (Integer > 0; G1A ≠ G2A ≠ G3AG1B ≠ G2B ≠ G3B;)
        """
        return self.__cardinfo.G1A

    @G1A.setter
    def G1A(self, value: int) -> None:
        self.__cardinfo.G1A = value

    @property
    def G2A(self) -> int:
        """
           G2A
        """
        return self.__cardinfo.G2A

    @G2A.setter
    def G2A(self, value: int) -> None:
        self.__cardinfo.G2A = value

    @property
    def G3A(self) -> int:
        """
           G3A
        """
        return self.__cardinfo.G3A

    @G3A.setter
    def G3A(self, value: int) -> None:
        self.__cardinfo.G3A = value

    @property
    def G1B(self) -> int:
        """
           G1B
        """
        return self.__cardinfo.G1B

    @G1B.setter
    def G1B(self, value: int) -> None:
        self.__cardinfo.G1B = value

    @property
    def G2B(self) -> int:
        """
           G2B
        """
        return self.__cardinfo.G2B

    @G2B.setter
    def G2B(self, value: int) -> None:
        self.__cardinfo.G2B = value

    @property
    def G3B(self) -> int:
        """
           G3B
        """
        return self.__cardinfo.G3B

    @G3B.setter
    def G3B(self, value: int) -> None:
        self.__cardinfo.G3B = value


class CORD1S(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCord1s)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def CIDA(self) -> int:
        """
           Coordinate system identification number. (Integer > 0)
        """
        return self.__cardinfo.CIDA

    @CIDA.setter
    def CIDA(self, value: int) -> None:
        self.__cardinfo.CIDA = value

    @property
    def CIDB(self) -> int:
        """
           CIDB
        """
        return self.__cardinfo.CIDB

    @CIDB.setter
    def CIDB(self, value: int) -> None:
        self.__cardinfo.CIDB = value

    @property
    def G1A(self) -> int:
        """
           CardGrid point identification numbers. (Integer > 0; G1A ≠ G2A ≠ G3AG1B ≠ G2B ≠ G3B;)
        """
        return self.__cardinfo.G1A

    @G1A.setter
    def G1A(self, value: int) -> None:
        self.__cardinfo.G1A = value

    @property
    def G2A(self) -> int:
        """
           G2A
        """
        return self.__cardinfo.G2A

    @G2A.setter
    def G2A(self, value: int) -> None:
        self.__cardinfo.G2A = value

    @property
    def G3A(self) -> int:
        """
           G3A
        """
        return self.__cardinfo.G3A

    @G3A.setter
    def G3A(self, value: int) -> None:
        self.__cardinfo.G3A = value

    @property
    def G1B(self) -> int:
        """
           G1B
        """
        return self.__cardinfo.G1B

    @G1B.setter
    def G1B(self, value: int) -> None:
        self.__cardinfo.G1B = value

    @property
    def G2B(self) -> int:
        """
           G2B
        """
        return self.__cardinfo.G2B

    @G2B.setter
    def G2B(self, value: int) -> None:
        self.__cardinfo.G2B = value

    @property
    def G3B(self) -> int:
        """
           G3B
        """
        return self.__cardinfo.G3B

    @G3B.setter
    def G3B(self, value: int) -> None:
        self.__cardinfo.G3B = value


class CORD2C(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCord2c)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def CID(self) -> int:
        """
           Coordinate system identification number. (Integer > 0)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value

    @property
    def RID(self) -> int:
        """
           Identification number of a coordinate system that is defined independently from this coordinate system. (Integer > 0; Default = 0 is the basic coordinate
           system.)
        """
        return self.__cardinfo.RID

    @RID.setter
    def RID(self, value: int) -> None:
        self.__cardinfo.RID = value

    @property
    def A1(self) -> float:
        """
           Coordinates of three points in coordinate system defined in field 3. (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value

    @property
    def B1(self) -> float:
        """
           B1
        """
        return self.__cardinfo.B1

    @B1.setter
    def B1(self, value: float) -> None:
        self.__cardinfo.B1 = value

    @property
    def B2(self) -> float:
        """
           B2
        """
        return self.__cardinfo.B2

    @B2.setter
    def B2(self, value: float) -> None:
        self.__cardinfo.B2 = value

    @property
    def B3(self) -> float:
        """
           B3
        """
        return self.__cardinfo.B3

    @B3.setter
    def B3(self, value: float) -> None:
        self.__cardinfo.B3 = value

    @property
    def C1(self) -> float:
        """
           C1
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: float) -> None:
        self.__cardinfo.C1 = value

    @property
    def C2(self) -> float:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: float) -> None:
        self.__cardinfo.C2 = value

    @property
    def C3(self) -> float:
        """
           C3
        """
        return self.__cardinfo.C3

    @C3.setter
    def C3(self, value: float) -> None:
        self.__cardinfo.C3 = value


class CORD2R(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCord2r)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def CID(self) -> int:
        """
           Coordinate system identification number. (Integer > 0)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value

    @property
    def RID(self) -> int:
        """
           Identification number of a coordinate system that is defined independently from this coordinate system. (Integer > 0; Default = 0 is the basic coordinate
           system.)
        """
        return self.__cardinfo.RID

    @RID.setter
    def RID(self, value: int) -> None:
        self.__cardinfo.RID = value

    @property
    def A1(self) -> float:
        """
           Coordinates of three points in coordinate system defined in field 3. (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value

    @property
    def B1(self) -> float:
        """
           B1
        """
        return self.__cardinfo.B1

    @B1.setter
    def B1(self, value: float) -> None:
        self.__cardinfo.B1 = value

    @property
    def B2(self) -> float:
        """
           B2
        """
        return self.__cardinfo.B2

    @B2.setter
    def B2(self, value: float) -> None:
        self.__cardinfo.B2 = value

    @property
    def B3(self) -> float:
        """
           B3
        """
        return self.__cardinfo.B3

    @B3.setter
    def B3(self, value: float) -> None:
        self.__cardinfo.B3 = value

    @property
    def C1(self) -> float:
        """
           C1
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: float) -> None:
        self.__cardinfo.C1 = value

    @property
    def C2(self) -> float:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: float) -> None:
        self.__cardinfo.C2 = value

    @property
    def C3(self) -> float:
        """
           C3
        """
        return self.__cardinfo.C3

    @C3.setter
    def C3(self, value: float) -> None:
        self.__cardinfo.C3 = value


class CORD2S(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCord2s)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def CID(self) -> int:
        """
           Coordinate system identification number. (Integer > 0)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value

    @property
    def RID(self) -> int:
        """
           Identification number of a coordinate system that is defined independently from this coordinate system. (Integer > 0; Default = 0 is the basic coordinate
           system.)
        """
        return self.__cardinfo.RID

    @RID.setter
    def RID(self, value: int) -> None:
        self.__cardinfo.RID = value

    @property
    def A1(self) -> float:
        """
           Coordinates of three points in coordinate system defined in field 3. (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value

    @property
    def B1(self) -> float:
        """
           B1
        """
        return self.__cardinfo.B1

    @B1.setter
    def B1(self, value: float) -> None:
        self.__cardinfo.B1 = value

    @property
    def B2(self) -> float:
        """
           B2
        """
        return self.__cardinfo.B2

    @B2.setter
    def B2(self, value: float) -> None:
        self.__cardinfo.B2 = value

    @property
    def B3(self) -> float:
        """
           B3
        """
        return self.__cardinfo.B3

    @B3.setter
    def B3(self, value: float) -> None:
        self.__cardinfo.B3 = value

    @property
    def C1(self) -> float:
        """
           C1
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: float) -> None:
        self.__cardinfo.C1 = value

    @property
    def C2(self) -> float:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: float) -> None:
        self.__cardinfo.C2 = value

    @property
    def C3(self) -> float:
        """
           C3
        """
        return self.__cardinfo.C3

    @C3.setter
    def C3(self, value: float) -> None:
        self.__cardinfo.C3 = value


class CPENTANAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCpentaNas)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSOLID or PLSOLID entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected grid points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value

    @property
    def G11(self) -> int:
        """
           G11
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: int) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> int:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: int) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> int:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: int) -> None:
        self.__cardinfo.G13 = value

    @property
    def G14(self) -> int:
        """
           G14
        """
        return self.__cardinfo.G14

    @G14.setter
    def G14(self, value: int) -> None:
        self.__cardinfo.G14 = value

    @property
    def G15(self) -> int:
        """
           G15
        """
        return self.__cardinfo.G15

    @G15.setter
    def G15(self, value: int) -> None:
        self.__cardinfo.G15 = value


class CPENTAOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCpentaOpt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSOLID or PLSOLID entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected grid points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value

    @property
    def G11(self) -> int:
        """
           G11
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: int) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> int:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: int) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> int:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: int) -> None:
        self.__cardinfo.G13 = value

    @property
    def G14(self) -> int:
        """
           G14
        """
        return self.__cardinfo.G14

    @G14.setter
    def G14(self, value: int) -> None:
        self.__cardinfo.G14 = value

    @property
    def G15(self) -> int:
        """
           G15
        """
        return self.__cardinfo.G15

    @G15.setter
    def G15(self, value: int) -> None:
        self.__cardinfo.G15 = value

    @property
    def CORDM(self) -> str:
        """
           Flag indicating that the following field(s) reference data to determine the material coordinate system.
        """
        return self.__cardinfo.CORDM

    @CORDM.setter
    def CORDM(self, value: str) -> None:
        self.__cardinfo.CORDM = value

    @property
    def CID(self) -> int:
        """
           Material coordinate system identification number. Default = 0 (Integer ≥ -1)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value

    @property
    def THETA(self) -> float:
        """
           Angle of rotation of the elemental X-axis and Y-axis about the elemental Z-axis. The new coordinate system formed after this rotational transformation
           represents the material system (the PHI field can further transform the material system). Note: For positive THETA, the elemental X-axis is rotated
           towards the elemental Y-axis. Default = blank (Real)
        """
        return self.__cardinfo.THETA

    @THETA.setter
    def THETA(self, value: float) -> None:
        self.__cardinfo.THETA = value

    @property
    def PHI(self) -> float:
        """
           This angle is applied on the new coordinate system derived after transformation with THETA. Angle of rotation of the elemental Z-axis and new X-axis
           about the new Y-axis.The new coordinate system formed after this rotational transformation represents the material system.
           Note: For positive PHI, the new X-axis is rotated towards the elemental Z-axis. Default = blank (Real)
        """
        return self.__cardinfo.PHI

    @PHI.setter
    def PHI(self, value: float) -> None:
        self.__cardinfo.PHI = value


class CPYRA(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCpyra)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Unique element identification number. No default (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           A PSOLID property entry identification number. Default = EID (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. Default = blank(Integer ≥ 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value

    @property
    def G11(self) -> int:
        """
           G11
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: int) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> int:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: int) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> int:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: int) -> None:
        self.__cardinfo.G13 = value

    @property
    def CORDM(self) -> str:
        """
           Flag indicating that the following field reference data to determine the material coordinate system.
        """
        return self.__cardinfo.CORDM

    @CORDM.setter
    def CORDM(self, value: str) -> None:
        self.__cardinfo.CORDM = value

    @property
    def CID(self) -> int:
        """
           Material coordinate system identification number. Default = 0 (Integer ≥ -1)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value


class CQUAD4(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCquad4, CardCquad4*, *CardCquad4, ...)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSHELL, PCOMP, or PLPLANE entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integers > 0, all unique.)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def THETA(self) -> float:
        """
           Material property orientation angle in degrees. THETA is ignored for hyperelastic elements.See Figure 8-46. (Real; Default = 0.0)
        """
        return self.__cardinfo.THETA

    @THETA.setter
    def THETA(self, value: float) -> None:
        self.__cardinfo.THETA = value

    @property
    def MCID(self) -> int:
        """
           Material coordinate system identification number. The x-axis of the material coordinate system is determined by projecting the x-axis
           of the MCID coordinate system(defined by the CORDij entry or zero for the basic coordinate system) onto the surface of the element.
           Use DIAG 38 to print the computed THETA values. MCID is ignored for hyperelastic elements. For SOL 600, only CORD2R is allowed.
           (Integer >= 0; If blank, then THETA = 0.0 is assumed.)
        """
        return self.__cardinfo.MCID

    @MCID.setter
    def MCID(self, value: int) -> None:
        self.__cardinfo.MCID = value

    @property
    def ZOFFS(self) -> float:
        """
           Offset from the surface of grid points to the element reference plane. ZOFFS is ignored for hyperelastic elements.See Remark 6. (Real)
        """
        return self.__cardinfo.ZOFFS

    @ZOFFS.setter
    def ZOFFS(self, value: float) -> None:
        self.__cardinfo.ZOFFS = value

    @property
    def TFLAG(self) -> int:
        """
           An integer flag, signifying the meaning of the Ti values. (Integer 0, 1, or blank)
        """
        return self.__cardinfo.TFLAG

    @TFLAG.setter
    def TFLAG(self, value: int) -> None:
        self.__cardinfo.TFLAG = value

    @property
    def T1(self) -> float:
        """
           Membrane thickness of element at grid points G1 through G4.If “TFLAG” is zero or blank, then Ti are actual user specified thicknesses.
           See Remark 4*. for default. (Real >= 0.0 or blank, not all zero.)
           If “TFLAG” is one, then the Ti are fractions relative to the T value of the PSHELL.
           (Real > 0.0 or blank, not all zero.Default = 1.0)
           Ti are ignored for hyperelastic elements.

            *Remark 4: The continuation is optional. If it is not supplied, then T1 through T4 will be set equal to the
            value of T on the PSHELL entry.
        """
        return self.__cardinfo.T1

    @T1.setter
    def T1(self, value: float) -> None:
        self.__cardinfo.T1 = value

    @property
    def T2(self) -> float:
        """
           T2
        """
        return self.__cardinfo.T2

    @T2.setter
    def T2(self, value: float) -> None:
        self.__cardinfo.T2 = value

    @property
    def T3(self) -> float:
        """
           T3
        """
        return self.__cardinfo.T3

    @T3.setter
    def T3(self, value: float) -> None:
        self.__cardinfo.T3 = value

    @property
    def T4(self) -> float:
        """
           T4
        """
        return self.__cardinfo.T4

    @T4.setter
    def T4(self, value: float) -> None:
        self.__cardinfo.T4 = value


class CQUAD8(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCquad8, CardCquad8*, *CardCquad8, ...)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSHELL, PCOMP, or PLPLANE entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected corner grid points.Required data for all four grid points. (Unique Integers > 0)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           Identification numbers of connected edge grid points. Optional data for any or all four grid points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value

    @property
    def T1(self) -> float:
        """
           Membrane thickness of element at grid points G1 through G4.If “TFLAG” is zero or blank, then Ti are actual user specified thicknesses.
           See Remark 4*. for default. (Real >= 0.0 or blank, not all zero.)
           If “TFLAG” is one, then the Ti are fractions relative to the T value of the PSHELL.
           (Real > 0.0 or blank, not all zero.Default = 1.0)
           Ti are ignored for hyperelastic elements.

           *Remark 4: The continuation is optional. If it is not supplied, then T1 through T4 will be set equal to the
           value of T on the PSHELL entry.
        """
        return self.__cardinfo.T1

    @T1.setter
    def T1(self, value: float) -> None:
        self.__cardinfo.T1 = value

    @property
    def T2(self) -> float:
        """
           T2
        """
        return self.__cardinfo.T2

    @T2.setter
    def T2(self, value: float) -> None:
        self.__cardinfo.T2 = value

    @property
    def T3(self) -> float:
        """
           T3
        """
        return self.__cardinfo.T3

    @T3.setter
    def T3(self, value: float) -> None:
        self.__cardinfo.T3 = value

    @property
    def T4(self) -> float:
        """
           T4
        """
        return self.__cardinfo.T4

    @T4.setter
    def T4(self, value: float) -> None:
        self.__cardinfo.T4 = value

    @property
    def THETA(self) -> float:
        """
           Material property orientation angle in degrees. THETA is ignored for hyperelastic elements.See Figure 8-46. (Real; Default = 0.0)
        """
        return self.__cardinfo.THETA

    @THETA.setter
    def THETA(self, value: float) -> None:
        self.__cardinfo.THETA = value

    @property
    def MCID(self) -> int:
        """
           Material coordinate system identification number. The x-axis of the material coordinate system is determined by projecting the x-axis
           of the MCID coordinate system(defined by the CORDij entry or zero for the basic coordinate system) onto the surface of the element.
           Use DIAG 38 to print the computed THETA values. MCID is ignored for hyperelastic elements. For SOL 600, only CORD2R is allowed.
           (Integer >= 0; If blank, then THETA = 0.0 is assumed.)
        """
        return self.__cardinfo.MCID

    @MCID.setter
    def MCID(self, value: int) -> None:
        self.__cardinfo.MCID = value

    @property
    def ZOFFS(self) -> float:
        """
           Offset from the surface of grid points to the element reference plane. ZOFFS is ignored for hyperelastic elements.See Remark 6. (Real)
        """
        return self.__cardinfo.ZOFFS

    @ZOFFS.setter
    def ZOFFS(self, value: float) -> None:
        self.__cardinfo.ZOFFS = value

    @property
    def TFLAG(self) -> int:
        """
           An integer flag, signifying the meaning of the Ti values. (Integer 0, 1, or blank)
        """
        return self.__cardinfo.TFLAG

    @TFLAG.setter
    def TFLAG(self, value: int) -> None:
        self.__cardinfo.TFLAG = value


class CROD(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCrod)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PROD entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integer > 0 ; G1 ≠ G2)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value


class CSHEAR(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCshear)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSHEAR entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected grid points. (Integer >= 0 ; G1 ≠ G2 ≠ G3 ≠ G4)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value


class CTETRANAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCtetraNas)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSOLID or PLSOLID entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected grid points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value


class CTETRAOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCtetraOpt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSOLID or PLSOLID entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected grid points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           G4
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def G7(self) -> int:
        """
           G7
        """
        return self.__cardinfo.G7

    @G7.setter
    def G7(self, value: int) -> None:
        self.__cardinfo.G7 = value

    @property
    def G8(self) -> int:
        """
           G8
        """
        return self.__cardinfo.G8

    @G8.setter
    def G8(self, value: int) -> None:
        self.__cardinfo.G8 = value

    @property
    def G9(self) -> int:
        """
           G9
        """
        return self.__cardinfo.G9

    @G9.setter
    def G9(self, value: int) -> None:
        self.__cardinfo.G9 = value

    @property
    def G10(self) -> int:
        """
           G10
        """
        return self.__cardinfo.G10

    @G10.setter
    def G10(self, value: int) -> None:
        self.__cardinfo.G10 = value

    @property
    def CORDM(self) -> str:
        """
           Flag indicating that the following field references the material coordinate system.
        """
        return self.__cardinfo.CORDM

    @CORDM.setter
    def CORDM(self, value: str) -> None:
        self.__cardinfo.CORDM = value

    @property
    def CID(self) -> int:
        """
           Material coordinate system identification number. Default = 0 (Integer ≥ -1)
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value


class CTRIA3(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCtria3, CardCtria3*, *CardCtria3, ...)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSHELL, PCOMP, or PLPLANE entry. (Integer > 0; Default = EID)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integers > 0, all unique.)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def THETA(self) -> float:
        """
           Material property orientation angle in degrees. THETA is ignored for hyperelastic elements. (Real; Default = 0.0)
        """
        return self.__cardinfo.THETA

    @THETA.setter
    def THETA(self, value: float) -> None:
        self.__cardinfo.THETA = value

    @property
    def MCID(self) -> int:
        """
           Material coordinate system identification number. The x-axis of the material coordinate system is determined by projecting the x-axis
           of the MCID coordinate system(defined by the CORDij entry or zero for the basic coordinate system) onto the surface of the element.
           Use DIAG 38 to print the computed THETA values. MCID is ignored for hyperelastic elements. For SOL 600, only CORD2R is allowed.
           (Integer >= 0; If blank, then THETA = 0.0 is assumed.)
        """
        return self.__cardinfo.MCID

    @MCID.setter
    def MCID(self, value: int) -> None:
        self.__cardinfo.MCID = value

    @property
    def ZOFFS(self) -> float:
        """
           Offset from the surface of grid points to the element reference plane. ZOFFS is ignored for hyperelastic elements.See Remark 3. (Real)
        """
        return self.__cardinfo.ZOFFS

    @ZOFFS.setter
    def ZOFFS(self, value: float) -> None:
        self.__cardinfo.ZOFFS = value

    @property
    def TFLAG(self) -> int:
        """
           An integer flag, signifying the meaning of the Ti values. (Integer 0, 1, or blank)
        """
        return self.__cardinfo.TFLAG

    @TFLAG.setter
    def TFLAG(self, value: int) -> None:
        self.__cardinfo.TFLAG = value

    @property
    def T1(self) -> float:
        """
           Membrane thickness of element at grid points G1 through G4.If “TFLAG” is zero or blank, then Ti are actual user specified thicknesses.
           See Remark 4*. for default. (Real >= 0.0 or blank, not all zero.)
           If “TFLAG” is one, then the Ti are fractions relative to the T value of the PSHELL.
           (Real > 0.0 or blank, not all zero.Default = 1.0)
           Ti are ignored for hyperelastic elements.
        """
        return self.__cardinfo.T1

    @T1.setter
    def T1(self, value: float) -> None:
        self.__cardinfo.T1 = value

    @property
    def T2(self) -> float:
        """
           T2
        """
        return self.__cardinfo.T2

    @T2.setter
    def T2(self, value: float) -> None:
        self.__cardinfo.T2 = value

    @property
    def T3(self) -> float:
        """
           T3
        """
        return self.__cardinfo.T3

    @T3.setter
    def T3(self, value: float) -> None:
        self.__cardinfo.T3 = value


class CTRIA6(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCtria6, CardCtria6*, *CardCtria6, ...)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           Property identification number of a PSHELL, PCOMP, or PLPLANE entry. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           Identification numbers of connected corner grid points. (Unique Integers > 0)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def G3(self) -> int:
        """
           G3
        """
        return self.__cardinfo.G3

    @G3.setter
    def G3(self, value: int) -> None:
        self.__cardinfo.G3 = value

    @property
    def G4(self) -> int:
        """
           Identification number of connected edge grid points. Optional data for any or all three points. (Integer >= 0 or blank)
        """
        return self.__cardinfo.G4

    @G4.setter
    def G4(self, value: int) -> None:
        self.__cardinfo.G4 = value

    @property
    def G5(self) -> int:
        """
           G5
        """
        return self.__cardinfo.G5

    @G5.setter
    def G5(self, value: int) -> None:
        self.__cardinfo.G5 = value

    @property
    def G6(self) -> int:
        """
           G6
        """
        return self.__cardinfo.G6

    @G6.setter
    def G6(self, value: int) -> None:
        self.__cardinfo.G6 = value

    @property
    def THETA(self) -> float:
        """
           Material property orientation angle in degrees. THETA is ignored for hyperelastic elements. (Real; Default = 0.0)
        """
        return self.__cardinfo.THETA

    @THETA.setter
    def THETA(self, value: float) -> None:
        self.__cardinfo.THETA = value

    @property
    def MCID(self) -> int:
        """
           Material coordinate system identification number. The x-axis of the material coordinate system is determined by projecting the x-axis
           of the MCID coordinate system(defined by the CORDij entry or zero for the basic coordinate system) onto the surface of the element.
           Use DIAG 38 to print the computed THETA values. MCID is ignored for hyperelastic elements. For SOL 600, only CORD2R is allowed.
           (Integer >= 0; If blank, then THETA = 0.0 is assumed.)
        """
        return self.__cardinfo.MCID

    @MCID.setter
    def MCID(self, value: int) -> None:
        self.__cardinfo.MCID = value

    @property
    def ZOFFS(self) -> float:
        """
           Offset from the surface of grid points to the element reference plane. ZOFFS is ignored for hyperelastic elements.See Remark 3. (Real)
        """
        return self.__cardinfo.ZOFFS

    @ZOFFS.setter
    def ZOFFS(self, value: float) -> None:
        self.__cardinfo.ZOFFS = value

    @property
    def T1(self) -> float:
        """
           Membrane thickness of element at grid points G1 through G4.If “TFLAG” is zero or blank, then Ti are actual user specified thicknesses.
           See Remark 4*. for default. (Real >= 0.0 or blank, not all zero.)
           If “TFLAG” is one, then the Ti are fractions relative to the T value of the PSHELL.
           (Real > 0.0 or blank, not all zero.Default = 1.0)
           Ti are ignored for hyperelastic elements.
        """
        return self.__cardinfo.T1

    @T1.setter
    def T1(self, value: float) -> None:
        self.__cardinfo.T1 = value

    @property
    def T2(self) -> float:
        """
           T2
        """
        return self.__cardinfo.T2

    @T2.setter
    def T2(self, value: float) -> None:
        self.__cardinfo.T2 = value

    @property
    def T3(self) -> float:
        """
           T3
        """
        return self.__cardinfo.T3

    @T3.setter
    def T3(self, value: float) -> None:
        self.__cardinfo.T3 = value

    @property
    def TFLAG(self) -> int:
        """
           An integer flag, signifying the meaning of the Ti values. (Integer 0, 1, or blank)
        """
        return self.__cardinfo.TFLAG

    @TFLAG.setter
    def TFLAG(self, value: int) -> None:
        self.__cardinfo.TFLAG = value


class CWELD(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardCweld)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EWID(self) -> int:
        """
           CardCweld element identification number. See Remark 1. (Integer > 0)
           * Remark 1:
           CardCweld defines a flexible connection between two surface patches, between a point and a surface patch, or between two shell vertex grid points.
           See Figure 8-72 through Figure 8-76.
        """
        return self.__cardinfo.EWID

    @EWID.setter
    def EWID(self, value: int) -> None:
        self.__cardinfo.EWID = value

    @property
    def PWID(self) -> int:
        """
           Property identification number of a PWELD entry. (Integer > 0)
        """
        return self.__cardinfo.PWID

    @PWID.setter
    def PWID(self, value: int) -> None:
        self.__cardinfo.PWID = value

    @property
    def GS(self) -> int:
        """
           Identification number of a grid point which defines the location of the connector.See Remarks 2. and 3.
           * Remark 2:
           CardGrid point GS defines the approximate location of the connector in space. GS is projected on surface patch A and on surface patch B.The resulting piercing
           points GA and GB define the axis of the connector. GS must have a normal projection on surface patch A and B. GS does not have to lie on the surface
           patches. GS is ignored for format “ALIGN”. GA is used instead of GS if GS is not specified. For the formats “ELPAT” and “PARTPAT,” if GS and GA are
           not specified, then XS, YS, and ZS must be specified.
           * Remark 3:
           The connectivity between grid points on surface patch A and grid points on surface patch B is generated depending on the location of GS and the cross
           sectional area of the connector.Diagnostic print outs, checkout runs and non default settings of search and projection parameters are requested on the
           SWLDPRM Bulk Data entry.It is recommended to start with the default settings.
        """
        return self.__cardinfo.GS

    @GS.setter
    def GS(self, value: int) -> None:
        self.__cardinfo.GS = value

    @property
    def TYPE(self) -> str:
        """
           Character string indicating the type of connection.The format of the subsequent entries depends on the type. “PARTPAT”, for example, indicates that the
           connectivity of surface patch A to surface patch B is defined with two property identification numbers of PSHELL entries, PIDA and PIDB, respectively.The
           “PARTPAT” format connects up to 3x3 elements per patch. See Remark 4. Character string indicating that the connectivity of surface patch A to surface
           patch B is defined with two shell element identification numbers, SHIDA and SHIDB, respectively.The “ELPAT” format connects up to 3x3 elements per patch.
           See Remark 6. The “ELEMID” format connects one shell element perpatch. See Remark 7. Character string indicating that the  connectivity of surface patch
           A to surface patch B is defined with two sequences of grid point identification numbers, GAi and GBi, respectively.The “GRIDID” format connects the
           surface of any element.See Remark 8. Character string indicating that the connectivity of surface A to surface B is defined with two shell vertex grid points
           GA and GB, respectively. See Remark 11.
           * Remark 4:
           The format “PARTPAT” defines a connection of two shell element patches A and B with PSHELL property identification numbers PIDA and PIDB, respectively.
           The two property identification numbers must be different, see Figure 8-72. Depending on the location of the piercing points GA, GB and the
           size of the diameter D, the number of connected elements per patch ranges from a single element up to 3x3 elements.The diameter D is defined on the
           PWELD property entry. For this option, shell element patches A and B are allowed to share a common grid.
           * Remark 6:
           The format “ELPAT” defines a connection of two shell element patches A and B with shell element identification numbers SHIDA and SHIDB, see
           Figure 8-72. The connectivity is similar to the format “PARTPAT”. Depending on the location of the piercing points GA, GB and the size of the
           diameter D, the number of connected elements per patch may range from a single element up to 3x3 elements.For this option, shell element patches A
           and B are allowed to share a common grid.
           * Remark 7:
           The format “ELEMID” defines a connection of two shell element patches A and B with shell element identification numbers SHIDA and SHIDB, see
           Figure 8-73. The connectivity is restricted to a single element per patch regardless of the location of GA, GB and regardless of the size of the diameter
           of the connector.In addition, the format “ELEMID” can define a point to patch connection if SHIDB is left blank, see Figure 8-74. Then grid GS is
           connected to shell SHIDA.
           * Remark 8:
           The format “GRIDID” defines a connection of two surface patches A and B with a sequence of grid points GAi and GBi, see Figure 8-73. In addition, the
           format “GRIDID” can define a point to patch connection if all GBi fields are left blank, see Figure 8-74. Then grid GS is connected to grids GAi.The grids
           GAi and GBi do not have to belong to shell elements.
           * Remark 11:
           The format "ALIGN" defines a point to point connection, see Figure 8-76. GA and GB are required, they must be existing vertex nodes of shell elements.
           For the other formats, GA and GB are not required. Two shell normals in the direction GA-GB are generated at GA and GB, respectively.
        """
        return self.__cardinfo.TYPE

    @TYPE.setter
    def TYPE(self, value: str) -> None:
        self.__cardinfo.TYPE = value

    @property
    def GA(self) -> int:
        """
           CardGrid point identification numbers of piercing points on surface A and surface B, respectively. See Remark 5. (Integer > 0 or blank)
           * Remark 5:
           The definition of the piercing grid points GA and GB is optional for all formats with the exception of the format “ALIGN”. If GA and GB are given,
           GS is ignored.If GA and GB are not specified, they are generated from the normal projection of GS on surface patches A and B.For the formats
           “ELEMID” and “GRIDID,” internal identification numbers are generated for GA and GB starting with 101e+6 by default. The offset number can be
           changed with PARAM, OSWPPT. If GA and GB are specified, they must lie on or at least have a projection on surface patches A and B, respectively. The
           locations of GA and GB are corrected so that they lie on surface patches A and B within machine precision accuracy.The length of the connector is the
           distance of grid point GA to GB.
           Vertex grid identification number of shell A and B, respectively. (Integer > 0)
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value

    @property
    def PIDA(self) -> int:
        """
           Property identification numbers of PSHELL entries defining surface A and B respectively. (Integer > 0)
        """
        return self.__cardinfo.PIDA

    @PIDA.setter
    def PIDA(self, value: int) -> None:
        self.__cardinfo.PIDA = value

    @property
    def PIDB(self) -> int:
        """
           PIDB
        """
        return self.__cardinfo.PIDB

    @PIDB.setter
    def PIDB(self, value: int) -> None:
        self.__cardinfo.PIDB = value

    @property
    def XS(self) -> float:
        """
           Coordinates of spot weld location in basic. See Remark 2. (Real)
           * Remark 2:
           CardGrid point GS defines the approximate location of the connector in space. GS is projected on surface patch A and on surface patch B.The resulting piercing
           points GA and GB define the axis of the connector. GS must have a normal projection on surface patch A and B. GS does not have to lie on the surface
           patches. GS is ignored for format “ALIGN”. GA is used instead of GS if GS is not specified. For the formats “ELPAT” and “PARTPAT,” if GS and GA are
           not specified, then XS, YS, and ZS must be specified.
        """
        return self.__cardinfo.XS

    @XS.setter
    def XS(self, value: float) -> None:
        self.__cardinfo.XS = value

    @property
    def YS(self) -> float:
        """
           YS
        """
        return self.__cardinfo.YS

    @YS.setter
    def YS(self, value: float) -> None:
        self.__cardinfo.YS = value

    @property
    def ZS(self) -> float:
        """
           ZS
        """
        return self.__cardinfo.ZS

    @ZS.setter
    def ZS(self, value: float) -> None:
        self.__cardinfo.ZS = value

    @property
    def SHIDA(self) -> int:
        """
           Shell element identification numbers of elements on patch A and B, respectively. (Integer > 0)
        """
        return self.__cardinfo.SHIDA

    @SHIDA.setter
    def SHIDA(self, value: int) -> None:
        self.__cardinfo.SHIDA = value

    @property
    def SHIDB(self) -> int:
        """
           SHIDB
        """
        return self.__cardinfo.SHIDB

    @SHIDB.setter
    def SHIDB(self, value: int) -> None:
        self.__cardinfo.SHIDB = value

    @property
    def SPTYP(self) -> str:
        """
           Character string indicating types of surface patches A and B.SPTYP=”QQ”, “TT”, “QT”, “TQ”, “Q” or “T”. See Remark 9.
           * Remark 9:
           SPTYP defines the type of surface patches to be connected. SPTYP is required for the format "GRIDID" to identify quadrilateral or triangular patches.The
           combinations are:
           SPTYP           Description
           QQ              Connects a quadrilateral surface patch A(Q4 to Q8) with a quadrilateral surface patch B(Q4 to Q8).
           QT              Connects a quadrilateral surface patch A(Q4 to Q8) with a triangular surface patch B(T3 to T6).
           TT              Connects a triangular surface patch A(T3 to T6) with a triangular surface patch B(T3 to T6).
           TQ              Connects a triangular surface patch A(T3 to T6) with a quadrilateral surface patch B(Q4 to Q8).
           Q               Connects the shell vertex grid GS with a quadrilateral surface patch A(Q4 to Q8) if surface patch B is not specified.
           T               Connects the shell vertex grid GS with a triangular surface patch A (T3 to T6) if surface patch B is not specified.
        """
        return self.__cardinfo.SPTYP

    @SPTYP.setter
    def SPTYP(self, value: str) -> None:
        self.__cardinfo.SPTYP = value

    @property
    def GA1(self) -> int:
        """
           CardGrid identification numbers of surface patch A.GA1 to GA3 are required. See Remark 10. (Integer > 0)
           * Remark 10:
           GAi are required for the format "GRIDID". At least 3 and at most 8 grid IDs may be specified for GAi and GBi, respectively.The rules of the triangular
           and quadrilateral elements apply for the order of GAi and GBi, see Figure 8-75. Missing midside nodes are allowed.
        """
        return self.__cardinfo.GA1

    @GA1.setter
    def GA1(self, value: int) -> None:
        self.__cardinfo.GA1 = value

    @property
    def GA2(self) -> int:
        """
           GA2
        """
        return self.__cardinfo.GA2

    @GA2.setter
    def GA2(self, value: int) -> None:
        self.__cardinfo.GA2 = value

    @property
    def GA3(self) -> int:
        """
           GA3
        """
        return self.__cardinfo.GA3

    @GA3.setter
    def GA3(self, value: int) -> None:
        self.__cardinfo.GA3 = value

    @property
    def GA4(self) -> int:
        """
           GA4
        """
        return self.__cardinfo.GA4

    @GA4.setter
    def GA4(self, value: int) -> None:
        self.__cardinfo.GA4 = value

    @property
    def GA5(self) -> int:
        """
           GA5
        """
        return self.__cardinfo.GA5

    @GA5.setter
    def GA5(self, value: int) -> None:
        self.__cardinfo.GA5 = value

    @property
    def GA6(self) -> int:
        """
           GA6
        """
        return self.__cardinfo.GA6

    @GA6.setter
    def GA6(self, value: int) -> None:
        self.__cardinfo.GA6 = value

    @property
    def GA7(self) -> int:
        """
           GA7
        """
        return self.__cardinfo.GA7

    @GA7.setter
    def GA7(self, value: int) -> None:
        self.__cardinfo.GA7 = value

    @property
    def GA8(self) -> int:
        """
           GA8
        """
        return self.__cardinfo.GA8

    @GA8.setter
    def GA8(self, value: int) -> None:
        self.__cardinfo.GA8 = value

    @property
    def GB1(self) -> int:
        """
           CardGrid identification numbers of surface patch B. See Remark 10. (Integer > 0)
           * Remark 10:
           GAi are required for the format "GRIDID". At least 3 and at most 8 grid IDs may be specified for GAi and GBi, respectively.The rules of the triangular
           and quadrilateral elements apply for the order of GAi and GBi, see Figure 8-75. Missing midside nodes are allowed.
        """
        return self.__cardinfo.GB1

    @GB1.setter
    def GB1(self, value: int) -> None:
        self.__cardinfo.GB1 = value

    @property
    def GB2(self) -> int:
        """
           GB2
        """
        return self.__cardinfo.GB2

    @GB2.setter
    def GB2(self, value: int) -> None:
        self.__cardinfo.GB2 = value

    @property
    def GB3(self) -> int:
        """
           GB3
        """
        return self.__cardinfo.GB3

    @GB3.setter
    def GB3(self, value: int) -> None:
        self.__cardinfo.GB3 = value

    @property
    def GB4(self) -> int:
        """
           GB4
        """
        return self.__cardinfo.GB4

    @GB4.setter
    def GB4(self, value: int) -> None:
        self.__cardinfo.GB4 = value

    @property
    def GB5(self) -> int:
        """
           GB5
        """
        return self.__cardinfo.GB5

    @GB5.setter
    def GB5(self, value: int) -> None:
        self.__cardinfo.GB5 = value

    @property
    def GB6(self) -> int:
        """
           GB6
        """
        return self.__cardinfo.GB6

    @GB6.setter
    def GB6(self, value: int) -> None:
        self.__cardinfo.GB6 = value

    @property
    def GB7(self) -> int:
        """
           GB7
        """
        return self.__cardinfo.GB7

    @GB7.setter
    def GB7(self, value: int) -> None:
        self.__cardinfo.GB7 = value

    @property
    def GB8(self) -> int:
        """
           GB8
        """
        return self.__cardinfo.GB8

    @GB8.setter
    def GB8(self, value: int) -> None:
        self.__cardinfo.GB8 = value


class GRID(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (GRID, GRID*, *GRID, ...)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def ID(self) -> int:
        """
           CardCardGrid point identification number. (0 < Integer < 100000000)
        """
        return self.__cardinfo.ID

    @ID.setter
    def ID(self, value: int) -> None:
        self.__cardinfo.ID = value

    @property
    def CP(self) -> int:
        """
           Identification number of coordinate system in which the location of the grid point is defined. (Integer >= 0 or blank*)
        """
        return self.__cardinfo.CP

    @CP.setter
    def CP(self, value: int) -> None:
        self.__cardinfo.CP = value

    @property
    def X1(self) -> float:
        """
           Location of the grid point in coordinate system CP. (Real; Default = 0.0)
        """
        return self.__cardinfo.X1

    @X1.setter
    def X1(self, value: float) -> None:
        self.__cardinfo.X1 = value

    @property
    def X2(self) -> float:
        """
           Location of the grid point in coordinate system CP. (Real; Default = 0.0)
        """
        return self.__cardinfo.X2

    @X2.setter
    def X2(self, value: float) -> None:
        self.__cardinfo.X2 = value

    @property
    def X3(self) -> float:
        """
           Location of the grid point in coordinate system CP. (Real; Default = 0.0)
        """
        return self.__cardinfo.X3

    @X3.setter
    def X3(self, value: float) -> None:
        self.__cardinfo.X3 = value

    @property
    def CD(self) -> int:
        """
           Identification number of coordinate system in which the displacements, degrees-of-freedom, constraints,
           and solution vectors are defined at the grid point. (Integer >= -1 or blank)*
        """
        return self.__cardinfo.CD

    @CD.setter
    def CD(self, value: int) -> None:
        self.__cardinfo.CD = value

    @property
    def PS(self) -> int:
        """
           Permanent single-point constraints associated with the grid point.
           (Any of the Integers 1 through 6 with no embedded blanks, or blank*.)
        """
        return self.__cardinfo.PS

    @PS.setter
    def PS(self, value: int) -> None:
        self.__cardinfo.PS = value

    @property
    def SEID(self) -> int:
        """
           Superelement identification number. (Integer >= 0; Default = 0)
        """
        return self.__cardinfo.SEID

    @SEID.setter
    def SEID(self, value: int) -> None:
        self.__cardinfo.SEID = value


class MAT10NAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat10Nas)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def BULK(self) -> float:
        """
           Bulk modulus. (Real > 0.0)
        """
        return self.__cardinfo.BULK

    @BULK.setter
    def BULK(self, value: float) -> None:
        self.__cardinfo.BULK = value

    @property
    def RHO(self) -> float:
        """
           Mass density. (Real > 0.0)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def C(self) -> float:
        """
           Speed of sound. (Real > 0.0)
        """
        return self.__cardinfo.C

    @C.setter
    def C(self, value: float) -> None:
        self.__cardinfo.C = value

    @property
    def GE(self) -> float:
        """
           Fluid element damping coefficient. (Real)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value


class MAT10OPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat10Opt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Unique material identification. No default (Integer > 0 or <String>)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def BULK(self) -> float:
        """
           Bulk modulus. No default (Real > 0.0)
        """
        return self.__cardinfo.BULK

    @BULK.setter
    def BULK(self, value: float) -> None:
        self.__cardinfo.BULK = value

    @property
    def RHO(self) -> float:
        """
           Mass density. Automatically computes the mass. No default (Real > 0.0)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def C(self) -> float:
        """
           Speed of sound. No default (Real > 0.0)
        """
        return self.__cardinfo.C

    @C.setter
    def C(self, value: float) -> None:
        self.__cardinfo.C = value

    @property
    def GE(self) -> float:
        """
           Fluid element damping coefficient. No default (Real)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def ALPHA(self) -> float:
        """
           Normalized porous material damping coefficient. Since the admittance is a function of frequency, the value of ALPHA should be chosen for the frequency range
           of interest for the analysis. No default (Real)
        """
        return self.__cardinfo.ALPHA

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA = value


class MAT1NAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat1Nas)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def E(self) -> float:
        """
           Young’s modulus. (Real > 0.0 or blank)
        """
        return self.__cardinfo.E

    @E.setter
    def E(self, value: float) -> None:
        self.__cardinfo.E = value

    @property
    def G(self) -> float:
        """
           Shear modulus. (Real > 0.0 or blank)
        """
        return self.__cardinfo.G

    @G.setter
    def G(self, value: float) -> None:
        self.__cardinfo.G = value

    @property
    def NU(self) -> float:
        """
           Poisson’s ratio. (-1.0 < Real < 0.5 or blank)
        """
        return self.__cardinfo.NU

    @NU.setter
    def NU(self, value: float) -> None:
        self.__cardinfo.NU = value

    @property
    def RHO(self) -> float:
        """
           Mass density. See Remark 5. (Real)
           * Remark 5:
           The mass density RHO will be used to compute mass for all structural elements automatically.
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def A(self) -> float:
        """
           Thermal expansion coefficient. (Real)
        """
        return self.__cardinfo.A

    @A.setter
    def A(self, value: float) -> None:
        self.__cardinfo.A = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation of thermal loads, or a temperature-dependent thermal expansion coefficient. See Remarks 9. and 10.
           (Real; Default = 0.0 if A is specified.)
           * Remark 9:
           TREF and GE are ignored if the MAT1 entry is referenced by a PCOMP entry.
           * Remark 10:
           TREF is used in two different ways:
           • In nonlinear static analysis(SOL 106), TREF is used only for the calculation of a temperature-dependent thermal expansion coefficient.
           The reference temperature for the calculation of thermal loads is obtained from the TEMPERATURE(INITIAL) set selection.
           • In all SOLs except 106, TREF is used only as the reference temperature for the calculation of thermal loads.TEMPERATURE(INITIAL) may
           be used for this purpose, but TREF must be blank.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. See Remarks 8., 9., and 4. (Real)
           * Remark 8:
           To obtain the damping coefficient GE, multiply the critical damping ratio C ⁄ C0, by 2.0.
           * Remark 9:
           TREF and GE are ignored if the MAT1 entry is referenced by a PCOMP entry.
           * Remark 4:
           MAT1 materials may be made temperature-dependent by use of the MATT1 entry.In SOL 106, linear and nonlinear elastic material properties in the
           residual structure will be updated as prescribed under the TEMPERATURE Case Control command.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def ST(self) -> float:
        """
           Stress limits for tension, compression, and shear are optionally supplied, used only to compute margins of safety in certain elements;
           and have no effect on the computational procedures.See “Beam Element (CBEAM)” in Chapter 3 of the MSC.Nastran Reference Guide. (Real > 0.0 or blank)
        """
        return self.__cardinfo.ST

    @ST.setter
    def ST(self, value: float) -> None:
        self.__cardinfo.ST = value

    @property
    def SC(self) -> float:
        """
           SC
        """
        return self.__cardinfo.SC

    @SC.setter
    def SC(self, value: float) -> None:
        self.__cardinfo.SC = value

    @property
    def SS(self) -> float:
        """
           SS
        """
        return self.__cardinfo.SS

    @SS.setter
    def SS(self, value: float) -> None:
        self.__cardinfo.SS = value

    @property
    def MCSID(self) -> int:
        """
           Material coordinate system identification number. Used only for PARAM,CURV processing.See “Parameters” on page 631. (Integer > 0 or blank)
        """
        return self.__cardinfo.MCSID

    @MCSID.setter
    def MCSID(self, value: int) -> None:
        self.__cardinfo.MCSID = value


class MAT1OPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat1Opt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def E(self) -> float:
        """
           Young’s modulus. (Real > 0.0 or blank)
        """
        return self.__cardinfo.E

    @E.setter
    def E(self, value: float) -> None:
        self.__cardinfo.E = value

    @property
    def G(self) -> float:
        """
           Shear modulus. (Real > 0.0 or blank)
        """
        return self.__cardinfo.G

    @G.setter
    def G(self, value: float) -> None:
        self.__cardinfo.G = value

    @property
    def NU(self) -> float:
        """
           Poisson’s ratio. If < 0.0, a warning is issued. (-1.0 < Real < 0.5 or blank)
        """
        return self.__cardinfo.NU

    @NU.setter
    def NU(self, value: float) -> None:
        self.__cardinfo.NU = value

    @property
    def RHO(self) -> float:
        """
           Mass density. Used to automatically compute mass for all structural elements. No default (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def A(self) -> float:
        """
           Thermal expansion coefficient. No default (Real)
        """
        return self.__cardinfo.A

    @A.setter
    def A(self, value: float) -> None:
        self.__cardinfo.A = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for thermal loading. Default = 0.0 (Real)
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. No default (Real)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def ST(self) -> float:
        """
           Stress limits in tension, compression and shear. Used for composite ply failure calculations. No default (Real)
        """
        return self.__cardinfo.ST

    @ST.setter
    def ST(self, value: float) -> None:
        self.__cardinfo.ST = value

    @property
    def SC(self) -> float:
        """
           SC
        """
        return self.__cardinfo.SC

    @SC.setter
    def SC(self, value: float) -> None:
        self.__cardinfo.SC = value

    @property
    def SS(self) -> float:
        """
           SS
        """
        return self.__cardinfo.SS

    @SS.setter
    def SS(self, value: float) -> None:
        self.__cardinfo.SS = value

    @property
    def MODULI(self) -> str:
        """
           Continuation line flag for moduli temporal property.
        """
        return self.__cardinfo.MODULI

    @MODULI.setter
    def MODULI(self, value: str) -> None:
        self.__cardinfo.MODULI = value

    @property
    def MTIME(self) -> str:
        """
           Material temporal property. This field controls the interpretation of the input material property for viscoelasticity.
           INSTANT
           This material property is considered as the Instantaneous material input for viscoelasticity on the MATVE entry.
           LONG(Default)
           This material property is considered as the Long-term relaxed material input for viscoelasticity on the MATVE entry.
        """
        return self.__cardinfo.MTIME

    @MTIME.setter
    def MTIME(self, value: str) -> None:
        self.__cardinfo.MTIME = value


class MAT2NAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat2Nas)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. See Remark 13. (Integer > 0)
           * Remark 13:
           PCOMP entries generate MAT2 entries equal to 100,000,000 plus the PCOMP PID.Explicitly specified MAT2 IDs must not conflict with internally
           generated MAT2 IDs.Furthermore, if MID is greater than 400,000,000 then A1, A2, and A3 are a special format. They are [G4] ⋅ [α4] not [α4]. If MIDs
           larger than 99999999 are used, PARAM, NOCOMPS,-1 must be specified to obtain stress output.
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def G11(self) -> float:
        """
           The material property matrix. (Real)
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: float) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> float:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: float) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> float:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: float) -> None:
        self.__cardinfo.G13 = value

    @property
    def G22(self) -> float:
        """
           G22
        """
        return self.__cardinfo.G22

    @G22.setter
    def G22(self, value: float) -> None:
        self.__cardinfo.G22 = value

    @property
    def G23(self) -> float:
        """
           G23
        """
        return self.__cardinfo.G23

    @G23.setter
    def G23(self, value: float) -> None:
        self.__cardinfo.G23 = value

    @property
    def G33(self) -> float:
        """
           G33
        """
        return self.__cardinfo.G33

    @G33.setter
    def G33(self, value: float) -> None:
        self.__cardinfo.G33 = value

    @property
    def RHO(self) -> float:
        """
           Mass density. (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def A1(self) -> float:
        """
           Thermal expansion coefficient vector. (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation of thermal loads, or a temperature-dependent thermal expansion coefficient. See Remarks 10 and 11.
           (Real or blank)
           * Remark 10:
           TREF and GE are ignored if this entry is referenced by a PCOMP entry.
           * Remark 11:
           TREF is used in two different ways:
           • In nonlinear static analysis(SOL 106), TREF is used only for the calculation of a temperature-dependent thermal expansion coefficient.
           The reference temperature for the calculation of thermal loads is obtained from the TEMPERATURE(INITIAL) set selection.
           • In all SOLs except 106, TREF is used only as the reference temperature for the calculation of thermal loads.TEMPERATURE(INITIAL) may
           be used for this purpose, but TREF must be blank.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. See Remarks 7., 10., and 12. (Real)
           * Remark 7:
           To obtain the damping coefficient GE, multiply the critical damping ratio C ⁄ C0, by 2.0.
           * Remark 10:
           TREF and GE are ignored if the MAT1 entry is referenced by a PCOMP entry.
           * Remark 12:
           If PARAM,W4 is not specified, GE is ignored in transient analysis. See “Parameters” on page 631.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def ST(self) -> float:
        """
           Stress limits for tension, compression, and shear are optionally supplied, used only to compute margins of safety in certain elements;
           and have no effect on the computational procedures.See “Beam Element (CBEAM)” in Chapter 3 of the MSC.Nastran Reference Guide. (Real or blank)
        """
        return self.__cardinfo.ST

    @ST.setter
    def ST(self, value: float) -> None:
        self.__cardinfo.ST = value

    @property
    def SC(self) -> float:
        """
           SC
        """
        return self.__cardinfo.SC

    @SC.setter
    def SC(self, value: float) -> None:
        self.__cardinfo.SC = value

    @property
    def SS(self) -> float:
        """
           SS
        """
        return self.__cardinfo.SS

    @SS.setter
    def SS(self, value: float) -> None:
        self.__cardinfo.SS = value

    @property
    def MCSID(self) -> int:
        """
           Material coordinate system identification number. Used only for PARAM,CURV processing.See “Parameters” on page 631. (Integer >= 0 or blank)
        """
        return self.__cardinfo.MCSID

    @MCSID.setter
    def MCSID(self, value: int) -> None:
        self.__cardinfo.MCSID = value


class MAT2OPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat2Opt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def G11(self) -> float:
        """
           The material property matrix. No default. (Real)
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: float) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> float:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: float) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> float:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: float) -> None:
        self.__cardinfo.G13 = value

    @property
    def G22(self) -> float:
        """
           G22
        """
        return self.__cardinfo.G22

    @G22.setter
    def G22(self, value: float) -> None:
        self.__cardinfo.G22 = value

    @property
    def G23(self) -> float:
        """
           G23
        """
        return self.__cardinfo.G23

    @G23.setter
    def G23(self, value: float) -> None:
        self.__cardinfo.G23 = value

    @property
    def G33(self) -> float:
        """
           G33
        """
        return self.__cardinfo.G33

    @G33.setter
    def G33(self, value: float) -> None:
        self.__cardinfo.G33 = value

    @property
    def RHO(self) -> float:
        """
           Mass density. Used to automatically compute mass for all structural elements. No default (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def A1(self) -> float:
        """
           Thermal expansion coefficient vector. No default (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation of thermal loads. Data from the MAT2 entry is used directly, without adjustment of equivalent E, G, or NU values.
           Default = blank(Real or blank)
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. No default (Real)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def ST(self) -> float:
        """
           Stress limits in tension, compression and shear. Used for composite ply failure calculations. No default (Real)
        """
        return self.__cardinfo.ST

    @ST.setter
    def ST(self, value: float) -> None:
        self.__cardinfo.ST = value

    @property
    def SC(self) -> float:
        """
           SC
        """
        return self.__cardinfo.SC

    @SC.setter
    def SC(self, value: float) -> None:
        self.__cardinfo.SC = value

    @property
    def SS(self) -> float:
        """
           SS
        """
        return self.__cardinfo.SS

    @SS.setter
    def SS(self, value: float) -> None:
        self.__cardinfo.SS = value


class MAT3(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat3)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def EX(self) -> float:
        """
           Young’s moduli in the x, , and z directions, respectively. (Real > 0.0)
        """
        return self.__cardinfo.EX

    @EX.setter
    def EX(self, value: float) -> None:
        self.__cardinfo.EX = value

    @property
    def ETH(self) -> float:
        """
           ETH
        """
        return self.__cardinfo.ETH

    @ETH.setter
    def ETH(self, value: float) -> None:
        self.__cardinfo.ETH = value

    @property
    def EZ(self) -> float:
        """
           EZ
        """
        return self.__cardinfo.EZ

    @EZ.setter
    def EZ(self, value: float) -> None:
        self.__cardinfo.EZ = value

    @property
    def NUXTH(self) -> float:
        """
           Poisson’s ratios (coupled strain ratios in the x , z , and zx directions, respectively). (Real)
        """
        return self.__cardinfo.NUXTH

    @NUXTH.setter
    def NUXTH(self, value: float) -> None:
        self.__cardinfo.NUXTH = value

    @property
    def NUTHZ(self) -> float:
        """
           NUTHZ
        """
        return self.__cardinfo.NUTHZ

    @NUTHZ.setter
    def NUTHZ(self, value: float) -> None:
        self.__cardinfo.NUTHZ = value

    @property
    def NUZX(self) -> float:
        """
           NUZX
        """
        return self.__cardinfo.NUZX

    @NUZX.setter
    def NUZX(self, value: float) -> None:
        self.__cardinfo.NUZX = value

    @property
    def RHO(self) -> float:
        """
           Mass density. (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def GZX(self) -> float:
        """
           Shear modulus. (Real > 0.0)
        """
        return self.__cardinfo.GZX

    @GZX.setter
    def GZX(self, value: float) -> None:
        self.__cardinfo.GZX = value

    @property
    def AX(self) -> float:
        """
           Thermal expansion coefficients. (Real)
        """
        return self.__cardinfo.AX

    @AX.setter
    def AX(self, value: float) -> None:
        self.__cardinfo.AX = value

    @property
    def ATH(self) -> float:
        """
           ATH
        """
        return self.__cardinfo.ATH

    @ATH.setter
    def ATH(self, value: float) -> None:
        self.__cardinfo.ATH = value

    @property
    def AZ(self) -> float:
        """
           AZ
        """
        return self.__cardinfo.AZ

    @AZ.setter
    def AZ(self, value: float) -> None:
        self.__cardinfo.AZ = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation of thermal loads or a temperature-dependent thermal expansion coefficient. See Remark 10. (Real or blank)
           * Remark 10:
           TREF is used for two different purposes:
           • In nonlinear static analysis(SOL 106), TREF is used only for the calculation of a temperature-dependent thermal expansion
           coefficient.The reference temperature for the calculation of thermal loads is obtained from the TEMPERATURE(INITIAL) set selection. See Remark 10.
           under the MAT1 description.
           • In all SOLs except 106, TREF is used only as the reference temperature for the calculation of thermal loads.TEMPERATURE(INITIAL) may
           be used for this purpose, but TREF must be blank.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. See Remarks 9. and 11. (Real)
           * Remark 9:
           To obtain the damping coefficient GE, multiply the critical damping ratio C ⁄ C0 by 2.0.
           * Remark 11:
           If PARAM,W4 is not specified, GE is ignored in transient analysis. See “Parameters” on page 631.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value


class MAT4(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat4)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def K(self) -> float:
        """
           Thermal conductivity. (Blank or Real > 0.0)
        """
        return self.__cardinfo.K

    @K.setter
    def K(self, value: float) -> None:
        self.__cardinfo.K = value

    @property
    def CP(self) -> float:
        """
           Heat capacity per unit mass at constant pressure (specific heat). (Blank or Real > 0.0)
        """
        return self.__cardinfo.CP

    @CP.setter
    def CP(self, value: float) -> None:
        self.__cardinfo.CP = value

    @property
    def p(self) -> float:
        """
           Density. (Real > 0.0; Default = 1.0)
        """
        return self.__cardinfo.p

    @p.setter
    def p(self, value: float) -> None:
        self.__cardinfo.p = value

    @property
    def H(self) -> float:
        """
           Free convection heat transfer coefficient. (Real or blank)
        """
        return self.__cardinfo.H

    @H.setter
    def H(self, value: float) -> None:
        self.__cardinfo.H = value

    @property
    def u(self) -> float:
        """
           Dynamic viscosity. See Remark 2. (Real > 0.0 or blank)
        """
        return self.__cardinfo.u

    @u.setter
    def u(self, value: float) -> None:
        self.__cardinfo.u = value

    @property
    def HGEN(self) -> float:
        """
           Heat generation capability used with QVOL entries. (Real > 0.0; Default = 1.0)
        """
        return self.__cardinfo.HGEN

    @HGEN.setter
    def HGEN(self, value: float) -> None:
        self.__cardinfo.HGEN = value

    @property
    def REFENTH(self) -> float:
        """
           Reference enthalpy. (Real or blank)
        """
        return self.__cardinfo.REFENTH

    @REFENTH.setter
    def REFENTH(self, value: float) -> None:
        self.__cardinfo.REFENTH = value

    @property
    def TCH(self) -> float:
        """
           Lower temperature limit at which phase change region is to occur. (Real or blank)
        """
        return self.__cardinfo.TCH

    @TCH.setter
    def TCH(self, value: float) -> None:
        self.__cardinfo.TCH = value

    @property
    def TDELTA(self) -> float:
        """
           Total temperature change range within which a phase change is to occur. (Real > 0.0 or blank)
        """
        return self.__cardinfo.TDELTA

    @TDELTA.setter
    def TDELTA(self, value: float) -> None:
        self.__cardinfo.TDELTA = value

    @property
    def QLAT(self) -> float:
        """
           Latent heat of fusion per unit mass associated with the phase change. (Real > 0.0 or blank)
        """
        return self.__cardinfo.QLAT

    @QLAT.setter
    def QLAT(self, value: float) -> None:
        self.__cardinfo.QLAT = value


class MAT5(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat5)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def KXX(self) -> float:
        """
           Thermal conductivity. (Real)
        """
        return self.__cardinfo.KXX

    @KXX.setter
    def KXX(self, value: float) -> None:
        self.__cardinfo.KXX = value

    @property
    def KXY(self) -> float:
        """
           KXY
        """
        return self.__cardinfo.KXY

    @KXY.setter
    def KXY(self, value: float) -> None:
        self.__cardinfo.KXY = value

    @property
    def KXZ(self) -> float:
        """
           KXZ
        """
        return self.__cardinfo.KXZ

    @KXZ.setter
    def KXZ(self, value: float) -> None:
        self.__cardinfo.KXZ = value

    @property
    def KYY(self) -> float:
        """
           KYY
        """
        return self.__cardinfo.KYY

    @KYY.setter
    def KYY(self, value: float) -> None:
        self.__cardinfo.KYY = value

    @property
    def KYZ(self) -> float:
        """
           KYZ
        """
        return self.__cardinfo.KYZ

    @KYZ.setter
    def KYZ(self, value: float) -> None:
        self.__cardinfo.KYZ = value

    @property
    def KZZ(self) -> float:
        """
           KZZ
        """
        return self.__cardinfo.KZZ

    @KZZ.setter
    def KZZ(self, value: float) -> None:
        self.__cardinfo.KZZ = value

    @property
    def CP(self) -> float:
        """
           Heat capacity per unit mass. (Real > 0.0 or blank)
        """
        return self.__cardinfo.CP

    @CP.setter
    def CP(self, value: float) -> None:
        self.__cardinfo.CP = value

    @property
    def RHO(self) -> float:
        """
           Density. (Real>0.0; Default=1.0)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def HGEN(self) -> float:
        """
           Heat generation capability used with QVOL entries. (Real > 0.0; Default = 1.0)
        """
        return self.__cardinfo.HGEN

    @HGEN.setter
    def HGEN(self, value: float) -> None:
        self.__cardinfo.HGEN = value


class MAT8(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat8)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. Referenced on a PSHELL or PCOMP entry only. (0 < Integer< 100,000,000)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def E1(self) -> float:
        """
           Modulus of elasticity in longitudinal direction, also defined as the fiber direction or 1-direction. (Real ≠ 0.0)
        """
        return self.__cardinfo.E1

    @E1.setter
    def E1(self, value: float) -> None:
        self.__cardinfo.E1 = value

    @property
    def E2(self) -> float:
        """
           Modulus of elasticity in lateral direction, also defined as the matrix direction or 2-direction. (Real ≠ 0.0)
        """
        return self.__cardinfo.E2

    @E2.setter
    def E2(self, value: float) -> None:
        self.__cardinfo.E2 = value

    @property
    def NU12(self) -> float:
        """
           Poisson’s ratio (ε2 ⁄ ε1 for uniaxial loading in 1-direction). Note that υ21 = ε1 ⁄ ε2 for uniaxial loading in 2-direction is related to 12, E1, and E2
           by the relation υ12E2 = υ21E1. (Real)
        """
        return self.__cardinfo.NU12

    @NU12.setter
    def NU12(self, value: float) -> None:
        self.__cardinfo.NU12 = value

    @property
    def G12(self) -> float:
        """
           In-plane shear modulus. (Real > 0.0; Default = 0.0)
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: float) -> None:
        self.__cardinfo.G12 = value

    @property
    def G1Z(self) -> float:
        """
           Transverse shear modulus for shear in 1-Z plane. (Real > 0.0; Default implies infinite shear modulus.)
        """
        return self.__cardinfo.G1Z

    @G1Z.setter
    def G1Z(self, value: float) -> None:
        self.__cardinfo.G1Z = value

    @property
    def G2Z(self) -> float:
        """
           Transverse shear modulus for shear in 2-Z plane. (Real > 0.0; Default implies infinite shear modulus.)
        """
        return self.__cardinfo.G2Z

    @G2Z.setter
    def G2Z(self, value: float) -> None:
        self.__cardinfo.G2Z = value

    @property
    def RHO(self) -> float:
        """
           Mass density. (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def A1(self) -> float:
        """
           Thermal expansion coefficient in i-direction. (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation of thermal loads, or a temperature-dependent thermal expansion coefficient.See Remarks 4. and 5. (Real or blank)
           * Remark 4:
           Xt, Yt, and S are required for composite element failure calculations when requested in the FT field of the PCOMP entry.Xc and Yc are also used but
           not required.
           * Remark 5:
           TREF and GE are ignored if this entry is referenced by a PCOMP entry.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def Xt(self) -> float:
        """
           Allowable stresses or strains in tension and compression, respectively, in the longitudinal direction.Required if failure index is desired. See
           the FT field on the PCOMP entry. (Real > 0.0; Default value for Xc is Xt.)
        """
        return self.__cardinfo.Xt

    @Xt.setter
    def Xt(self, value: float) -> None:
        self.__cardinfo.Xt = value

    @property
    def Xc(self) -> float:
        """
           Xc
        """
        return self.__cardinfo.Xc

    @Xc.setter
    def Xc(self, value: float) -> None:
        self.__cardinfo.Xc = value

    @property
    def Yt(self) -> float:
        """
           Allowable stresses or strains in tension and compression, respectively, in the lateral direction.Required if failure index is desired. (Real > 0.0;
           Default value for Yc is Yt.)
        """
        return self.__cardinfo.Yt

    @Yt.setter
    def Yt(self, value: float) -> None:
        self.__cardinfo.Yt = value

    @property
    def Yc(self) -> float:
        """
           Yc
        """
        return self.__cardinfo.Yc

    @Yc.setter
    def Yc(self, value: float) -> None:
        self.__cardinfo.Yc = value

    @property
    def S(self) -> float:
        """
           Allowable stress or strain for in-plane shear. See the FT field on the PCOMP entry. (Real > 0.0)
        """
        return self.__cardinfo.S

    @S.setter
    def S(self, value: float) -> None:
        self.__cardinfo.S = value

    @property
    def GE(self) -> float:
        """
           Structural damping coefficient. See Remarks 4. and 6. (Real)
           * Remark 4:
           Xt, Yt, and S are required for composite element failure calculations when requested in the FT field of the PCOMP entry.Xc and Yc are also used but
           not required.
           * Remark 6:
           TREF is used in two different ways:
           • In nonlinear static analysis(SOL 106), TREF is used only for the calculation of a temperature-dependent thermal expansion
           coefficient.The reference temperature for the calculation of thermal loads is obtained from the TEMPERATURE(INITIAL) set selection.
           See Figure 8-94 in Remark 10. in the MAT1 description.
           • In all SOLs except 106, TREF is used only as the reference temperature for the calculation of thermal loads.TEMPERATURE(INITIAL) may
           be used for this purpose, but TREF must then be blank.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def F12(self) -> float:
        """
           Interaction term in the tensor polynomial theory of Tsai-Wu. Required if failure index by Tsai-Wu theory is desired and if value of F12 is
           different from 0.0. See the FT field on the PCOMP entry. (Real)
        """
        return self.__cardinfo.F12

    @F12.setter
    def F12(self, value: float) -> None:
        self.__cardinfo.F12 = value

    @property
    def STRN(self) -> float:
        """
           For the maximum strain theory only (see STRN in PCOMP entry). Indicates whether Xt, Xc, Yt, Yc, and S are stress or strain allowables.
           [Real = 1.0 for strain allowables; blank(Default) for stress allowables.]
        """
        return self.__cardinfo.STRN

    @STRN.setter
    def STRN(self, value: float) -> None:
        self.__cardinfo.STRN = value


class MAT9NAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat9Nas)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def G11(self) -> float:
        """
           Elements of the 6 x 6 symmetric material property matrix in the material coordinate system. (Real)
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: float) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> float:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: float) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> float:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: float) -> None:
        self.__cardinfo.G13 = value

    @property
    def G14(self) -> float:
        """
           G14
        """
        return self.__cardinfo.G14

    @G14.setter
    def G14(self, value: float) -> None:
        self.__cardinfo.G14 = value

    @property
    def G15(self) -> float:
        """
           G15
        """
        return self.__cardinfo.G15

    @G15.setter
    def G15(self, value: float) -> None:
        self.__cardinfo.G15 = value

    @property
    def G16(self) -> float:
        """
           G16
        """
        return self.__cardinfo.G16

    @G16.setter
    def G16(self, value: float) -> None:
        self.__cardinfo.G16 = value

    @property
    def G22(self) -> float:
        """
           G22
        """
        return self.__cardinfo.G22

    @G22.setter
    def G22(self, value: float) -> None:
        self.__cardinfo.G22 = value

    @property
    def G23(self) -> float:
        """
           G23
        """
        return self.__cardinfo.G23

    @G23.setter
    def G23(self, value: float) -> None:
        self.__cardinfo.G23 = value

    @property
    def G24(self) -> float:
        """
           G24
        """
        return self.__cardinfo.G24

    @G24.setter
    def G24(self, value: float) -> None:
        self.__cardinfo.G24 = value

    @property
    def G25(self) -> float:
        """
           G25
        """
        return self.__cardinfo.G25

    @G25.setter
    def G25(self, value: float) -> None:
        self.__cardinfo.G25 = value

    @property
    def G26(self) -> float:
        """
           G26
        """
        return self.__cardinfo.G26

    @G26.setter
    def G26(self, value: float) -> None:
        self.__cardinfo.G26 = value

    @property
    def G33(self) -> float:
        """
           G33
        """
        return self.__cardinfo.G33

    @G33.setter
    def G33(self, value: float) -> None:
        self.__cardinfo.G33 = value

    @property
    def G34(self) -> float:
        """
           G34
        """
        return self.__cardinfo.G34

    @G34.setter
    def G34(self, value: float) -> None:
        self.__cardinfo.G34 = value

    @property
    def G35(self) -> float:
        """
           G35
        """
        return self.__cardinfo.G35

    @G35.setter
    def G35(self, value: float) -> None:
        self.__cardinfo.G35 = value

    @property
    def G36(self) -> float:
        """
           G36
        """
        return self.__cardinfo.G36

    @G36.setter
    def G36(self, value: float) -> None:
        self.__cardinfo.G36 = value

    @property
    def G44(self) -> float:
        """
           G44
        """
        return self.__cardinfo.G44

    @G44.setter
    def G44(self, value: float) -> None:
        self.__cardinfo.G44 = value

    @property
    def G45(self) -> float:
        """
           G45
        """
        return self.__cardinfo.G45

    @G45.setter
    def G45(self, value: float) -> None:
        self.__cardinfo.G45 = value

    @property
    def G46(self) -> float:
        """
           G46
        """
        return self.__cardinfo.G46

    @G46.setter
    def G46(self, value: float) -> None:
        self.__cardinfo.G46 = value

    @property
    def G55(self) -> float:
        """
           G55
        """
        return self.__cardinfo.G55

    @G55.setter
    def G55(self, value: float) -> None:
        self.__cardinfo.G55 = value

    @property
    def G56(self) -> float:
        """
           G56
        """
        return self.__cardinfo.G56

    @G56.setter
    def G56(self, value: float) -> None:
        self.__cardinfo.G56 = value

    @property
    def G66(self) -> float:
        """
           G66
        """
        return self.__cardinfo.G66

    @G66.setter
    def G66(self, value: float) -> None:
        self.__cardinfo.G66 = value

    @property
    def RHO(self) -> float:
        """
           Mass density. (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def A1(self) -> float:
        """
           Thermal expansion coefficient. (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value

    @property
    def A4(self) -> float:
        """
           A4
        """
        return self.__cardinfo.A4

    @A4.setter
    def A4(self, value: float) -> None:
        self.__cardinfo.A4 = value

    @property
    def A5(self) -> float:
        """
           A5
        """
        return self.__cardinfo.A5

    @A5.setter
    def A5(self, value: float) -> None:
        self.__cardinfo.A5 = value

    @property
    def A6(self) -> float:
        """
           A6
        """
        return self.__cardinfo.A6

    @A6.setter
    def A6(self, value: float) -> None:
        self.__cardinfo.A6 = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation thermal loads, or a temperature-dependent thermal expansion coefficient.See Remark 7. (Real or blank)
           * Remark 7:
           TREF is used in two different ways:
           • In nonlinear static analysis(e.g., SOL 106), TREF is used only for the calculation of a temperature-dependent thermal expansion
           coefficient.The reference temperature for the calculation of thermal loads is obtained from the TEMPERATURE(INITIAL) set selection.
           See Figure 5-91 in Remark 10. in the MAT1 description.
           • In all solutions except nonlinear static analysis, TREF is used only as the reference temperature for the calculation of thermal loads.
           TEMPERATURE(INITIAL) may be used for this purpose, but TREF must then be blank.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. See Remarks 6. and 8. (Real)
           * Remark 6:
           The damping coefficient GE is given by GE = 2.0 * C / Co
           * Remark 8:
           If PARAM,W4 is not specified, GE is ignored in transient analysis. See “Parameters” on page 631.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value


class MAT9OPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardMat9Opt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def MID(self) -> int:
        """
           Unique material identification. No default (Integer > 0 or <String>)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def G11(self) -> float:
        """
           The material property matrix. No default (Real)
        """
        return self.__cardinfo.G11

    @G11.setter
    def G11(self, value: float) -> None:
        self.__cardinfo.G11 = value

    @property
    def G12(self) -> float:
        """
           G12
        """
        return self.__cardinfo.G12

    @G12.setter
    def G12(self, value: float) -> None:
        self.__cardinfo.G12 = value

    @property
    def G13(self) -> float:
        """
           G13
        """
        return self.__cardinfo.G13

    @G13.setter
    def G13(self, value: float) -> None:
        self.__cardinfo.G13 = value

    @property
    def G14(self) -> float:
        """
           G14
        """
        return self.__cardinfo.G14

    @G14.setter
    def G14(self, value: float) -> None:
        self.__cardinfo.G14 = value

    @property
    def G15(self) -> float:
        """
           G15
        """
        return self.__cardinfo.G15

    @G15.setter
    def G15(self, value: float) -> None:
        self.__cardinfo.G15 = value

    @property
    def G16(self) -> float:
        """
           G16
        """
        return self.__cardinfo.G16

    @G16.setter
    def G16(self, value: float) -> None:
        self.__cardinfo.G16 = value

    @property
    def G22(self) -> float:
        """
           G22
        """
        return self.__cardinfo.G22

    @G22.setter
    def G22(self, value: float) -> None:
        self.__cardinfo.G22 = value

    @property
    def G23(self) -> float:
        """
           G23
        """
        return self.__cardinfo.G23

    @G23.setter
    def G23(self, value: float) -> None:
        self.__cardinfo.G23 = value

    @property
    def G24(self) -> float:
        """
           G24
        """
        return self.__cardinfo.G24

    @G24.setter
    def G24(self, value: float) -> None:
        self.__cardinfo.G24 = value

    @property
    def G25(self) -> float:
        """
           G25
        """
        return self.__cardinfo.G25

    @G25.setter
    def G25(self, value: float) -> None:
        self.__cardinfo.G25 = value

    @property
    def G26(self) -> float:
        """
           G26
        """
        return self.__cardinfo.G26

    @G26.setter
    def G26(self, value: float) -> None:
        self.__cardinfo.G26 = value

    @property
    def G33(self) -> float:
        """
           G33
        """
        return self.__cardinfo.G33

    @G33.setter
    def G33(self, value: float) -> None:
        self.__cardinfo.G33 = value

    @property
    def G34(self) -> float:
        """
           G34
        """
        return self.__cardinfo.G34

    @G34.setter
    def G34(self, value: float) -> None:
        self.__cardinfo.G34 = value

    @property
    def G35(self) -> float:
        """
           G35
        """
        return self.__cardinfo.G35

    @G35.setter
    def G35(self, value: float) -> None:
        self.__cardinfo.G35 = value

    @property
    def G36(self) -> float:
        """
           G36
        """
        return self.__cardinfo.G36

    @G36.setter
    def G36(self, value: float) -> None:
        self.__cardinfo.G36 = value

    @property
    def G44(self) -> float:
        """
           G44
        """
        return self.__cardinfo.G44

    @G44.setter
    def G44(self, value: float) -> None:
        self.__cardinfo.G44 = value

    @property
    def G45(self) -> float:
        """
           G45
        """
        return self.__cardinfo.G45

    @G45.setter
    def G45(self, value: float) -> None:
        self.__cardinfo.G45 = value

    @property
    def G46(self) -> float:
        """
           G46
        """
        return self.__cardinfo.G46

    @G46.setter
    def G46(self, value: float) -> None:
        self.__cardinfo.G46 = value

    @property
    def G55(self) -> float:
        """
           G55
        """
        return self.__cardinfo.G55

    @G55.setter
    def G55(self, value: float) -> None:
        self.__cardinfo.G55 = value

    @property
    def G56(self) -> float:
        """
           G56
        """
        return self.__cardinfo.G56

    @G56.setter
    def G56(self, value: float) -> None:
        self.__cardinfo.G56 = value

    @property
    def G66(self) -> float:
        """
           G66
        """
        return self.__cardinfo.G66

    @G66.setter
    def G66(self, value: float) -> None:
        self.__cardinfo.G66 = value

    @property
    def RHO(self) -> float:
        """
           Mass density. Used to automatically compute mass for all structural elements. No default (Real)
        """
        return self.__cardinfo.RHO

    @RHO.setter
    def RHO(self, value: float) -> None:
        self.__cardinfo.RHO = value

    @property
    def A1(self) -> float:
        """
           Thermal expansion coefficient vector. No default (Real)
        """
        return self.__cardinfo.A1

    @A1.setter
    def A1(self, value: float) -> None:
        self.__cardinfo.A1 = value

    @property
    def A2(self) -> float:
        """
           A2
        """
        return self.__cardinfo.A2

    @A2.setter
    def A2(self, value: float) -> None:
        self.__cardinfo.A2 = value

    @property
    def A3(self) -> float:
        """
           A3
        """
        return self.__cardinfo.A3

    @A3.setter
    def A3(self, value: float) -> None:
        self.__cardinfo.A3 = value

    @property
    def A4(self) -> float:
        """
           A4
        """
        return self.__cardinfo.A4

    @A4.setter
    def A4(self, value: float) -> None:
        self.__cardinfo.A4 = value

    @property
    def A5(self) -> float:
        """
           A5
        """
        return self.__cardinfo.A5

    @A5.setter
    def A5(self, value: float) -> None:
        self.__cardinfo.A5 = value

    @property
    def A6(self) -> float:
        """
           A6
        """
        return self.__cardinfo.A6

    @A6.setter
    def A6(self, value: float) -> None:
        self.__cardinfo.A6 = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature for the calculation of thermal loads. Default = blank(Real or blank)
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Structural element damping coefficient. No default (Real)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def MODULI(self) -> str:
        """
           Continuation line flag for moduli temporal property.
        """
        return self.__cardinfo.MODULI

    @MODULI.setter
    def MODULI(self, value: str) -> None:
        self.__cardinfo.MODULI = value

    @property
    def MTIME(self) -> str:
        """
           Material temporal property. This field controls the interpretation of the input material property for viscoelasticity.
           INSTANT
           This material property is considered as the Instantaneous material input for viscoelasticity on the MATVE entry.
           LONG(Default)
           This material property is considered as the Long-term relaxed material input for viscoelasticity on the MATVE entry.
        """
        return self.__cardinfo.MTIME

    @MTIME.setter
    def MTIME(self, value: str) -> None:
        self.__cardinfo.MTIME = value


class MPC(N2PCard):
    """Nastran/Optistruct Multi Point Constriction Card"""

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """Card code (MPC)"""
        return self.__cardinfo.Charname

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.Charname = value

    @property
    def SID(self) -> int:
        """Set identification number. (Integer > 0)"""
        return self.__cardinfo.Sid

    @SID.setter
    def SID(self, value: int) -> None:
        self.__cardinfo.Sid = value

    @property
    def G(self) -> list[int]:
        """Identification number of grid or scalar point. (Integer > 0)"""
        return IndexTrackingList((ite for ite in self.__cardinfo.Gi), self.__cardinfo.Gi)

    @G.setter
    def G(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.Gi[i] = val

    @property
    def C(self) -> list[str]:
        """Component number. (Any one of the Integers 1 through 6 for grid points; blank or zero for scalar points.)"""
        return IndexTrackingList((ite for ite in self.__cardinfo.Ci), self.__cardinfo.Ci)

    @C.setter
    def C(self, value: list[str]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.Ci[i] = val

    @property
    def A(self) -> list[float]:
        """Coefficient. (Real; Default = 0.0 except A1 must be nonzero.)"""
        return IndexTrackingList((ite for ite in self.__cardinfo.Ai), self.__cardinfo.Ai)

    @A.setter
    def A(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.Ai[i] = val


    def add_GiCiAi(self, gi: int, ci: int, ai: float) -> None:
        """Add a new set of values Gi, Ci, Ai to the MPC Card.
        
        Args:
            gi (int)
                Grid ID to be constrained
            ci (int)
                Degrees of freedom to be constrained. 1 to 6.
            ai (float)
                Coefficient to be applied. Can be any real number.

        Example:
            >>> mpc = model.ModelInputData.get_cards_by_field("MPC")[0]
            >>> mpc.add_GiCiAi(1010, 123, 0.7)
            >>> mpc.add_GiCiAi(1011, 1236, 3.3)
            >>> mpc.add_GiCiAi(1012, 456, -2.1)

        """
        error = self.__cardinfo.AddGiCiAi2Metadata(gi, ci, float(ai))
        if int(error) != 0:
            N2PLog.Error.E317(self.CardType, int(error), error.ToString())
        
    def add_multiple_GiCiAi(self, values: list[tuple[int, int, float]]) -> None:
        """Add sevaral new sets of values Gi, Ci, Ai to the MPC Card using a list of tuples.
        
        Args:
            values (list[tuple[int, int, float]])
                List of tuples with three values: Gi, Ci, Ai.
                Gi: Grid ID to be constrained
                Ci: Degrees of freedom to be constrained. 1 to 6.
                Ai: Coefficient to be applied. Can be any real number.

        Example:
            >>> mpc = model.ModelInputData.get_cards_by_field("MPC")[0]
            >>> mpc.add_multiple_GiCiAi([(1010, 123, 0.7), (1011, 1236, 3.3), (1012, 456, -2.1)])
            
        """
        aux = [System.ValueTuple.Create[int, int, float](*_) for _ in values]
        error = self.__cardinfo.AddMultipleGiCiAi2Metadata(*aux)
        if int(error) != 0:
            N2PLog.Error.E317(self.CardType, int(error), error.ToString())
        
    def delete_GiCiAi(self, grid: int) -> None:
        """Deletes a set of values Gi, Ci, Ai of the MPC Card.
        
        Args:
            gi (int)
                Grid ID to be deleted with it Ci and Ai

        Note:
            As the Ci and Ai are linked to a Gi, only the Gi is required to delete the three values.

        Example:
            >>> mpc = model.ModelInputData.get_cards_by_field("MPC")[0]
            >>> mpc.delete_GiCiAi(1010)
            >>> mpc.delete_GiCiAi(1011)
            >>> mpc.delete_GiCiAi(1012)
            
        """
        error = self.__cardinfo.DeleteGiCiAiFromMetadata(grid, 0, 0.0)
        if int(error) != 0:
            N2PLog.Error.E317(self.CardType, int(error), error.ToString())
        
    def delete_multiple_GiCiAi(self, grids: list[int]) -> None:
        """Deletes several sets of values Gi, Ci, Ai of the MPC Card.
        
        Args:
            grids (list[int])
                Grid IDs whose associated Ci and Ai values will be deleted.

        Note:
            As the Ci and Ai are linked to a Gi, only the Gi is required to delete the three values.

        Example:
            >>> mpc = model.ModelInputData.get_cards_by_field("MPC")[0]
            >>> mpc.delete_multiple_GiCiAi([1010, 1011, 1012])
            
        """
        aux = [(i, 0, 0.0) for i in grids]
        error = self.__cardinfo.DeleteMultipleGiCiAiFromMetadata(*aux)
        if int(error) != 0:
            N2PLog.Error.E317(self.CardType, int(error), error.ToString())
        
    def get_item_value(self, row: int, col: int) -> any:
        """Gets the value placed in the row and column specified from the MPC Card.
        
        Args:
            row (int)
                Number of row (starts in 1)
            col (int)
                Number of column (starts in 1)

        Example:
            >>> mpc = model.ModelInputData.get_cards_by_field("MPC")[0]
            >>> c1 = mpc.get_item_value(1, 4)
            >>> g4 = mpc.get_item_value(2, 6)
            
        """
        value = self.__cardinfo.GetMetadataItemValue(row, col)  # Returns a ValueTuple
        error = value.Item1
        if int(error) != 0:
            N2PLog.Error.E317(self.CardType, int(error), error.ToString())
    
        return value.Item2
        
    def get_item_values(self, positions: list[tuple[int, int]]) -> list[any]:
        """Gets the values placed in the row and column described as a tuple.
        
        Args:
            positions (list[tuple[int, int]])
                List with the tuple of positions of the values to get: (row, column)

        Example:
            >>> mpc = model.ModelInputData.get_cards_by_field("MPC")[0]
            >>> c1, g4 = mpc.get_item_values([(1, 4), (2, 6)])
            
        """
        aux = [System.ValueTuple.Create(*_) for _ in positions]
        value = self.__cardinfo.GetMetadataItemsValues(False, *aux)  # Returns a ValueTuple
        error = value.Item1
        if int(error) != 0:
            N2PLog.Error.E317(self.CardType, int(error), error.ToString())

        return list(value.Item2)
    
    def modify_items_values(self, updates: list[tuple[int, int, any]]) -> None:
        """Modify a value placed in the row and column specified of the MPC Card.
        
        Args:
            updates (list[tuple[int, int, any]])
                List with the tuple of positions and values to modify: (row, column, new_value)

        Example:
            >>> mpc = model.ModelInputData.get_cards_by_field("MPC")[0]
            >>> mpc.modify_items_values([(1, 3, 1010), (1, 4, 23), (1, 5, -2.1)])
            >>> # The value in (1,3) is replaced by 1010. It is a grid id
            >>> # The value in (1,4) is replaced by 23. They are the DoF to constrain
            >>> # The value in (1,5) is replaced by -2.1. It is the coefficient
        """

        aux = [System.ValueTuple.Create[int, int, System.Object](*_) for _ in updates]
        error = self.__cardinfo.ModifyMetadataItemsValues(False, *aux)
        if int(error) != 0:
            N2PLog.Error.E317(self.CardType, int(error), error.ToString())
        
    def modify_item_value(self, row: int, col: int, value: any) -> None:
        """Modify a value placed in the row and column specified of the MPC Card.
        
        Args:
            row (int)
                Number of row (starts in 1)
            col (int)
                Number of column (starts in 1)
            value (any)
                New value. The type and range must be valid

        Example:
            >>> mpc = model.ModelInputData.get_cards_by_field("MPC")[0]
            >>> mpc.modify_item_value(1, 3, 1010)  # The value in (1,3) is replaced by 1010. It is a grid id
            >>> mpc.modify_item_value(1, 4, 23)  # The value in (1,4) is replaced by 23. They are the DoF to constrain
            >>> mpc.modify_item_value(1, 5, -2.1)  # The value in (1,5) is replaced by -2.1. It is the coefficient
            
        """
        error = self.__cardinfo.ModifyMetadataItemValue(row, col, value)
        if int(error) != 0:
            N2PLog.Error.E317(self.CardType, int(error), error.ToString())
        
    def print_card_attributes(self) -> None:
        """Prints the card attributes: Ai, Ci, Gi, CharName, etc"""
        self.__cardinfo.PrintCardAttributes()
        
    def print_documentation_table(self) -> None:
        """Prints the table with the name of the cell of the Card
        """
        self.__cardinfo.PrintDocumentationFixedFormatTable()

    def print_fixed_format_table(self) -> None:
        """Prints the table with the value of the cell of the Card
        """
        self.__cardinfo.PrintFixedFormatTable()


class PBAR(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PLPLANE)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Identification number of a MATHP entry. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def A(self) -> float:
        """
           Area of bar cross section. (Real; Default = 0.0)
        """
        return self.__cardinfo.A

    @A.setter
    def A(self, value: float) -> None:
        self.__cardinfo.A = value

    @property
    def I1(self) -> float:
        """
           I1, I2:
           Area moments of inertia.See Figure 8-177. (Real; I1 > 0.0, I2 > 0.0, I1* I2 > ; Default = 0.0)
        """
        return self.__cardinfo.I1

    @I1.setter
    def I1(self, value: float) -> None:
        self.__cardinfo.I1 = value

    @property
    def I2(self) -> float:
        """
           I2
        """
        return self.__cardinfo.I2

    @I2.setter
    def I2(self, value: float) -> None:
        self.__cardinfo.I2 = value

    @property
    def J(self) -> float:
        """
           Torsional constant. See Figure 8-177. (Real; Default = for SOL 600 and 0.0 for all other solution sequences)
        """
        return self.__cardinfo.J

    @J.setter
    def J(self, value: float) -> None:
        self.__cardinfo.J = value

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit length. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value

    @property
    def C1(self) -> float:
        """
           C1, C2, D1, D2, E1, E2, F1, F2:
           Stress recovery coefficients. (Real; Default = 0.0)
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: float) -> None:
        self.__cardinfo.C1 = value

    @property
    def C2(self) -> float:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: float) -> None:
        self.__cardinfo.C2 = value

    @property
    def D1(self) -> float:
        """
           D1
        """
        return self.__cardinfo.D1

    @D1.setter
    def D1(self, value: float) -> None:
        self.__cardinfo.D1 = value

    @property
    def D2(self) -> float:
        """
           D2
        """
        return self.__cardinfo.D2

    @D2.setter
    def D2(self, value: float) -> None:
        self.__cardinfo.D2 = value

    @property
    def E1(self) -> float:
        """
           E1
        """
        return self.__cardinfo.E1

    @E1.setter
    def E1(self, value: float) -> None:
        self.__cardinfo.E1 = value

    @property
    def E2(self) -> float:
        """
           E2
        """
        return self.__cardinfo.E2

    @E2.setter
    def E2(self, value: float) -> None:
        self.__cardinfo.E2 = value

    @property
    def F1(self) -> float:
        """
           F1
        """
        return self.__cardinfo.F1

    @F1.setter
    def F1(self, value: float) -> None:
        self.__cardinfo.F1 = value

    @property
    def F2(self) -> float:
        """
           F2
        """
        return self.__cardinfo.F2

    @F2.setter
    def F2(self, value: float) -> None:
        self.__cardinfo.F2 = value

    @property
    def K1(self) -> float:
        """
           Area factor for shear. See Remark 5. (Real or blank)
        """
        return self.__cardinfo.K1

    @K1.setter
    def K1(self, value: float) -> None:
        self.__cardinfo.K1 = value

    @property
    def K2(self) -> float:
        """
           K2
        """
        return self.__cardinfo.K2

    @K2.setter
    def K2(self, value: float) -> None:
        self.__cardinfo.K2 = value

    @property
    def I12(self) -> float:
        """
           Area moments of inertia.See Figure 8-177. (Real; I1 > 0.0, I2 > 0.0, I1* I2 > ; Default = 0.0)
        """
        return self.__cardinfo.I12

    @I12.setter
    def I12(self, value: float) -> None:
        self.__cardinfo.I12 = value


class PBARL(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PMASS)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Material identification number (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def GROUP(self) -> str:
        """
           Cross-section group.See Remarks 6. and 8. (Character;
           Default = “MSCBML0")
        """
        return self.__cardinfo.GROUP

    @GROUP.setter
    def GROUP(self, value: str) -> None:
        self.__cardinfo.GROUP = value

    @property
    def TYPE(self) -> str:
        """
           Cross-section type.See Remarks 6. and 8. and Figure 8-112. (Character:
           “ROD”, “TUBE”, “I”, “CHAN”, “T”, “BOX”, “BAR”, “CROSS”, “H”,
           “T1", “I1", “CHAN1", “Z”, “CHAN2", “T2", “BOX1", “HEXA”, “HAT”,
           “HAT1”, “DBOX” for GROUP=“MSCBML0")
        """
        return self.__cardinfo.TYPE

    @TYPE.setter
    def TYPE(self, value: str) -> None:
        self.__cardinfo.TYPE = value

    @property
    def DIM(self) -> list[float]:
        """
           DIM
           PBARL	PID		MID		GROUP	TYPE
           DIM1	DIM2    DIM3	DIM4    DIM5	DIM6    DIM7	DIM8
           DIM9	-etc.	NSM
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.DIM), self.__cardinfo.DIM)

    @DIM.setter
    def DIM(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.DIM[i] = val

    @property
    def NSM(self) -> float:
        """
           NSM
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value


class PBEAM(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PSOLID_NASTRAN)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0 or string)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Material identification number. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def A_A(self) -> float:
        """
           Area of the beam cross section at end A. (Real > 0.0)
        """
        return self.__cardinfo.A_A

    @A_A.setter
    def A_A(self, value: float) -> None:
        self.__cardinfo.A_A = value

    @property
    def I1_A(self) -> float:
        """
           Area moment of inertia at end A for bending in plane 1 about the neutral axis.See Remark 10. (Real > 0.0)
        """
        return self.__cardinfo.I1_A

    @I1_A.setter
    def I1_A(self, value: float) -> None:
        self.__cardinfo.I1_A = value

    @property
    def I2_A(self) -> float:
        """
           Area moment of inertia at end A for bending in plane 2 about the neutral axis.See Remark 10. (Real > 0.0)
        """
        return self.__cardinfo.I2_A

    @I2_A.setter
    def I2_A(self, value: float) -> None:
        self.__cardinfo.I2_A = value

    @property
    def I12_A(self) -> float:
        """
           Area product of inertia at end A. See Remark 10. (Real, but I1*I2 - I12^2 > 0.00)
        """
        return self.__cardinfo.I12_A

    @I12_A.setter
    def I12_A(self, value: float) -> None:
        self.__cardinfo.I12_A = value

    @property
    def J_A(self) -> float:
        """
           Torsional stiffness parameter at end A. See Remark 10. (Real >= 0.0 but > 0.0 if warping is present)
        """
        return self.__cardinfo.J_A

    @J_A.setter
    def J_A(self, value: float) -> None:
        self.__cardinfo.J_A = value

    @property
    def NSM_A(self) -> float:
        """
           Nonstructural mass per unit length at end A. (Real)
        """
        return self.__cardinfo.NSM_A

    @NSM_A.setter
    def NSM_A(self, value: float) -> None:
        self.__cardinfo.NSM_A = value

    @property
    def C1_A(self) -> float:
        """
           C1_A, C2_A, D1_A, D2_A, E1_A, E2_A, F1_A, F2_A:
           The y and z locations (i = 1 corresponds to y and
           i = 2 corresponds to z) in element coordinates
           relative to the shear center(see the diagram
           following the remarks) at end A for stress data
           recovery. (Real)
        """
        return self.__cardinfo.C1_A

    @C1_A.setter
    def C1_A(self, value: float) -> None:
        self.__cardinfo.C1_A = value

    @property
    def C2_A(self) -> float:
        """
           C2_A
        """
        return self.__cardinfo.C2_A

    @C2_A.setter
    def C2_A(self, value: float) -> None:
        self.__cardinfo.C2_A = value

    @property
    def D1_A(self) -> float:
        """
           D1_A
        """
        return self.__cardinfo.D1_A

    @D1_A.setter
    def D1_A(self, value: float) -> None:
        self.__cardinfo.D1_A = value

    @property
    def D2_A(self) -> float:
        """
           D2_A
        """
        return self.__cardinfo.D2_A

    @D2_A.setter
    def D2_A(self, value: float) -> None:
        self.__cardinfo.D2_A = value

    @property
    def E1_A(self) -> float:
        """
           E1_A
        """
        return self.__cardinfo.E1_A

    @E1_A.setter
    def E1_A(self, value: float) -> None:
        self.__cardinfo.E1_A = value

    @property
    def E2_A(self) -> float:
        """
           E2_A
        """
        return self.__cardinfo.E2_A

    @E2_A.setter
    def E2_A(self, value: float) -> None:
        self.__cardinfo.E2_A = value

    @property
    def F1_A(self) -> float:
        """
           F1_A
        """
        return self.__cardinfo.F1_A

    @F1_A.setter
    def F1_A(self, value: float) -> None:
        self.__cardinfo.F1_A = value

    @property
    def F2_A(self) -> float:
        """
           F2_A
        """
        return self.__cardinfo.F2_A

    @F2_A.setter
    def F2_A(self, value: float) -> None:
        self.__cardinfo.F2_A = value

    @property
    def SO(self) -> str:
        """
           Stress output request option.See Remark 9.
           (Character)
           Required*
           “YES” Stresses recovered at points Ci, Di, Ei, and
           Fi on the next continuation.
           “YESA” Stresses recovered at points with the same
           y and z location as end A.
           “NO” No stresses or forces are recovered.
        """
        return self.__cardinfo.SO

    @SO.setter
    def SO(self, value: str) -> None:
        self.__cardinfo.SO = value

    @property
    def X_XB(self) -> float:
        """
           “NO” No stresses or forces are recovered.
           Distance from end A in the element coordinate
           system divided by the length of the element See
           Figure 8-184 in Remark 10. (Real, 0.0 < x/xb ≤ 1.0)
        """
        return self.__cardinfo.X_XB

    @X_XB.setter
    def X_XB(self, value: float) -> None:
        self.__cardinfo.X_XB = value

    @property
    def A(self) -> float:
        """
           A, I1, I2, I12, II2 Area, moments of inertia, torsional stiffness
           parameter, and nonstructural mass for the cross
           section located at x. (Real; J > 0.0 if warping is
           present.)
        """
        return self.__cardinfo.A

    @A.setter
    def A(self, value: float) -> None:
        self.__cardinfo.A = value

    @property
    def I1(self) -> float:
        """
           I1
        """
        return self.__cardinfo.I1

    @I1.setter
    def I1(self, value: float) -> None:
        self.__cardinfo.I1 = value

    @property
    def I2(self) -> float:
        """
           I2
        """
        return self.__cardinfo.I2

    @I2.setter
    def I2(self, value: float) -> None:
        self.__cardinfo.I2 = value

    @property
    def I12(self) -> float:
        """
           I12
        """
        return self.__cardinfo.I12

    @I12.setter
    def I12(self, value: float) -> None:
        self.__cardinfo.I12 = value

    @property
    def J(self) -> float:
        """
           J
        """
        return self.__cardinfo.J

    @J.setter
    def J(self, value: float) -> None:
        self.__cardinfo.J = value

    @property
    def NSM(self) -> float:
        """
           NSM
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value

    @property
    def C1(self) -> float:
        """
           C1, C2, D1, D2, E1, E2, F1, F2:
           The y and z locations (i = 1 corresponds to y and
           i = 2 corresponds to z) in element coordinates
           relative to the shear center(see the diagram
           following the remarks) at end A for stress data
           recovery. (Real)
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: float) -> None:
        self.__cardinfo.C1 = value

    @property
    def C2(self) -> float:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: float) -> None:
        self.__cardinfo.C2 = value

    @property
    def D1(self) -> float:
        """
           D1
        """
        return self.__cardinfo.D1

    @D1.setter
    def D1(self, value: float) -> None:
        self.__cardinfo.D1 = value

    @property
    def D2(self) -> float:
        """
           D2
        """
        return self.__cardinfo.D2

    @D2.setter
    def D2(self, value: float) -> None:
        self.__cardinfo.D2 = value

    @property
    def E1(self) -> float:
        """
           E1
        """
        return self.__cardinfo.E1

    @E1.setter
    def E1(self, value: float) -> None:
        self.__cardinfo.E1 = value

    @property
    def E2(self) -> float:
        """
           E2
        """
        return self.__cardinfo.E2

    @E2.setter
    def E2(self, value: float) -> None:
        self.__cardinfo.E2 = value

    @property
    def F1(self) -> float:
        """
           F1
        """
        return self.__cardinfo.F1

    @F1.setter
    def F1(self, value: float) -> None:
        self.__cardinfo.F1 = value

    @property
    def F2(self) -> float:
        """
           F2
        """
        return self.__cardinfo.F2

    @F2.setter
    def F2(self, value: float) -> None:
        self.__cardinfo.F2 = value

    @property
    def K1(self) -> float:
        """
           K1, K2:
           Shear stiffness factor K in K* A*G for plane 1 and
           plane 2. See Remark 12. (Real)
        """
        return self.__cardinfo.K1

    @K1.setter
    def K1(self, value: float) -> None:
        self.__cardinfo.K1 = value

    @property
    def K2(self) -> float:
        """
           K2
        """
        return self.__cardinfo.K2

    @K2.setter
    def K2(self, value: float) -> None:
        self.__cardinfo.K2 = value

    @property
    def S1(self) -> float:
        """
           S1, S2:
           Shear relief coefficient due to taper for plane 1 and
           plane 2. Ignored for beam p-elements. (Real)
        """
        return self.__cardinfo.S1

    @S1.setter
    def S1(self, value: float) -> None:
        self.__cardinfo.S1 = value

    @property
    def S2(self) -> float:
        """
           S2
        """
        return self.__cardinfo.S2

    @S2.setter
    def S2(self, value: float) -> None:
        self.__cardinfo.S2 = value

    @property
    def NSI_A(self) -> float:
        """
           NSI(A), NSI(B):
           Nonstructural mass moment of inertia per unit
           length about nonstructural mass center of gravity at
           end A and end B.See Figure 8-184. (Real)
        """
        return self.__cardinfo.NSI_A

    @NSI_A.setter
    def NSI_A(self, value: float) -> None:
        self.__cardinfo.NSI_A = value

    @property
    def NSI_B(self) -> float:
        """
           NSI_B
        """
        return self.__cardinfo.NSI_B

    @NSI_B.setter
    def NSI_B(self, value: float) -> None:
        self.__cardinfo.NSI_B = value

    @property
    def CW_A(self) -> float:
        """
           CW(A), CW(B):
           Warping coefficient for end A and end B.Ignored
           for beam p-elements.See Remark 11. (Real)
        """
        return self.__cardinfo.CW_A

    @CW_A.setter
    def CW_A(self, value: float) -> None:
        self.__cardinfo.CW_A = value

    @property
    def CW_B(self) -> float:
        """
           CW_B
        """
        return self.__cardinfo.CW_B

    @CW_B.setter
    def CW_B(self, value: float) -> None:
        self.__cardinfo.CW_B = value

    @property
    def M1_A(self) -> float:
        """
           M1(A), M2(A), M1(B), M2(B):
           (y, z) coordinates of center of gravity of
           nonstructural mass for end A and end B.See
           Figure 8-184. (Real)
        """
        return self.__cardinfo.M1_A

    @M1_A.setter
    def M1_A(self, value: float) -> None:
        self.__cardinfo.M1_A = value

    @property
    def M2_A(self) -> float:
        """
           M2_A
        """
        return self.__cardinfo.M2_A

    @M2_A.setter
    def M2_A(self, value: float) -> None:
        self.__cardinfo.M2_A = value

    @property
    def M1_B(self) -> float:
        """
           M1_B
        """
        return self.__cardinfo.M1_B

    @M1_B.setter
    def M1_B(self, value: float) -> None:
        self.__cardinfo.M1_B = value

    @property
    def M2_B(self) -> float:
        """
           M2_B
        """
        return self.__cardinfo.M2_B

    @M2_B.setter
    def M2_B(self, value: float) -> None:
        self.__cardinfo.M2_B = value

    @property
    def N1_A(self) -> float:
        """
           N1(A), N2(A), N1(B), N2(B):
           (y, z) coordinates of neutral axis for end A and end B (Real)
        """
        return self.__cardinfo.N1_A

    @N1_A.setter
    def N1_A(self, value: float) -> None:
        self.__cardinfo.N1_A = value

    @property
    def N2_A(self) -> float:
        """
           N2_A
        """
        return self.__cardinfo.N2_A

    @N2_A.setter
    def N2_A(self, value: float) -> None:
        self.__cardinfo.N2_A = value

    @property
    def N1_B(self) -> float:
        """
           N1_B
        """
        return self.__cardinfo.N1_B

    @N1_B.setter
    def N1_B(self, value: float) -> None:
        self.__cardinfo.N1_B = value

    @property
    def N2_B(self) -> float:
        """
           N2_B
        """
        return self.__cardinfo.N2_B

    @N2_B.setter
    def N2_B(self, value: float) -> None:
        self.__cardinfo.N2_B = value


class PBEAML(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PMASS)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Material identification number (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def GROUP(self) -> str:
        """
           Cross-section group. (Character; Default = “MSCBML0")
        """
        return self.__cardinfo.GROUP

    @GROUP.setter
    def GROUP(self, value: str) -> None:
        self.__cardinfo.GROUP = value

    @property
    def TYPE(self) -> str:
        """
           Cross-section shape.See Remark 4. (Character: “ROD”, “TUBE”, “L”,
           “I”, “CHAN”, “T”, “BOX”, “BAR”, “CROSS”, “H”, “T1", “I1",
           “CHAN1", “Z”, “CHAN2", “T2", “BOX1", “HEXA”, “HAT”, “HAT1”,
           “DBOX” for GROUP = “MSCBML0")
        """
        return self.__cardinfo.TYPE

    @TYPE.setter
    def TYPE(self, value: str) -> None:
        self.__cardinfo.TYPE = value

    @property
    def DIM_A(self) -> list[float]:
        """
           Cross-section dimensions at end A
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.DIM_A), self.__cardinfo.DIM_A)

    @DIM_A.setter
    def DIM_A(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.DIM_A[i] = val

    @property
    def DIM_B(self) -> list[float]:
        """
           Cross-section dimensions at end B
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.DIM_B), self.__cardinfo.DIM_B)

    @DIM_B.setter
    def DIM_B(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.DIM_B[i] = val

    @property
    def DIM(self) -> float:
        """
           <para>
           Cross-section dimensions at intermediate stations. (Real > 0.0 for GROUP = “MSCBML0")
           </para>
           <para>
           1-N sections, NOT including <see cref="DIM_A"/> nor <see cref="DIM_B"/>
           </para>
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.DIM), self.__cardinfo.DIM)

    @DIM.setter
    def DIM(self, value: float) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.DIM[i] = val

    @property
    def NSM(self) -> list[float]:
        """
           <para>
           Nonstructural mass per unit length. (Default = 0.0)
           </para>
           <para>
           1-N sections, NOT including <see cref="NSM_A"/> nor <see cref="NSM_B"/>
           </para>
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.NSM), self.__cardinfo.NSM)

    @NSM.setter
    def NSM(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.NSM[i] = val

    @property
    def NSM_A(self) -> float:
        """
           Nonstructural mass per unit length in section A. (Default = 0.0)
        """
        return self.__cardinfo.NSM_A

    @NSM_A.setter
    def NSM_A(self, value: float) -> None:
        self.__cardinfo.NSM_A = value

    @property
    def NSM_B(self) -> float:
        """
           Nonstructural mass per unit length in section B. (Default = 0.0)
        """
        return self.__cardinfo.NSM_B

    @NSM_B.setter
    def NSM_B(self, value: float) -> None:
        self.__cardinfo.NSM_B = value

    @property
    def SO(self) -> list[str]:
        """
           <para>
           Stress output request option for intermediate station j. (Character; Default = “YES”)
           </para>
           <para>
           YES: Stresses recovered at all points on next continuation and
           shown in Figure 8-116 as C, D, E, and F.
           </para>
           <para>
           NO: No stresses or forces are recovered.
           </para>
           <para>
           Section B NOT included, see <see cref="SO_B"/>
           </para>
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.SO), self.__cardinfo.SO)

    @SO.setter
    def SO(self, value: list[str]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.SO[i] = val

    @property
    def SO_B(self) -> str:
        """
           <para>
           Stress output request option for section B. (Character; Default = “YES”)
           </para>
           <para>
           YES: Stresses recovered at all points on next continuation and
           shown in Figure 8-116 as C, D, E, and F.
           </para>
           <para>
           NO: No stresses or forces are recovered.
           </para>
        """
        return self.__cardinfo.SO_B

    @SO_B.setter
    def SO_B(self, value: str) -> None:
        self.__cardinfo.SO_B = value

    @property
    def X_XB(self) -> list[float]:
        """
           Distance from end A to intermediate station j in the element
           coordinate system divided by the length of the element. (Real>0.0;
           Default = 1.0)
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.X_XB), self.__cardinfo.X_XB)

    @X_XB.setter
    def X_XB(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.X_XB[i] = val


class PBUSHNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PLPLANE)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           <para>PID: <see cref="CardPbushNas"/> does not have an associate property. Returns <see cref="uint.MaxValue"/></para>
           <para>Implemented to use the interface <see cref="ICardProperty"/></para>
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def K(self) -> str:
        """
           Flag indicating that the next 1 to 6 fields are stiffness values in the element
           coordinate system. (Character)
        """
        return self.__cardinfo.K

    @K.setter
    def K(self, value: str) -> None:
        self.__cardinfo.K = value

    @property
    def K1(self) -> float:
        """
           Ki: Nominal stiffness values in directions 1 through 6. See Remarks 2. and 3.
           (Real; Default = 0.0)
        """
        return self.__cardinfo.K1

    @K1.setter
    def K1(self, value: float) -> None:
        self.__cardinfo.K1 = value

    @property
    def K2(self) -> float:
        """
           K2
        """
        return self.__cardinfo.K2

    @K2.setter
    def K2(self, value: float) -> None:
        self.__cardinfo.K2 = value

    @property
    def K3(self) -> float:
        """
           K3
        """
        return self.__cardinfo.K3

    @K3.setter
    def K3(self, value: float) -> None:
        self.__cardinfo.K3 = value

    @property
    def K4(self) -> float:
        """
           K4
        """
        return self.__cardinfo.K4

    @K4.setter
    def K4(self, value: float) -> None:
        self.__cardinfo.K4 = value

    @property
    def K5(self) -> float:
        """
           K5
        """
        return self.__cardinfo.K5

    @K5.setter
    def K5(self, value: float) -> None:
        self.__cardinfo.K5 = value

    @property
    def K6(self) -> float:
        """
           K6
        """
        return self.__cardinfo.K6

    @K6.setter
    def K6(self, value: float) -> None:
        self.__cardinfo.K6 = value

    @property
    def B(self) -> str:
        """
           Flag indicating that the next 1 to 6 fields are force-per-velocity damping.
           (Character)
        """
        return self.__cardinfo.B

    @B.setter
    def B(self, value: str) -> None:
        self.__cardinfo.B = value

    @property
    def B1(self) -> float:
        """
           Bi: Nominal damping coefficients in direction 1 through 6 in units of force per unit velocity.See Remarks 2., 3., and 9. (Real; Default = 0.0)
        """
        return self.__cardinfo.B1

    @B1.setter
    def B1(self, value: float) -> None:
        self.__cardinfo.B1 = value

    @property
    def B2(self) -> float:
        """
           B2
        """
        return self.__cardinfo.B2

    @B2.setter
    def B2(self, value: float) -> None:
        self.__cardinfo.B2 = value

    @property
    def B3(self) -> float:
        """
           B3
        """
        return self.__cardinfo.B3

    @B3.setter
    def B3(self, value: float) -> None:
        self.__cardinfo.B3 = value

    @property
    def B4(self) -> float:
        """
           B4
        """
        return self.__cardinfo.B4

    @B4.setter
    def B4(self, value: float) -> None:
        self.__cardinfo.B4 = value

    @property
    def B5(self) -> float:
        """
           B5
        """
        return self.__cardinfo.B5

    @B5.setter
    def B5(self, value: float) -> None:
        self.__cardinfo.B5 = value

    @property
    def B6(self) -> float:
        """
           B6
        """
        return self.__cardinfo.B6

    @B6.setter
    def B6(self, value: float) -> None:
        self.__cardinfo.B6 = value

    @property
    def GE(self) -> str:
        """
           Flag indicating that the next fields, 1 through 6 are structural damping
           constants.See Remark 7. (Character)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: str) -> None:
        self.__cardinfo.GE = value

    @property
    def GE1(self) -> float:
        """
           Nominal stiffness values in directions 1 through 6. See Remarks 2. and 3.
           (Real; Default = 0.0)
        """
        return self.__cardinfo.GE1

    @GE1.setter
    def GE1(self, value: float) -> None:
        self.__cardinfo.GE1 = value

    @property
    def GE2(self) -> float:
        """
           GE2
        """
        return self.__cardinfo.GE2

    @GE2.setter
    def GE2(self, value: float) -> None:
        self.__cardinfo.GE2 = value

    @property
    def GE3(self) -> float:
        """
           GE3
        """
        return self.__cardinfo.GE3

    @GE3.setter
    def GE3(self, value: float) -> None:
        self.__cardinfo.GE3 = value

    @property
    def GE4(self) -> float:
        """
           GE4
        """
        return self.__cardinfo.GE4

    @GE4.setter
    def GE4(self, value: float) -> None:
        self.__cardinfo.GE4 = value

    @property
    def GE5(self) -> float:
        """
           GE5
        """
        return self.__cardinfo.GE5

    @GE5.setter
    def GE5(self, value: float) -> None:
        self.__cardinfo.GE5 = value

    @property
    def GE6(self) -> float:
        """
           GE6
        """
        return self.__cardinfo.GE6

    @GE6.setter
    def GE6(self, value: float) -> None:
        self.__cardinfo.GE6 = value

    @property
    def RCV(self) -> str:
        """
           Flag indicating that the next 1 to 4 fields are stress or strain coefficients.
           (Character)
        """
        return self.__cardinfo.RCV

    @RCV.setter
    def RCV(self, value: str) -> None:
        self.__cardinfo.RCV = value

    @property
    def SA(self) -> float:
        """
           Nominal stiffness values in directions 1 through 6. See Remarks 2. and 3.
           (Real; Default = 0.0)
        """
        return self.__cardinfo.SA

    @SA.setter
    def SA(self, value: float) -> None:
        self.__cardinfo.SA = value

    @property
    def ST(self) -> float:
        """
           ST
        """
        return self.__cardinfo.ST

    @ST.setter
    def ST(self, value: float) -> None:
        self.__cardinfo.ST = value

    @property
    def EA(self) -> float:
        """
           EA
        """
        return self.__cardinfo.EA

    @EA.setter
    def EA(self, value: float) -> None:
        self.__cardinfo.EA = value

    @property
    def ET(self) -> float:
        """
           ET
        """
        return self.__cardinfo.ET

    @ET.setter
    def ET(self, value: float) -> None:
        self.__cardinfo.ET = value

    @property
    def Mflag(self) -> str:
        """
           Flag indicating that the following entries are mass properties for the CBUSH element.If
           inertia properties(Iij )are desired CONM2 should be used.
        """
        return self.__cardinfo.Mflag

    @Mflag.setter
    def Mflag(self, value: str) -> None:
        self.__cardinfo.Mflag = value

    @property
    def M(self) -> float:
        """
           Lumped mass of the CBUSH. (Real≥0.0; Default=0.0)
        """
        return self.__cardinfo.M

    @M.setter
    def M(self, value: float) -> None:
        self.__cardinfo.M = value


class PBUSHOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PLPLANE)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           <para>PID: <see cref="CardPbushNas"/> does not have an associate property. Returns <see cref="uint.MaxValue"/></para>
           <para>Implemented to use the interface <see cref="ICardProperty"/></para>
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def K(self) -> str:
        """
           Flag indicating that the next 1 to 6 fields are stiffness values in the element
           coordinate system. (Character)
        """
        return self.__cardinfo.K

    @K.setter
    def K(self, value: str) -> None:
        self.__cardinfo.K = value

    @property
    def K1(self) -> float:
        """
           Ki: Nominal stiffness values in directions 1 through 6. See Remarks 2. and 3.
           (Real; Default = 0.0)
        """
        return self.__cardinfo.K1

    @K1.setter
    def K1(self, value: float) -> None:
        self.__cardinfo.K1 = value

    @property
    def K2(self) -> float:
        """
           K2
        """
        return self.__cardinfo.K2

    @K2.setter
    def K2(self, value: float) -> None:
        self.__cardinfo.K2 = value

    @property
    def K3(self) -> float:
        """
           K3
        """
        return self.__cardinfo.K3

    @K3.setter
    def K3(self, value: float) -> None:
        self.__cardinfo.K3 = value

    @property
    def K4(self) -> float:
        """
           K4
        """
        return self.__cardinfo.K4

    @K4.setter
    def K4(self, value: float) -> None:
        self.__cardinfo.K4 = value

    @property
    def K5(self) -> float:
        """
           K5
        """
        return self.__cardinfo.K5

    @K5.setter
    def K5(self, value: float) -> None:
        self.__cardinfo.K5 = value

    @property
    def K6(self) -> float:
        """
           K6
        """
        return self.__cardinfo.K6

    @K6.setter
    def K6(self, value: float) -> None:
        self.__cardinfo.K6 = value

    @property
    def KMAG(self) -> str:
        """
           Flag indicating that the next 1 to 6 fields are stiffness magnitude(K*) values. 4
           No default (Character)
        """
        return self.__cardinfo.KMAG

    @KMAG.setter
    def KMAG(self, value: str) -> None:
        self.__cardinfo.KMAG = value

    @property
    def KMAG1(self) -> float:
        """
           Nominal stiffness magnitude(K*) values in directions 1 through 6. 4 6 8 9
           Default = 0.0 (Real)
        """
        return self.__cardinfo.KMAG1

    @KMAG1.setter
    def KMAG1(self, value: float) -> None:
        self.__cardinfo.KMAG1 = value

    @property
    def KMAG3(self) -> float:
        """
           KMAG3
        """
        return self.__cardinfo.KMAG3

    @KMAG3.setter
    def KMAG3(self, value: float) -> None:
        self.__cardinfo.KMAG3 = value

    @property
    def KMAG4(self) -> float:
        """
           KMAG4
        """
        return self.__cardinfo.KMAG4

    @KMAG4.setter
    def KMAG4(self, value: float) -> None:
        self.__cardinfo.KMAG4 = value

    @property
    def KMAG5(self) -> float:
        """
           KMAG5
        """
        return self.__cardinfo.KMAG5

    @KMAG5.setter
    def KMAG5(self, value: float) -> None:
        self.__cardinfo.KMAG5 = value

    @property
    def KMAG6(self) -> float:
        """
           KMAG6
        """
        return self.__cardinfo.KMAG6

    @KMAG6.setter
    def KMAG6(self, value: float) -> None:
        self.__cardinfo.KMAG6 = value

    @property
    def B(self) -> str:
        """
           Flag indicating that the next 1 to 6 fields are force-per-velocity damping.
           (Character)
        """
        return self.__cardinfo.B

    @B.setter
    def B(self, value: str) -> None:
        self.__cardinfo.B = value

    @property
    def B1(self) -> float:
        """
           Bi: Nominal damping coefficients in direction 1 through 6 in units of force per unit velocity.See Remarks 2., 3., and 9. (Real; Default = 0.0)
        """
        return self.__cardinfo.B1

    @B1.setter
    def B1(self, value: float) -> None:
        self.__cardinfo.B1 = value

    @property
    def B2(self) -> float:
        """
           B2
        """
        return self.__cardinfo.B2

    @B2.setter
    def B2(self, value: float) -> None:
        self.__cardinfo.B2 = value

    @property
    def B3(self) -> float:
        """
           B3
        """
        return self.__cardinfo.B3

    @B3.setter
    def B3(self, value: float) -> None:
        self.__cardinfo.B3 = value

    @property
    def B4(self) -> float:
        """
           B4
        """
        return self.__cardinfo.B4

    @B4.setter
    def B4(self, value: float) -> None:
        self.__cardinfo.B4 = value

    @property
    def B5(self) -> float:
        """
           B5
        """
        return self.__cardinfo.B5

    @B5.setter
    def B5(self, value: float) -> None:
        self.__cardinfo.B5 = value

    @property
    def B6(self) -> float:
        """
           B6
        """
        return self.__cardinfo.B6

    @B6.setter
    def B6(self, value: float) -> None:
        self.__cardinfo.B6 = value

    @property
    def GE(self) -> str:
        """
           Flag indicating that the next fields, 1 through 6 are structural damping
           constants.See Remark 7. (Character)
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: str) -> None:
        self.__cardinfo.GE = value

    @property
    def GE1(self) -> float:
        """
           Nominal stiffness values in directions 1 through 6. See Remarks 2. and 3.
           (Real; Default = 0.0)
        """
        return self.__cardinfo.GE1

    @GE1.setter
    def GE1(self, value: float) -> None:
        self.__cardinfo.GE1 = value

    @property
    def GE2(self) -> float:
        """
           GE2
        """
        return self.__cardinfo.GE2

    @GE2.setter
    def GE2(self, value: float) -> None:
        self.__cardinfo.GE2 = value

    @property
    def GE3(self) -> float:
        """
           GE3
        """
        return self.__cardinfo.GE3

    @GE3.setter
    def GE3(self, value: float) -> None:
        self.__cardinfo.GE3 = value

    @property
    def GE4(self) -> float:
        """
           GE4
        """
        return self.__cardinfo.GE4

    @GE4.setter
    def GE4(self, value: float) -> None:
        self.__cardinfo.GE4 = value

    @property
    def GE5(self) -> float:
        """
           GE5
        """
        return self.__cardinfo.GE5

    @GE5.setter
    def GE5(self, value: float) -> None:
        self.__cardinfo.GE5 = value

    @property
    def GE6(self) -> float:
        """
           GE6
        """
        return self.__cardinfo.GE6

    @GE6.setter
    def GE6(self, value: float) -> None:
        self.__cardinfo.GE6 = value

    @property
    def ANGLE(self) -> str:
        """
           Flag indicating that the next 1 to 6 fields are Loss angles defined in degrees. 9
        """
        return self.__cardinfo.ANGLE

    @ANGLE.setter
    def ANGLE(self, value: str) -> None:
        self.__cardinfo.ANGLE = value

    @property
    def ANGLE1(self) -> float:
        """
           Nominal angle values in directions 1 through 6 in degrees.
        """
        return self.__cardinfo.ANGLE1

    @ANGLE1.setter
    def ANGLE1(self, value: float) -> None:
        self.__cardinfo.ANGLE1 = value

    @property
    def ANGLE2(self) -> float:
        """
           ANGLE2
        """
        return self.__cardinfo.ANGLE2

    @ANGLE2.setter
    def ANGLE2(self, value: float) -> None:
        self.__cardinfo.ANGLE2 = value

    @property
    def ANGLE3(self) -> float:
        """
           ANGLE3
        """
        return self.__cardinfo.ANGLE3

    @ANGLE3.setter
    def ANGLE3(self, value: float) -> None:
        self.__cardinfo.ANGLE3 = value

    @property
    def ANGLE4(self) -> float:
        """
           ANGLE4
        """
        return self.__cardinfo.ANGLE4

    @ANGLE4.setter
    def ANGLE4(self, value: float) -> None:
        self.__cardinfo.ANGLE4 = value

    @property
    def ANGLE5(self) -> float:
        """
           ANGLE5
        """
        return self.__cardinfo.ANGLE5

    @ANGLE5.setter
    def ANGLE5(self, value: float) -> None:
        self.__cardinfo.ANGLE5 = value

    @property
    def ANGLE6(self) -> float:
        """
           ANGLE6
        """
        return self.__cardinfo.ANGLE6

    @ANGLE6.setter
    def ANGLE6(self, value: float) -> None:
        self.__cardinfo.ANGLE6 = value

    @property
    def M(self) -> str:
        """
           Flag indicating that the next 1 to 6 fields are directional masses.
        """
        return self.__cardinfo.M

    @M.setter
    def M(self, value: str) -> None:
        self.__cardinfo.M = value

    @property
    def M1(self) -> float:
        """
           Mi: Nominal mass values in directions 1 through 6.
           In case of implicit analysis: 10
           M1
           For translational mass calculation.
           Default = 0.0(Real)
           M2, M3
           If defined, they must be same as M1.
           Default = blank(Real)
           M4, M5, M6
           For inertia calculation.
           In this case, Inertia = max. (M4, M5, M6).
           Default = blank(Real)
           In case of explicit analysis:
           M1
           Required for translational mass calculation.
           No default (Real)
           M2, M3
           If defined, they must be same as M1.
           Default = blank(Real)
           M4
           For inertia calculation.
           For zero length CBUSH elements:
           M4
           Required. No default (Real)
           For non-zero length CBUSH elements:
           M4
           Optional. Default = blank(Real)
           M5, M6
           These are currently ignored.
           Default = blank(Real)
        """
        return self.__cardinfo.M1

    @M1.setter
    def M1(self, value: float) -> None:
        self.__cardinfo.M1 = value

    @property
    def M2(self) -> float:
        """
           M2
        """
        return self.__cardinfo.M2

    @M2.setter
    def M2(self, value: float) -> None:
        self.__cardinfo.M2 = value

    @property
    def M3(self) -> float:
        """
           M3
        """
        return self.__cardinfo.M3

    @M3.setter
    def M3(self, value: float) -> None:
        self.__cardinfo.M3 = value

    @property
    def M4(self) -> float:
        """
           M4
        """
        return self.__cardinfo.M4

    @M4.setter
    def M4(self, value: float) -> None:
        self.__cardinfo.M4 = value

    @property
    def M5(self) -> float:
        """
           M5
        """
        return self.__cardinfo.M5

    @M5.setter
    def M5(self, value: float) -> None:
        self.__cardinfo.M5 = value

    @property
    def M6(self) -> float:
        """
           M6
        """
        return self.__cardinfo.M6

    @M6.setter
    def M6(self, value: float) -> None:
        self.__cardinfo.M6 = value


class PCOMPNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPcompNas)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (0 < Integer < 10000000)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def Z0(self) -> float:
        """
           Distance from the reference plane to the bottom surface. See Remark 10. (Real; Default = -0.5 times the element thickness.)
           * Remark 10:
           If the value specified for Z0 is not equal to -0.5 times the thickness of the element and PARAM,NOCOMPS,-1 is specified, then the homogeneous
           element stresses are incorrect, while element forces and strains are correct. For correct homogeneous stresses, use ZOFFS on the corresponding
           connection entry.
        """
        return self.__cardinfo.Z0

    @Z0.setter
    def Z0(self, value: float) -> None:
        self.__cardinfo.Z0 = value

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit area. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value

    @property
    def SB(self) -> float:
        """
           Allowable shear stress of the bonding material (allowable interlaminar shear stress). Required if FT is also specified. (Real > 0.0)
        """
        return self.__cardinfo.SB

    @SB.setter
    def SB(self, value: float) -> None:
        self.__cardinfo.SB = value

    @property
    def FT(self) -> str:
        """
           Failure theory. The following theories are allowed (Character or blank. If blank, then no failure calculation will be performed) See Remark 7.
           “HILL” for the Hill theory.
           “HOFF” for the Hoffman theory.
           “TSAI” for the Tsai-Wu theory.
           “STRN” for the Maximum Strain theory.
           * Remark 7:
           In order to get failure index output the following must be present:
           a.ELSTRESS or ELSTRAIN Case Control commands,
           b. SB, FT, and SOUTi on the PCOMP Bulk Data entry,
           c. Xt, Xc, Yt, Yc, and S on all referenced MAT8 Bulk Data entries if stress allowables are used, or Xt, Xc, Yt, S, and STRN = 1.0 if strain allowables are used.
        """
        return self.__cardinfo.FT

    @FT.setter
    def FT(self, value: str) -> None:
        self.__cardinfo.FT = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature. See Remark 3. (Real; Default = 0.0)
           * Remark 3:
           The TREF specified on the material entries referenced by plies are not used.
           Instead TREF on the PCOMP entry is used for all plies of the element.If not specified, it defaults to “0.0.”
           If the PCOMP references temperature dependent material properties, then the TREF given on the PCOMP will be used as the temperature to determine
           material properties.
           TEMPERATURE Case Control commands are ignored for deriving the equivalent PSHELL and MAT2 entries used to describe the composite element.
           If for a nonlinear static analysis the parameter COMPMATT is set to YES, the temperature at the current load step will be used to determine temperature dependent
           material properties for the plies and the equivalent PSHELL and MAT2 entries for the composite element.The TREF on the PCOMP entry will
           be used for the initial thermal strain on the composite element and the stresses on the individual plies.If the parameter EPSILONT is also set to
           INTEGRAL,TREF is not applicable.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Damping coefficient. See Remarks 4. and 12. (Real; Default = 0.0)
           * Remark 4:
           GE given on the PCOMP entry will be used for the element and the values supplied on material entries for individual plies are ignored.The user is
           responsible for supplying the equivalent damping value on the PCOMP entry.If PARAM, W4 is not specified GE is ignored in transient analysis. See
           “Parameters” on page 631.
           * Remark 12:
           To obtain the damping coefficient GE, multiply the critical damping ratio C ⁄ C0 by 2.0.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def LAM(self) -> str:
        """
           Laminate Options. (Character or blank, Default = blank). See Remarks 13. and 14.
           “Blank” All plies must be specified and all stiffness terms are developed.
           “SYM” Only plies on one side of the element centerline are specified. The plies are numbered starting with 1 for the bottom layer.If an odd number of plies
           are desired, the center ply thickness (T1) should be half the actual thickness.
           “MEM” All plies must be specified, but only membrane terms (MID1 on the derived PSHELL entry) are computed.
           “BEND” All plies must be specified, but only bending terms (MID2 on the derived PSHELL entry) are computed.
           “SMEAR” All plies must be specified, stacking sequence is ignored MID1 = MID2 on the derived PSHELL entry and MID3, MID4 and TS/T and 12I/T**3 terms are
           set as blanks).
           “SMCORE”All plies must be specified, with the last ply specifying core properties and the previous plies specifying face sheet properties.
           The stiffness matrix is computed by placing half the face sheet thicknesses above the core and the other half below with the result that the laminate is
           symmetric about the midplane of the core.Stacking sequence is ignored in calculating the face sheet stiffness.
           * Remark 13:
           The SYM option for the LAM option computes the complete stiffness properties while specifying half the plies.The MEM, BEND, SMEAR and
           SMCORE options provide special purpose stiffness calculations.SMEAR ignores stacking sequence and is intended for cases where this sequence is
           not yet known, stiffness properties are smeared. SMCORE allows simplified modeling of a sandwich panel with equal face sheets and a central core.
           * Remark 14:
           Element output for the SMEAR and SMCORE options is produced using the PARAM NOCOMPS -1 methodology that suppresses ply stress/strain
           results and prints results for the equivalent homogeneous element.
        """
        return self.__cardinfo.LAM

    @LAM.setter
    def LAM(self, value: str) -> None:
        self.__cardinfo.LAM = value

    @property
    def MIDi(self) -> list[int]:
        """
           Laminate Options. (Character or blank, Default = blank). See Remarks 13. and 14.
           “Blank” All plies must be specified and all stiffness terms are developed.
           “SYM” Only plies on one side of the element centerline are specified. The plies are numbered starting with 1 for the bottom layer.If an odd number of plies
           are desired, the center ply thickness (T1) should be half the actual thickness.
           “MEM” All plies must be specified, but only membrane terms (MID1 on the derived PSHELL entry) are computed.
           “BEND” All plies must be specified, but only bending terms (MID2 on the derived PSHELL entry) are computed.
           “SMEAR” All plies must be specified, stacking sequence is ignored MID1 = MID2 on the derived PSHELL entry and MID3, MID4 and TS/T and 12I/T**3 terms are
           set as blanks).
           “SMCORE”All plies must be specified, with the last ply specifying core properties and the previous plies specifying face sheet properties.
           The stiffness matrix is computed by placing half the face sheet thicknesses above the core and the other half below with the result that the laminate is
           symmetric about the midplane of the core.Stacking sequence is ignored in calculating the face sheet stiffness.
           * Remark 13:
           The SYM option for the LAM option computes the complete stiffness properties while specifying half the plies.The MEM, BEND, SMEAR and
           SMCORE options provide special purpose stiffness calculations.SMEAR ignores stacking sequence and is intended for cases where this sequence is
           not yet known, stiffness properties are smeared. SMCORE allows simplified modeling of a sandwich panel with equal face sheets and a central core.
           * Remark 14:
           Element output for the SMEAR and SMCORE options is produced using the PARAM NOCOMPS -1 methodology that suppresses ply stress/strain
           results and prints results for the equivalent homogeneous element.
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.MIDi), self.__cardinfo.MIDi)

    @MIDi.setter
    def MIDi(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.MIDi[i] = val

    @property
    def Ti(self) -> list[float]:
        """
           Laminate Options. (Character or blank, Default = blank). See Remarks 13. and 14.
           “Blank” All plies must be specified and all stiffness terms are developed.
           “SYM” Only plies on one side of the element centerline are specified. The plies are numbered starting with 1 for the bottom layer.If an odd number of plies
           are desired, the center ply thickness (T1) should be half the actual thickness.
           “MEM” All plies must be specified, but only membrane terms (MID1 on the derived PSHELL entry) are computed.
           “BEND” All plies must be specified, but only bending terms (MID2 on the derived PSHELL entry) are computed.
           “SMEAR” All plies must be specified, stacking sequence is ignored MID1 = MID2 on the derived PSHELL entry and MID3, MID4 and TS/T and 12I/T**3 terms are
           set as blanks).
           “SMCORE”All plies must be specified, with the last ply specifying core properties and the previous plies specifying face sheet properties.
           The stiffness matrix is computed by placing half the face sheet thicknesses above the core and the other half below with the result that the laminate is
           symmetric about the midplane of the core.Stacking sequence is ignored in calculating the face sheet stiffness.
           * Remark 13:
           The SYM option for the LAM option computes the complete stiffness properties while specifying half the plies.The MEM, BEND, SMEAR and
           SMCORE options provide special purpose stiffness calculations.SMEAR ignores stacking sequence and is intended for cases where this sequence is
           not yet known, stiffness properties are smeared. SMCORE allows simplified modeling of a sandwich panel with equal face sheets and a central core.
           * Remark 14:
           Element output for the SMEAR and SMCORE options is produced using the PARAM NOCOMPS -1 methodology that suppresses ply stress/strain
           results and prints results for the equivalent homogeneous element.
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.Ti), self.__cardinfo.Ti)

    @Ti.setter
    def Ti(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.Ti[i] = val

    @property
    def THETAi(self) -> list[float]:
        """
           Laminate Options. (Character or blank, Default = blank). See Remarks 13. and 14.
           “Blank” All plies must be specified and all stiffness terms are developed.
           “SYM” Only plies on one side of the element centerline are specified. The plies are numbered starting with 1 for the bottom layer.If an odd number of plies
           are desired, the center ply thickness (T1) should be half the actual thickness.
           “MEM” All plies must be specified, but only membrane terms (MID1 on the derived PSHELL entry) are computed.
           “BEND” All plies must be specified, but only bending terms (MID2 on the derived PSHELL entry) are computed.
           “SMEAR” All plies must be specified, stacking sequence is ignored MID1 = MID2 on the derived PSHELL entry and MID3, MID4 and TS/T and 12I/T**3 terms are
           set as blanks).
           “SMCORE”All plies must be specified, with the last ply specifying core properties and the previous plies specifying face sheet properties.
           The stiffness matrix is computed by placing half the face sheet thicknesses above the core and the other half below with the result that the laminate is
           symmetric about the midplane of the core.Stacking sequence is ignored in calculating the face sheet stiffness.
           * Remark 13:
           The SYM option for the LAM option computes the complete stiffness properties while specifying half the plies.The MEM, BEND, SMEAR and
           SMCORE options provide special purpose stiffness calculations.SMEAR ignores stacking sequence and is intended for cases where this sequence is
           not yet known, stiffness properties are smeared. SMCORE allows simplified modeling of a sandwich panel with equal face sheets and a central core.
           * Remark 14:
           Element output for the SMEAR and SMCORE options is produced using the PARAM NOCOMPS -1 methodology that suppresses ply stress/strain
           results and prints results for the equivalent homogeneous element.
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.THETAi), self.__cardinfo.THETAi)

    @THETAi.setter
    def THETAi(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.THETAi[i] = val

    @property
    def SOUTi(self) -> list[str]:
        """
           Laminate Options. (Character or blank, Default = blank). See Remarks 13. and 14.
           “Blank” All plies must be specified and all stiffness terms are developed.
           “SYM” Only plies on one side of the element centerline are specified. The plies are numbered starting with 1 for the bottom layer.If an odd number of plies
           are desired, the center ply thickness (T1) should be half the actual thickness.
           “MEM” All plies must be specified, but only membrane terms (MID1 on the derived PSHELL entry) are computed.
           “BEND” All plies must be specified, but only bending terms (MID2 on the derived PSHELL entry) are computed.
           “SMEAR” All plies must be specified, stacking sequence is ignored MID1 = MID2 on the derived PSHELL entry and MID3, MID4 and TS/T and 12I/T**3 terms are
           set as blanks).
           “SMCORE”All plies must be specified, with the last ply specifying core properties and the previous plies specifying face sheet properties.
           The stiffness matrix is computed by placing half the face sheet thicknesses above the core and the other half below with the result that the laminate is
           symmetric about the midplane of the core.Stacking sequence is ignored in calculating the face sheet stiffness.
           * Remark 13:
           The SYM option for the LAM option computes the complete stiffness properties while specifying half the plies.The MEM, BEND, SMEAR and
           SMCORE options provide special purpose stiffness calculations.SMEAR ignores stacking sequence and is intended for cases where this sequence is
           not yet known, stiffness properties are smeared. SMCORE allows simplified modeling of a sandwich panel with equal face sheets and a central core.
           * Remark 14:
           Element output for the SMEAR and SMCORE options is produced using the PARAM NOCOMPS -1 methodology that suppresses ply stress/strain
           results and prints results for the equivalent homogeneous element.
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.SOUTi), self.__cardinfo.SOUTi)

    @SOUTi.setter
    def SOUTi(self, value: list[str]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.SOUTi[i] = val


class PCOMPOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPcompOpt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (0 < Integer < 10000000)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def Z0(self) -> float:
        """
           Distance from the reference plane to the bottom surface. See Remark 10. (Real; Default = -0.5 times the element thickness.)
           * Remark 10:
           If the value specified for Z0 is not equal to -0.5 times the thickness of the element and PARAM,NOCOMPS,-1 is specified, then the homogeneous
           element stresses are incorrect, while element forces and strains are correct. For correct homogeneous stresses, use ZOFFS on the corresponding
           connection entry.
        """
        return self.__cardinfo.Z0

    @Z0.setter
    def Z0(self, value: float) -> None:
        self.__cardinfo.Z0 = value

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit area. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value

    @property
    def SB(self) -> float:
        """
           Allowable shear stress of the bonding material (allowable interlaminar shear stress). Required if FT is also specified. (Real > 0.0)
        """
        return self.__cardinfo.SB

    @SB.setter
    def SB(self, value: float) -> None:
        self.__cardinfo.SB = value

    @property
    def FT(self) -> str:
        """
           Failure theory. The following theories are allowed (Character or blank. If blank, then no failure calculation will be performed) See Remark 7.
           “HILL” for the Hill theory.
           “HOFF” for the Hoffman theory.
           “TSAI” for the Tsai-Wu theory.
           “STRN” for the Maximum Strain theory.
           * Remark 7:
           In order to get failure index output the following must be present:
           a.ELSTRESS or ELSTRAIN Case Control commands,
           b. SB, FT, and SOUTi on the PCOMP Bulk Data entry,
           c. Xt, Xc, Yt, Yc, and S on all referenced MAT8 Bulk Data entries if stress allowables are used, or Xt, Xc, Yt, S, and STRN = 1.0 if strain allowables are used.
        """
        return self.__cardinfo.FT

    @FT.setter
    def FT(self, value: str) -> None:
        self.__cardinfo.FT = value

    @property
    def TREF(self) -> float:
        """
           Reference temperature. See Remark 3. (Real; Default = 0.0)
           * Remark 3:
           The TREF specified on the material entries referenced by plies are not used.
           Instead TREF on the PCOMP entry is used for all plies of the element.If not specified, it defaults to “0.0.”
           If the PCOMP references temperature dependent material properties, then the TREF given on the PCOMP will be used as the temperature to determine
           material properties.
           TEMPERATURE Case Control commands are ignored for deriving the equivalent PSHELL and MAT2 entries used to describe the composite element.
           If for a nonlinear static analysis the parameter COMPMATT is set to YES, the temperature at the current load step will be used to determine temperature dependent
           material properties for the plies and the equivalent PSHELL and MAT2 entries for the composite element.The TREF on the PCOMP entry will
           be used for the initial thermal strain on the composite element and the stresses on the individual plies.If the parameter EPSILONT is also set to
           INTEGRAL,TREF is not applicable.
        """
        return self.__cardinfo.TREF

    @TREF.setter
    def TREF(self, value: float) -> None:
        self.__cardinfo.TREF = value

    @property
    def GE(self) -> float:
        """
           Damping coefficient. See Remarks 4. and 12. (Real; Default = 0.0)
           * Remark 4:
           GE given on the PCOMP entry will be used for the element and the values supplied on material entries for individual plies are ignored.The user is
           responsible for supplying the equivalent damping value on the PCOMP entry.If PARAM, W4 is not specified GE is ignored in transient analysis. See
           “Parameters” on page 631.
           * Remark 12:
           To obtain the damping coefficient GE, multiply the critical damping ratio C ⁄ C0 by 2.0.
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value

    @property
    def LAM(self) -> str:
        """
           Laminate Options. (Character or blank, Default = blank). See Remarks 13. and 14.
           “Blank” All plies must be specified and all stiffness terms are developed.
           “SYM” Only plies on one side of the element centerline are specified. The plies are numbered starting with 1 for the bottom layer.If an odd number of plies
           are desired, the center ply thickness (T1) should be half the actual thickness.
           “MEM” All plies must be specified, but only membrane terms (MID1 on the derived PSHELL entry) are computed.
           “BEND” All plies must be specified, but only bending terms (MID2 on the derived PSHELL entry) are computed.
           “SMEAR” All plies must be specified, stacking sequence is ignored MID1 = MID2 on the derived PSHELL entry and MID3, MID4 and TS/T and 12I/T**3 terms are
           set as blanks).
           “SMCORE”All plies must be specified, with the last ply specifying core properties and the previous plies specifying face sheet properties.
           The stiffness matrix is computed by placing half the face sheet thicknesses above the core and the other half below with the result that the laminate is
           symmetric about the midplane of the core.Stacking sequence is ignored in calculating the face sheet stiffness.
           * Remark 13:
           The SYM option for the LAM option computes the complete stiffness properties while specifying half the plies.The MEM, BEND, SMEAR and
           SMCORE options provide special purpose stiffness calculations.SMEAR ignores stacking sequence and is intended for cases where this sequence is
           not yet known, stiffness properties are smeared. SMCORE allows simplified modeling of a sandwich panel with equal face sheets and a central core.
           * Remark 14:
           Element output for the SMEAR and SMCORE options is produced using the PARAM NOCOMPS -1 methodology that suppresses ply stress/strain
           results and prints results for the equivalent homogeneous element.
        """
        return self.__cardinfo.LAM

    @LAM.setter
    def LAM(self, value: str) -> None:
        self.__cardinfo.LAM = value

    @property
    def MIDi(self) -> list[int]:
        """
           Material ID of the various plies.The plies are identified by serially numbering them from 1 at the bottom layer. The MIDs must refer to MAT1,
           MAT2, or MAT8 Bulk Data entries.See Remarks 1. and 15. (Integer > 0 or blank, except MID1 must be specified.)
           * Remark 1:
           The default for MID2, ..., MIDn is the last defined MIDi. In the example above, MID1 is the default for MID2, MID3, and MID4.The same logic applies to Ti.
           * Remark 15:
           Temperature-dependent ply properties only available in SOL 106. See PARAM,COMPMATT for details.
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.MIDi), self.__cardinfo.MIDi)

    @MIDi.setter
    def MIDi(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.MIDi[i] = val

    @property
    def Ti(self) -> list[float]:
        """
           Thicknesses of the various plies. See Remarks 1. (Real or blank, except T1 must be specified.)
           * Remark 1:
           The default for MID2, ..., MIDn is the last defined MIDi. In the example above, MID1 is the default for MID2, MID3, and MID4.The same logic applies to Ti.
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.Ti), self.__cardinfo.Ti)

    @Ti.setter
    def Ti(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.Ti[i] = val

    @property
    def THETAi(self) -> list[float]:
        """
           Thicknesses of the various plies. See Remarks 1. (Real or blank, except T1 must be specified.)
           * Remark 1:
           The default for MID2, ..., MIDn is the last defined MIDi. In the example above, MID1 is the default for MID2, MID3, and MID4.The same logic applies to Ti.
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.THETAi), self.__cardinfo.THETAi)

    @THETAi.setter
    def THETAi(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.THETAi[i] = val

    @property
    def SOUTi(self) -> list[str]:
        """
           Stress or strain output request. See Remarks 5. and 6. (Character: “YES” or “NO”; Default = “NO”)
           * Remark 5:
           Stress and strain output for individual plies are available in all superelement static and normal modes analysis and requested by the STRESS and STRAIN
           Case Control commands.
           * Remark 6:
           If PARAM,NOCOMPS is set to -1, stress and strain output for individual plies will be suppressed and the homogeneous stress and strain output will be printed.
           See also Remark 10.
           * Remark 10:
           If the value specified for Z0 is not equal to -0.5 times the thickness of the element and PARAM,NOCOMPS,-1 is specified, then the homogeneous
           element stresses are incorrect, while element forces and strains are correct. For correct homogeneous stresses, use ZOFFS on the corresponding
           connection entry.
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.SOUTi), self.__cardinfo.SOUTi)

    @SOUTi.setter
    def SOUTi(self, value: list[str]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.SOUTi[i] = val

    @property
    def DS(self) -> float:
        """
           Design switch. If non-zero (1.0), the elements associated with this PCOMP data are included in the topology design volume or space. Default = blank
           (Real = 1.0 or blank)
        """
        return self.__cardinfo.DS

    @DS.setter
    def DS(self, value: float) -> None:
        self.__cardinfo.DS = value

    @property
    def NRPT(self) -> int:
        """
           Number of repeat laminates 20. Default = blank(Integer > 0 or blank)
        """
        return self.__cardinfo.NRPT

    @NRPT.setter
    def NRPT(self, value: int) -> None:
        self.__cardinfo.NRPT = value

    @property
    def EXPLICIT(self) -> str:
        """
           Flag indicating that parameters for Explicit Analysis are to follow.
        """
        return self.__cardinfo.EXPLICIT

    @EXPLICIT.setter
    def EXPLICIT(self, value: str) -> None:
        self.__cardinfo.EXPLICIT = value

    @property
    def ISOPE(self) -> str:
        """
           Element formulation flag for Explicit Analysis. 21 22 23
           BT                                                                       Belytschko-Tsay.
           BWC(Default for four-noded CQUAD4 elements in explicit analysis)          Belytschko-Wong-Chiang with full projection.
           blank
        """
        return self.__cardinfo.ISOPE

    @ISOPE.setter
    def ISOPE(self, value: str) -> None:
        self.__cardinfo.ISOPE = value

    @property
    def HGID(self) -> int:
        """
           Identification number of the hourglass control (HOURGLS) entry. Default = Blank(Integer > 0)
        """
        return self.__cardinfo.HGID

    @HGID.setter
    def HGID(self, value: int) -> None:
        self.__cardinfo.HGID = value

    @property
    def NIP(self) -> int:
        """
           Number of Gauss points through thickness. Default = 3 (1 ≤ Integer ≤ 10)
        """
        return self.__cardinfo.NIP

    @NIP.setter
    def NIP(self, value: int) -> None:
        self.__cardinfo.NIP = value


class PELAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PLPLANE)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID1(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID1

    @PID1.setter
    def PID1(self, value: int) -> None:
        self.__cardinfo.PID1 = value

    @property
    def K1(self) -> float:
        """
           Elastic property value. (Real)
        """
        return self.__cardinfo.K1

    @K1.setter
    def K1(self, value: float) -> None:
        self.__cardinfo.K1 = value

    @property
    def GE1(self) -> float:
        """
           Damping coefficient, . See Remarks 5. and 6. (Real)
        """
        return self.__cardinfo.GE1

    @GE1.setter
    def GE1(self, value: float) -> None:
        self.__cardinfo.GE1 = value

    @property
    def S1(self) -> float:
        """
           Stress coefficient. (Real)
        """
        return self.__cardinfo.S1

    @S1.setter
    def S1(self, value: float) -> None:
        self.__cardinfo.S1 = value

    @property
    def PID2(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID2

    @PID2.setter
    def PID2(self, value: int) -> None:
        self.__cardinfo.PID2 = value

    @property
    def K2(self) -> float:
        """
           Elastic property value. (Real)
        """
        return self.__cardinfo.K2

    @K2.setter
    def K2(self, value: float) -> None:
        self.__cardinfo.K2 = value

    @property
    def GE2(self) -> float:
        """
           Damping coefficient, . See Remarks 5. and 6. (Real)
        """
        return self.__cardinfo.GE2

    @GE2.setter
    def GE2(self, value: float) -> None:
        self.__cardinfo.GE2 = value

    @property
    def S2(self) -> float:
        """
           Stress coefficient. (Real)
        """
        return self.__cardinfo.S2

    @S2.setter
    def S2(self, value: float) -> None:
        self.__cardinfo.S2 = value


class PFAST(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PFAST)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           <para>PID: <see cref="CardPfast"/> does not have an associate property. Returns <see cref="uint.MaxValue"/></para>
           <para>Implemented to use the interface <see cref="ICardProperty"/></para>
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def D(self) -> float:
        """
           D
        """
        return self.__cardinfo.D

    @D.setter
    def D(self, value: float) -> None:
        self.__cardinfo.D = value

    @property
    def MCID(self) -> int:
        """
           MCID
        """
        return self.__cardinfo.MCID

    @MCID.setter
    def MCID(self, value: int) -> None:
        self.__cardinfo.MCID = value

    @property
    def MFLAG(self) -> int:
        """
           MCID
        """
        return self.__cardinfo.MFLAG

    @MFLAG.setter
    def MFLAG(self, value: int) -> None:
        self.__cardinfo.MFLAG = value

    @property
    def KT1(self) -> float:
        """
           KT1
        """
        return self.__cardinfo.KT1

    @KT1.setter
    def KT1(self, value: float) -> None:
        self.__cardinfo.KT1 = value

    @property
    def KT2(self) -> float:
        """
           KT2
        """
        return self.__cardinfo.KT2

    @KT2.setter
    def KT2(self, value: float) -> None:
        self.__cardinfo.KT2 = value

    @property
    def KT3(self) -> float:
        """
           KT3
        """
        return self.__cardinfo.KT3

    @KT3.setter
    def KT3(self, value: float) -> None:
        self.__cardinfo.KT3 = value

    @property
    def KR1(self) -> float:
        """
           KR1
        """
        return self.__cardinfo.KR1

    @KR1.setter
    def KR1(self, value: float) -> None:
        self.__cardinfo.KR1 = value

    @property
    def KR2(self) -> float:
        """
           KR2
        """
        return self.__cardinfo.KR2

    @KR2.setter
    def KR2(self, value: float) -> None:
        self.__cardinfo.KR2 = value

    @property
    def KR3(self) -> float:
        """
           KR3
        """
        return self.__cardinfo.KR3

    @KR3.setter
    def KR3(self, value: float) -> None:
        self.__cardinfo.KR3 = value

    @property
    def MASS(self) -> float:
        """
           MASS
        """
        return self.__cardinfo.MASS

    @MASS.setter
    def MASS(self, value: float) -> None:
        self.__cardinfo.MASS = value

    @property
    def GE(self) -> float:
        """
           MASS
        """
        return self.__cardinfo.GE

    @GE.setter
    def GE(self, value: float) -> None:
        self.__cardinfo.GE = value


class PLOTEL(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPlotel)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (Integer > 0)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def PID(self) -> int:
        """
           <para>PID: <see cref="CardPlotel"/> does not have an associate property. Returns <see cref="uint.MaxValue"/></para>
           <para>Implemented to use the interface <see cref="ICardElement"/></para>
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def G1(self) -> int:
        """
           CardGrid point identification numbers of connection points. (Integer > 0 ; G1 ≠ G2)
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def G2(self) -> int:
        """
           G2
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value


class PLPLANE(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPlplane)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Identification number of a MATHP entry. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def CID(self) -> int:
        """
           Identification number of a coordinate system defining the plane of deformation.See Remarks 2. and 3. (Integer >= 0; Default = 0)
           * Remark 2:
           Plane strain hyperelastic elements must lie on the x-y plane of the CID coordinate system.Stresses and strains are output in the CID coordinate system.
           * Remark 3:
           Axisymmetric hyperelastic elements must lie on the x-y plane of the basic coordinate system.CID may not be specified and stresses and strains are
           output in the basic coordinate system.
        """
        return self.__cardinfo.CID

    @CID.setter
    def CID(self, value: int) -> None:
        self.__cardinfo.CID = value

    @property
    def STR(self) -> str:
        """
           Location of stress and strain output. (Character: “GAUS” or “GRID”, Default = “GRID”)
        """
        return self.__cardinfo.STR

    @STR.setter
    def STR(self, value: str) -> None:
        self.__cardinfo.STR = value


class PMASS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPmass)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID1(self) -> int:
        """
           PIDi Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID1

    @PID1.setter
    def PID1(self, value: int) -> None:
        self.__cardinfo.PID1 = value

    @property
    def M1(self) -> float:
        """
           Mi Value of scalar mass. (Real)
        """
        return self.__cardinfo.M1

    @M1.setter
    def M1(self, value: float) -> None:
        self.__cardinfo.M1 = value

    @property
    def PID2(self) -> int:
        """
           PID2
        """
        return self.__cardinfo.PID2

    @PID2.setter
    def PID2(self, value: int) -> None:
        self.__cardinfo.PID2 = value

    @property
    def M2(self) -> float:
        """
           M2
        """
        return self.__cardinfo.M2

    @M2.setter
    def M2(self, value: float) -> None:
        self.__cardinfo.M2 = value

    @property
    def PID3(self) -> int:
        """
           PID3
        """
        return self.__cardinfo.PID3

    @PID3.setter
    def PID3(self, value: int) -> None:
        self.__cardinfo.PID3 = value

    @property
    def M3(self) -> float:
        """
           M3
        """
        return self.__cardinfo.M3

    @M3.setter
    def M3(self, value: float) -> None:
        self.__cardinfo.M3 = value

    @property
    def PID4(self) -> int:
        """
           PID4
        """
        return self.__cardinfo.PID4

    @PID4.setter
    def PID4(self, value: int) -> None:
        self.__cardinfo.PID4 = value

    @property
    def M4(self) -> float:
        """
           M4
        """
        return self.__cardinfo.M4

    @M4.setter
    def M4(self, value: float) -> None:
        self.__cardinfo.M4 = value


class PROD(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PLPLANE)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Material identification number
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def A(self) -> float:
        """
           Area of bar cross section. (Real; Default = 0.0)
        """
        return self.__cardinfo.A

    @A.setter
    def A(self, value: float) -> None:
        self.__cardinfo.A = value

    @property
    def J(self) -> float:
        """
           Torsional constant. See Figure 8-177. (Real; Default = for SOL 600 and 0.0 for all other solution sequences)
        """
        return self.__cardinfo.J

    @J.setter
    def J(self, value: float) -> None:
        self.__cardinfo.J = value

    @property
    def C(self) -> float:
        """
           Coefficient to determine torsional stress. (Real; Default = 0.0)
        """
        return self.__cardinfo.C

    @C.setter
    def C(self, value: float) -> None:
        self.__cardinfo.C = value

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit length. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value


class PSHEAR(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PLPLANE)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Material identification number
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def T(self) -> float:
        """
           Thickness of shear panel. (Real 0.0)
        """
        return self.__cardinfo.T

    @T.setter
    def T(self, value: float) -> None:
        self.__cardinfo.T = value

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit length. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value

    @property
    def F1(self) -> float:
        """
           F1
        """
        return self.__cardinfo.F1

    @F1.setter
    def F1(self, value: float) -> None:
        self.__cardinfo.F1 = value

    @property
    def F2(self) -> float:
        """
           F2
        """
        return self.__cardinfo.F2

    @F2.setter
    def F2(self, value: float) -> None:
        self.__cardinfo.F2 = value


class PSHELLNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPshellNas)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID1(self) -> int:
        """
           Material identification number for the membrane. (Integer >= 0 or blank)
        """
        return self.__cardinfo.MID1

    @MID1.setter
    def MID1(self, value: int) -> None:
        self.__cardinfo.MID1 = value

    @property
    def T(self) -> float:
        """
           Default membrane thickness for Ti on the connection entry. If T is blank then the thickness must be specified for Ti on the CQUAD4, CTRIA3,
           CQUAD8, and CTRIA6 entries. (Real or blank)
        """
        return self.__cardinfo.T

    @T.setter
    def T(self, value: float) -> None:
        self.__cardinfo.T = value

    @property
    def MID2(self) -> int:
        """
           Material identification number for bending. (Integer >= -1 or blank)
        """
        return self.__cardinfo.MID2

    @MID2.setter
    def MID2(self, value: int) -> None:
        self.__cardinfo.MID2 = value

    @property
    def INERTIA(self) -> float:
        """
           Bending moment of inertia ratio, 12I T⁄ 3. Ratio of the actual bending moment inertia of the shell, I, to the bending moment of inertia of a
           homogeneous shell, T3 ⁄ 12. The default value is for a homogeneous shell. (Real > 0.0; Default = 1.0)
        """
        return self.__cardinfo.INERTIA

    @INERTIA.setter
    def INERTIA(self, value: float) -> None:
        self.__cardinfo.INERTIA = value

    @property
    def MID3(self) -> int:
        """
           Material identification number for transverse shear. (Integer > 0 or blank; unless MID2 > 0, must be blank.)
        """
        return self.__cardinfo.MID3

    @MID3.setter
    def MID3(self, value: int) -> None:
        self.__cardinfo.MID3 = value

    @property
    def TST(self) -> float:
        """
           Transverse shear thickness ratio, . Ratio of the shear thickness, to the membrane thickness of the shell, T.The default value is for a
           homogeneous shell. (Real > 0.0; Default = .833333)
        """
        return self.__cardinfo.TST

    @TST.setter
    def TST(self, value: float) -> None:
        self.__cardinfo.TST = value

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit area. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value

    @property
    def Z1(self) -> float:
        """
           Fiber distances for stress calculations. The positive direction is determined by the right-hand rule, and the order in which the grid
           points are listed on the connection entry.See Remark 11. for defaults. (Real or blank)
           * Remark 11:
           The default for Z1 is -T/2, and for Z2 is +T/2. T is the local plate thickness defined either by T on this entry or by membrane thicknesses at connected
           grid points, if they are input on connection entries.
        """
        return self.__cardinfo.Z1

    @Z1.setter
    def Z1(self, value: float) -> None:
        self.__cardinfo.Z1 = value

    @property
    def Z2(self) -> float:
        """
           Z2
        """
        return self.__cardinfo.Z2

    @Z2.setter
    def Z2(self, value: float) -> None:
        self.__cardinfo.Z2 = value

    @property
    def MID4(self) -> int:
        """
           Material identification number for membrane-bending coupling. See Remarks 6. and 13. (Integer > 0 or blank, must be blank unless MID1 > 0 and MID2 > 0,
           may not equal MID1 or MID2.)
           * Remark 6:
           The following should be considered when using MID4.
           The MID4 field should be left blank if the material properties are symmetric with respect to the middle surface of the shell.If the element centerline
           is offset from the plane of the grid points but the material properties are symmetric, the preferred method for modeling the offset is by use
           of the ZOFFS field on the connection entry. Although the MID4 field may be used for this purpose, it may produce ill-conditioned stiffness matrices
           (negative terms on factor diagonal) if done incorrectly.
           Only one of the options MID4 or ZOFFS should be used; if both methods are specified the effects are cumulative.Since this is probably not what the user
           intented, unexpected answers will result. Note that the mass properties are not modified to reflect the existence of the offset when the ZOFFS and MID4
           methods are used.If the weight or mass properties of an offset plate are to be used in ananalysis, the RBAR method must be used to represent the offset. See
           “Shell Elements (CTRIA3, CTRIA6, CTRIAR, CQUAD4, CQUAD8, CQUADR)” on page 131 of the MSC.Nastran Reference Guide.
           The effects of MID4 are not considered in the calculation of differential stiffness.Therefore, it is recommended that MID4 be left blank in buckling analysis.
           * Remark 13:
           For the CQUADR and CTRIAR elements, the MID4 field should be left blankbecause their formulation does not include membrane-bending coupling.
        """
        return self.__cardinfo.MID4

    @MID4.setter
    def MID4(self, value: int) -> None:
        self.__cardinfo.MID4 = value


class PSHELLOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPshellOpt)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID1(self) -> int:
        """
           Material identification number for the membrane. (Integer >= 0 or blank)
        """
        return self.__cardinfo.MID1

    @MID1.setter
    def MID1(self, value: int) -> None:
        self.__cardinfo.MID1 = value

    @property
    def T(self) -> float:
        """
           Default membrane thickness for Ti on the connection entry. If T is blank then the thickness must be specified for Ti on the CQUAD4, CTRIA3,
           CQUAD8, and CTRIA6 entries. (Real or blank)
        """
        return self.__cardinfo.T

    @T.setter
    def T(self, value: float) -> None:
        self.__cardinfo.T = value

    @property
    def MID2(self) -> int:
        """
           Material identification number for bending. (Integer >= -1 or blank)
        """
        return self.__cardinfo.MID2

    @MID2.setter
    def MID2(self, value: int) -> None:
        self.__cardinfo.MID2 = value

    @property
    def INERTIA(self) -> float:
        """
           Bending moment of inertia ratio, 12I T⁄ 3. Ratio of the actual bending moment inertia of the shell, I, to the bending moment of inertia of a
           homogeneous shell, T3 ⁄ 12. The default value is for a homogeneous shell. (Real > 0.0; Default = 1.0)
        """
        return self.__cardinfo.INERTIA

    @INERTIA.setter
    def INERTIA(self, value: float) -> None:
        self.__cardinfo.INERTIA = value

    @property
    def MID3(self) -> int:
        """
           Material identification number for transverse shear. (Integer > 0 or blank; unless MID2 > 0, must be blank.)
        """
        return self.__cardinfo.MID3

    @MID3.setter
    def MID3(self, value: int) -> None:
        self.__cardinfo.MID3 = value

    @property
    def TST(self) -> float:
        """
           Transverse shear thickness ratio, . Ratio of the shear thickness, to the membrane thickness of the shell, T.The default value is for a
           homogeneous shell. (Real > 0.0; Default = .833333)
        """
        return self.__cardinfo.TST

    @TST.setter
    def TST(self, value: float) -> None:
        self.__cardinfo.TST = value

    @property
    def NSM(self) -> float:
        """
           Nonstructural mass per unit area. (Real)
        """
        return self.__cardinfo.NSM

    @NSM.setter
    def NSM(self, value: float) -> None:
        self.__cardinfo.NSM = value

    @property
    def Z1(self) -> float:
        """
           Fiber distances for stress calculations. The positive direction is determined by the right-hand rule, and the order in which the grid
           points are listed on the connection entry.See Remark 11. for defaults. (Real or blank)
           * Remark 11:
           The default for Z1 is -T/2, and for Z2 is +T/2. T is the local plate thickness defined either by T on this entry or by membrane thicknesses at connected
           grid points, if they are input on connection entries.
        """
        return self.__cardinfo.Z1

    @Z1.setter
    def Z1(self, value: float) -> None:
        self.__cardinfo.Z1 = value

    @property
    def Z2(self) -> float:
        """
           Z2
        """
        return self.__cardinfo.Z2

    @Z2.setter
    def Z2(self, value: float) -> None:
        self.__cardinfo.Z2 = value

    @property
    def MID4(self) -> int:
        """
           Material identification number for membrane-bending coupling. See Remarks 6. and 13. (Integer > 0 or blank, must be blank unless MID1 > 0 and MID2 > 0,
           may not equal MID1 or MID2.)
           * Remark 6:
           The following should be considered when using MID4.
           The MID4 field should be left blank if the material properties are symmetric with respect to the middle surface of the shell.If the element centerline
           is offset from the plane of the grid points but the material properties are symmetric, the preferred method for modeling the offset is by use
           of the ZOFFS field on the connection entry. Although the MID4 field may be used for this purpose, it may produce ill-conditioned stiffness matrices
           (negative terms on factor diagonal) if done incorrectly.
           Only one of the options MID4 or ZOFFS should be used; if both methods are specified the effects are cumulative.Since this is probably not what the user
           intented, unexpected answers will result. Note that the mass properties are not modified to reflect the existence of the offset when the ZOFFS and MID4
           methods are used.If the weight or mass properties of an offset plate are to be used in ananalysis, the RBAR method must be used to represent the offset. See
           “Shell Elements (CTRIA3, CTRIA6, CTRIAR, CQUAD4, CQUAD8, CQUADR)” on page 131 of the MSC.Nastran Reference Guide.
           The effects of MID4 are not considered in the calculation of differential stiffness.Therefore, it is recommended that MID4 be left blank in buckling analysis.
           * Remark 13:
           For the CQUADR and CTRIAR elements, the MID4 field should be left blankbecause their formulation does not include membrane-bending coupling.
        """
        return self.__cardinfo.MID4

    @MID4.setter
    def MID4(self, value: int) -> None:
        self.__cardinfo.MID4 = value

    @property
    def T0(self) -> float:
        """
           The base thickness of the elements in topology and free-size optimization. Only for MAT1, T0 can be > 0.0. (Real ≥ 0.0 or blank for MAT1,
           Real = 0.0 or blank for MAT2, MAT8)
        """
        return self.__cardinfo.T0

    @T0.setter
    def T0(self, value: float) -> None:
        self.__cardinfo.T0 = value

    @property
    def ZOFFS(self) -> float:
        """
           Offset from the plane defined by element grid points to the shell reference plane. Real or Character Input(Top/Bottom)
        """
        return self.__cardinfo.ZOFFS

    @ZOFFS.setter
    def ZOFFS(self, value: float) -> None:
        self.__cardinfo.ZOFFS = value

    @property
    def EXPLICIT(self) -> str:
        """
           Flag indicating that parameters for Explicit Analysis are to follow.
        """
        return self.__cardinfo.EXPLICIT

    @EXPLICIT.setter
    def EXPLICIT(self, value: str) -> None:
        self.__cardinfo.EXPLICIT = value

    @property
    def ISOPE(self) -> int:
        """
           Element formulation flag for Explicit Analysis.
           BT                           Belytschko-Tsay.
           BWC                          Belytschko-Wong-Chiang with full projection. 4
           Blank
           Default = BWC for four-noded CQUAD4 elements in explicit analysis.
        """
        return self.__cardinfo.ISOPE

    @ISOPE.setter
    def ISOPE(self, value: int) -> None:
        self.__cardinfo.ISOPE = value

    @property
    def HGID(self) -> int:
        """
           Identification number of an hourglass control (HOURGLS) entry. Default = Blank(Integer > 0 or blank)
        """
        return self.__cardinfo.HGID

    @HGID.setter
    def HGID(self, value: int) -> None:
        self.__cardinfo.HGID = value

    @property
    def NIP(self) -> int:
        """
           Number of through thickness Gauss points. Default = 3 (1 ≤ Integer ≤ 10)
        """
        return self.__cardinfo.NIP

    @NIP.setter
    def NIP(self, value: int) -> None:
        self.__cardinfo.NIP = value


class PSOLIDNAS(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (CardPsolidNas)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Identification number of a MAT1, MAT4, MAT5, MAT9, or MAT10 entry. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def CORDM(self) -> int:
        """
           Identification number of a MAT1, MAT4, MAT5, MAT9, or MAT10 entry. (Integer > 0)
        """
        return self.__cardinfo.CORDM

    @CORDM.setter
    def CORDM(self, value: int) -> None:
        self.__cardinfo.CORDM = value

    @property
    def IN(self) -> str:
        """
           Integration network. See Remarks 5., 6., 7., and 9. (Integer, Character, or blank)
        """
        return self.__cardinfo.IN

    @IN.setter
    def IN(self, value: str) -> None:
        self.__cardinfo.IN = value

    @property
    def STRESS(self) -> str:
        """
           Location selection for stress output. See Remarks 8. and 9. (Integer, Character, or blank)
        """
        return self.__cardinfo.STRESS

    @STRESS.setter
    def STRESS(self, value: str) -> None:
        self.__cardinfo.STRESS = value

    @property
    def ISOP(self) -> str:
        """
           Integration scheme. See Remarks 5., 6., 7., and 9. (Integer, Character, or blank)
        """
        return self.__cardinfo.ISOP

    @ISOP.setter
    def ISOP(self, value: str) -> None:
        self.__cardinfo.ISOP = value

    @property
    def FCTN(self) -> str:
        """
           Fluid element flag. (Character: “PFLUID” indicates a fluid element, “SMECH” indicates a structural element; Default = “SMECH.”)
        """
        return self.__cardinfo.FCTN

    @FCTN.setter
    def FCTN(self, value: str) -> None:
        self.__cardinfo.FCTN = value


class PSOLIDOPT(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PSOLID_NASTRAN)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0 or string)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Identification number of a MAT1, MAT4, MAT5, MAT9, or MAT10 entry. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def CORDM(self) -> int:
        """
           Identification number of a MAT1, MAT4, MAT5, MAT9, or MAT10 entry. (Integer > 0)
        """
        return self.__cardinfo.CORDM

    @CORDM.setter
    def CORDM(self, value: int) -> None:
        self.__cardinfo.CORDM = value

    @property
    def ISOP(self) -> str:
        """
           Integration scheme. See Remarks 5., 6., 7., and 9. (Integer, Character, or blank)
        """
        return self.__cardinfo.ISOP

    @ISOP.setter
    def ISOP(self, value: str) -> None:
        self.__cardinfo.ISOP = value

    @property
    def FCTN(self) -> str:
        """
           Fluid element flag. (Character: “PFLUID” indicates a fluid element, “SMECH” indicates a structural element; Default = “SMECH.”)
        """
        return self.__cardinfo.FCTN

    @FCTN.setter
    def FCTN(self, value: str) -> None:
        self.__cardinfo.FCTN = value

    @property
    def EXPLICIT(self) -> str:
        """
           Flag indicating that parameters for Explicit Analysis are to follow.
        """
        return self.__cardinfo.EXPLICIT

    @EXPLICIT.setter
    def EXPLICIT(self, value: str) -> None:
        self.__cardinfo.EXPLICIT = value

    @property
    def ISOPE(self) -> str:
        """
           sri: Selective reduced integration for eight-noded CHEXA and six-noded CPENTA elements in explicit analysis.Full integration for deviatoric term and one-point integration for bulk term.
           URI: Uniform reduced integration for eight-noded CHEXA elements in explicit analysis.One-point integration is used.
           AURI: Average uniform reduced integration for eight-noded CHEXA elements in explicit analysis.B matrix is a volume average over the element.
           AVE: Nodal pressure averaged formulation. 10
           Defaults:
           AURI for eight-noded CHEXA elements in explicit analysis.
           AVE for four-noded CTETRA elements in explicit analysis.
        """
        return self.__cardinfo.ISOPE

    @ISOPE.setter
    def ISOPE(self, value: str) -> None:
        self.__cardinfo.ISOPE = value

    @property
    def HGID(self) -> int:
        """
           Identification number of the hourglass control (HOURGLS) Bulk Data Entry. No default
        """
        return self.__cardinfo.HGID

    @HGID.setter
    def HGID(self, value: int) -> None:
        self.__cardinfo.HGID = value

    @property
    def HGHOR(self) -> str:
        """
           Specifies the element formulation for ten-noded CTETRA elements in explicit analysis.
        """
        return self.__cardinfo.HGHOR

    @HGHOR.setter
    def HGHOR(self, value: str) -> None:
        self.__cardinfo.HGHOR = value


class PWELD(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (PLPLANE)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def PID(self) -> int:
        """
           Property identification number. (Integer > 0)
        """
        return self.__cardinfo.PID

    @PID.setter
    def PID(self, value: int) -> None:
        self.__cardinfo.PID = value

    @property
    def MID(self) -> int:
        """
           Identification number of a MATHP entry. (Integer > 0)
        """
        return self.__cardinfo.MID

    @MID.setter
    def MID(self, value: int) -> None:
        self.__cardinfo.MID = value

    @property
    def D(self) -> float:
        """
           Diameter of the connector
        """
        return self.__cardinfo.D

    @D.setter
    def D(self, value: float) -> None:
        self.__cardinfo.D = value

    @property
    def MSET(self) -> str:
        """
           Active ONLY for "PARAM,OLDWELD,YES".
           Flag to eliminate m-set degrees-of-freedom
           (DOFs). The MSET parameter has no effect in a
           nonlinear SOL 400 analysis.
           =OFF m-set DOFs are eliminated, constraints are
           incorporated in the stiffness, see Remark 2.
           =ON m-set DOFs are not eliminated, constraints
           are generated.
        """
        return self.__cardinfo.MSET

    @MSET.setter
    def MSET(self, value: str) -> None:
        self.__cardinfo.MSET = value

    @property
    def TYPE(self) -> str:
        """
           Character string indicating the type of connection,
           see Remarks 3. and 4.
           =blank general connector
           = “SPOT” spot weld connector
        """
        return self.__cardinfo.TYPE

    @TYPE.setter
    def TYPE(self, value: str) -> None:
        self.__cardinfo.TYPE = value

    @property
    def LDMIN(self) -> float:
        """
           Active ONLY for "PARAM,OLDWELD,YES".
           Smallest ratio of length to diameter for stiffness
           calculation, see Remark 4.
        """
        return self.__cardinfo.LDMIN

    @LDMIN.setter
    def LDMIN(self, value: float) -> None:
        self.__cardinfo.LDMIN = value

    @property
    def LDMAX(self) -> float:
        """
           Active ONLY for "PARAM,OLDWELD,YES".
           Largest ratio of length to diameter for stiffness
           calculation, see Remark 4.
        """
        return self.__cardinfo.LDMAX

    @LDMAX.setter
    def LDMAX(self, value: float) -> None:
        self.__cardinfo.LDMAX = value


class RBAR(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (RBAR)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def GA(self) -> int:
        """
           Grid point identification number of connection points. (Integer > 0)
           GA
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value

    @property
    def CNA(self) -> list[int]:
        """
           Component numbers of independent degrees-of-freedom in the global coordinate system for the element at grid points GA and GB.
           See Remark 3. (Integers 1 through 6 with no embedded blanks, or zero or blank.)
           * Remark 3:
           For the linear method, the total number of components in CNA and CNB must equal six; for example, CNA = 1236, CNB = 34. Furthermore, they must
           jointly be capable of representing any general rigid body motion of the element.For the Lagrange method, the total number of components must
           also be six.However, only CNA = 123456 or CNB = 123456 is allowed.If both CNA and CNB are blank, then CNA = 123456.For this method, RBAR1 gives
           the simpler input format.
           CNA
        """
        return list(self.__cardinfo.CNA)

    @CNA.setter
    def CNA(self, value: list[int]) -> None:
        self.__cardinfo.CNA = value

    @property
    def CNB(self) -> list[int]:
        """
           CNB
        """
        return list(self.__cardinfo.CNB)

    @CNB.setter
    def CNB(self, value: list[int]) -> None:
        self.__cardinfo.CNB = value

    @property
    def CMA(self) -> list[int]:
        """
           Component numbers of dependent degrees-of-freedom in the global coordinate system assigned by the element at grid points GA and GB.
           See Remarks 4. and 5. (Integers 1 through 6 with no embedded blanks, or zero or blank.)
           * Remark 4:
           If both CMA and CMB are zero or blank, all of the degrees-of-freedom not in CNA and CNB will be made dependent.For the linear method, the
           dependent degrees-of-freedom will be made members of the m-set.For the Lagrange method, they may or may not be member of the m-set, depending
           on the method selected in the RIGID Case Control command.However, the rules regarding the m-set described below apply to both methods.
           * Remark 5:
           The m-set coordinates specified on this entry may not be specified on other entries that define mutually exclusive sets.
           See “Degree-of-Freedom Sets” on page 887 for a list of these entries.
           CMA
        """
        return list(self.__cardinfo.CMA)

    @CMA.setter
    def CMA(self, value: list[int]) -> None:
        self.__cardinfo.CMA = value

    @property
    def CMB(self) -> list[int]:
        """
           CMB
        """
        return list(self.__cardinfo.CMB)

    @CMB.setter
    def CMB(self, value: list[int]) -> None:
        self.__cardinfo.CMB = value

    @property
    def ALPHA(self) -> float:
        """
           Thermal expansion coefficient. See Remark 11. (Real > 0.0 or blank)
           * Remark 11:
           For the Lagrange method, the thermal expansion effect will be computed for the rigid bar element if user supplies the thermal expansion
           coefficient ALPHA, and the thermal load is requested by the TEMPERATURE(INITIAL) and TEMPERATURE(LOAD) Case Control
           commands.The temperature of the element is taken as the average temperature of the two connected grid points GA and GB.
        """
        return self.__cardinfo.ALPHA

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA = value


class RBAR1(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (RBAR1)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def GA(self) -> int:
        """
           Grid point identification number of connection points. (Integer > 0)
           GA
        """
        return self.__cardinfo.GA

    @GA.setter
    def GA(self, value: int) -> None:
        self.__cardinfo.GA = value

    @property
    def GB(self) -> int:
        """
           GB
        """
        return self.__cardinfo.GB

    @GB.setter
    def GB(self, value: int) -> None:
        self.__cardinfo.GB = value

    @property
    def CB(self) -> list[int]:
        """
           Component numbers in the global coordinate system at GB, which are constrained to move as the rigid bar.
           See Remark 4. (Integers 1 through6 with no embedded blanks or blank.)
           * Remark 4:
           When CB = “123456” or blank, the grid point GB is constrained to move with GA as a rigid bar.For default CB = “123456”.
           Any number of degrees-offreedom at grid point GB can be released not to move with the rigid body.
        """
        return list(self.__cardinfo.CB)

    @CB.setter
    def CB(self, value: list[int]) -> None:
        self.__cardinfo.CB = value

    @property
    def ALPHA(self) -> float:
        """
           Thermal expansion coefficient. See Remark 8. (Real > 0.0 or blank)
           * Remark 8:
           Rigid elements are ignored in heat transfer problems.
        """
        return self.__cardinfo.ALPHA

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA = value


class RBE1(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (RBE1)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def GN(self) -> list[int]:
        """
           Grid points at which independent degrees-of-freedom for the element are assigned. (Integer > 0)
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.GN), self.__cardinfo.GN)

    @GN.setter
    def GN(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.GN[i] = val

    @property
    def CN(self) -> list[int]:
        """
           Independent degrees-of-freedom in the global coordinate system for the rigid element at grid point(s) GNi.
           See Remark 1. (Integers 1 through 6 with no embedded blanks.)
           * Remark 1:
           Two methods are available to process rigid elements: equation elimination or Lagrange multipliers.
           The Case Control command, RIGID, selects the method.
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.CN), self.__cardinfo.CN)

    @CN.setter
    def CN(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.CN[i] = val

    @property
    def UM(self) -> str:
        """
           Indicates the start of the dependent degrees-of-freedom. (Character)
        """
        return self.__cardinfo.UM.Value

    @UM.setter
    def UM(self, value: str) -> None:
        self.__cardinfo.UM.Value = value

    @property
    def GM(self) -> list[int]:
        """
           Grid points at which dependent degrees-of-freedom are assigned. (Integer > 0)
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.GM), self.__cardinfo.GM)

    @GM.setter
    def GM(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.GM[i] = val

    @property
    def CM(self) -> list[int]:
        """
           Dependent degrees-of-freedom in the global coordinate system at grid point(s) GMj. (Integers 1 through 6 with no embedded blanks.)
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.CM), self.__cardinfo.CM)

    @CM.setter
    def CM(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.CM[i] = val

    @property
    def ALPHA(self) -> float:
        """
           Thermal expansion coefficient. See Remark 13. (Real > 0.0 or blank)
           * Remark 13:
           For the Lagrange method, the thermal expansion effect will be computed, if user supplies the thermal expansion coefficient ALPHA, and the thermal
           load is requested by the TEMPERATURE(INITIAL) and TEMPERATURE(LOAD) Case Control commands.The temperature of the
           element is taken as follows: the temperature of the bar connecting the grid point GN1 and any dependent grid point are taken as the average
           temperature of the two connected grid points.
        """
        return self.__cardinfo.ALPHA.Value

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA.Value = value


class RBE2(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (RBE2)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def GN(self) -> int:
        """
           Identification number of grid point to which all six independent degrees-of-freedom for the element are assigned. (Integer > 0)
        """
        return self.__cardinfo.GN

    @GN.setter
    def GN(self, value: int) -> None:
        self.__cardinfo.GN = value

    @property
    def CM(self) -> list[int]:
        """
           Component numbers of the dependent degrees-of-freedom in the global coordinate system at grid points GMi.
           (Integers 1 through 6 with no embedded blanks.)
        """
        return list(self.__cardinfo.CM)

    @CM.setter
    def CM(self, value: list[int]) -> None:
        self.__cardinfo.CM = value

    @property
    def GM(self) -> list[int]:
        """
           Grid point identification numbers at which dependent degrees-offreedom are assigned. (Integer > 0)
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.GM), self.__cardinfo.GM)

    @GM.setter
    def GM(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.GM[i] = val

    @property
    def ALPHA(self) -> float:
        """
           Thermal expansion coefficient. See Remark 11. (Real > 0.0 or blank)
           * Remark 11:
           For the Lagrange method, the thermal expansion effect will be computed, if user supplies the thermal expansion coefficient ALPHA, and the thermal
           load is requested by the TEMPERATURE(INITIAL) and TEMPERATURE(LOAD) Case Control commands.The temperature of the element is taken as follows:
           the temperature of the bar connecting the grid point GN and any dependent grid point are taken as the average temperature of the two
           connected grid points.
        """
        return self.__cardinfo.ALPHA

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA = value


class RBE3(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (RBE3)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. Unique with respect to all elements. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def REFGRID(self) -> int:
        """
           Reference grid point identification number. (Integer > 0)
        """
        return self.__cardinfo.REFGRID

    @REFGRID.setter
    def REFGRID(self, value: int) -> None:
        self.__cardinfo.REFGRID = value

    @property
    def REFC(self) -> list[int]:
        """
           Component numbers at the reference grid point. (Any of the integers 1 through 6 with no embedded blanks.)
        """
        return list(self.__cardinfo.REFC)

    @REFC.setter
    def REFC(self, value: list[int]) -> None:
        self.__cardinfo.REFC = value

    @property
    def WT(self) -> list[float]:
        """
           Weighting factor for components of motion on the following entry at grid points Gi,j. (Real)
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.WT), self.__cardinfo.WT)

    @WT.setter
    def WT(self, value: list[float]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.WT[i] = val

    @property
    def C(self) -> list[int]:
        """
           Component numbers with weighting factor WTi at grid points Gi,j. (Any of the integers 1 through 6 with no embedded blanks.)
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.C), self.__cardinfo.C)

    @C.setter
    def C(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.C[i] = val

    @property
    def G(self) -> list[int]:
        """
           Grid points with components Ci that have weighting factor WTi in the averaging equations. (Integer > 0)
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.G), self.__cardinfo.G)

    @G.setter
    def G(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.G[i] = val

    @property
    def UM(self) -> str:
        """
           Indicates the start of the degrees-of-freedom belonging to the dependent degrees-of-freedom.The default action is to assign only the components
           in REFC to the dependent degrees-of-freedom. (Character)
        """
        return self.__cardinfo.UM.Value

    @UM.setter
    def UM(self, value: str) -> None:
        self.__cardinfo.UM.Value = value

    @property
    def GM(self) -> list[int]:
        """
           Identification numbers of grid points with degrees-of-freedom in the m-set. (Integer > 0)
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.GM), self.__cardinfo.GM)

    @GM.setter
    def GM(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.GM[i] = val

    @property
    def CM(self) -> list[int]:
        """
           Component numbers of GMi to be assigned to the m-set. (Any of the Integers 1 through 6 with no embedded blanks.)
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.CM), self.__cardinfo.CM)

    @CM.setter
    def CM(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.CM[i] = val

    @property
    def ALPHAC(self) -> str:
        """
           Indicates that the next number is the coefficient of thermal expansion. (Character)
        """
        return self.__cardinfo.ALPHAC.Value

    @ALPHAC.setter
    def ALPHAC(self, value: str) -> None:
        self.__cardinfo.ALPHAC.Value = value

    @property
    def ALPHA(self) -> float:
        """
           Thermal expansion coefficient. See Remark 14. (Real > 0.0 or blank)
           * Remark 13:
           For the Lagrange method, the thermal expansion effect will be computed, if user supplies the thermal expansion coefficient ALPHA, and the thermal
           load is requested by the TEMPERATURE(INITIAL) and TEMPERATURE(LOAD) Case Control commands.The temperature of the element is taken as follows:
           the temperature of the bar connecting the reference grid point REFGRID and any other grid point Gij are taken as the
           average temperature of the two connected grid points.
        """
        return self.__cardinfo.ALPHA.Value

    @ALPHA.setter
    def ALPHA(self, value: float) -> None:
        self.__cardinfo.ALPHA.Value = value


class RSPLINE(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (RSPLINE)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def EID(self) -> int:
        """
           Element identification number. (0 < Integer < 100,000,000)
        """
        return self.__cardinfo.EID

    @EID.setter
    def EID(self, value: int) -> None:
        self.__cardinfo.EID = value

    @property
    def DL(self) -> float:
        """
           Ratio of the diameter of the elastic tube to the sum of the lengths of all segments. (Real > 0.0; Default = 0.1)
        """
        return self.__cardinfo.DL

    @DL.setter
    def DL(self, value: float) -> None:
        self.__cardinfo.DL = value

    @property
    def G(self) -> list[int]:
        """
           Grid point identification number. (Integer > 0)
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.G), self.__cardinfo.G)

    @G.setter
    def G(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.G[i] = val

    @property
    def C(self) -> list[int]:
        """
           Components to be constrained. See Remark 2. (Blank or any combination of the Integers 1 through 6.)
           * Remark 2:
           A blank field for Ci indicates that all six degrees-of-freedom at Gi are independent.Since G1 must be independent, no field is provided for C1.
           Since the last grid point must also be independent, the last field must be a Gi, not a Ci.For the example shown G1, G3, and G6 are independent.G2 has
           six constrained degrees-of-freedom while G4 and G5 each have three.
        """
        return IndexTrackingList((ite.Value for ite in self.__cardinfo.C), self.__cardinfo.C)

    @C.setter
    def C(self, value: list[int]) -> None:
        if len(value) != len(self.__cardinfo.MIDi):
            N2PLog.Error.E400()
        else:
            for i, val in enumerate(value):
                self.__cardinfo.C[i] = val


class SPC(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (SPC)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def SID(self) -> int:
        """
           Identification number of the single-point constraint set
        """
        return self.__cardinfo.SID

    @SID.setter
    def SID(self, value: int) -> None:
        self.__cardinfo.SID = value

    @property
    def G1(self) -> int:
        """
           Grid point identification number of connection points. (Integer > 0)
           GA
        """
        return self.__cardinfo.G1

    @G1.setter
    def G1(self, value: int) -> None:
        self.__cardinfo.G1 = value

    @property
    def C1(self) -> int:
        """
           C1
        """
        return self.__cardinfo.C1

    @C1.setter
    def C1(self, value: int) -> None:
        self.__cardinfo.C1 = value


    @property
    def D1(self) -> float:
        """
           D1: enforced motion for components C1 at G1
        """
        return self.__cardinfo.D1

    @D1.setter
    def D1(self, value: float) -> None:
        self.__cardinfo.D1 = value

    @property
    def G2(self) -> int:
        """
           Grid point identification number of connection points. (Integer > 0)
           GA
        """
        return self.__cardinfo.G2

    @G2.setter
    def G2(self, value: int) -> None:
        self.__cardinfo.G2 = value

    @property
    def C2(self) -> int:
        """
           C2
        """
        return self.__cardinfo.C2

    @C2.setter
    def C2(self, value: int) -> None:
        self.__cardinfo.C2 = value


    @property
    def D2(self) -> float:
        """
           D2: enforced motion for components C2 at G2
        """
        return self.__cardinfo.D2

    @D2.setter
    def D2(self, value: float) -> None:
        self.__cardinfo.D2 = value


class SPC1(N2PCard):

    def __init__(self, cardinfo):
        super().__init__(cardinfo)
        self.__cardinfo = cardinfo

    @property
    def CharName(self) -> str:
        """
           Card code (SPC1)
        """
        return self.__cardinfo.CharName

    @CharName.setter
    def CharName(self, value: str) -> None:
        self.__cardinfo.CharName = value

    @property
    def SID(self) -> int:
        """
           Identification number of the single-point constraint set
        """
        return self.__cardinfo.SID

    @SID.setter
    def SID(self, value: int) -> None:
        self.__cardinfo.SID = value

    @property
    def C(self) -> int:
        """
           Component numbers: 123456
        """
        return self.__cardinfo.C

    @C.setter
    def C(self, value: int) -> None:
        self.__cardinfo.C = value


    @property
    def Grids(self) -> list[int, ...]:
        """
           Grid or scalar point identification numbers
        """
        return self.__cardinfo.NodeArray

    @C.setter
    def Grids(self, value: list[int, ...]) -> None:
        self.__cardinfo.NodeArray = value

# Diccionario con todas clases.
CONSTRUCTDICT = {"CBAR": CBAR,
                 "CBEAM": CBEAM,
                 "CBUSH": CBUSH,
                 "CELAS1": CELAS1,
                 "CELAS2": CELAS2,
                 "CELAS3": CELAS3,
                 "CELAS4": CELAS4,
                 "CFAST": CFAST,
                 "CHEXA_NASTRAN": CHEXANAS,
                 "CHEXA_OPTISTRUCT": CHEXAOPT,
                 "CONM2": CONM2,
                 "CORD1C": CORD1C,
                 "CORD1R": CORD1R,
                 "CORD1S": CORD1S,
                 "CORD2C": CORD2C,
                 "CORD2R": CORD2R,
                 "CORD2S": CORD2S,
                 "CPENTA_NASTRAN": CPENTANAS,
                 "CPENTA_OPTISTRUCT": CPENTAOPT,
                 "CPYRA": CPYRA,
                 "CQUAD4": CQUAD4,
                 "CQUAD8": CQUAD8,
                 "CROD": CROD,
                 "CSHEAR": CSHEAR,
                 "CTETRA_NASTRAN": CTETRANAS,
                 "CTETRA_OPTISTRUCT": CTETRAOPT,
                 "CTRIA3": CTRIA3,
                 "CTRIA6": CTRIA6,
                 "CWELD": CWELD,
                 "GRID": GRID,
                 "MAT10_NASTRAN": MAT10NAS,
                 "MAT10_OPTISTRUCT": MAT10OPT,
                 "MAT1_NASTRAN": MAT1NAS,
                 "MAT1_OPTISTRUCT": MAT1OPT,
                 "MAT2_NASTRAN": MAT2NAS,
                 "MAT2_OPTISTRUCT": MAT2OPT,
                 "MAT3": MAT3,
                 "MAT4": MAT4,
                 "MAT5": MAT5,
                 "MAT8": MAT8,
                 "MAT9_NASTRAN": MAT9NAS,
                 "MAT9_OPTISTRUCT": MAT9OPT,
                 "MPC": MPC,
                 "PBAR": PBAR,
                 "PBARL": PBARL,
                 "PBEAM": PBEAM,
                 "PBEAML": PBEAML,
                 "PBUSH_NASTRAN": PBUSHNAS,
                 "PBUSH_OPTISTRUCT": PBUSHOPT,
                 "PCOMP_NASTRAN": PCOMPNAS,
                 "PCOMP_OPTISTRUCT": PCOMPOPT,
                 "PELAS": PELAS,
                 "PFAST": PFAST,
                 "PLOTEL": PLOTEL,
                 "PLPLANE": PLPLANE,
                 "PMASS": PMASS,
                 "PROD": PROD,
                 "PSHEAR": PSHEAR,
                 "PSHELL_NASTRAN": PSHELLNAS,
                 "PSHELL_OPTISTRUCT": PSHELLOPT,
                 "PSOLID_NASTRAN": PSOLIDNAS,
                 "PSOLID_OPTISTRUCT": PSOLIDOPT,
                 "PWELD": PWELD,
                 "RBAR": RBAR,
                 "RBAR1": RBAR1,
                 "RBE1": RBE1,
                 "RBE2": RBE2,
                 "RBE3": RBE3,
                 "RSPLINE": RSPLINE,
                 "SPC": SPC,
                 "SPC1": SPC1,
                 "UNSUPPORTED": N2PCard
                 }