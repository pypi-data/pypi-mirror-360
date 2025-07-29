# region Imports 

"""
Class that represents a single joint, that is, a N2PBolt and a series of N2PPlate objects. 
"""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

import csv
import numpy as np 
from typing import Literal 

from NaxToPy import N2PLog
from NaxToPy.Core.N2PModelContent import N2PModelContent
from NaxToPy.Core.Classes.N2PAbaqusInputData import * 
from NaxToPy.Core.Classes.N2PElement import N2PElement 
from NaxToPy.Core.Classes.N2PLoadCase import N2PLoadCase
from NaxToPy.Core.Classes.N2PNastranInputData import * 
from NaxToPy.Core.Classes.N2PNode import N2PNode
from NaxToPy.Modules.static.fasteners.joints.N2PAttachment import N2PAttachment 
from NaxToPy.Modules.static.fasteners.joints.N2PBolt import N2PBolt 
from NaxToPy.Modules.static.fasteners.joints.N2PFastenerSystem import N2PFastenerSystem
from NaxToPy.Modules.static.fasteners.joints.N2PJointAnalysisParameters import N2PJointAnalysisParameters
from NaxToPy.Modules.static.fasteners.joints.N2PPlate import N2PPlate 
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysis.Core.Functions.N2PRotation import angle_between_2_systems, \
     point_in_element, system_to_matrix

# endregion 
# region N2PJoint 

class N2PJoint: 

    """
    Class that represents a single joint, that is, a N2PBolt and a series of N2PPlate objects. 

    Properties: 
        Diameter: float -> joint's diameter. 
        Bolt: N2PBolt -> associated N2PBolt. 
        ID: int -> joint's internal identificator. 
        TypeFastener: str -> type of joint. 
        PlateList: list[N2PPlate] -> list of unique N2PPlates associated to the N2PJoint. 
        SwitchPlates: bool -> boolean that shows if the joint's plates have to be switched. 
        PartID: str -> joint's part ID. 
        BoltElementList: list[N2PElement] -> list of N2PElements that make up the bolt. 
        BoltElementIDList: list[int] -> list of the IDs of the elements that make up the bolt. 
        BoltElementInternalIDList: list[int] -> list of the internal IDs of the elements that make up the bolt. 
        BoltNodeList: list[N2PNode] -> list of N2PNodes that make up the bolt. 
        PlateElementList: list[list[N2PElement]] -> list of N2PElements that make up the plates. 
        PlateElementIDList: list[list[int]] -> list of the IDs of the elements that make up the plates. 
        PlateElementInternalIDList: list[list[int]] -> list of the internal IDs of the elements that make up the plates. 
        PlateNodeList: list[list[tuple[N2PNode]]] -> list of N2PNodes that make up the plates. 
        PlatePartID: list[str] -> list of the part IDs of the plates. 
        Attachment: N2PAttachment -> joint's attachment. 
        Pitch: float -> joint's pitch.
        FastenerSystem: N2PFastenerSystem -> joint's Fastener System associated
        JointAnalysisParameters: N2PJointAnalysisParameters -> joint's Analysis Parameter associated
    """

    __slots__ = ("__info__", 
                 "__input_data_father__", 
                 "_diameter", 
                 "_bolt", 
                 "_plate_list", 
                 "_switch_plates", 
                 "_attachment", 
                 "_attached_elements", 
                 "_pitch",
                 "_fastener_system",
                 "_joint_analysis_parameters"
                 )

    # N2PJoint constructor ---------------------------------------------------------------------------------------------
    def __init__(self, info, input_data_father): 

        """
        In this constructor, the N2PBolt associated to the N2PJoint is created. Also, all N2PPlates associated to the 
        N2PJoint are created and then some of them are removed if two (or more) of them share the same solver ID (that 
        is, the same N2PElements are associated to both N2PPlates). 
        """
        
        self.__info__ = info 
        self.__input_data_father__ = input_data_father 

        self._diameter: float = None 
        self._bolt: N2PBolt = N2PBolt(self.__info__.Bolt, self.__input_data_father__) 
        self._bolt._joint = self
        
        if self.__info__.Plates and not None in list(self.__info__.Plates): 
            self._plate_list = [N2PPlate(i, self.__input_data_father__) for i in self.__info__.Plates]
            for i in self._plate_list: 
                i._joint = self 
        else: 
            self._plate_list = []
        self._switch_plates: bool = False 

        self._attachment: N2PAttachment = None 
        self._attached_elements: set[N2PElement] = None 
        self._pitch: float = None 
        self._fastener_system: N2PFastenerSystem = None
        self._joint_analysis_parameters: N2PJointAnalysisParameters = None
    # ------------------------------------------------------------------------------------------------------------------
        
    # region Getters 

    # Getters ----------------------------------------------------------------------------------------------------------
    @property 
    def Diameter(self) -> float: 

        """
        Property that returns the diameter attribute, that is, the joint's diameter. 
        """

        return self._diameter
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def Bolt(self) -> N2PBolt: 

        """
        Property that returns the bolt attribute, that is, the N2PBolt associated to the N2PJoint. 
        """
        
        return self._bolt
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def ID(self) -> int: 

        """
        Property that returns the joint's internal identificator. 
        """
    
        return self.Bolt.ID 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def TypeFastener(self) -> str: 

        """
        Property that returns the type of joint that is being used. 
        """
        
        return self.Bolt.Type
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def PlateList(self) -> list[N2PPlate]: 

        """
        Property that returns the plate_list attribute, that is, the list of N2PPlates associated to the N2PJoint. 
        """
        
        return self._plate_list
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def SwitchPlates(self) -> bool: 

        """
        Property that returns the switch_plates attribute, that is, whether the joint's plates have to be switched or 
        not. 
        """
        
        return self._switch_plates
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def PartID(self) -> int: 

        """
        Property that returns the part ID of the elements that make up the bolt. 
        """

        return self.Bolt.PartID 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def BoltElementList(self) -> list[N2PElement]: 

        """
        Property that returns the list of N2PElements that make up the joint's bolt. 
        """
        
        return self.Bolt.ElementList 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def BoltElementIDList(self) -> list[int]: 

        """
        Property that returns the list of the IDs of the N2PElements that make up the joint's bolt. 
        """
        
        return self.Bolt.ElementIDList
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def BoltElementInternalIDList(self) -> list[int]: 

        """
        Property that returns the list of the internal IDs of the N2PElements that make up the joint's bolt.
        """

        return self.Bolt.ElementInternalIDList
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def BoltNodeList(self) -> list[N2PNode]: 

        """
        Property that returns the list of N2PNodes that make up the joint's bolt. 
        """
        
        return self.Bolt.NodeList
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def PlateElementList(self) -> list[list[N2PElement]]: 

        """
        Property that returns the list of N2PElements that make up the joint's plates. 
        """
    
        return [j.ElementList for j in self.PlateList]
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def PlateElementIDList(self) -> list[list[int]]: 

        """
        Property that returns the list of the IDs of the N2PElements that make up the joint's plates. 
        """
        
        return [j.ElementIDList for j in self.PlateList]
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def PlateElementInternalIDList(self) -> list[list[int]]: 

        """
        Property that returns the internal ID of the N2PElements that make up the joint's plates. 
        """

        return [j.ElementInternalIDList for j in self.PlateList]
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def PlateNodeList(self) -> list[list[tuple[N2PNode]]]: 

        """
        Property that returns the list of N2PNodes that make up the joint's plates. 
        """
        
        return [j.NodeList for j in self.PlateList]
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def PlatePartID(self) -> list[str]: 

        """
        Property that returns the part ID of each element that makes up the plates. 
        """

        return [j.PartID for j in self.PlateList]
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Attachment(self) -> N2PAttachment: 

        """
        Property that returns the attachment attribute, that is, the joint's N2PAttachment. 
        """

        return self._attachment
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Pitch(self) -> float: 

        """
        Property that returns the pitch attribute, that is, the joint's pitch. 
        """

        return self._pitch
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def FastenerSystem(self) -> N2PFastenerSystem: 

        """
        Property that returns the N2PFastenerSystem of the joint. 
        """

        return self._fastener_system
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def JointAnalysisParameters(self) -> N2PJointAnalysisParameters: 

        """
        Property that returns the N2PJointAnalysisParameters of the joint.
        """

        return self._joint_analysis_parameters
    # ------------------------------------------------------------------------------------------------------------------

    # endregion 
    # region Setters 

    # Setters ----------------------------------------------------------------------------------------------------------
    @Diameter.setter 
    def Diameter(self, value: float) -> None: 

        if not isinstance(value, float) and not isinstance(value, int): 
            N2PLog.Warning.W527(value, float)
        else: 
            self._diameter = value
    # ------------------------------------------------------------------------------------------------------------------

    @SwitchPlates.setter 
    def SwitchPlates(self, value: bool) -> None: 

        if not isinstance(value, bool): 
            N2PLog.Warning.W527(value, bool)
        else: 
            self._switch_plates = value
    # ------------------------------------------------------------------------------------------------------------------
    
    @FastenerSystem.setter 
    def FastenerSystem(self, value: N2PFastenerSystem) -> None: 

        if not isinstance(value, N2PFastenerSystem): 
            N2PLog.Warning.W527(value, N2PFastenerSystem)
        else: 
            self._fastener_system = value
    # ------------------------------------------------------------------------------------------------------------------

    @JointAnalysisParameters.setter 
    def JointAnalysisParameters(self, value: N2PJointAnalysisParameters) -> None: 

        if not isinstance(value, N2PJointAnalysisParameters): 
            N2PLog.Warning.W527(value, N2PJointAnalysisParameters)
        else: 
            self._joint_analysis_parameters = value
    # ------------------------------------------------------------------------------------------------------------------
    
    # endregion 
    # region Public methods 

    # Method used to obtain the intersection point of a N2PPlate -------------------------------------------------------
    def get_intersection(self, model: N2PModelContent = None, domain: set[N2PElement] = None, 
                         getDistanceBool: bool = False, errorCounter: int = 0, maxErrorCounter: int = 50): 
        
        """
        Method that calculates the intersection point of a N2PPlate, its normal, its A and B CFASTs, their direction 
        and factor and, optionally, the distance from each N2PJoint to the closest free edge. 

        Args: 
            model: N2PModelContent 
            domain: set[N2PElement] -> domain of elements to be searched 
            getDistanceBool: bool -> boolean that shows if the actual distance will be calculated or not

        The following steps are followed: 
            1. The intersection points between every N2PPlate and its N2PJoint is obtained, as well as its normal 
            direction. 
            2. The A and B bolts are assigned for each plate, as well as the CFAST factor and the bolt direction using 
            the position of the nodes, their normal direction and the content of their cards. 
            3. All the elements that are attached to the element where the intersection point is are retrieved using 
            the function “get_elements_attached”. Right after this, “get_free_edges” obtains a list of segments from  
            the attached elements which define the free edges of the selection.
            4. Finally, the distance between the intersection point to each segments is obtained and compared to the 
            rest in order to get the minimum one, which is of course the desired value. 

        Calling example: 
            >>> myJoint.get_intersection(model1, domain, True)
        """
        
        boltNodes = [j for i in self.BoltNodeList for j in i]
        s = set() 
        for i in boltNodes: 
            if i not in s: 
                s.add(i) 
            else: 
                boltNodes.remove(i)
        intersection = [i.GlobalCoords for i in boltNodes]
        # Of course, one distance will be needed form every N2PPlate in the N2PJoint. 
        for index, p in enumerate(self.PlateList): 

            if len(p.ElementList) == 0: 
                # An error appears if a plate has no elements due to a problem with its geometry 
                errorCounter = errorCounter + 1
                if errorCounter == maxErrorCounter: 
                    N2PLog.Warning.W546(512)
                    N2PLog.set_console_level("ERROR")
                N2PLog.Warning.W512(p, self)
                continue

            plateElem = p.CentralElement 

            # The normal direction to the plate is obtained by using three of its nodes 
            nodesCoords = [np.array(i.GlobalCoords) for i in plateElem.Nodes]
            normalPlane = np.cross(nodesCoords[2] - nodesCoords[0], nodesCoords[1] - nodesCoords[0]) 
            normalPlane = normalPlane / np.linalg.norm(normalPlane)

            p._normal = normalPlane.tolist()            
            p._intersection = list(intersection[index])
            
            p._bolt_element_list = {"A": None, "B": None}
            p._bolt_direction = {"A": None, "B": None}
            p._cfast_factor = {"A": 0, "B": 0} 
            # for k in range(len(self.BoltElementList)): 
                # The direction of the fastener is obtained through its nodes 
                # dir = (np.array(self.BoltElementList[k].Nodes[1].GlobalCoords) - \
                #         np.array(self.BoltElementList[k].Nodes[0].GlobalCoords))
                # dir = dir / np.linalg.norm(dir) 
                # if p.Normal @ dir > 0: 
                #     if k == index: # nodo A, n = n 
                #         p._bolt_element_list["B"] = self.BoltElementList[k]
                #         p._bolt_direction["B"] = "->"
                #         p._cfast_factor["B"] = 1 
                #     if k + 1 == index: # nodo B, n = n 
                #         p._bolt_element_list["A"] = self.BoltElementList[k]
                #         p._bolt_direction["A"] = "->"
                #         p._cfast_factor["A"] = -1 
                # else: 
                #     if k == index: # nodo A, n = -n 
                #         p._bolt_element_list["A"] = self.BoltElementList[k]
                #         p._bolt_direction["A"] = "<-"
                #         p._cfast_factor["A"] = 1 
                #     if k + 1 == index: # nodo B, n = -n 
                #         p._bolt_element_list["B"] = self.BoltElementList[k]
                #         p._bolt_direction["B"] = "<-"
                #         p._cfast_factor["B"] = -1 
        directionJoint = np.array(self.PlateList[-1].Intersection) - np.array(self.PlateList[0].Intersection)
        for index, p in enumerate(self.PlateList): 
            directionPlate = np.array(p.CentralElement.ElemSystemArray[-3:]) 
            if directionPlate @ directionJoint > 0: 
                if index == 0: 
                    p._bolt_element_list["A"] = self.BoltElementList[0]
                    p._cfast_factor["A"] = 1 
                    if np.array(self.BoltElementList[0].ElemSystemArray[:3]) @ directionJoint > 0: 
                        p._bolt_direction["A"] = "->"
                    else: 
                        p._bolt_direction["A"] = "<-"
                elif p == self.PlateList[-1]: 
                    p._bolt_element_list["B"] = self.BoltElementList[-1]
                    p._cfast_factor["B"] = 1 
                    if np.array(self.BoltElementList[-1].ElemSystemArray[:3]) @ directionJoint > 0: 
                        p._bolt_direction["B"] = "->"
                    else: 
                        p._bolt_direction["B"] = "<-"
                else: 
                    p._bolt_element_list["A"] = self.BoltElementList[index]
                    p._cfast_factor["A"] = 1 
                    p._bolt_element_list["B"] = self.BoltElementList[index - 1]
                    p._cfast_factor["B"] = -1 
                    if np.array(self.BoltElementList[index].ElemSystemArray[:3]) @ directionJoint > 0: 
                        p._bolt_direction["A"] = "->"
                    else: 
                        p._bolt_direction["A"] = "<-"
                    if np.array(self.BoltElementList[index - 1].ElemSystemArray[:3]) @ directionJoint > 0: 
                        p._bolt_direction["B"] = "->"
                    else: 
                        p._bolt_direction["B"] = "<-"
            else: 
                if index == 0: 
                    p._bolt_element_list["B"] = self.BoltElementList[0]
                    p._cfast_factor["B"] = 1 
                    if np.array(self.BoltElementList[0].ElemSystemArray[:3]) @ directionJoint > 0: 
                        p._bolt_direction["B"] = "->"
                    else: 
                        p._bolt_direction["B"] = "<-"
                elif p == self.PlateList[-1]: 
                    p._bolt_element_list["A"] = self.BoltElementList[-1]
                    p._cfast_factor["A"] = -1 
                    if np.array(self.BoltElementList[-1].ElemSystemArray[:3]) @ directionJoint > 0: 
                        p._bolt_direction["A"] = "->"
                    else: 
                        p._bolt_direction["A"] = "<-"
                else: 
                    p._bolt_element_list["B"] = self.BoltElementList[index]
                    p._cfast_factor["B"] = 1 
                    p._bolt_element_list["A"] = self.BoltElementList[index - 1]
                    p._cfast_factor["A"] = -1 
                    if np.array(self.BoltElementList[index - 1].ElemSystemArray[:3]) @ directionJoint > 0: 
                        p._bolt_direction["A"] = "->"
                    else: 
                        p._bolt_direction["A"] = "<-"
                    if np.array(self.BoltElementList[index].ElemSystemArray[:3]) @ directionJoint > 0: 
                        p._bolt_direction["B"] = "->"
                    else: 
                        p._bolt_direction["B"] = "<-"


            # The plate's free edges are obtained
            if getDistanceBool: 
                attachedElementsOld = model.get_elements_attached([plateElem])
                attachedElements = {element for element in attachedElementsOld if element in domain}
                p._attached_elements = attachedElements
                freeEdges = model.get_free_edges(attachedElements)
                p._free_edges = freeEdges
                intersectionPlate = p.Intersection 

                A = np.array([j[1].GlobalCoords for j in freeEdges])
                B = np.array([j[2].GlobalCoords for j in freeEdges])
                edgeVectors = B - A 
                lengths2 = np.sum(edgeVectors**2, axis = 1)
                relativePosition = intersectionPlate - A 
                ts = np.clip(np.einsum('ij,ij->i', relativePosition, edgeVectors) / lengths2, 0, 1)
                closestPoints = A + ts[:, np.newaxis] * edgeVectors 
                distanceVectors = closestPoints - intersectionPlate 
                distances2 = np.sum(distanceVectors**2, axis = 1)
                minID = np.argmin(distances2) 
                p._distance = distances2[minID] ** 0.5
                p._distance_vector = distanceVectors[minID]
        return errorCounter
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to obtain the model's forces -------------------------------------------------------------------------
    def get_forces(self, results: np.ndarray, loadCaseList: list[N2PLoadCase], compressionEqualsZero: bool = True, 
                   pullThroughAsIs: bool = True, shearAsIs: bool = True, 
                   typeAnalysis: Literal["PAG", "ALTAIR"] = "PAG"): 
        """
        Method that takes an N2PJoint and obtains its 1D forces, as well as the 1D forces associated to each of its 
        N2PPlates. Forces will be obtained as N2PPlate or N2PBolt attributes as dictionaries in the form: 
                {Load Case ID: [FX, FY, FZ]}    or      {Load Case ID: F or Load Angle}
        depending on what is obtained. 

        Args: 
            results: np.ndarray -> results array. 
            loadCaseList: list[N2PLoadCase] -> load cases to be studied. 
            compressionEqualsZero: bool -> boolean that shows whether or not the pullthrough force is set to zero when 
            the fastener is compressed. 
            pullThroughAsIs: bool -> boolean that shows if the pullthrough is to be set to the value found in the 
            results file or not. 
            shearAsIs: bool -> boolean that shows if the shear force is to be set to the value found in the results 
            files or not. 
            typeAnalysis: Literal["PAG", "ALTAIR"] -> type of analysis that will be done. The difference is whether or 
            not plates pierced by two fasteners have a pullthrough force of 0

        The following attributes are obtained: 
            - shear_force: dictionary in the form {Load Case ID: Bolt Element ID: F} which represents the 1D force in 
            the bolt's element reference frame. It is a N2PBolt attribute. 
            - axial_force: dictionary in the form {Load Case ID: Bolt Element ID: F} which represents the axial force 
            (pulltrhrough force) in the 1st plate's material reference frame. It will be positive if the fastener is 
            extended or 0 if it is compressed. It is a N2PBolt attribute. 
            - translational_fastener_forces: dictionary in the form {Load Case ID: [[FX, FY, FZ], [FX, FY, FZ]]} which 
            represents the 1D forces that each the N2PElements associated to the N2PBolt associated to the N2PPlate 
            experience. It is represented in a local reference frame, in which the x-axis is the same as 
            the N2PPlate's material reference frame's x-axis, the z-axis is coincident with the axial direction of the 
            bolt and the y-axis is obtained via the cross product. If there is only one fastener attached to the plate, 
            the second list will be filled with zeros. It is a N2PPlate attribute. 
            - bearing_force: dictionary in the form {Load Case ID: [FX, FY, FZ]} which represents the 1D force 
            experienced by the bolt, as calculated by Altair. It takes into account if there are two CFASTs attached 
            to the plate and, if so, sums up their contributions. It is represented in the local reference frame and it 
            is a N2PPlate attribute. 
            - max_axial_force: dictionary in the form {Load Case ID: Bolt Element ID: F} which represents the maximum 
            axial force (bolt tension) of the whole bolt. It is a N2PBolt attribute.
            - load_angle: dictionary in the form {Load Case ID: Bolt Element ID: Angle} which represents the joint's 
            load angle in degrees. It is a N2PBolt attribute. 

        The following steps are followed: 
            1. Forces are adequately rotated into the plate's material reference frame. 
            2. The shear and axial forces are calculated with their formulas, as well as the load angle. 
            3. If there are two CFASTs attached to a plate, the shear and axial force may be updated. 
            4. The final force that the plate experiences (called here bearing_force) is obtained by adding the 
            contributions of both CFAST, if they exist, or taking into account if the existing CFAST is the A or B one. 

        Calling example: 
            >>> myForces = myJoint.get_forces(loads.Results, loads.LoadCases, False, False, False, "ALTAIR")
        """

        N = len(loadCaseList)
        for k in self.PlateList: 
            matSystem = k.BoxSystem 
            M = system_to_matrix(matSystem) 
            forces = [] 
            for l,m in k.BoltElementList.items(): 
                if not m: 
                    # If a fastener is not present, its contribution is filled with zeros 
                    forces.append([np.zeros(3) for _ in range(N)])
                else: 
                    system1D = m.ElemSystemArray 
                    S = system_to_matrix(system1D) 
                    fx, fy, fz = results[:,0:3,m.InternalID].T
                    f = np.array([fx, fy, fz]).T
                    forcesBolt = f@S@M.T*k.CFASTFactor[l]
                    if pullThroughAsIs: 
                        forcesBolt[:,2] = fx
                    forces.append(forcesBolt) 
                    # The axial force (bolt tension) is either 0, if the bolt is compressed, or the pullthrough force, 
                    # if it is extended
                    axialForce = np.maximum(fx, 0)
                    loadAngle = np.arctan2(forcesBolt[:,0], forcesBolt[:,1])
                    if shearAsIs: 
                        shearForce = np.linalg.norm(f[:,1:3], axis = 1)
                    else: 
                        shearForce = np.linalg.norm(forcesBolt[:,0:2], axis = 1)
                    for n, j in enumerate(loadCaseList): 
                        if not self.Bolt.AxialForce.get(j.ID): 
                            self._bolt._axial_force[j.ID] = {}
                            self._bolt._shear_force[j.ID] = {}
                            self._bolt._load_angle[j.ID] = {}
                        self._bolt._axial_force[j.ID][m.ID] = axialForce[n]
                        self._bolt._shear_force[j.ID][m.ID] = shearForce[n]
                        self._bolt._load_angle[j.ID][m.ID] = loadAngle[n]
            # The bearing force is obtained with the sum of the contributions of both potential fasteners 
            altairForce = forces[0] + forces[1]
            # If a plate is connected to two fasteners, its pullthrough force is set to zero for the PAG analysis
            if k.BoltDirection["A"] is not None and k.BoltDirection["B"] is not None and typeAnalysis == "PAG": 
                altairForce[:,2] = np.zeros(N)
            if compressionEqualsZero: 
                altairForce[:,2] = np.array([max(0,i) for i in altairForce[:,2]])
            for n,lc in enumerate(loadCaseList): 
                k._bearing_force[lc.ID] = altairForce[n]
                k._translational_fastener_forces[lc.ID] = np.array([forces[0][n], forces[1][n]])
        for n,lc in enumerate(loadCaseList): 
            self._bolt._max_axial_force[lc.ID] = max(self.Bolt.AxialForce[lc.ID].values())
    # ------------------------------------------------------------------------------------------------------------------