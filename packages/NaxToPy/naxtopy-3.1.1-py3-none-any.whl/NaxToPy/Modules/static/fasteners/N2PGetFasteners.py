# region Imports 

"""
The N2PGetFasteners class is used to obtain all necessary geometrical information about a model's fasteners, including 
the creation of N2PJoint, N2PBolt, and N2PPlate objects. The instance of this class must be prepared using the 
required properties before calling its method calculate(). 
"""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

import os 
import numpy as np 
import sys 
from time import time 
from typing import Union 

from NaxToPy import N2PLog
from NaxToPy.Core.N2PModelContent import N2PModelContent 
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Modules.common.data_input_hdf5 import DataEntry 
from NaxToPy.Modules.common.hdf5 import HDF5_NaxTo
from NaxToPy.Modules.static.fasteners.joints.N2PAttachment import N2PAttachment
from NaxToPy.Modules.static.fasteners.joints.N2PBolt import N2PBolt 
from NaxToPy.Modules.static.fasteners.joints.N2PJoint import N2PJoint
from NaxToPy.Modules.static.fasteners.joints.N2PPlate import N2PPlate 
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysis.Core.Functions.N2PGetAttachments import get_attachments

# endregion 
# region GetFasteners

class N2PGetFasteners: 

    """
    The N2PGetFasteners class is used to obtain all necessary geometrical information about a model's fasteners, 
    including the creation of N2PJoint, N2PBolt, and N2PPlate objects.

    Properties: 
        Model: N2PModelContent -> N2PModelContent object representing the model to be analysed. 
        GetAttachmentsBool: bool -> boolean that shows if the attachments will be calculated or not. 
        GetDistanceBool: bool -> boolean that shows if the distance attribute will be calculated or not for plates. 
        Thresh: float -> numerical tolerance used in the creation of the joints. 
        ElementList: list[N2PElement] -> list of 1D elements to be transformed into joints. Currently, only CFAST and 
        CWELD elements are supported.
        JointsList: list[N2PJoint] -> list of N2PJoint objects representing the transformed fasteners. 
        PlateList: list[N2PPlate] -> list of N2PPlate objets representing the transformed plates. 
        AttachmentsList: list[N2PAttachment] -> list of N2PAttachment objects representing fasteners that join exactly 
        the same part of a model. 
        ExportLocation: str -> path to the .h5 file in which results will be exported. 
    """

    __slots__ = ("_model", 
                 "_get_attachments_bool", 
                 "_get_distance_bool", 
                 "_thresh", 
                 "_element_list", 
                 "_export_location", 
                 "_joints_list", 
                 "_attachments_list", 
                 "_error", 
                 "_max_error_counter")

    # N2PGetFasteners constructor --------------------------------------------------------------------------------------
    def __init__(self): 

        """
        The constructor creates an empty N2PGetFasteners instance. Its attributes must be added as properties.

        Calling example: 
            >>> import NaxToPy as NP 
            >>> from NaxToPy.Modules.Fasteners.N2PGetFasteners import N2PGetFasteners
            >>> model1 = NP.load_model(r"route.fem") # Model is loaded 
            >>> fasteners = N2PGetFasteners()
            >>> fasteners.Model = model1 # Compulsory input
            >>> fasteners.ElementList = model1.get_elements([10, 11, 12, 13, 14]) # Only some joints are to be 
            analyzed (optional but recommended)
            >>> fasteners.Thresh = 1.5 # Custom threshold is selected (optional)
            >>> fasteners.GetAttachmentsBool = False # Attachments will not be obtained; True by default
            >>> fasteners.GetDistanceBool = True # The distance attribute will be obtained, False by default 
            >>> fasteners.ExportLocation = r"folder_route" # Results are exported to an hdf5 file
            >>> fasteners.calculate()
        """

        self._model: N2PModelContent = None 
        self._get_attachments_bool: bool = True 
        self._get_distance_bool: bool = False 

        self._thresh: float = 2.0 
        self._element_list: list[N2PElement] = None 
        self._export_location: str = None 

        self._joints_list: list[N2PJoint] = None  
        self._attachments_list: list[N2PAttachment] = None 

        self._error: bool = False 
        self._max_error_counter: int = 10
    # ------------------------------------------------------------------------------------------------------------------
        
    # endregion
    # region Getters 

    # Getters ----------------------------------------------------------------------------------------------------------
    @property 
    def Model(self) -> N2PModelContent: 

        """
        Property that returns the model attribute, that is, the model to be analyzed. 
        """
        
        return self._model 
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def GetAttachmentsBool(self) -> bool: 

        """
        Property that returns the get_attachments_bool attribute, that is, the boolean that shows if the 
        get_attachments() method will be used inside calculate().
        """
        
        return self._get_attachments_bool
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def GetDistanceBool(self) -> bool: 

        """
        Property that returns the get_distance_bool attribute, that is, the boolean that shows if the Distance and 
        DistanceVector attributes will be calculated. 
        """
        
        return self._get_distance_bool
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def Thresh(self) -> float: 

        """
        Property that returns the thresh attribute, that is, the tolerance used in the obtention of N2PJoints. 
        """

        return self._thresh
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def ElementList(self) -> list[N2PElement]: 

        """
        Property that returns the element_list attribute, that is, the list of the loaded CFASTs. 
        """

        return self._element_list 
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
        Property that returns the list of N2PPlates. 
        """
        
        return [j for i in self.JointsList for j in i.PlateList]
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def AttachmentsList(self) -> list[N2PAttachment]: 

        """
        Property that returns the attachments_list attribute, that is, the list of N2PAttachments. 
        """
        
        return self._attachments_list 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def ExportLocation(self) -> str: 

        """
        Property that returns the export_location attribute, that is, the path where the results are to be exported. 
        """
        
        return self._export_location
    # ------------------------------------------------------------------------------------------------------------------

    # endregion
    # region Setters 

    # Setters ----------------------------------------------------------------------------------------------------------
    @Model.setter 
    def Model(self, value: N2PModelContent) -> None: 

        if not isinstance(value, N2PModelContent): 
            self._error = True 
            N2PLog.Error.E535(value, N2PModelContent)
        else: 
            self._model = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @GetAttachmentsBool.setter 
    def GetAttachmentsBool(self, value: bool) -> None: 

        if not isinstance(value, bool): 
            N2PLog.Warning.W527(value, bool)
        else: 
            self._get_attachments_bool = value 
    # ------------------------------------------------------------------------------------------------------------------

    @GetDistanceBool.setter 
    def GetDistanceBool(self, value: bool) -> None: 

        if not isinstance(value, bool): 
            N2PLog.Warning.W527(value, bool)
        else: 
            self._get_distance_bool = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @Thresh.setter
    def Thresh(self, value: float) -> None: 

        if not isinstance(value, float) and not isinstance(value, int): 
            N2PLog.Warning.W527(value, float)
        else: 
            self._thresh = value 
    # ------------------------------------------------------------------------------------------------------------------

    @ElementList.setter 
    def ElementList(self, value: Union[list[N2PElement], tuple[N2PElement], set[N2PElement], N2PElement]) -> None: 

        if type(value) == tuple or type(value) == set: 
            value = list(value) 
        elif type(value) == N2PElement: 
            value = [value]
        elif type(value) == list: 
            pass 
        else: 
            N2PLog.Warning.W527(value, list)

        for i in value: 
            if not isinstance(i, N2PElement) or i.TypeElement in {"CQUAD4", "CTRIA3"}: 
                N2PLog.Warning.W527(i, N2PElement)
                value.remove(i)

        if value == []: 
            self._error = True 
            N2PLog.Error.E520("ElementList", N2PElement)
        else: 
            self._element_list = value 
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

    # endregion 
    # region Public methods 

    # Method used to create all joints, plates and bolts ---------------------------------------------------------------
    def get_joints(self) -> None: 

        """
        Method used to create all N2PJoints, N2PPlates and N2PBolts and assign them certain useful attributes.

        The following steps are followed: 
            1. All N2PJoints are created. Inside this, all N2PBolts and N2PPlates associated to each N2PJoint are also 
            created. 
            2. All N2PBolts, N2PPlates are assigned certain important attributes, such as CentralElement or 
            ElementList. 

        Calling example: 
            >>> fasteners.get_joints()
        """

        t1 = time() 
        # If the model has not been loaded, an error appears
        if self.Model is None: 
            self._error = True 
            N2PLog.Error.E521() 
            return None 

        # The N2Joints are created from the C# core 
        if self.ElementList:
            globalIDList = [i.InternalID for i in self.ElementList]
            n2joints = self.Model._N2PModelContent__vzmodel.GetJoints(self._thresh, global_id_list = globalIDList)
        else:  
            n2joints = self.Model._N2PModelContent__vzmodel.GetJoints(self._thresh)


        # N2PJoints are created from the N2Joints
        self._joints_list = [N2PJoint(i, self._model.ModelInputData) for i in n2joints]
                
        elementList = list(self.Model.ElementsDict.values())
        for i in self.PlateList: 
            # Plates are assigned their elements as attributes 
            i._element_list = [elementList[j] for j in i.GlobalID]
            i._central_element = self.Model.get_elements(i.PlateCentralCellSolverID)
        for i in self.JointsList: 
            # Bolts are assigned their elements as an attribute 
            i.Bolt._element_list = [elementList[j] for j in i.Bolt.OneDimElemsIDList]
        # Broken joints are removed   
        brokenJoints = [j for j in self.JointsList if j.PlateList == [] or not j.PlateList]
        if len(brokenJoints) != 0: 
            N2PLog.Warning.W529([l for k in brokenJoints for l in k.BoltElementIDList])
        for i in brokenJoints: 
            self._joints_list.remove(i)
        if self.JointsList is None or self.JointsList == []: 
            self._error = True 
            N2PLog.Error.E525()

        t2 = time()
        N2PLog.Debug.D601(t2, t1)
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to obtain the distance from each N2PBolt to its N2PPlates' edge --------------------------------------
    def get_intersection(self) -> None: 

        """
        Method used to obtain the distance from every N2PPlate's edge to its N2PJoint (optional), the intersection 
        between an N2PPlate and its N2PJoint, the perpendicular direction to the N2PPlates, the A and B CFASTs for each 
        plate, and their direction and factor. The get_joints() method must be used before this one. Otherwise, an 
        error will occur. 

        Calling example: 
            >>> fasteners.get_intersection() 
        """

        t1 = time() 
        # If the list of joints has not been obtained (because this method has been called before the previous one), an 
        # error appears 
        if self.JointsList is None: 
            N2PLog.Warning.W532() 
            self.get_joints()

        # Only CQUAD4 and CTRIA3 elements are supported. 
        supportedElements = {"CQUAD4", "CTRIA3"}
        domain = {i for i in self.Model.get_elements() if i.TypeElement in supportedElements}
        # The get_intersection method is called for each N2PJoint 
        errorCounter = 0 
        for j in self.JointsList: 
            errorCounter = j.get_intersection(self.Model, domain, self.GetDistanceBool, errorCounter, 
                                              self._max_error_counter) 
        N2PLog.set_console_level("WARNING")
        t2 = time()
        N2PLog.Debug.D605(t2, t1)
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to obtain a list of attachments ----------------------------------------------------------------------
    def get_attachments(self) -> None: 


        """
        Method used to obtain the list of N2PAttachments and calculate their pitch. The get_joints() method must be 
        used before this one. Otherwise, an error will occur. 

        Calling example: 
            >>> fasteners.get_attachments() 
        """

        t1 = time()
        # If the plates do not have a Intersection attribute (because this method has been called before the previous 
        # one), an error appears 
        if self.PlateList[0].Intersection is None: 
            N2PLog.Warning.W533() 
            self.get_intersection()

        # Attachments are obtained 
        self._attachments_list = get_attachments(self.Model, self.JointsList)
        # The pitch is obtained for each N2PAttachment 
        for i in self.AttachmentsList: 
            i.get_pitch()
        t2 = time()
        N2PLog.Debug.D603(t2, t1)
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to use all previous methods --------------------------------------------------------------------------
    def calculate(self) -> None: 

        """
        Method used to do all the previous calculations. 

        Calling example: 
            >>> fasteners.calculate()
        """

        if self._error: 
            return None 
        self.get_joints() 
        if self._error: 
            return None 
        self.get_intersection() 
        if self.GetAttachmentsBool: 
            self.get_attachments()
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to export the obtained PAG results as a HDF5 file ----------------------------------------------------
    def export_fasteners(self): 

        """
        Method used to export the fasteners to an HDF5 file. The first plate in the array will get the value -1000, the 
        last plate in the array will get the value 1000, and all the middle plates will get the value 0. 

        Calling example: 
            >>> fasteners.export_fasteners() 
        """

        hdf5 = HDF5_NaxTo() 
        hdf5.FilePath = self.ExportLocation 
        hdf5.create_hdf5() 
        dataInput = DataEntry() 
        dataInput.DataInputName = "PLATE'S GEOMETRICAL INFORMATION"
        inputDataType = np.dtype([("FIRST PLATE", "f4"), ("MIDDLE PLATES", "f4"), ("LAST PLATE", "f4")])
        dataInput.DataInput = np.array([(-1000.0, 0.0, 1000.0)], inputDataType)
        hdf5._modules_input_data([dataInput])
        dataEntryList = [] 
        for joint in self.JointsList:
            for n, p in enumerate(joint.PlateList): 
                partDict = self.Model._N2PModelContent__StrPartToID
                platePart = str((partDict.get(p.PartID[0]), p.PartID[0]))

                dataType = np.dtype([("ID_ENTITY", "i4"), ("VALUE", "f4")])

                if n == 0: 
                    value = -1000.0
                elif n == len(joint.PlateList) - 1: 
                    value = 1000.0 
                else: 
                    value = 0.0 

                resultList = np.array([(p.PlateCentralCellSolverID, value)], dataType) 
                dataInput = np.array([()])

                dataEntry = DataEntry() 
                dataEntry.ResultsName = "FASTENERS"
                dataEntry.LoadCase = 0 
                dataEntry.LoadCaseName = "NO_LOADCASE"
                dataEntry.Section = "None"
                dataEntry.Part = platePart 
                dataEntry.Data = resultList
                dataEntryList.append(dataEntry)
        hdf5.write_dataset(dataEntryList)
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to flip the list of plates of the necessary joints 
    def flip_plates(self) -> None: 

        """
        Method used to flip some plate lists. 

        Calling example: 
            >>> fasteners.flip_plates()
        """

        for i in self.JointsList: 
            if i.SwitchPlates: 
                i.PlateList.reverse()
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to assign a certain diameter to some of the joints ---------------------------------------------------
    def assign_diameter(self, elementList: list[N2PElement], diameter: float) -> None: 

        """
        Method used to assign a certain diameter to some joints, as defined by the N2PElements of their fastener. 
        
        Args: 
            elementList: list[N2PElement] -> list of the N2PElements that make up the fasteners 
            diameter: float -> diameter to be assigned

        Calling example: 
            >>> fasteners.assign_diameter([fasteners.Model.get_elements(50052541, 50052538, 50052544)], 6.4)
        """

        newJointsList = {}
        elementIDList = [element.ID for element in elementList]
        newJointsList = {joint for joint in self.JointsList for element in joint.BoltElementIDList 
                         if element in elementIDList and joint not in newJointsList}
        for joint in newJointsList: 
            joint.Diameter = diameter 
    # ------------------------------------------------------------------------------------------------------------------