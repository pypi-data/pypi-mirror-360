import numpy as np
from NaxToPy import N2PLog
from typing import Literal 

class DataEntry:

    # DataEntry constructor --------------------------------------------------------------------------------------------
    def __init__(self):

        """
        Class that represents a single entry into a dataset. 

        Attributes: 
            results: str = "RESULTS" -> type of results to be exported. 
            loadcase: int -> load case ID. 
            increment: int = 1 -> increment ID. By default, it is set to 1 (in case that there are no increments)
            section: str = "None" -> section where the results are obtained. By default, it is set to "None" (in case
            that there are no, or only one, sections). 
            data: np.ndarray -> Numpy array which includes both the results to be exported, and their datatypes. It 
            must be written in a manner similar to this: 
                >>> data = np.array([(1, -0.243, 11.658), (2, 0.0, 613.2)], 
                                    np.dtype([("ID", "i4"), ("VALUE 1", "f4"), ("VALUE 2", "f8")]))
            Note that the datatype must include the name of the value (which will be the header of the column of the 
            dataset), the type of data (i for integer and f for float) and its precision (4 for 32 bits and 8 for 64 
            bits).
        """
        
        self._results_name: str = "RESULTS" 
        self._results_name_description: str = "RESULTS"
        self._results_name_type: str = "ELEMENTS"
        self._loadcase: int = None 
        self._loadcase_description: str = "LOAD CASE"
        self._loadcase_name: str = None
        self._increment: int = 1 
        self._increment_description: str = "INCREMENT"
        self._increment_value: float = 0.0 
        self._section: str = "None"
        self._section_description: str = "SECTION"
        self._part: str = None 
        self._data: np.ndarray = None
        self._data_input: np.ndarray = None
        self._data_input_name: str = None
        self._data_description: str = "Data"
    
    # Getters ----------------------------------------------------------------------------------------------------------
    # Method to obtain the Results type --------------------------------------------------------------------------------
    @property 
    def ResultsName (self) -> str: 

        """
        Returns the type of results.
        """

        return self._results_name 
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Results description -------------------------------------------------------------------------
    @property 
    def ResultsNameDescription (self) -> str: 

        """
        Returns the description of the results.
        """

        return self._results_name_description
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Results type --------------------------------------------------------------------------------
    @property 
    def ResultsNameType (self) -> Literal["ELEMENTS", "ELEMENT_NODES", "NODES"]: 

        """
        Returns the type of results.
        """

        return self._results_name_type 
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Load Case -----------------------------------------------------------------------------------
    @property
    def LoadCase (self) -> int:

        """
        Returns the Load Case ID.
        """

        return self._loadcase
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Load Case description -----------------------------------------------------------------------
    @property
    def LoadCaseDescription (self) -> str:

        """
        Returns the Load Case description. 
        """

        return self._loadcase_description
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Increment -----------------------------------------------------------------------------------
    @property
    def Increment (self) -> int:

        """
        Returns the Increment ID. 
        """

        return self._increment
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Increment Description -----------------------------------------------------------------------
    @property
    def IncrementDescription (self) -> str:

        """
        Returns the Increment description. 
        """

        return self._increment_description
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Increment Value -----------------------------------------------------------------------------
    @property
    def IncrementValue (self) -> float:

        """
        Returns the Increment value. 
        """

        return self._increment_value 
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Section -------------------------------------------------------------------------------------
    @property
    def Section (self) -> str:

        """
        Returns the Section
        """

        return self._section
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Section Description -------------------------------------------------------------------------
    @property
    def SectionDescription (self) -> str:

        """
        Returns the Section Description 
        """

        return self._section_description
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Part Name -----------------------------------------------------------------------------------
    @property
    def Part (self) -> str:

        """
        Returns the part name. 
        """

        return self._part
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Data ----------------------------------------------------------------------------------------
    @property
    def Data (self) -> np.ndarray:

        """
        Returns the numpy array of the data
        """

        return self._data
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Data ----------------------------------------------------------------------------------------
    @property
    def DataInput (self) -> np.ndarray:

        """
        Returns the numpy array of the data input
        """

        return self._data_input
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Data ----------------------------------------------------------------------------------------
    @property
    def DataInputName (self) -> str:

        """
        Returns the data Input name. 
        """

        return self._data_input_name
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Data ----------------------------------------------------------------------------------------
    @property
    def DataDescription (self) -> str:

        """
        Returns the data description. 
        """

        return self._data_description
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the LoadCase Name -------------------------------------------------------------------------------
    @property
    def LoadCaseName(self) -> str:
        """
        Returns the Load Case Name
        """

        return self._loadcase_name
    #-------------------------------------------------------------------------------------------------------------------



    # Setters ----------------------------------------------------------------------------------------------------------
    @ResultsName.setter 
    def ResultsName(self, value: str) -> None: 
        if type(value) == str: 
            self._results_name = value 
        else: 
            N2PLog.Warning.W527(value, str)
    # ------------------------------------------------------------------------------------------------------------------

    @ResultsNameDescription.setter 
    def ResultsNameDescription(self, value: str) -> None: 
        if type(value) == str: 
            self._results_name_description = value 
        else: 
            N2PLog.Warning.W527(value, str)
    # ------------------------------------------------------------------------------------------------------------------

    @ResultsNameType.setter 
    def ResultsNameType(self, value: Literal["ELEMENTS", "ELEMENT_NODES", "NODES"]) -> None: 
        if type(value) == str: 
            if value == "ELEMENTS" or value == "ELEMENT_NODES" or value == "NODES": 
                self._results_name_type = value 
            else: 
                N2PLog.Warning.W701(value) 
        else: 
            N2PLog.Warning.W527(value, str)
    # ------------------------------------------------------------------------------------------------------------------

    @LoadCase.setter
    def LoadCase(self, value: int) -> None:
        if type(value) == int: 
            self._loadcase = value 
        else: 
            N2PLog.Error.E535(value, int)
    # ------------------------------------------------------------------------------------------------------------------

    @LoadCaseDescription.setter
    def LoadCaseDescription(self, value: str) -> None:
        if type(value) == str: 
            self._loadcase_description = value 
        else: 
            N2PLog.Error.E535(value, str)
    # ------------------------------------------------------------------------------------------------------------------

    @Increment.setter
    def Increment(self, value: int) -> None:
        if type(value) == int: 
            self._increment = value 
        else: 
            N2PLog.Warning.W527(value, int)
    # ------------------------------------------------------------------------------------------------------------------

    @IncrementDescription.setter
    def IncrementDescription(self, value: str) -> None:
        if type(value) == str: 
            self._increment_description = value 
        else: 
            N2PLog.Error.E535(value, str)
    # ------------------------------------------------------------------------------------------------------------------

    @IncrementValue.setter
    def IncrementValue(self, value: float) -> None:
        if type(value) == float: 
            self._increment_value = value 
        else: 
            N2PLog.Error.E535(value, float)
    # ------------------------------------------------------------------------------------------------------------------

    @Section.setter
    def Section(self, value: str) -> None:
        if type(value) == str: 
            self._section = value 
        else: 
            N2PLog.Error.E535(value, str)
    # ------------------------------------------------------------------------------------------------------------------

    @SectionDescription.setter
    def SectionDescription(self, value: str) -> None:
        if type(value) == str: 
            self._section_description = value 
        else: 
            N2PLog.Error.E535(value, str)
    # ------------------------------------------------------------------------------------------------------------------

    @Part.setter
    def Part(self, value: str) -> None:
        if type(value) == str: 
            self._part = value 
        else: 
            N2PLog.Error.E535(value, str)
    # ------------------------------------------------------------------------------------------------------------------

    @Data.setter
    def Data(self, value: np.ndarray) -> None:
        if type(value) == np.ndarray: 
            numpyIntegers = [np.int8, np.int16, np.int32, np.int64]
            for i in value: 
                if type(i[0]) in numpyIntegers: 
                    self._data = value 
                else: 
                    N2PLog.Error.E537()
        else: 
            N2PLog.Error.E535(value, np.ndarray)
    # ------------------------------------------------------------------------------------------------------------------

    @DataInput.setter
    def DataInput(self, value: np.ndarray) -> None:
        self._data_input = value
    # ------------------------------------------------------------------------------------------------------------------

    @DataDescription.setter
    def DataDescription(self, value: str) -> None:
        if type(value) == str: 
            self._data_description = value 
        else: 
            N2PLog.Error.E535(value, str)
    # ------------------------------------------------------------------------------------------------------------------

    @DataInputName.setter
    def DataInputName(self, value: str) -> None:
        if type(value) == str: 
            self._data_input_name = value 
        else: 
            N2PLog.Error.E535(value, str)
    # ------------------------------------------------------------------------------------------------------------------

    @LoadCaseName.setter
    def LoadCaseName(self, value: str) -> None:
        if type(value) == str: 
            self._loadcase_name = value 
        else: 
            N2PLog.Error.E535(value, str)
    # ------------------------------------------------------------------------------------------------------------------

