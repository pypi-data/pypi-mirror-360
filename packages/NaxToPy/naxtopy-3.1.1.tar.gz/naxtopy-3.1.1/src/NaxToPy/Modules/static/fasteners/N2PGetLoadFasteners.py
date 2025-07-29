# region Imports 

"""
The N2PGetLoadFasteners class is used to calculate the bearing and bypass loads of a collection of joints. The instance 
of this class must be prepared using the required properties before calling its method calculate(). 
"""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

import csv 
import numpy as np
import os 
import sys 
from time import asctime, gmtime, time
from typing import Literal, Union 

import NaxToPy as NP 
from NaxToPy import N2PLog
from NaxToPy.Core.Constants import Constants
from NaxToPy.Core.N2PModelContent import N2PModelContent 
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core.Classes.N2PLoadCase import N2PLoadCase
from NaxToPy.Modules.common.data_input_hdf5 import DataEntry 
from NaxToPy.Modules.common.hdf5 import HDF5_NaxTo
from NaxToPy.Modules.static.fasteners.N2PGetFasteners import N2PGetFasteners
from NaxToPy.Modules.static.fasteners.joints.N2PJoint import N2PJoint
from NaxToPy.Modules.static.fasteners.joints.N2PPlate import N2PPlate
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysis.Core.Functions.N2PGetResults import get_results  
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysis.Core.Functions.N2PLoadModel import load_reduced_model, \
     import_results

# endregion 
# region GetLoadFasteners

class N2PGetLoadFasteners: 

    """
    The N2PGetLoadFasteners class is used to calculate the bearing and bypass loads of a collection of joints. 

    Properties: 
        BypassResults: str -> path to the .h5 file in which the bypass results have been obtained and are to be loaded.
        ResultsFiles: list[str] -> list of paths to the .op2 or equivalent results files. 
        GetFasteners: N2PGetFasteners -> N2PGetFasteners object with fasteners to be analysed. 
        Model: N2PModelContent -> reduced N2PModelContent object representing the model that is being analysed. 
        JointsList: list[N2PJoint] -> list of N2PJoint objects representing the joints to be anlysed. 
        PlateList: list[N2PPlate] -> list of N2PPlate objects representing the plates to be analysed. 
        LoadCases: list[N2PLoadCase] -> list of N2PLoadCase objects representing the load cases to be analysed. 
        AnalysisName: str -> name of the file that will be exported. 
        ExportLocation: str -> path to the folder in which results will be exported. 
        TypeAnalysis: Literal["PAG", "ALTAIR"] -> type of analysis to be executed. 
        TypeExport: Literal["ALTAIR", "TXT", "CSV", "HDF5", "REDUCED_HDF5"] -> way in which results will be exported. 
        OptionalAttributes: _N2POptionalAttributes: _N2POptionalAttributes object representing all optional attributes 
        that would usually not be modified.
    """

    __slots__ = ("_bypass_results", 
                 "_results_files", 
                 "_get_fasteners", 
                 "_joints_list", 
                 "_plate_list", 
                 "_model", 
                 "_load_cases", 
                 "_analysis_name", 
                 "_export_location", 
                 "_type_analysis", 
                 "_type_export", 
                 "_results", 
                 "_corner_results", 
                 "_optional_attributes", 
                 "_error", 
                 "_new_lc", 
                 "_max_error_counter")

    # N2PGetLoadFasteners constructor ----------------------------------------------------------------------------------
    def __init__(self): 

        """
        The constructor creates an empty N2PGetLoadFasteners instance. Its attributes must be added as properties.

        Calling example: 
            >>> import NaxToPy as NP 
            >>> from NaxToPy.Modules.Fasteners.N2PGetFasteners import N2PGetFasteners
            >>> from NaxToPy.Modules.Fasteners.N2PGetLoadFasteners import N2PGetLoadFasteners
            >>> model1 = NP.get_model(r"route.fem") # model loaded 
            >>> fasteners = N2PGetFasteners() 
            >>> fasteners.Model = model1 # compulsory input 
            >>> fasteners.ElementList = model1.get_elements([10, 11, 12, 13, 14]) # joints to be analysed
            >>> fasteners.calculate() 
            >>> fasteners.assign_diameter(model1.get_elements([10, 11, 12]), 6.0) # Some joints are assigned a certain 
            diameter
            >>> loads = N2PGetLoadFasteners()
            >>> loads.GetFasteners = fasteners # Compulsory input 
            >>> loads.ResultsFiles = [r"route1.op2", r"route2.op2", r"route3.op2"] # The desired results files are 
            loaded
            >>> loads.OptionalAttributes.AdjacencyLevel = 3 # A custom adjacency level is selected (optional)
            >>> loads.LoadCases = loads.Model.get_load_case([1, 2, 133986]) # Only some loadcases are analysed 
            (optional)
            >>> loads.OptionalAttributes.CornerData = True # The previous load cases have corner data (optional)
            >>> # Some bypass parameters are changed (optional and not recommended)
            >>> loads.OptionalAttributes.MaxIterations = 50 
            >>> loads.OptionalAttributes.ProjectionTolerance = 1e-6 
            >>> loads.OptionalAttributes.DefaultDiameter = 3.6 #  Joints with no previously assigned diameter will get 
            this diameter (optional)
            >>> loads.AnalysisName = "Analysis_1" # Name of the file where the results will be exported (optional)
            >>> loads.ExportLocation = r"path" # Results are to be exported to a certain path (optional)
            >>> loads.TypeAnalysis = "PAG" # The analysis will be made in the PAG style (optional)
            >>> loads.TypeExport = "HDF5" # Results will be exported in the PAG HDF5 style (optional)
            >>> loads.OptionalAttributes.ExportPrecision = 8 # Results will be exported to the HDF5 file with double 
            precision 
            >>> loads.OptionalAttributes.CompressionEqualsZero = False # Certain bearing parameters are modified 
            >>> loads.OptionalAttributes.PullThroughAsIs = False 
            >>> loads.OptionalAttributes.ShearAsIs = False 
            >>> loads.calculate() # calculations will be made and results will be exported

        Instead of using loads.GetFasteners, the user could also set these attributes:
            >>> loads.Model = model1 # the same model is loaded, compulsory input 
            >>> loads.JointsList = fasteners.JointsList[0:10] # only a certain amount of joints is loaded, compulsory 
            input 
            >>> loadFasteners.calculate() # calculations will be made with all of the default parameters and, 
            therefore, results will not be exported. 
        """
        
        self._bypass_results: str = None 
        self._results_files: list[str] = None 
        self._get_fasteners: N2PGetFasteners = None 
        self._joints_list: list[N2PJoint] = None 
        self._plate_list: list[N2PPlate] = None 
        self._model: N2PModelContent = None 
        self._load_cases: list[N2PLoadCase] = None 
        self._analysis_name: str = "JointAnalysis"
        self._export_location: str = None 
        self._type_analysis: Literal["ALTAIR", "PAG"] = "PAG"
        self._type_export: Literal["ALTAIR", "TXT", "CSV", "HDF5", "REDUCED_HDF5"] = "TXT"
        self._optional_attributes: _N2POptionalAttributes = _N2POptionalAttributes(self)

        self._results: np.ndarray = None 
        self._corner_results: np.ndarray = None 
        self._error: bool = False 
        self._new_lc = None 
        self._max_error_counter: int = 10
    # ------------------------------------------------------------------------------------------------------------------
    
    # endregion 
    # region Getters 

    # Getters ----------------------------------------------------------------------------------------------------------
    @property 
    def BypassResults(self) -> str: 

        """
        Property that returns the bypass_results attribute, that is, the results obtained from a .h5 file.  
        """

        return self._bypass_results 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def ResultsFiles(self) -> list[str]: 
        """
        Property that returns the results_files attribute, that is, the results files to be analysed.
        """

        return self._results_files
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def GetFasteners(self) -> N2PGetFasteners: 

        """
        Property that returns the get_fasteners attribute, that is, the N2PGetFasteners object from which fasteners are 
        extracted.
        """

        return self._get_fasteners
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def Model(self) -> N2PModelContent: 

        """
        Property that returns the model attribute, that is, the reduced model that is created to do the analysis.
        """

        return self._model 
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def JointsList(self) -> list[N2PJoint]: 

        """
        Property that returns the joints_list attribute, that is, the list of N2PJoints to be analyzed. 
        """

        return self._joints_list
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def PlateList(self) -> list[N2PPlate]: 

        """
        Property that returns the plate_list attribute, that is, the list of N2PPlates to be analyzed. 
        """

        return self._plate_list 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def LoadCases(self) -> list[N2PLoadCase]: 

        """
        Property that returns the load_cases attributes, that is, the list of the load cases to be analyzed. 
        """
        
        return self._load_cases 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def AnalysisName(self) -> str: 

        """
        Property that returns the analysis_name attribute, that is, the name of the file in which results will be 
        extracted.
        """
        
        return self._analysis_name
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def ExportLocation(self) -> str: 

        """
        Property that returns the export_location attribute, that is, the path in which the results files will be 
        created. 
        """
        
        return self._export_location
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def TypeAnalysis(self) -> Literal["ALTAIR", "PAG"]: 

        """
        Property that returns the path where the type_analysis attribute, that is, whether the results are analyzed in 
        the Altair or PAG style. 
        """
        
        return self._type_analysis
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def TypeExport(self) -> Literal["ALTAIR", "TXT", "CSV", "HDF5", "REDUCED_HDF5"]: 

        """
        Property that returns the path where the type_export attribute, that is, whether the results are exported in 
        a txt, csv, or h5 file. 
        """
        
        return self._type_export
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def OptionalAttributes(self): 

        """
        Property that returns the optional_attributes attribute, that is, the class used to insert the optional 
        attributes.
        """
        
        return self._optional_attributes
    # ------------------------------------------------------------------------------------------------------------------

    # endregion 
    # region Setters 

    # Setters ----------------------------------------------------------------------------------------------------------
    @BypassResults.setter 
    def BypassResults(self, value: str): 

        if os.path.exists(value) and os.path.isfile(value): 
            self._bypass_results = value 
            if self.JointsList and self.Model: 
                self._model.import_results_from_files(self.BypassResults)
        else:
            self._error = True 
            N2PLog.Error.E524(value)
            return None            
    # ------------------------------------------------------------------------------------------------------------------

    @ResultsFiles.setter 
    def ResultsFiles(self, value: Union[list[str], str]): 

        # If "value" is a list, then it must be a list of op2 files. 
        if type(value) == list: 
            for i in value: 
                if not os.path.exists(i) or not os.path.isfile(i): 
                    self._error = True 
                    N2PLog.Error.E524(i)
                    return None 
            self._results_files = value 
        elif os.path.exists(value): 
            # If "value" is a string and a file, it is a single op2 file. 
            if os.path.isfile(value): 
                self._results_files = [value]
            # If "value" is a string and not a file, it is a folder. 
            else: 
                self._results_files = import_results(value) 
        else: 
            self._error = True 
            N2PLog.Error.E524(value)
            return None 

        if self.JointsList and self.Model: 
            self.__create_model() 
    # ------------------------------------------------------------------------------------------------------------------

    @GetFasteners.setter 
    def GetFasteners(self, value: N2PGetFasteners) -> None: 

        if not isinstance(value, N2PGetFasteners): 
            N2PLog.Warning.W527(value, N2PGetFasteners)

        if self.Model is not None or self.JointsList is not None: 
            N2PLog.Warning.W522() 

        self._get_fasteners = value 
        self._joints_list = self._get_fasteners._joints_list
        self._model = self._get_fasteners._model 
        self._plate_list = self.GetFasteners.PlateList
        if self.ResultsFiles: 
            self.__create_model() 
        elif self.BypassResults: 
            self._model.import_results_from_files(self.BypassResults)
    # ------------------------------------------------------------------------------------------------------------------

    @Model.setter 
    def Model(self, value: N2PModelContent) -> None: 

        if not isinstance(value, N2PModelContent): 
            N2PLog.Warning.W527(value, N2PModelContent)

        if self.GetFasteners is not None: 
            N2PLog.Warning.W523() 

        self._model = value 
        if self.JointsList and self.ResultsFiles: 
            self.__create_model() 
        elif self.JointsList and self.BypassResults: 
            self._model.import_results_from_files(self.BypassResults)
    # ------------------------------------------------------------------------------------------------------------------
        
    @JointsList.setter 
    def JointsList(self, value: Union[list[N2PJoint], tuple[N2PJoint], set[N2PJoint], N2PJoint]) -> None: 

        if self.GetFasteners is not None: 
            N2PLog.Warning.W524() 

        if type(value) == tuple or type(value) == set: 
            value = list(value) 
        elif type(value) == N2PJoint: 
            value = [value]

        errorCounter = 0 
        for i in value: 
            if not isinstance(i, N2PJoint): 
                errorCounter = errorCounter + 1 
                if errorCounter == self._max_error_counter: 
                    N2PLog.Warning.W546(527)
                    N2PLog.set_console_level("ERROR")
                N2PLog.Warning.W527(i, N2PJoint)
                value.remove(i)

        N2PLog.set_console_level("WARNING")
        if value == []: 
            N2PLog.Warning.W534("JointsList", N2PJoint)
        else: 
            self._joints_list = value 
            self._plate_list = [plate for joint in self.JointsList for plate in joint.PlateList]
    # ------------------------------------------------------------------------------------------------------------------
        
    @LoadCases.setter 
    def LoadCases(self, value: Union[list[N2PLoadCase], tuple[N2PLoadCase], set[N2PLoadCase], N2PLoadCase]) -> None: 

        if type(value) == tuple or type(value) == set: 
            value = list(value) 
        elif type(value) == N2PLoadCase: 
            value = [value]

        errorCounter = 0 
        for i in value: 
            if not isinstance(i, N2PLoadCase): 
                errorCounter = errorCounter + 1 
                if errorCounter == self._max_error_counter: 
                    N2PLog.Warning.W546(527)
                    N2PLog.set_console_level("ERROR")
                N2PLog.Warning.W527(i, N2PLoadCase)
                value.remove(i)
        
        N2PLog.set_console_level("WARNING")
        if value == []: 
            N2PLog.Warning.W534("LoadCases", N2PLoadCase)
        else: 
            self._load_cases = value
    # ------------------------------------------------------------------------------------------------------------------
        
    @AnalysisName.setter 
    def AnalysisName(self, value: str) -> None: 

        if not isinstance(value, str): 
            N2PLog.Warning.W527(value, str)
        else: 
            self._analysis_name = value 
    # ------------------------------------------------------------------------------------------------------------------

    @ExportLocation.setter 
    def ExportLocation(self, value: str) -> None: 

        if not isinstance(value, str): 
            N2PLog.Warning.W527(value, str)
        elif not os.path.exists(value) or not os.path.isdir(value): 
            N2PLog.Warning.W547()
        else: 
            self._export_location = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @TypeAnalysis.setter 
    def TypeAnalysis(self, value: Literal["ALTAIR", "PAG"]) -> None: 

        if not isinstance(value, str): 
            N2PLog.Warning.W527(value, str)
        else: 
            value = value.upper().replace(" ", "")
            if value == "ALTAIR" or value == "PAG": 
                self._type_analysis = value 
            else: 
                N2PLog.Warning.W525()
    # ------------------------------------------------------------------------------------------------------------------

    @TypeExport.setter 
    def TypeExport(self, value: Literal["ALTAIR", "TXT", "CSV", "HDF5", "REDUCED_HDF5"]) -> None: 

        if not isinstance(value, str): 
            N2PLog.Warning.W527(value, str)
        else: 
            value = value.upper().replace(" ", "")
            acceptedValues = ["ALTAIR", "TXT", "CSV", "HDF5", "REDUCED_HDF5"]
            if value in acceptedValues: 
                self._type_export = value 
            else: 
                N2PLog.Warning.W525()
    # ------------------------------------------------------------------------------------------------------------------
        
    # endregion 
    # region Public methods 

    # Method used to create the bypass box -----------------------------------------------------------------------------
    def get_bypass_box(self): 

        """
        Method used to obtain the bypass box and to know what elements to ask results for. Also, if no load cases have 
        been selected, all of them are. 

        Calling example: 
            >>> loads.get_bypass_box() 
        """

        t1 = time()

        if self.Model is None: 
            self._error = True 
            N2PLog.Error.E521() 
            return None 
        if self.JointsList is None: 
            self._error = True 
            N2PLog.Error.E523() 
            return None 

        # The diameter that is assigned to fasteners is, in the following order: 
        # - If a diameter has been manually assigned, either using the assign_diameter() method in N2PGetFasteners or 
        # manually, this value is used. 
        # - If the fastener's card has a diameter attribute, this value is used. 
        # - If the DefaultDiameter attribute has been set, this value is used. 
        # - Otherwise, no diameter is used and the joint is removed from the list. 
        for i in self.JointsList: 
            if i.Diameter is None: 
                try: 
                    i._diameter = self.Model.PropertyDict[i.Bolt.ElementList[0].Prop].Diameter
                except: 
                    if self.OptionalAttributes.DefaultDiameter: 
                        i._diameter = self.OptionalAttributes.DefaultDiameter
        
        # Joints with no diameter are identified and removed 
        wrongJoints = {i for i in self.JointsList if i.Diameter is None or i.Diameter <= 0}
        wrongJointsID = {i.ID for i in wrongJoints}
        if len(wrongJointsID) > 0: 
            N2PLog.Warning.W535(wrongJointsID)
        for i in self.JointsList: 
            if i in wrongJoints: 
                self._joints_list.remove(i)
                for p in i.PlateList: 
                    self._plate_list.remove(p)

        errorCounter = 0 
        for i in self.PlateList: 
            if not i.Intersection: 
                errorCounter = errorCounter + 1
                if errorCounter == self._max_error_counter: 
                    N2PLog.Warning.W546(530)
                    N2PLog.set_console_level("ERROR")
                N2PLog.Warning.W530(i) 
                i._error = True 
                continue 
            elif not i.Normal: 
                errorCounter = errorCounter + 1
                if errorCounter == self._max_error_counter: 
                    N2PLog.Warning.W546(521)
                    N2PLog.set_console_level("ERROR")
                N2PLog.Warning.W521(i) 
                i._error = True 
                continue
            elif not i.ElementList or len(i.ElementList) == 0: 
                errorCounter = errorCounter + 1
                if errorCounter == self._max_error_counter: 
                    N2PLog.Warning.W546(512)
                    N2PLog.set_console_level("ERROR")
                N2PLog.Warning.W512(i, i.Joint)
                i._error = True 
                continue
            else: 
                if self.Model.PropertyDict.get(i.ElementList[0].Prop).PropertyType == "PCOMP": 
                    materialFactor = self.OptionalAttributes.MaterialFactorComposite
                else: 
                    materialFactor = self.OptionalAttributes.MaterialFactorMetal

                errorCounter = i.get_bypass_box(self.Model, materialFactor, self.OptionalAttributes.AreaFactor, 
                                                self.OptionalAttributes.MaxIterations, 
                                                self.OptionalAttributes.ProjectionTolerance, errorCounter, 
                                                self._max_error_counter)
        N2PLog.set_console_level("WARNING")
        # If no load cases have been selected, all of them are 
        if self.LoadCases == [] or not self.LoadCases: 
            self._load_cases = self.Model.LoadCases 
            N2PLog.Info.I500()
        if self.LoadCases is None or self.LoadCases == []: 
            self._error = True 
            N2PLog.Error.E504()
            return None 

        t2 = time() 
        N2PLog.Debug.D600(t2, t1)
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to obtain the load cases' results --------------------------------------------------------------------
    def get_results(self, loadCaseList: list[N2PLoadCase] = None): 

        """
        Method used to obtain the results of the model. 

        The following steps are followed: 
        
            1. Results are obtained with the get_results() function. Its outputs are, (a), the results per se, (b), the 
            results in the corners, in case that it has been asked, and (c), the list of broken load cases, that is, 
            the list of load cases that lack an important result. 
            2. If there are some broken load cases, they are removed from the _load_cases attribute and. If all load 
            cases were broken (meaning that the current _load_cases attribute is empty), an error is displayed. 

        Args: 
            loadCaseList: list[N2PLoadCase] -> load cases to be analysed 

        Calling example: 
            >>> loads.get_results(loads.LoadCases[0:10])
        """

        t1 = time() 
        if self.Model is None: 
            self._error = True 
            N2PLog.Error.E521() 
            return None 
        if self.JointsList is None: 
            self._error = True 
            N2PLog.Error.E523() 
            return None 
        if self.ResultsFiles is None: 
            self._error = True 
            N2PLog.Error.E522() 
            return None 
        if self.JointsList[0].PlateList[0].BoxElements == {}: 
            N2PLog.Warning.W536()
            self.get_bypass_box()

        self._new_lc = None 

        if self.OptionalAttributes.LoadSecondModel: 
            boltList = [k for j in self.JointsList for k in j.BoltElementList]
            plateList = [p.CentralElement for p in self.PlateList]
            boxElements = [k for p in self.PlateList for k in p.BoxElements.values()]
            boxElementsAdjacent = self.Model.get_elements_adjacent(boxElements)
            self.__create_model_2(list(set(boltList + plateList + boxElementsAdjacent)))
            self.OptionalAttributes.LoadSecondModel = False 
            if loadCaseList: 
                loadCaseList = self.Model.get_load_case([k.ID for k in loadCaseList])

        # Results and broken load cases are obtained 
        if not loadCaseList: 
            loadCaseList = self.LoadCases 
        resultsList = get_results(self.Model, loadCaseList, self.OptionalAttributes.CornerData)
        if resultsList is None: 
            self._error = True 
            return None 
        self._results = resultsList[0]
        self._corner_results = resultsList[1]
        brokenLC = resultsList[2]
        # Broken load cases are removed 
        if len(brokenLC) != 0: 
            N2PLog.Warning.W545(brokenLC)
            for i in brokenLC: 
                loadCaseList.remove(i) 
                self._load_cases.remove(i)
            self._new_lc = loadCaseList 
        # If all load cases are broken, an error occurs 
        if self.LoadCases is None or self.LoadCases == []: 
            self._error = True 
            N2PLog.Error.E519()
        t2 = time() 
        N2PLog.Debug.D600(t2, t1)
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to obtain the results from a h5 file -----------------------------------------------------------------
    def get_results_h5(self, loadCaseList: list[N2PLoadCase] = None): 

        """
        Method used to obtain the results of the model from a .h5 file and assign them to plates and bolts. 

        Args: 
            loadCaseList: list[N2PLoadCase] -> load cases to be analysed 

        Calling example: 
            >>> loads.get_results_h5(loads.LoadCases[0:10])
        """

        if not loadCaseList: 
            loadCaseList = self.LoadCases 
        components = ["BYPASS FLUX NXX", "BYPASS FLUX NYY", "BYPASS FLUX NXY", "X BEARING FORCE", "Y BEARING FORCE", 
                      "PULLTHROUGH FORCE", "BOLT TENSION"] 

        lclist = [(i, i.ActiveN2PIncrement) for i in loadCaseList]
        extractedForces = self.Model.get_result_by_LCs_Incr(lclist, "FASTENER ANALYSIS", components)
        results = np.array([[extractedForces[i[0].ID, i[1].ID, j] for j in components] for i in lclist])
        for plate in self.PlateList: 
            iid = plate.CentralElement.InternalID 
            if plate.BoltElementList["A"] and not plate.BoltElementList["B"]: 
                boltID = plate.BoltElementList["A"].ID 
            elif not plate.BoltElementList["A"] and plate.BoltElementList["B"]: 
                boltID = plate.BoltElementList["B"].ID 
            else: 
                boltID = -1 
            for i, comp in enumerate(results): 
                lcid = loadCaseList[i].ID 
                plate._nx_bypass[lcid] = comp[0][iid]
                plate._ny_bypass[lcid] = comp[1][iid]
                plate._nxy_bypass[lcid] = comp[2][iid]
                plate._bearing_force[lcid] = np.array([comp[3][iid], comp[4][iid], comp[5][iid]])
                if boltID != -1: 
                    if not plate.Bolt._axial_force.get(lcid): 
                        plate.Bolt._axial_force[lcid] = {} 
                    plate.Bolt._axial_force[lcid][boltID] = comp[6][iid]
        self.Model.clear_results_memory()
    # ------------------------------------------------------------------------------------------------------------------
        
    # Method used to obtain the joint's forces -------------------------------------------------------------------------
    def get_forces(self, loadCaseList: list[N2PLoadCase] = None): 
        
        """
        Method used to obtain the 1D forces of each joint. In order to work, the results attribute must have been 
        previously filled (by having called get_results()). If it has not, an error will occur. 

        Args: 
            loadCaseList: list[N2PLoadCase] -> load cases to be analysed 

        Calling example: 
            >>> loads.get_forces(loads.LoadCases[0:10])
        """

        t1 = time() 
        if self._results is None: 
            N2PLog.Warning.W539() 
            self.get_results(loadCaseList)

        if not loadCaseList: 
            loadCaseList = self.LoadCases
        for j in self.JointsList: 
            j.get_forces(self._results, loadCaseList, self.OptionalAttributes.CompressionEqualsZero, 
                         self.OptionalAttributes.PullThroughAsIs, self.OptionalAttributes.ShearAsIs, self.TypeAnalysis)
        t2 = time() 
        N2PLog.Debug.D606(t2, t1)
    # ------------------------------------------------------------------------------------------------------------------
        
    # Method used to obtain the joint's bypass loads -------------------------------------------------------------------    
    def get_bypass_loads(self, loadCaseList: list[N2PLoadCase] = None): 

        """
        Method used to obtain the bypass loads of each joint. If an N2PJoint has no diameter, the default diameter is 
        assigned (in case it has been defined by the user). In order to work, the results attribute must have been 
        previously filled (by having called get_results_joints()). If it has not, an error will occur. 

        Args: 
            loadCaseList: list[N2PLoadCase] -> load cases to be analysed 

        Calling example: 
            >>> loads.get_bypass_loads(loads.LoadCases[0:10])
        """

        t1 = time()
        if self._results is None: 
            N2PLog.Warning.W539() 
            self.get_results(loadCaseList)

        errorCounter = 0 
        if not loadCaseList: 
            loadCaseList = self.LoadCases

        for i in self.PlateList: 
            if i._error: 
                i._box_dimension = np.nan 
                i._box_points = {j+1: np.array([np.nan, np.nan, np.nan]) for j in range(9)}
                i._box_elements = {j+1: i.CentralElement for j in range(9)}
                i._box_fluxes = {lc.ID: {j+1: [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan] 
                for j in range(8)} for lc in loadCaseList}
                i._nx_bypass = i._ny_bypass = i._nxy_bypass = i._nx_total = i._ny_total = i._nxy_total = i._mx_total = \
                i._my_total = i._mxy_total = i._bypass_max = i._bypass_min = {lc.ID: np.nan for lc in loadCaseList}
                aux1 = [np.nan, np.nan, np.nan, np.nan]
                aux2 = [aux1, aux1, aux1, aux1, aux1, aux1]
                i._bypass_sides = {lc.ID: aux2 for lc in loadCaseList}
            else: 
                if self.OptionalAttributes.CornerData: 
                    results = self._corner_results 
                else: 
                    results = self._results 
                errorCounter = i.get_bypass_loads(self.Model, results, loadCaseList, 
                                                  self.OptionalAttributes.CornerData, self.TypeAnalysis, 
                                                  self.OptionalAttributes.ProjectionTolerance, errorCounter, 
                                                  self._max_error_counter)

        N2PLog.set_console_level("WARNING")
        t2 = time() 
        N2PLog.Debug.D607(t2, t1)
    # ------------------------------------------------------------------------------------------------------------------
        
    # Method used to export the obtained results to a CSV file ---------------------------------------------------------
    def export_results(self): 

        """
        Method used to export the obtained results to a CSV file. 

        Calling example: 
            >>> loads.export_results()
        """

        t1 = time()
        if self.JointsList[0].PlateList[0].BearingForce == {}:  
            N2PLog.Warning.W537() 
            self.get_forces()
        elif self.JointsList[0].PlateList[0].NxBypass == {}: 
            N2PLog.Warning.W538()
            self.get_bypass_loads()
        if self.TypeExport == "TXT": 
            self.__export_txt()
        elif self.TypeExport == "HDF5" or self.TypeExport == "REDUCED_HDF5": 
            self.__export_hdf5() 
        else: 
            self.__export_csv() 
        t2 = time() 
        N2PLog.Debug.D608(t2, t1)
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to obtain the main fastener analysis -----------------------------------------------------------------
    def get_analysis(self, loadCaseList: list[N2PLoadCase] = None): 

        """
        Method used to do the previous analysis and, optionally, export the results. 

        Args: 
            loadCaseList: list[N2PLoadCase] -> load cases to be analysed 

        Calling example: 
            >>> loads.get_analysis(loads.LoadCases[0:10])
        """

        t1 = time()
        if not loadCaseList: 
            loadCaseList = self.LoadCases 
        if self._error: 
            return None 
        self.get_forces(loadCaseList) 
        if self._error: 
            return None 
        self.get_bypass_loads(loadCaseList)
        if self._error: 
            return None 
        N2PLog.Debug.D602(time(), t1)
    # ------------------------------------------------------------------------------------------------------------------
    
    # Method used to do the entire analysis ----------------------------------------------------------------------------
    def calculate(self): 

        """
        Method used to do all the previous calculations and, optionally, export the results. 

        Calling example: 
            >>> loads.calculate()
        """
        
        t1 = time()
        if self._error: 
            return None 
        self.get_bypass_box()
        N = len(self.LoadCases)
        n = self.OptionalAttributes.LoadCaseNumber
        if n == -1: 
            n = N 
        for i in range(N//n): 
            loadCaseList = self.LoadCases[i*n: (i+1)*n]
            self.get_results(loadCaseList) 
            if self._error: 
                return None 
            if self._new_lc: 
                loadCaseList = self._new_lc
            self.get_analysis(loadCaseList)
        if (N//n)*n != N: 
            loadCaseList = self.LoadCases[n*(N//n):N]
            self.get_results(loadCaseList) 
            if self._error: 
                return None 
            if self._new_lc: 
                loadCaseList = self._new_lc
            self.get_analysis(loadCaseList)
        if self.ExportLocation: 
            self.export_results()
        N2PLog.Debug.D604(time(), t1)
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to load results from a .h5 file ----------------------------------------------------------------------
    def load_h5(self): 
        
        """
        Method used to load the results obtained from a previous N2PGetLoadFastener analysis from a .h5 file. 

        Calling example: 
            >>> loads.load_h5()
        """

        t1 = time() 
        if self.Model is None: 
            self._error = True 
            N2PLog.Error.E521() 
            return None 
        if self.JointsList is None: 
            self._error = True 
            N2PLog.Error.E523() 
            return None 
        if not self.BypassResults: 
            self._error = True 
            N2PLog.Error.E522() 
            return None 
        
        if not self.LoadCases: 
            self._load_cases = self.Model.LoadCases 
        N = len(self.LoadCases)
        n = self.OptionalAttributes.LoadCaseNumber 
        if n == -1: 
            n = N 
        for i in range(N//n): 
            loadCaseList = self.LoadCases[i*n: (i+1)*n] 
            self.get_results_h5(loadCaseList) 
        if (N//n)*n != N: 
            loadCaseList = self.LoadCases[n*(N//n): N] 
            self.get_results_h5(loadCaseList) 

        t2 = time() 
        N2PLog.Debug.D600(t2, t1)
    # ------------------------------------------------------------------------------------------------------------------

    # endregion 
    # region Private methods 

    # Method used to sort plates ---------------------------------------------------------------------------------------
    def __sort_plates(self, plateList: list[N2PPlate]) -> None: 

        """
        Method used to sort plates by its central element's ID, so results are exported in order. 

        Args: 
            plateList: list[N2PPlate]

        Calling example: 
            >>> loads.__sort_plates(loads.PlateList) 
        """

        for i in range(1,len(plateList)): 
            key = plateList[i]
            keyID = key.PlateCentralCellSolverID
            j = i - 1 
            while j >= 0 and keyID < plateList[j].PlateCentralCellSolverID: 
                plateList[j+1] = plateList[j]
                j -= 1 
            plateList[j+1] = key 
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to export the obtained PAG results as a txt file -----------------------------------------------------
    def __export_txt(self):
        
        """
            Method used to export the obtained results, if they are in PAG style, in a txt. It works similarly as the other 
            export options but, in order to follow the same methodology as the one followed in PAG, this method cannot be 
            in the N2PJoint file. 

            Calling example: 
                >>> loads.__export_txt() 
            """

        pathComp = f"{self.ExportLocation}\\{self.AnalysisName}_fastpph_comp.txt"
        pathMetal = f"{self.ExportLocation}\\{self.AnalysisName}_fastpph_metal.txt"
        propDict = self.Model.PropertyDict 
        plateList = self.PlateList.copy()

        self.__sort_plates(plateList)

        plateListComp = [plate for plate in plateList if propDict[plate.CentralElement.Prop].PropertyType == "PCOMP"]
        plateListMetal = [plate for plate in plateList if propDict[plate.CentralElement.Prop].PropertyType != "PCOMP"]

        lcList = [i.ID for i in self.LoadCases]
        
        if plateListComp != []: 
            
            t = asctime()
            headers = [
                " Idaero Solutions S.L.  N2PGetLoadFasteners (composite)",
                " ======================================================",
                "",
                "",
                " ======================================",
                "                          SETTING/VALUE",
                " ======================================",
                f"                     Date/Time  {t[11:19]}, {str(gmtime()[2])}-{t[4:7]}-{t[20:24]}",
                f"               NaxToPy Version  {Constants.VERSION}",
                f"                 NaxTo Version  {Constants.NAXTO_VERSION}",
                f"                  BoxDimension  {plateListComp[0].BoxDimension:5.2f}",
                f"         CompressionEqualsZero  {self.OptionalAttributes.CompressionEqualsZero}",
                f"               PullThroughAsIs  {self.OptionalAttributes.PullThroughAsIs}",
                f"                     ShearAsIs  {self.OptionalAttributes.ShearAsIs}",
                f"                 Analysis Type  {self.TypeAnalysis}",
                "  Extraction Coordinate System  Material",
                "                 Material Type  Composite",
                "",
                "",
                "",
                " ================================================",
                "       ELEMENT/CONNECTOR-SYSTEM/EXTRACTION_POINTS",
                " ================================================",
                "               /|               *p7....*p6....*p5   ",
                "              / |               .             .     ",
                "             /  |               .             .     ",
                "            /GA |         GB    .             .     ",
                "            | *=====>=====*     *p8   --->    *p4   ",
                "    CFAST_A |   | CFAST_B       .     mat0°   .     ",
                " *=====<====|=* /               .             .     ",
                " GB         |GA/                .             .     ",
                "            | /                 *p1....*p2....*p3   ",
                "            |/                                      ",
                f"          A/B-ELEM              alen = {plateListComp[0].BoxDimension:5.2f}mm",
                "",
                "",
                " ----------  ----------------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "------------------------------  ------------------------------  ------------------------------  "
                "------------------------------  ------------------------------  ------------------------------  "
                "------------------------------  ------------------------------",
                "   A/B-ELEM      A/B-PROPERTY     CFAST_A     CFAST_B  DIRECTIONS    EXT.ZONE   ELEMENT_1   "
                "ELEMENT_2   ELEMENT_3   ELEMENT_4   ELEMENT_5   ELEMENT_6   ELEMENT_7   ELEMENT_8                  "
                "POINT_1(X,Y,Z)                  POINT_2(X,Y,Z)                  POINT_3(X,Y,Z)                  "
                "POINT_4(X,Y,Z)                  POINT_5(X,Y,Z)                  POINT_6(X,Y,Z)                  "
                "POINT_7(X,Y,Z)                  POINT_8(X,Y,Z)",
                " ----------  ----------------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "------------------------------  ------------------------------  ------------------------------  "
                "------------------------------  ------------------------------  ------------------------------  "
                "------------------------------  ------------------------------"
            ]
            
            fastenerHeader = [
                "",
                " ----------  ----------------  ----------  ----------  ----------  ----------  ----------  "
                "----------  -----------------------",
                "   CFAST-ID    CFAST-PROPERTY     GS-NODE     GA-NODE     GB-NODE      A-ELEM      B-ELEM    "
                "DIAM(mm)  MATERIAL",
                " ----------  ----------------  ----------  ----------  ----------  ----------  ----------  "
                "----------  -----------------------"
            ]
            
            resultsHeader = [
                "",
                " =======",
                " RESULTS",
                " =======",
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ------------  --------------  --------------  -------------- "
                " --------------  --------------",
                "   A/B-ELEM      A/B-PROPERTY                    LOADCASE,SUBCASE  BypassFlux  BypassFlux  "
                "BypassFlux    Xbearing    Ybearing   PullThrough   TotalMomentum   TotalMomentum   TotalMomentum       "
                "BoltShear     BoltTension",
                " ----------  ----------------  ----------------------------------   Nxx(N/mm)   Nyy(N/mm)   "
                "Nxy(N/mm)    Force(N)     Force(N)     Force(N)      Flux_Mxx(N)     Flux_Myy(N)     Flux_Mxy(N)       "
                "Force(N)        Force(N)",
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ------------  --------------  --------------  --------------  "
                "--------------  --------------"
            ]
            
            translationalHeader = [
                "",
                " =============================",
                " TRANSLATIONAL_FASTENER_FORCES",
                " =============================",
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------",
                "   A/B-ELEM      A/B-PROPERTY                    LOADCASE,SUBCASE  ----------     CFAST_A  "
                "----------  ----------     CFAST_B  ----------     CFAST_A     CFAST_B",
                " ----------  ----------------  ----------------------------------   Fxx(N/mm)   Fyy(N/mm)   "
                "Fzz(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fzz(N/mm)   Factor(-)   Factor(-)",
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------"
            ]
            
            forceFluxesHeader = [
                "",
                " ===================================",
                " EXTRACTION_POINT_SHELL_FORCE_FLUXES",
                " ===================================",
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------",
                "   A/B-ELEM      A/B-PROPERTY                    LOADCASE,SUBCASE  ----------     POINT_1  "
                "----------  ----------     POINT_2  ----------  ----------     POINT_3  ----------  ----------     "
                "POINT_4  ----------  ----------     POINT_5  ----------  ----------     POINT_6  ----------  "
                "----------     POINT_7  ----------  ----------     POINT_8  ----------  ----------   AVG_NORTH  "
                "----------  ----------   AVG_SOUTH  ----------  ----------    AVG_WEST  ----------  ----------    "
                "AVG_EAST  ----------  ----------      BYPASS  ----------",
                " ----------  ----------------  ----------------------------------   Fxx(N/mm)   Fyy(N/mm)   "
                "Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   "
                "Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   "
                "Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   "
                "Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   "
                "Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)",
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------"
            ]
            
            momentFluxesHeader = [
                "",
                " ======================================",
                " EXTRACTION_POINT_SHELL_MOMENTUM_FLUXES",
                " ======================================",
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------",
                "   A/B-ELEM      A/B-PROPERTY                    LOADCASE,SUBCASE  ----------     POINT_1  "
                "----------  ----------     POINT_2  ----------  ----------     POINT_3  ----------  ----------     "
                "POINT_4  ----------  ----------     POINT_5  ----------  ----------     POINT_6  ----------  "
                "----------     POINT_7  ----------  ----------     POINT_8  ----------  ----------   AVG_NORTH  "
                "----------  ----------   AVG_SOUTH  ----------  ----------    AVG_WEST  ----------  ----------    "
                "AVG_EAST  ----------  ----------      BYPASS  ----------",
                " ----------  ----------------  ----------------------------------       Mxx(N)      Myy(N)      "
                "Mxy(N)      Mxx(N)      Myy(N)      Mxy(N)      Mxx(N)      Myy(N)      Mxy(N)      Mxx(N)      "
                "Myy(N)      Mxy(N)      Mxx(N)      Myy(N)      Mxy(N)      Mxx(N)      Myy(N)      Mxy(N)      "
                "Mxx(N)      Myy(N)      Mxy(N)      Mxx(N)      Myy(N)      Mxy(N)      Mxx(N)      Myy(N)      "
                "Mxy(N)      Mxx(N)      Myy(N)      Mxy(N)      Mxx(N)      Myy(N)      Mxy(N)      Mxx(N)      "
                "Myy(N)      Mxy(N)      Mxx(N)      Myy(N)      Mxy(N)   ",
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------"
            ]

            def format_loadcase(lcid, loadCases):
                name = f"SC{lcid}{[lc for lc in loadCases if lc.ID == lcid][0].Name}"
                return name[:34].ljust(34)
            
            plateData = []
            for p in plateListComp:
                plateElem = p.ElementList[0]
                prop = f"{propDict[plateElem.Prop].PropertyType}.{plateElem.Prop[0]}"
                boltElementList = p.BoltElementList
                if boltElementList["A"]:
                    cfastA_id = f"{boltElementList['A'].ID:12}"
                    directionA = p.BoltDirection["A"]
                else:
                    cfastA_id = f"{0:12}"
                    directionA = "  "
                    
                if boltElementList["B"]:
                    cfastB_id = f"{boltElementList['B'].ID:12}"
                    directionB = p.BoltDirection["B"]
                else:
                    cfastB_id = f"{0:12}"
                    directionB = "  "
                    
                elemNodes = plateElem.Nodes
                if len(elemNodes) == 3:
                    extZone = "        TRIA"
                else:
                    elemCoords = np.array([np.array(elem.GlobalCoords) for elem in elemNodes])
                    newCoords = elemCoords - elemCoords[0]
                    d1 = np.linalg.norm(newCoords[1] - newCoords[0])
                    d2 = np.linalg.norm(newCoords[2] - newCoords[1])
                    d3 = np.linalg.norm(newCoords[3] - newCoords[2])
                    d4 = np.linalg.norm(newCoords[0] - newCoords[3])
                    tol = 0.1
                    if abs(d1 - d3) < tol and abs(d2 - d4) < tol:
                        extZone = "      SQUARE"
                    else:
                        extZone = "     POLYGON"
                        
                boltElementsPlate = [l.ID for l in p.BoltElementList.values() if l]
                
                plateLine = f"{plateElem.ID:11}    {prop}{cfastA_id}{cfastB_id}       "
                plateLine += f"{directionA}|{directionB}{extZone}"
                for element in p.BoxElements.values():
                    plateLine += f"{element.ID:12}"
                boxPoints = list(p.BoxPoints.values())
                plateLine += "     "
                for point in boxPoints:
                    plateLine += f"[{point[0]:.2f},{point[1]:.2f},{point[2]:.2f}]     "
                plateData.append(plateLine)
            
            fastenerData = []
            for joint in self.JointsList:
                for enum, b in enumerate(joint.Bolt.ElementList):
                    if propDict.get(b.Prop):
                        propfast = f"{propDict[b.Prop].PropertyType}.{b.Prop[0]}"
                    else:
                        propfast = "N/A           "
                        
                    gs = "N/A     "
                    idb = joint.PlateList[enum+1].PlateCentralCellSolverID
                    ida = joint.PlateList[enum].PlateCentralCellSolverID
                    
                    line = f"{b.ID:11}    {propfast}    {gs}{b.Nodes[1].ID:12}"
                    line += f"{b.Nodes[0].ID:12}{idb:12}{ida:12}"
                    line += f"{joint.Diameter:12.2f}  N/A"
                    
                    fastenerData.append(line)
            
            resultsData = []
            for p in plateListComp:
                plateElem = p.ElementList[0]
                prop = f"{propDict[plateElem.Prop].PropertyType}.{plateElem.Prop[0]}"
                boltElementsPlate = [l.ID for l in p.BoltElementList.values() if l]
                
                for j in lcList:
                    loadcase = format_loadcase(j, self.Model.LoadCases)
                    
                    line = f"{plateElem.ID:11}    {prop}  {loadcase}"
                    line += f"{p.NxBypass[j]:12.2f}{p.NyBypass[j]:12.2f}"
                    line += f"{p.NxyBypass[j]:12.2f}{p.BearingForce[j][0]:12.2f}"
                    line += f"{p.BearingForce[j][1]:12.2f}{p.BearingForce[j][2]:14.2f}"
                    line += f"{p.MxTotal[j]:16.2f}{p.MyTotal[j]:16.2f}"
                    line += f"{p.MxyTotal[j]:16.2f}"
                    shear = max([p.Bolt.ShearForce[j][l] for l in boltElementsPlate])
                    axial = max([p.Bolt.AxialForce[j][l] for l in boltElementsPlate])
                    line += f"{shear:16.2f}{axial:16.2f}"
                    resultsData.append(line)
            
            translationalData = []
            for p in plateListComp:
                plateElem = p.ElementList[0]
                prop = f"{propDict[plateElem.Prop].PropertyType}.{plateElem.Prop[0]}"
                
                for j in lcList:
                    tf = p.TranslationalFastenerForces[j]
                    loadcase = format_loadcase(j, self.LoadCases)
                    line = f"{plateElem.ID:11}    {prop}  {loadcase}"
                    line += f"{tf[0][0]:12.2f}{tf[0][1]:12.2f}{tf[0][2]:12.2f}"
                    line += f"{tf[1][0]:12.2f}{tf[1][1]:12.2f}{tf[1][2]:12.2f}"
                    line += f"{p.CFASTFactor['A']:12}{p.CFASTFactor['B']:12}"
                    translationalData.append(line)
            
            forceFluxesData = []
            for p in plateListComp:
                plateElem = p.ElementList[0]
                prop = f"{propDict[plateElem.Prop].PropertyType}.{plateElem.Prop[0]}"
                for j in lcList:
                    loadcase = format_loadcase(j, self.LoadCases)
                    bf = p.BoxFluxes[j]
                    bs = p.BypassSides[j]
                    line = f"{plateElem.ID:11}    {prop}  {loadcase}"
                    for i in range(1, 9):
                        line += f"{bf[i][0]:12.2f}{bf[i][1]:12.2f}{bf[i][2]:12.2f}"
                    for i in range(4):
                        line += f"{bs[0][i]:12.2f}{bs[1][i]:12.2f}{bs[2][i]:12.2f}"
                    line += f"{p.NxBypass[j]:12.2f}{p.NyBypass[j]:12.2f}{p.NxyBypass[j]:12.2f}"
                    forceFluxesData.append(line)
            
            momentFluxesData = []
            for p in plateListComp:
                plateElem = p.ElementList[0]
                prop = f"{propDict[plateElem.Prop].PropertyType}.{plateElem.Prop[0]}"
                for j in lcList:
                    loadcase = format_loadcase(j, self.LoadCases)
                    bf = p.BoxFluxes[j]
                    bs = p.BypassSides[j]
                    line = f"{plateElem.ID:11}    {prop}  {loadcase}"
                    for i in range(1, 9):
                        line += f"{bf[i][3]:12.2f}{bf[i][4]:12.2f}{bf[i][5]:12.2f}"
                    for i in range(4):
                        line += f"{bs[3][i]:12.2f}{bs[4][i]:12.2f}{bs[5][i]:12.2f}"
                    line += f"{p.MxTotal[j]:12.2f}{p.MyTotal[j]:12.2f}{p.MxyTotal[j]:12.2f}"
                    momentFluxesData.append(line)
            
            with open(pathComp, "w") as f:
                f.write('\n'.join(headers))
                f.write('\n')
                for line in plateData:
                    f.write(line)
                    f.write('\n')
                f.write('\n'.join(fastenerHeader))
                f.write('\n')
                for line in fastenerData:
                    f.write(line)
                    f.write('\n')
                f.write('\n'.join(resultsHeader))
                f.write('\n')
                for line in resultsData:
                    f.write(line)
                    f.write('\n')
                f.write('\n'.join(translationalHeader))
                f.write('\n')
                for line in translationalData:
                    f.write(line)
                    f.write('\n')
                f.write('\n'.join(forceFluxesHeader))
                f.write('\n')
                for line in forceFluxesData:
                    f.write(line)
                    f.write('\n')
                f.write('\n'.join(momentFluxesHeader))
                f.write('\n')
                for line in momentFluxesData:
                    f.write(line)
                    f.write('\n')

        if plateListMetal != []: 
            t = asctime()
            headers = [
                " Idaero Solutions S.L.  N2PGetLoadFasteners (metallic)",
                " ======================================================",
                "",
                "",
                " ======================================",
                "                          SETTING/VALUE",
                " ======================================",
                f"                     Date/Time  {t[11:19]}, {str(gmtime()[2])}-{t[4:7]}-{t[20:24]}",
                f"               NaxToPy Version  {Constants.VERSION}",
                f"                 NaxTo Version  {Constants.NAXTO_VERSION}",
                f"                  BoxDimension  {plateListComp[0].BoxDimension:5.2f}",
                f"         CompressionEqualsZero  {self.OptionalAttributes.CompressionEqualsZero}",
                f"               PullThroughAsIs  {self.OptionalAttributes.PullThroughAsIs}",
                f"                     ShearAsIs  {self.OptionalAttributes.ShearAsIs}",
                f"                 Analysis Type  {self.TypeAnalysis}",
                "  Extraction Coordinate System  Material",
                "                 Material Type  Metallic",
                "",
                "",
                "",
                " ================================================",
                "       ELEMENT/CONNECTOR-SYSTEM/EXTRACTION_POINTS",
                " ================================================",
                "               /|               *p7....*p6....*p5   ",
                "              / |               .             .     ",
                "             /  |               .             .     ",
                "            /GA |         GB    .             .     ",
                "            | *=====>=====*     *p8   --->    *p4   ",
                "    CFAST_A |   | CFAST_B       .     mat0°   .     ",
                " *=====<====|=* /               .             .     ",
                " GB         |GA/                .             .     ",
                "            | /                 *p1....*p2....*p3   ",
                "            |/                                      ",
                f"          A/B-ELEM              alen = {plateListComp[0].BoxDimension:5.2f}mm",
                "",
                "",
                " ----------  ----------------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "------------------------------  ------------------------------  ------------------------------  "
                "------------------------------  ------------------------------  ------------------------------  "
                "------------------------------  ------------------------------",
                "   A/B-ELEM      A/B-PROPERTY     CFAST_A     CFAST_B  DIRECTIONS    EXT.ZONE   ELEMENT_1   "
                "ELEMENT_2   ELEMENT_3   ELEMENT_4   ELEMENT_5   ELEMENT_6   ELEMENT_7   ELEMENT_8                  "
                "POINT_1(X,Y,Z)                  POINT_2(X,Y,Z)                  POINT_3(X,Y,Z)                  "
                "POINT_4(X,Y,Z)                  POINT_5(X,Y,Z)                  POINT_6(X,Y,Z)                  "
                "POINT_7(X,Y,Z)                  POINT_8(X,Y,Z)",
                " ----------  ----------------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "------------------------------  ------------------------------  ------------------------------  "
                "------------------------------  ------------------------------  ------------------------------  "
                "------------------------------  ------------------------------"
            ]
            
            fastenerHeader = [
                "",
                " ----------  ----------------  ----------  ----------  ----------  ----------  ----------  "
                "----------  -----------------------",
                "   CFAST-ID    CFAST-PROPERTY     GS-NODE     GA-NODE     GB-NODE      A-ELEM      B-ELEM    "
                "DIAM(mm)  MATERIAL",
                " ----------  ----------------  ----------  ----------  ----------  ----------  ----------  "
                "----------  -----------------------"
            ]

            resultsHeader = [
                "", 
                " =======",
                " RESULTS",
                " =======",
                "----------  ----------------  ----------------------------------  ----------  ----------"
                "----------  ----------  ----------  ----------  ----------  ------------  ------------  ------------", 
                "   A/B-ELEM      A/B-PROPERTY                    LOADCASE,SUBCASE   TotalFlux   TotalFlux   " 
                "TotalFlux     F_Shear     F_Shear    Fastener    Fastener   PullThrough     BoltShear   BoltTension", 
                " ----------  ----------------  ----------------------------------    Nx(N/mm)     Ny(N/mm)  "
                "Nxy(N/mm)       Fx(N)       Fy(N)       Fx(N)       Fy(N)         Fz(N)      Force(N)      Force(N)", 
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ------------  ------------  ------------"
            ]
            
            translationalHeader = [
                "",
                " =============================",
                " TRANSLATIONAL_FASTENER_FORCES",
                " =============================",
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------",
                "   A/B-ELEM      A/B-PROPERTY                    LOADCASE,SUBCASE  ----------     CFAST_A  "
                "----------  ----------     CFAST_B  ----------     CFAST_A     CFAST_B",
                " ----------  ----------------  ----------------------------------   Fxx(N/mm)   Fyy(N/mm)   "
                "Fzz(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fzz(N/mm)   Factor(-)   Factor(-)",
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------"
            ]
            
            forceFluxesHeader = [
                "",
                " ===================================",
                " EXTRACTION_POINT_SHELL_FORCE_FLUXES",
                " ===================================",
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------",
                "   A/B-ELEM      A/B-PROPERTY                    LOADCASE,SUBCASE  ----------     POINT_1  "
                "----------  ----------     POINT_2  ----------  ----------     POINT_3  ----------  ----------     "
                "POINT_4  ----------  ----------     POINT_5  ----------  ----------     POINT_6  ----------  "
                "----------     POINT_7  ----------  ----------     POINT_8  ----------  ----------   AVG_NORTH  "
                "----------  ----------   AVG_SOUTH  ----------  ----------    AVG_WEST  ----------  ----------    "
                "AVG_EAST  ----------  ----------      BYPASS  ----------",
                " ----------  ----------------  ----------------------------------   Fxx(N/mm)   Fyy(N/mm)   "
                "Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   "
                "Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   "
                "Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   "
                "Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   "
                "Fyy(N/mm)   Fxy(N/mm)   Fxx(N/mm)   Fyy(N/mm)   Fxy(N/mm)",
                " ----------  ----------------  ----------------------------------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------  ----------  ----------  ----------  "
                "----------  ----------  ----------  ----------  ----------"
            ]

            def format_loadcase(lcid, loadCases):
                name = f"SC{lcid}{[lc for lc in loadCases if lc.ID == lcid][0].Name}"
                return name[:34].ljust(34)
            
            plateData = []
            for p in plateListMetal:
                plateElem = p.ElementList[0]
                prop = f"{propDict[plateElem.Prop].PropertyType}.{plateElem.Prop[0]}"
                
                boltElementList = p.BoltElementList
                if boltElementList["A"]:
                    cfastA_id = f"{boltElementList['A'].ID:12}"
                    directionA = p.BoltDirection["A"]
                else:
                    cfastA_id = f"{0:12}"
                    directionA = "  "
                    
                if boltElementList["B"]:
                    cfastB_id = f"{boltElementList['B'].ID:12}"
                    directionB = p.BoltDirection["B"]
                else:
                    cfastB_id = f"{0:12}"
                    directionB = "  "
                elemNodes = plateElem.Nodes
                if len(elemNodes) == 3:
                    extZone = "        TRIA"
                else:
                    elemCoords = np.array([np.array(elem.GlobalCoords) for elem in elemNodes])
                    newCoords = elemCoords - elemCoords[0]
                    d1 = np.linalg.norm(newCoords[1] - newCoords[0])
                    d2 = np.linalg.norm(newCoords[2] - newCoords[1])
                    d3 = np.linalg.norm(newCoords[3] - newCoords[2])
                    d4 = np.linalg.norm(newCoords[0] - newCoords[3])
                    tol = 0.1
                    if abs(d1 - d3) < tol and abs(d2 - d4) < tol:
                        extZone = "      SQUARE"
                    else:
                        extZone = "     POLYGON"
                        
                boltElementsPlate = [l.ID for l in p.BoltElementList.values() if l]
                plateLine = f"{plateElem.ID:11}    {prop}{cfastA_id}{cfastB_id}       "
                plateLine += f"{directionA}|{directionB}{extZone}"
                
                for element in p.BoxElements.values():
                    plateLine += f"{element.ID:12}"
                    
                boxPoints = list(p.BoxPoints.values())
                plateLine += "     "
                for point in boxPoints:
                    plateLine += f"[{point[0]:.2f},{point[1]:.2f},{point[2]:.2f}]     "
                plateData.append(plateLine)
            
            fastenerData = []
            for joint in self.JointsList:
                for enum, b in enumerate(joint.Bolt.ElementList):
                    if propDict.get(b.Prop):
                        propfast = f"{propDict[b.Prop].PropertyType}.{b.Prop[0]}"
                    else:
                        propfast = "N/A           "
                    gs = "N/A     "
                    idb = joint.PlateList[enum+1].PlateCentralCellSolverID
                    ida = joint.PlateList[enum].PlateCentralCellSolverID
                    line = f"{b.ID:11}    {propfast}    {gs}{b.Nodes[1].ID:12}"
                    line += f"{b.Nodes[0].ID:12}{idb:12}{ida:12}"
                    line += f"{joint.Diameter:12.2f}  N/A"
                    fastenerData.append(line)
            
            resultsData = []
            for p in plateListMetal:
                plateElem = p.ElementList[0]
                prop = f"{propDict[plateElem.Prop].PropertyType}.{plateElem.Prop[0]}"
                boltElementsPlate = [l.ID for l in p.BoltElementList.values() if l]
                
                for j in lcList:
                    loadcase = format_loadcase(j, self.Model.LoadCases)

                    shear = max([p.Bolt.ShearForce[j][l] for l in boltElementsPlate])
                    axial = max([p.Bolt.AxialForce[j][l] for l in boltElementsPlate])
                    argShear = np.array(list(p.Bolt.ShearForce[j].values())).argmax()
                    angle = list(p.Bolt.LoadAngle[j].values())[argShear]
                    
                    line = f"{plateElem.ID:11}   {prop}  {loadcase}"
                    line += f"{p.NxTotal[j]:12.2f}{p.NyTotal[j]:12.2f}"
                    line += f"{p.NxyTotal[j]:12.2f}{shear*np.cos(angle):12.2f}" 
                    line += f"{shear*np.sin(angle):12.2f}{p.BearingForce[j][0]:12.2f}"
                    line += f"{p.BearingForce[j][1]:12.2f}{p.BearingForce[j][2]:14.2f}"
                    line += f"{shear:14.2f}{axial:15.2f}"
                    resultsData.append(line)
            
            translationalData = []
            for p in plateListMetal:
                plateElem = p.ElementList[0]
                prop = f"{propDict[plateElem.Prop].PropertyType}.{plateElem.Prop[0]}"
                
                for j in lcList:
                    tf = p.TranslationalFastenerForces[j]
                    loadcase = format_loadcase(j, self.LoadCases)
                    line = f"{plateElem.ID:11}    {prop}  {loadcase}"
                    line += f"{tf[0][0]:12.2f}{tf[0][1]:12.2f}{tf[0][2]:12.2f}"
                    line += f"{tf[1][0]:12.2f}{tf[1][1]:12.2f}{tf[1][2]:12.2f}"
                    line += f"{p.CFASTFactor['A']:12}{p.CFASTFactor['B']:12}"
                    translationalData.append(line)
            
            forceFluxesData = []
            for p in plateListMetal:
                plateElem = p.ElementList[0]
                prop = f"{propDict[plateElem.Prop].PropertyType}.{plateElem.Prop[0]}"
                for j in lcList:
                    loadcase = format_loadcase(j, self.LoadCases)
                    bf = p.BoxFluxes[j]
                    bs = p.BypassSides[j]
                    line = f"{plateElem.ID:11}    {prop}  {loadcase}"
                    for i in range(1, 9):
                        line += f"{bf[i][0]:12.2f}{bf[i][1]:12.2f}{bf[i][2]:12.2f}"
                    for i in range(4):
                        line += f"{bs[0][i]:12.2f}{bs[1][i]:12.2f}{bs[2][i]:12.2f}"
                    line += f"{p.NxBypass[j]:12.2f}{p.NyBypass[j]:12.2f}{p.NxyBypass[j]:12.2f}"
                    forceFluxesData.append(line)
            
            with open(pathMetal, "w") as f:
                f.write('\n'.join(headers))
                f.write('\n')
                for line in plateData:
                    f.write(line)
                    f.write('\n')
                f.write('\n'.join(fastenerHeader))
                f.write('\n')
                for line in fastenerData:
                    f.write(line)
                    f.write('\n')
                f.write('\n'.join(resultsHeader))
                f.write('\n')
                for line in resultsData:
                    f.write(line)
                    f.write('\n')
                f.write('\n'.join(translationalHeader))
                f.write('\n')
                for line in translationalData:
                    f.write(line)
                    f.write('\n')
                f.write('\n'.join(forceFluxesHeader))
                f.write('\n')
                for line in forceFluxesData:
                    f.write(line)
                    f.write('\n')
    # ------------------------------------------------------------------------------------------------------------------
        
    # Method used to export the obtained PAG results as a HDF5 file ----------------------------------------------------
    def __export_hdf5(self): 

        """
        Method used to export the PAG results to an HDF5 file. 

        Calling example: 
            >>> loads.__export_hdf5() 
        """

        hdf5 = HDF5_NaxTo() 
        newPathFile = "{}\\{}_fastpph.h5".format(self.ExportLocation, self.AnalysisName)
        hdf5.FilePath = newPathFile
        hdf5.create_hdf5() 

        dataInput = DataEntry() 
        dataInput.DataInputName = "FASTENER'S LOADS"
        pi = "i" + str(self.OptionalAttributes.ExportPrecision)
        pf = "f" + str(self.OptionalAttributes.ExportPrecision)

        inputDataType = np.dtype([("ANALYSED LOADCASES", pi), ("NUMBER OF ELEMENTS IN THE REDUCED MODEL", pi), 
                                  ("ADJACENCY LEVEL", pi), ("CORNER DATA", "S5"), ("MATERIAL FACTOR METAL", pf), 
                                  ("MATERIAL FACTOR COMPOSITE", pf), ("AREA FACTOR", pf), ("MAX ITERATIONS", pi), 
                                  ("PROJECTION TOLERANCE", pf), ("TYPE ANALYSIS", "S8"), ("EXPORT PRECISION", pi), 
                                  ("LOAD CASE NUMBER", pi), ("COMPRESSION EQUALS ZERO", "S5"), 
                                  ("PULLTHROUGH AS IS", "S5"), ("SHEAR AS IS", "S5")])
        
        inputData = np.array([(len(self.LoadCases), len(self.Model.get_elements()), 
                               self.OptionalAttributes.AdjacencyLevel, str(self.OptionalAttributes.CornerData), 
                               self.OptionalAttributes.MaterialFactorMetal, 
                               self.OptionalAttributes.MaterialFactorComposite, self.OptionalAttributes.AreaFactor, 
                               self.OptionalAttributes.MaxIterations, self.OptionalAttributes.ProjectionTolerance, 
                               self.TypeAnalysis, self.OptionalAttributes.ExportPrecision, 
                               self.OptionalAttributes.LoadCaseNumber, 
                               str(self.OptionalAttributes.CompressionEqualsZero), 
                               str(self.OptionalAttributes.PullThroughAsIs), str(self.OptionalAttributes.ShearAsIs))], 
                               inputDataType)
        
        dataInput.DataInput = inputData
        hdf5._modules_input_data([dataInput])

        plateList = self.PlateList.copy()

        self.__sort_plates(plateList)
        dataEntryList = [self.__transform_results(k, p) for k in self.LoadCases for p in plateList]
        hdf5.write_dataset(dataEntryList)
    # ------------------------------------------------------------------------------------------------------------------
    def __export_csv(self):

        """
        Method used to export results to a CSV file, with a different structure being used for the 'ALTAIR' export type 
        and the regular 'CSV' export type. 

        Calling example: 
            >>> loads.__export_csv() 
        """

        newPathFile = f"{self.ExportLocation}/{self.AnalysisName}_fastpph.csv"
        propDict = self.Model.PropertyDict
        timestamp = asctime()

        loadcases = [] 
        for lc in self.LoadCases:
            increment = lc.ActiveN2PIncrement.ID
            loadcases.append((lc.ID, self.Model.get_load_case(lc.ID).Name, increment))

        if self.TypeExport == "ALTAIR": 
            headline = [["Idaero Solutions S.L.  N2PGetLoadFasteners"], 
                            [f"Date/Time, {timestamp[11:19]}; {gmtime()[2]}-{timestamp[4:7]}-{timestamp[20:24]}"], 
                            [f"NaxToPy Version, {Constants.VERSION}"],
                            [f"NaxTo Version, {Constants.NAXTO_VERSION}"],
                            [f"CompressionEqualsZero, {self.OptionalAttributes.CompressionEqualsZero}"],
                            [f"PullThroughAsIs, {self.OptionalAttributes.PullThroughAsIs}"],
                            [f"ShearAsIs, {self.OptionalAttributes.ShearAsIs}"],
                            ["DDP", "entityid", "elementid", "Component Name", "elem 1 id", "elem 1 Node id", "elem 2 id", "elem 2 Node id", "box dimension", "loadcase", "file Name", "LoadCase Name",
                            "Time Step Name", "pierced location", "Fx", "Fy", "Fz", "MaxFz", *[f"p{n}" for n in range(1,9)], *[f"Fxx p{n}" for n in range(1,9)], *[f"Fyy p{n}" for n in range(1,9)],
                            *[f"Fxy p{n}" for n in range(1,9)], *[f"Mxx p{n}" for n in range(1,9)], *[f"Myy p{n}" for n in range(1,9)], *[f"Mxy p{n}" for n in range(1,9)],
                            "Nx bypass", "Nx total", "Ny bypass", "Ny total", "Nxy bypass", "Nxy total", "Mx total", "My total", "Mxy total"]]

            def closest_node_info(boltList, intersection):
                if boltList:
                    coords = [node.GlobalCoords for node in boltList.Nodes]
                    dists = np.linalg.norm(np.array(coords) - np.array(intersection), axis=1)
                    idx = int(np.argmin(dists))
                    return boltList.ID, boltList.Nodes[idx].ID
                return 0, 0

            with open(newPathFile, "a+", newline="") as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    for hdr in headline:
                        writer.writerow(hdr)
                
                for joint in self.JointsList:
                    for plate in joint.PlateList:
                        elem = plate.CentralElement
                        prop_str = f"{propDict[elem.Prop].PropertyType}.{elem.Prop[0]}"
                        a_id, node_a = closest_node_info(plate.BoltElementList.get("A"), plate.Intersection)
                        b_id, node_b = closest_node_info(plate.BoltElementList.get("B"), plate.Intersection)
                        box_dim = plate.BoxDimension
                        intersects = plate.Intersection
                        bearing = plate.BearingForce

                        box_pts = [list(_) for _ in plate.BoxPoints.values()]
                        flux = plate.BoxFluxes

                        for lc_id, lc_name, ts_name in loadcases:
                            row = [plate.Bolt.ID, plate.ID, plate.PlateCentralCellSolverID, prop_str, a_id, node_a, b_id, node_b, box_dim, lc_id, self.AnalysisName, lc_name, ts_name, intersects,
                                bearing[lc_id][0], bearing[lc_id][1], bearing[lc_id][2], plate.Bolt.MaxAxialForce[lc_id]]
                            row.extend(["".join(str(coord) + "," for coord in pt) for pt in box_pts])
                            for comp in range(6):
                                row.extend([flux[lc_id][i][comp] for i in range(1,9)])
                            row.extend([plate.NxBypass[lc_id], plate.NxTotal[lc_id], plate.NyBypass[lc_id], plate.NyTotal[lc_id],
                                        plate.NxyBypass[lc_id], plate.NxyTotal[lc_id], plate.MxTotal[lc_id], plate.MyTotal[lc_id], plate.MxyTotal[lc_id]])
                            writer.writerow(row)
        else: 
            headline = [["Idaero Solutions S.L.  N2PGetLoadFasteners"], 
                            [f"Date/Time, {timestamp[11:19]}; {gmtime()[2]}-{timestamp[4:7]}-{timestamp[20:24]}"], 
                            [f"NaxToPy Version, {Constants.VERSION}"],
                            [f"NaxTo Version, {Constants.NAXTO_VERSION}"],
                            [f"CompressionEqualsZero, {self.OptionalAttributes.CompressionEqualsZero}"],
                            [f"PullThroughAsIs, {self.OptionalAttributes.PullThroughAsIs}"],
                            [f"ShearAsIs, {self.OptionalAttributes.ShearAsIs}"],
                            ["PLATE ELEMENT ID", "LOAD CASE ID", "PROPERTY", "CFAST A ID", "CFAST B ID", "DIRECTION", "GA NODE CFAST A", "GB NODE CFAST A", "GA NODE CFAST B", "GB NODE CFAST B", "DIAMETER", 
                        "EXT. ZONE", *[f"ELEMENT {n} ID" for n in range(1, 9)], *[f"POINT {n} (X, Y, Z)" for n in range(1, 9)], "X BEARING FORCE", "Y BEARING FORCE", "PULLTHROUGH FORCE", "BOLT SHEAR", 
                        "BOLT TENSION", "NXX BYPASS", "NYY BYPASS", "NXY BYPASS", "NXX TOTAL", "NYY TOTAL", "NXY TOTAL","MXX TOTAL", "MYY TOTAL", "MXY TOTAL", "FXX CFAST A", "FYY CFAST A", "FZZ CFAST A", 
                        "FXX CFAST B", "FYY CFAST B", "FZZ CFAST B", "FACTOR CFAST A", "FACTOR CFAST B", 
                        *[f"{k} POINT {n}" for n in range(1,9) for k in ["FXX", "FYY", "FXY", "MXX", "MYY", "MXY"]], 
                        *[f"{k} {n}" for n in ["NORTH", "SOUTH", "WEST", "EAST"] for k in ["FXX", "FYY", "FXY", "MXX", "MYY", "MXY"]]]]
            def node_info(bolt: N2PElement):
                if bolt:
                    return bolt.ID, bolt.Nodes[0].ID, bolt.Nodes[1].ID 
                return 0, 0, 0 

            with open(newPathFile, "a+", newline="") as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    for hdr in headline:
                        writer.writerow(hdr)
                
                for joint in self.JointsList:
                    for plate in joint.PlateList:
                        elem = plate.CentralElement
                        prop_str = f"{propDict[elem.Prop].PropertyType}.{elem.Prop[0]}"
                        a_id, node_a1, node_a2 = node_info(plate.BoltElementList.get("A"))
                        b_id, node_b1, node_b2 = node_info(plate.BoltElementList.get("B"))
                        box_dim = plate.BoxDimension
                        intersects = plate.Intersection
                        bearing = plate.BearingForce
                        shear = plate.Bolt.ShearForce
                        boltElementsPlate = [b.ID for b in plate.BoltElementList.values() if b]
                        directionA, directionB = plate.BoltDirection.values() 
                        if not directionA: 
                            directionA = " "
                        if not directionB: 
                            directionB = " "
                        direction = directionA + "|" + directionB
                        elemNodes = plate.CentralElement.Nodes 
                        if len(elemNodes) == 3: 
                            extZone = "TRIA"
                        else: 
                            elemCoords = np.array([np.array(elem.GlobalCoords) for elem in elemNodes])
                            newCoords = elemCoords - elemCoords[0]
                            d1 = np.linalg.norm(newCoords[1] - newCoords[0])
                            d2 = np.linalg.norm(newCoords[2] - newCoords[1])
                            d3 = np.linalg.norm(newCoords[3] - newCoords[2])
                            d4 = np.linalg.norm(newCoords[0] - newCoords[3])
                            tol = 0.1 
                            if abs(d1 - d3) < tol and abs(d2 - d4) < tol: 
                                extZone = "SQUARE"
                            else: 
                                extZone = "POLYGON"

                        box_pts = [list(_) for _ in plate.BoxPoints.values()]
                        box_elems = [k.ID for k in plate.BoxElements.values()]
                        flux = plate.BoxFluxes
                        tf = plate.TranslationalFastenerForces

                        for lc_id, lc_name, ts_name in loadcases:
                            row = [plate.PlateCentralCellSolverID, lc_id, prop_str, a_id, b_id, direction, node_a1, node_a2, node_b1, node_b2, joint.Diameter, extZone]
                            row.extend(box_elems)
                            row.extend(["".join(str(coord) + "," for coord in pt) for pt in box_pts])
                            row.extend([bearing[lc_id][0], bearing[lc_id][1], bearing[lc_id][2], max([shear[lc_id][b] for b in boltElementsPlate]), 
                                        plate.Bolt.MaxAxialForce[lc_id], plate.NxBypass[lc_id], plate.NyBypass[lc_id], plate.NxyBypass[lc_id], 
                                        plate.NxTotal[lc_id], plate.NyTotal[lc_id], plate.NxyTotal[lc_id], plate.MxTotal[lc_id], plate.MyTotal[lc_id], 
                                        plate.MxyTotal[lc_id], tf[lc_id][0][0], tf[lc_id][0][1], tf[lc_id][0][2], tf[lc_id][1][0], tf[lc_id][1][1], 
                                        tf[lc_id][1][2], plate.CFASTFactor["A"], plate.CFASTFactor["B"]]) 
                            for i in range(1,9): 
                                row.extend([f"{flux[lc_id][i][comp]:.3f}" for comp in range(6)])
                            row.extend([f"{j:.3f}" for k in plate.BypassSides[lc_id].T for j in k])
                            writer.writerow(row)
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to create the model ----------------------------------------------------------------------------------
    def __create_model(self): 

        """
        Method used to create a new model and import its results. It fires when the model, joints_list (they may have 
        been filled with get_fasteners) and results_files attributes have been filled in. It also assigns certain 
        attributes (such as CFASTFactor and BoltDirection) to plates and updates some of them, because they included 
        N2PElements from the old model. 

        Calling example: 
            >>> loads.__create_model()
        """

        # Adjacent elements are selected and a new model is created 
        if self.OptionalAttributes.AdjacencyLevel != -1: 
            self._model = load_reduced_model(self.Model, self.JointsList, self.OptionalAttributes.AdjacencyLevel) 
            # Elements are updated 
            elementsDict = dict(self.Model.ElementsDict)
            partDict = self.Model._N2PModelContent__StrPartToID
            for i in self.JointsList: 
                # The Bolt.ElementList attribute is updated 
                i.Bolt._element_list = [elementsDict[(j, partDict[i.PartID])] for j in i.BoltElementIDList]
                for j in i.PlateList: 
                    # The Plate.ElementList and Plate.CentralElement attributes are updated 
                    j._element_list = [elementsDict[(j.ElementIDList[k], partDict[j.PartID[k]])] 
                                       for k in range(len(j.ElementIDList))]
                    j._central_element = elementsDict[(j.CentralElement.ID, partDict[j.CentralElement.PartID])]
                    j._face_elements = set(self.Model.get_elements_by_face([j.CentralElement]))
                    for k,l in j.BoltElementList.items(): 
                        if l: 
                            j._bolt_element_list[k] = elementsDict[(l.ID, partDict[l.PartID])]
        else: 
            for i in self.JointsList: 
                for j in i.PlateList: 
                    j._face_elements = set(self.Model.get_elements_by_face([j.CentralElement]))
        # Results are loaded onto the model 
        self._model.import_results_from_files(self.ResultsFiles) 
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to create the model ----------------------------------------------------------------------------------
    def __create_model_2(self, elementList: list[N2PElement]): 

        """
        Method used to create a new model and import its results. It fires when the model, joints_list (they may have 
        been filled with get_fasteners) and results_files attributes have been filled in. It also assigns certain 
        attributes (such as CFASTFactor and BoltDirection) to plates and updates some of them, because they included 
        N2PElements from the old model. 

        Calling example: 
            >>> loads.__create_model_2()
        """
        
        # Adjacent elements are selected and a new model is created 
        elementDictionary = {} 
        for i in elementList: 
            if i.PartID not in elementDictionary.keys(): 
                elementDictionary[i.PartID] = [i.ID] 
            else: 
                elementDictionary[i.PartID].append(i.ID)
        # Other, generally unimportant ModelContent attributes are obtained 
        path = self.Model.FilePath
        parallel = self.Model._N2PModelContent__vzmodel.LoadModelInParallel
        solver = self.Model.Solver
        # A new reduced model is created and returned 
        self._model = NP.load_model(path, parallel, solver, elementDictionary, 'ELEMENTS')
        if self.ResultsFiles: 
            self._model.import_results_from_files(self.ResultsFiles) 
            self._load_cases = self.Model.get_load_case([k.ID for k in self.LoadCases])
        elementsDict = dict(self.Model.ElementsDict)
        partDict = self.Model._N2PModelContent__StrPartToID
        for i in self.JointsList: 
            # The Bolt.ElementList attribute is updated 
            i.Bolt._element_list = [elementsDict[(j, partDict[i.PartID])] for j in i.BoltElementIDList]
            for j in i.PlateList: 
                # The Plate.ElementList and Plate.CentralElement attributes are updated 
                j._element_list = [elementsDict[(j.ElementIDList[k], partDict[j.PartID[k]])] 
                                   for k in range(len(j.ElementIDList))]
                j._central_element = elementsDict[(j.CentralElement.ID, partDict[j.CentralElement.PartID])]
                j._face_elements = set(self.Model.get_elements_by_face([j.CentralElement]))
                for k,l in j.BoltElementList.items(): 
                    if l: 
                        j._bolt_element_list[k] = elementsDict[(l.ID, partDict[l.PartID])]
                for k,l in j.BoxElements.items(): 
                    j._box_elements[k] = elementsDict[(l.ID, partDict[l.PartID])]
    # ------------------------------------------------------------------------------------------------------------------
        
    # Method used to transform the results into arrays to be exported into an HDF5 -------------------------------------
    def __transform_results(self, loadcase: N2PLoadCase, p: N2PPlate) -> DataEntry: 

        """
        Method used to transform the results obtained in the previous calculations into a DataEntry instance in order 
        to be exported to an HDF5 file. Reduced are exported differently depending on if the type of export is "HDF5" 
        or "REDUCED_HDF5". 

        Args: 
            loadcase: N2PLoadCase -> load case  
            p: N2PPlate -> plate to be analysed 

        Returns: 
            dataEntry: DataEntry -> DataEntry instance to be written to an HDF5 file.

        Calling example: 
            >>> loads.__transform_rseults(loads.LoadCases[7], loads.PlateList[213])
        """

        plateElem = p.ElementList[0]
        boltElementsPlate = [l.ID for l in p.BoltElementList.values() if l]
        partDict = self.Model._N2PModelContent__StrPartToID
        platePart = str((partDict.get(p.PartID[0]), p.PartID[0]))

        pi = "i" + str(self.OptionalAttributes.ExportPrecision)
        pf = "f" + str(self.OptionalAttributes.ExportPrecision)

        lc = loadcase.ID
        tension = max([p.Bolt.AxialForce[lc][l] for l in boltElementsPlate]) 

        if self.TypeExport == "HDF5": 
            dataType = np.dtype([("ID_ENTITY", pi), ("BYPASS FLUX NXX", pf), ("BYPASS FLUX NYY", pf), 
                                 ("BYPASS FLUX NXY", pf), ("TOTAL FORCE FLUX NXX", pf), ("TOTAL FORCE FLUX NYY", pf), 
                                 ("TOTAL FORCE FLUX NXY", pf), ("X BEARING FORCE", pf), ("Y BEARING FORCE", pf), 
                                 ("PULLTHROUGH FORCE", pf), ("TOTAL MOMENTUM FLUX MXX", pf), 
                                 ("TOTAL MOMENTUM FLUX MYY", pf), ("TOTAL MOMENTUM FLUX MXY", pf), ("BOLT SHEAR", pf), 
                                 ("BOLT TENSION", pf), ("FXX CFAST A", pf), ("FYY CFAST A", pf), ("FZZ CFAST A", pf), 
                                 ("FXX CFAST B", pf), ("FYY CFAST B", pf), ("FZZ CFAST B", pf), 
                                 ("FXX POINT 1", pf), ("FYY POINT 1", pf), ("FXY POINT 1", pf), 
                                 ("MXX POINT 1", pf), ("MYY POINT 1", pf), ("MXY POINT 1", pf), 
                                 ("FXX POINT 2", pf), ("FYY POINT 2", pf), ("FXY POINT 2", pf), 
                                 ("MXX POINT 2", pf), ("MYY POINT 2", pf), ("MXY POINT 2", pf),
                                 ("FXX POINT 3", pf), ("FYY POINT 3", pf), ("FXY POINT 3", pf), 
                                 ("MXX POINT 3", pf), ("MYY POINT 3", pf), ("MXY POINT 3", pf), 
                                 ("FXX POINT 4", pf), ("FYY POINT 4", pf), ("FXY POINT 4", pf), 
                                 ("MXX POINT 4", pf), ("MYY POINT 4", pf), ("MXY POINT 4", pf),
                                 ("FXX POINT 5", pf), ("FYY POINT 5", pf), ("FXY POINT 5", pf), 
                                 ("MXX POINT 5", pf), ("MYY POINT 5", pf), ("MXY POINT 5", pf), 
                                 ("FXX POINT 6", pf), ("FYY POINT 6", pf), ("FXY POINT 6", pf), 
                                 ("MXX POINT 6", pf), ("MYY POINT 6", pf), ("MXY POINT 6", pf),
                                 ("FXX POINT 7", pf), ("FYY POINT 7", pf), ("FXY POINT 7", pf), 
                                 ("MXX POINT 7", pf), ("MYY POINT 7", pf), ("MXY POINT 7", pf), 
                                 ("FXX POINT 8", pf), ("FYY POINT 8", pf), ("FXY POINT 8", pf), 
                                 ("MXX POINT 8", pf), ("MYY POINT 8", pf), ("MXY POINT 8", pf),
                                 ("FXX NORTH", pf), ("FYY NORTH", pf), ("FXY NORTH", pf), 
                                 ("FXX SOUTH", pf), ("FYY SOUTH", pf), ("FXY SOUTH", pf),
                                 ("FXX WEST", pf), ("FYY WEST", pf), ("FXY WEST", pf), 
                                 ("FXX EAST", pf), ("FYY EAST", pf), ("FXY EAST", pf),
                                 ("MXX NORTH", pf), ("MYY NORTH", pf), ("MXY NORTH", pf), 
                                 ("MXX SOUTH", pf), ("MYY SOUTH", pf), ("MXY SOUTH", pf),
                                 ("MXX WEST", pf), ("MYY WEST", pf), ("MXY WEST", pf), 
                                 ("MXX EAST", pf), ("MYY EAST", pf), ("MXY EAST", pf)])
            shear = max([p.Bolt.ShearForce[lc][l] for l in boltElementsPlate])
            tf = p.TranslationalFastenerForces[lc]
            bf = p.BoxFluxes[lc]
            bs = p.BypassSides[lc]
            resultList = np.array([(plateElem.ID, p.NxBypass[lc], p.NyBypass[lc], p.NxyBypass[lc], p.NxTotal[lc], 
                                    p.NyTotal[lc], p.NxyTotal[lc], p.BearingForce[lc][0], p.BearingForce[lc][1], 
                                    p.BearingForce[lc][2], p.MxTotal[lc], p.MyTotal[lc], p.MxyTotal[lc], shear, tension,
                                    tf[0][0], tf[0][1], tf[0][2], tf[1][0], tf[1][1], tf[1][2], 
                                    bf[1][0], bf[1][1], bf[1][2], bf[1][3], bf[1][4], bf[1][5], 
                                    bf[2][0], bf[2][1], bf[2][2], bf[2][3], bf[2][4], bf[2][5], 
                                    bf[3][0], bf[3][1], bf[3][2], bf[3][3], bf[3][4], bf[3][5], 
                                    bf[4][0], bf[4][1], bf[4][2], bf[4][3], bf[4][4], bf[4][5], 
                                    bf[5][0], bf[5][1], bf[5][2], bf[5][3], bf[5][4], bf[5][5], 
                                    bf[6][0], bf[6][1], bf[6][2], bf[6][3], bf[6][4], bf[6][5], 
                                    bf[7][0], bf[7][1], bf[7][2], bf[7][3], bf[7][4], bf[7][5], 
                                    bf[8][0], bf[8][1], bf[8][2], bf[8][3], bf[8][4], bf[8][5], 
                                    bs[0][0], bs[1][0], bs[2][0], bs[3][0], bs[4][0], bs[5][0], 
                                    bs[0][1], bs[1][1], bs[2][1], bs[3][1], bs[4][1], bs[5][1], 
                                    bs[0][2], bs[1][2], bs[2][2], bs[3][2], bs[4][2], bs[5][2], 
                                    bs[0][3], bs[1][3], bs[2][3], bs[3][3], bs[4][3], bs[5][3])], dataType) 
        else: 
            dataType = np.dtype([("ID_ENTITY", pi), ("BYPASS FLUX NXX", pf), ("BYPASS FLUX NYY", pf), 
                                 ("BYPASS FLUX NXY", pf), ("X BEARING FORCE", pf), ("Y BEARING FORCE", pf), 
                                 ("PULLTHROUGH FORCE", pf), ("BOLT TENSION", pf)])
            resultList = np.array([(plateElem.ID, p.NxBypass[lc], p.NyBypass[lc], p.NxyBypass[lc], 
                                    p.BearingForce[lc][0], p.BearingForce[lc][1], p.BearingForce[lc][2], 
                                    tension)], dataType) 

        dataEntry = DataEntry() 
        dataEntry.ResultsName = "FASTENER ANALYSIS"
        dataEntry.LoadCase = lc 
        dataEntry.Increment = loadcase.ActiveN2PIncrement.ID
        dataEntry.LoadCaseName = loadcase.Name 
        dataEntry.Section = "None"
        dataEntry.Part = platePart 
        dataEntry.Data = resultList

        return dataEntry
    # ------------------------------------------------------------------------------------------------------------------

# endregion 
# region OptionalAttributes

class _N2POptionalAttributes: 

    """
    The _N2POptionalAttributes class is used to save all optional attributes of N2PGetLoadFasteners. 

    Properties: 
        GetLoadFasteners: N2PGetLoadFasteners -> N2PGetLoadFasteners instance being used for this 
        _N2POptionalAttributes instance. 
        AdjacencyLevel: int -> number of times that the get_elements_attached() funcion is called when laoding a new 
        model. 
        LoadSecondModel: bool -> boolean that shows if another model will be loaded when obtaining the results. 
        CornerData: bool -> boolean that shows if there are results in the corners or not. 
        MaterialFactorMetal: float -> material factor used to create the bypass box for metallic plates. 
        MaterialFactorComposite: float -> material factor used to create the bypass box for composite plates. 
        AreaFactor: float -> area factor used to create the byapss box. 
        MaxIterations: int -> maximum number of iterations allowed to create the bypass box. 
        ProjectionTolerance: float -> tolerance used to determine if a point lies within an element. 
        DefaultDiameter: float -> diameter assigned to joints with no diameter. 
        ExportPrecision: int -> precision used when exporting results to an HDF5 file (4 or 8). 
        LoadCaseNumber: int -> number of load cases analysed at the same time. 
        CompressionEqualsZero: bool -> boolean that shows if the pullthrough force of a compressed plate will be set to 
        zero or kept negative.
        PullThroughAsIs: bool -> boolean that shows if the pullthrough force of a plate will be calculated or directly 
        extracted from the model. 
        ShearAsIs: bool -> boolean that shows if the shear force of a plate will be calculated or directly extracted 
        from the model. 
    """

    __slots__ = ("_get_load_fasteners", 
                 "_adjacency_level", 
                 "_load_second_model", 
                 "_corner_data", 
                 "_material_factor_metal", 
                 "_material_factor_composite", 
                 "_area_factor", 
                 "_max_iterations", 
                 "_projection_tolerance", 
                 "_default_diameter", 
                 "_export_precision", 
                 "_load_case_number", 
                 "_compression_equals_zero", 
                 "_pullthrough_as_is", 
                 "_shear_as_is")

    def __init__(self, loads):

        """
        The constructor creates an empty _N2POptionalAttributes instance. Its attributes must be added as properties.

        Calling example: 
            >>> att = _N2POptionalAttributes() 
            >>> att.GetLoadFasteners = loads 
            >>> att.AdjacencyLevel = 3 
            >>> att.LoadSecondModel = True 
            >>> att.CornerData = True 
            >>> att.MaterialFactorMetal = 3.5 
            >>> att.MaterialFactorComposite = 4.5 
            >>> att.areaFactor = 2.0 
            >>> att.MaxIterations = 50 
            >>> att.ProjectionTolerance = 1e-6 
            >>> att.DefaultDiameter = 5.6 
            >>> att.ExportPrecision = 8 
            >>> att.LoadCaseNumber = 50 
            >>> att.CompressionEqualsZero = False 
            >>> att.PullthroughAsIs = False 
            >>> att.ShearAsIs = False
        """

        self._get_load_fasteners: N2PGetLoadFasteners = loads 
        self._adjacency_level: int = -1
        self._load_second_model: bool = False  
        self._corner_data: bool = False 
        self._material_factor_metal: float = 4.0 
        self._material_factor_composite: float = 4.0
        self._area_factor: float = 2.5 
        self._max_iterations: int = 200 
        self._projection_tolerance: float = 0.01 
        self._default_diameter: float = None 
        self._export_precision: int = 4 
        self._load_case_number: int = -1 
        self._compression_equals_zero: bool = True 
        self._pullthrough_as_is: bool = True 
        self._shear_as_is: bool = True 
    # ------------------------------------------------------------------------------------------------------------------
    
    # endregion
    # region Getters

    @property 
    def GetLoadFasteners(self) -> N2PGetLoadFasteners: 
        """
        Property that returns the get_load_fasteners attribute, that is, the N2PGetLoadFasteners instance that is being 
        used for this N2POptionalAttributes instance.
        """
        return self._get_load_fasteners
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def AdjacencyLevel(self) -> int: 

        """
        Property that returns the adjacency_level attribute, that is, the number of times the get_elements_attached() 
        function will be called when loading the new model.
        """

        return self._adjacency_level
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def LoadSecondModel(self) -> bool: 

        """
        Property that returns the load_second_model attribute, that is, whether or not a second model will be loaded 
        to obtain results in that model. 
        """

        return self._load_second_model
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def CornerData(self) -> bool: 
        
        """
        Property that returns the corner_data attribute, that is, whether or not there are results in the corners. 
        """
        
        return self._corner_data 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def MaterialFactorMetal(self) -> float: 
        
        """
        Property that returns the material_factor_metal attribute, that is, the material factor used to create the 
        bypass box for metallic plates.
        """
        
        return self._material_factor_metal 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def MaterialFactorComposite(self) -> float: 
        
        """
        Property that returns the material_factor_composite attribute, that is, the material factor used to create the 
        bypass box for composite plates.
        """
        
        return self._material_factor_composite
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def AreaFactor(self) -> float: 
        
        """
        Property that returns the area_factor attribute, that is, the area factor used to create the bypass box.
        """
        
        return self._area_factor
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def MaxIterations(self) -> int: 
        
        """
        Property that returns the max_iterations attribute, that is, the maximum number of iterations allowed to create 
        the bypass boxes.
        """
        
        return self._max_iterations 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def ProjectionTolerance(self) -> float: 
        
        """
        Property that returns the projection_tolerance attribute, that is, the tolerance used when determining if a 
        point lies within an element.
        """
        
        return self._projection_tolerance 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def DefaultDiameter(self) -> float: 

        """
        Property that returns the default_diameter attribute, that is, the diameter that will be assigned to joints 
        with no diameter.
        """
        
        return self._default_diameter
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def ExportPrecision(self) -> int: 

        """
        Property that returns the export_precision atribute, that is, the precision used when exporting the results to 
        a HDF5 file. It can be either 4 or 8.
        """
        
        return self._export_precision    
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def LoadCaseNumber(self) -> int: 

        """
        Property that returns the load_case_number attribute, that is, the number of load cases that are analyzed at 
        the same time. 
        """
        
        return self._load_case_number    
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def CompressionEqualsZero(self) -> bool: 

        """
        Property that returns the compression_equals_zero attribute, that is, whether or not the pullthrough force 
        will be set to zero when the fastener is compressed. 
        """
        
        return self._compression_equals_zero    
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def PullThroughAsIs(self) -> bool: 

        """
        Property that returns the pullthrough_as_is attribute, that is, whether or not the pullthrough force will be 
        set to the value found in the results files. 
        """
        
        return self._pullthrough_as_is    
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def ShearAsIs(self) -> bool: 

        """
        Property that returns the shear_as_is attribute, that is, whether or not the shear force will be set to the 
        value found in the results files or not. 
        """
        
        return self._shear_as_is    
    # ------------------------------------------------------------------------------------------------------------------

    # endregion 
    # region Setters 

    # Setters ----------------------------------------------------------------------------------------------------------        
    @AdjacencyLevel.setter 
    def AdjacencyLevel(self, value: int) -> None: 

        if not isinstance(value, int): 
            N2PLog.Warning.W527(value, int)
        else: 
            self._adjacency_level = value 
            if self.GetLoadFasteners.Model and self.GetLoadFasteners.JointsList and self.GetLoadFasteners.ResultsFiles: 
                self.GetLoadFasteners._N2PGetLoadFasteners__create_model() 
    # ------------------------------------------------------------------------------------------------------------------
    
    @LoadSecondModel.setter 
    def LoadSecondModel(self, value: bool) -> None: 

        if not isinstance(value, bool): 
            N2PLog.Warning.W527(value, bool)
        else: 
            self._load_second_model = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @CornerData.setter 
    def CornerData(self, value: bool) -> None: 

        if not isinstance(value, bool): 
            N2PLog.Warning.W527(value, bool)
        else: 
            self._corner_data = value 
    # ------------------------------------------------------------------------------------------------------------------

    @MaterialFactorMetal.setter 
    def MaterialFactorMetal(self, value: float) -> None: 
        
        if not isinstance(value, float) and not isinstance(value, int): 
            N2PLog.Warning.W527(value, float)
        else: 
            self._material_factor_metal = value 
    # ------------------------------------------------------------------------------------------------------------------

    @MaterialFactorComposite.setter 
    def MaterialFactorComposite(self, value: float) -> None: 
        
        if not isinstance(value, float) and not isinstance(value, int): 
            N2PLog.Warning.W527(value, float)
        else: 
            self._material_factor_composite = value 
    # ------------------------------------------------------------------------------------------------------------------

    @AreaFactor.setter 
    def AreaFactor(self, value: float) -> None: 
        
        if not isinstance(value, float) and not isinstance(value, int): 
            N2PLog.Warning.W527(value, float)
        else: 
            self._area_factor = value 
    # ------------------------------------------------------------------------------------------------------------------

    @MaxIterations.setter 
    def MaxIterations(self, value: int) -> None: 
        
        if not isinstance(value, int): 
            N2PLog.Warning.W527(value, int)
        else: 
            self._max_iterations = value 
    # ------------------------------------------------------------------------------------------------------------------

    @ProjectionTolerance.setter 
    def ProjectionTolerance(self, value: float) -> None: 
        
        if not isinstance(value, float) and not isinstance(value, int): 
            N2PLog.Warning.W527(value, float)
        else: 
            self._projection_tolerance = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @DefaultDiameter.setter 
    def DefaultDiameter(self, value: float) -> None: 

        if not isinstance(value, float) and not isinstance(value, int): 
            N2PLog.Warning.W527(value, float)
        else: 
            self._default_diameter = value 
    # ------------------------------------------------------------------------------------------------------------------

    @ExportPrecision.setter 
    def ExportPrecision(self, value: int) -> None: 

        if not isinstance(value, int): 
            N2PLog.Warning.W527(value, int)
        else: 
            if value == 4 or value == 8: 
                self._export_precision = value 
            else: 
                N2PLog.Warning.W528()
    # ------------------------------------------------------------------------------------------------------------------

    @LoadCaseNumber.setter 
    def LoadCaseNumber(self, value: int) -> None: 

        if not isinstance(value, int): 
            N2PLog.Warning.W527(value, int)
        else: 
            self._load_case_number = value 
    # ------------------------------------------------------------------------------------------------------------------

    @CompressionEqualsZero.setter 
    def CompressionEqualsZero(self, value: bool) -> None: 

        if not isinstance(value, bool): 
            N2PLog.Warning.W527(value, bool)
        else: 
            self._compression_equals_zero = value 
    # ------------------------------------------------------------------------------------------------------------------

    @PullThroughAsIs.setter 
    def PullThroughAsIs(self, value: bool) -> None: 

        if not isinstance(value, bool): 
            N2PLog.Warning.W527(value, bool)
        else: 
            self._pullthrough_as_is = value 
    # ------------------------------------------------------------------------------------------------------------------

    @ShearAsIs.setter 
    def ShearAsIs(self, value: bool) -> None: 

        if not isinstance(value, bool): 
            N2PLog.Warning.W527(value, bool)
        else: 
            self._shear_as_is = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    # endregion 