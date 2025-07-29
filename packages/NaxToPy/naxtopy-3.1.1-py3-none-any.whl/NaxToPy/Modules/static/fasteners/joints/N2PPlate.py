# region Imports 

"""
Class that represents a single plate. 
"""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING

from NaxToPy import N2PLog
from NaxToPy.Core.N2PModelContent import N2PModelContent 
from NaxToPy.Core.Classes.N2PAbaqusInputData import * 
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core.Classes.N2PLoadCase import N2PLoadCase
from NaxToPy.Core.Classes.N2PNastranInputData import * 
from NaxToPy.Core.Classes.N2PNode import N2PNode
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysis.Core.Functions.N2PInterpolation import interpolation
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysis.Core.Functions.N2PRotation import point_in_element, \
     rotate_tensor2D, system_to_matrix, transformation_for_interpolation
if TYPE_CHECKING:
    from NaxToPy.Modules.static.fasteners.joints.N2PBolt import N2PBolt
    from NaxToPy.Modules.static.fasteners.joints.N2PJoint import N2PJoint

# endregion 
# region N2PPlate 

class N2PPlate: 

    """
    Class that represents a single plate. 

    Attributes: 
        ID: int -> plate's internal identificator. 
        GlobalID: list[int] -> global identificator of the plate. 
        SolverID: list[int] -> list of the solver IDs of the N2PElements that make up the N2PPlate. 
        PlateCentralCellSolverID: int -> solver ID of one N2PElement that could represent the entire N2PPlate. 
        cards: list[N2PCard] -> list of the N2PCards associated to the plate's elements. 
        Joint: N2PJoint -> N2PJoint associated to the N2PPlate. Several N2PPlates will be associated to the same 
        N2PJoint. 
        Bolt: N2PBolt -> N2PBolt associated to the plate. 
        ElementList: list[N2PElement] -> list of N2PElements associated to the N2PPlate. 
        ElementIDList: list[int] -> list of the IDs of the elements associated to the plate. 
        ElementInternalIDList: list[int] -> list of the internal IDs of the elements associated to the plate. 
        NodeList: list[tuple[N2PNode]] -> list of N2PNodes associated to the N2PPlate. 
        PartID: part ID of the associated elements. 
        CentralElement: N2PElement -> N2PElement that could represent the entire N2PPlate. 
        BoltElementList: dict[str, N2PElement] -> dictionary in the form {CFAST A: N2PElement 1, CFAST B: N2PElement 2},
        corresponding to the A and B CFASTs associated to the plate. If one of the CFAST is not present, 0 is displayed.
        BoltDirection: dict[str, str] -> dictionary in the form {CFAST A: Arrow, CFAST B: Arrow}, corresponding to the 
        direction (-> or <-) of the A and B CFASTs. If one of them is not present, 0 is displayed. 
        CFASTFactor: dict[str, int] -> dictionary in the form {CFAST A: Factor, CFAST B: Factor}, corresponding to the 
        multiplication factor (1 or -1) of the A and B CFASTs. If one of them is not present, 0 is displayed. 
        AttachmentID: int -> ID that the plate receives when it goes through get_attachments
        Intersection: list[float] -> intersection point between the N2PPlate and its N2PBolt. 
        DistanceVector: np.ndarray -> distance (as a vector) from the N2PPlate's edge to its N2PBolt. 
        Distance: float -> distance from the N2PPlate's edge to its N2PBolt. 
        Normal: list[float] -> perpendicular direction to the N2PPlate. 
        switched_bolt_elements: bool = False -> internal flag showing if the CFASTs have been switched, which must be 
        considered to calculate the 1D forces. 
        BearingForce: dict[int, list[float]] -> dictionary in the form {Load Case ID: [FX, FY, FZ]} corresponding to 
        the X and Y bearing force, and the pullthrough force. 
        TranslationalFastenerForces: dict[int, list[list[float]]] -> dictionary in the form 
        {Load Case ID: [[FX, FY, FZ], [FX, FY, FZ]]} corresponding to the 1D forces that each the N2PElements 
        associated to the N2PBolt associated to the N2PPlate experience. 
        NxBypass: dict[int, float] -> dictionary in the form {Load Case ID: Nx} corresponding to the bypass force in 
        the x axis. 
        NxTotal: dict[int, float] -> dictionary in the form {Load Case ID: Nx} corresponding to the total force in the
        x axis. 
        NyBypass: dict[int, float] -> dictionary in the form {Load Case ID: Ny} corresponding to the bypass force in 
        the y axis. 
        NyTotal: dict[int, float] -> dictionary in the form {Load Case ID: Ny} corresponding to the total force in the
        y axis. 
        NxyBypass: dict[int, float] -> dictionary in the form {Load Case ID: Nxy} corresponding to the bypass force in 
        the xy axis. 
        NxyTotal: dict[int, float] -> dictionary in the form {Load Case ID: Nxy} corresponding to the total force in 
        the xy axis. 
        MxTotal: dict[int, float] -> dictionary in the form {Load Case ID: Mx} corresponding to the total moment in 
        the x axis. 
        MyTotal: dict[int, float] -> dictionary in the form {Load Case ID: My} corresponding to the total moment in 
        the y axis. 
        MxyTotal: dict[int, float] -> dictionary in the form {Load Case ID: Mxy} corresponding to the total moment in 
        the xy axis. 
        BypassMax: dict[int, float] -> dictionary in the form {Load Case: N} corresponding to the maximum bypass force. 
        BypassMin: dict[int, float] -> dictionary in the form {Load Case: N} corresponding to the minimum bypass force. 
        BypassSides: dict[int, list[list[float]]] -> dictionary in the form 
            {Load Case: [[NxNorth, NxSouth, NxWest, NxEast], [NyNorth, ...], [NxyNorth, ...], [MxNorth, ...], 
            [MyNorth, ...], [MxyNorth, ...]]}
        BoxDimension: float -> dimension of the box used in the bypass calculations. 
        BoxSystem: list[float] -> reference frame used to define the bypass box. 
        BoxPoints: dict[int, np.ndarray] -> dictionary in the form {1: coords, 2: coords, ..., 8: coords} including 
        each point's coordinates that was used for the bypass calculations. 
        BoxElements: dict[int, N2PElement] -> dictionary in the form {1: N2PElement 1, 2: N2PElement 2, ..., 
        8: N2PElement 8} including the element in which each point is located. 
        BoxFluxes: dict[dict[int, list[float]]] -> dictionary in the form 
        {Load Case ID: {1: [FXX, FYY, FXY, MXX, MYY, MXY], 2: [], ..., 8: []}} including fluxes associated to each 
        box point. 
    """

    __slots__ = ("__info__", 
                 "__input_data_father__", 
                 "_solver_id", 
                 "_plate_central_cell_solver_id", 
                 "_joint", 
                 "_central_element", 
                 "_element_list", 
                 "_bolt_element_list", 
                 "_bolt_direction", 
                 "_cfast_factor", 
                 "_attachment_id", 
                 "_attached_elements", 
                 "_face_elements", 
                 "_free_edges", 
                 "_intersection", 
                 "_distance_vector", 
                 "_distance", 
                 "_normal", 
                 "_bearing_force", 
                 "_translational_fastener_forces", 
                 "_nx_bypass", 
                 "_nx_total", 
                 "_ny_bypass", 
                 "_ny_total", 
                 "_nxy_bypass", 
                 "_nxy_total", 
                 "_mx_total", 
                 "_my_total", 
                 "_mxy_total", 
                 "_bypass_max", 
                 "_bypass_min", 
                 "_bypass_sides", 
                 "_box_dimension", 
                 "_box_points", 
                 "_box_elements", 
                 "_box_fluxes", 
                 "_elements_to_rotate", 
                 "_error", 
                 "_true_elements")

    # N2PPlate constructor    ------------------------------------------------------------------------------------------
    def __init__(self, info, input_data_father): 

        self.__info__ = info 
        self.__input_data_father__ = input_data_father 

        self._solver_id: list[int] = list(self.__info__.SolverIds)
        self._plate_central_cell_solver_id: int = int(self.__info__.PlateCentralCellSolverId)
        if self._plate_central_cell_solver_id not in self._solver_id: 
            self._solver_id.append(self._plate_central_cell_solver_id)

        self._joint: N2PJoint = None 
        self._element_list: list[N2PElement] = None 
        self._central_element: N2PElement = None 
        self._bolt_element_list: dict[str, N2PElement] = None
        self._bolt_direction: dict[str, str] = None 
        self._cfast_factor: dict[str, int] = None 

        self._attachment_id: int = self.ID 
        self._attached_elements: set[N2PElement] = None 
        self._face_elements: list[N2PElement] = None 
        self._free_edges: list[tuple[N2PElement, N2PNode, N2PNode]] = None 

        self._intersection: list[float] = None 
        self._distance_vector: np.ndarray = None 
        self._distance: float = None 
        self._normal: list[float] = None 

        self._bearing_force: dict[int, list[float]] = {} 
        self._translational_fastener_forces: dict[int, list[list[float]]] = {}
        self._nx_bypass: dict[int, float] = {}
        self._nx_total: dict[int, float] = {}
        self._ny_bypass: dict[int, float] = {}
        self._ny_total: dict[int, float] = {}
        self._nxy_bypass: dict[int, float] = {}
        self._nxy_total: dict[int, float] = {}
        self._mx_total: dict[int, float] = {}
        self._my_total: dict[int, float] = {}
        self._mxy_total: dict[int, float] = {}
        self._bypass_max: dict[int, float] = {}
        self._bypass_min: dict[int, float] = {}
        self._bypass_sides: dict[int, list[list[float]]] = {}
        self._box_dimension: float = None
        self._box_points: dict[int, np.ndarray] = {}
        self._box_elements: dict[int, N2PElement] = {} 
        self._box_fluxes: dict[int, dict[int, list[float]]] = {}

        self._elements_to_rotate: dict[N2PElement, list[float]] = {}
        self._error: bool = False 
        self._true_elements = None
    # ------------------------------------------------------------------------------------------------------------------

    # endregion 
    # region Getters 

    # Getters ----------------------------------------------------------------------------------------------------------
    @property 
    def ID(self) -> int: 

        """
        Property that returns the id attribute, that is, the internal identificator. 
        """

        return int(self.__info__.ID)
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def GlobalID(self) -> list[int]: 

        """
        Property that returns the global_id attribute, that is, the global identificator. 
        """
        
        return list(self.__info__.GlobalIds)
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def SolverID(self) -> list[int]: 

        """
        Property that returns the solver_id attribute, that is, the solver IDs of the N2PElements that make up the 
        plate. 
        """
        
        return self._solver_id
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def PlateCentralCellSolverID(self) -> int: 

        """
        Property that returns the plate_central_cell_solver_id attribute, that is, the solver ID of one representative 
        N2PElement that makes up the plate. 
        """
        
        return self._plate_central_cell_solver_id
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Cards(self) -> list[N2PCard]: 

        """
        Property that returns the cards attribute, that is, the list of the N2PCards associated with the N2PPlate's 
        N2PElements. 
        """
        
        return [self.__input_data_father__._N2PNastranInputData__dictcardscston2p[i] for i in self.__info__.Cards 
                if self.__info__.Cards[0] is not None]
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Joint(self) -> N2PJoint:

        """
        Property that returns the joint attribute, that is, the N2PJoint associated to the plate. 
        """

        return self._joint
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Bolt(self) -> N2PBolt:

        """
        Property that returns the bolt attribute, that is, the N2PBolt associated to the plate. 
        """
    
        return self.Joint.Bolt
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def ElementList(self) -> list[N2PElement]: 

        """
        Property that returns the element_list attribute, that is, the list of N2PElements that make up the plate. 
        """
        
        return self._element_list
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def CentralElement(self) -> N2PElement: 

        """
        Property that returns the central_element attribute, that is, the representative N2PElement of the plate. 
        """
        
        return self._central_element
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def BoltElementList(self) -> dict[str, N2PElement]: 

        """
        Property that returns the bolt_element_list attribute, that is, the dictionary of the CFAST that are joined to 
        the plate. 
        """
        
        return self._bolt_element_list
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def BoltDirection(self) -> dict[str, str]: 

        """
        Property that returns the bolt_direction attribute, that is, the dictionary of the orientation of the CFASTs 
        that are joined to the plate. 
        """

        return self._bolt_direction
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def CFASTFactor(self) -> dict[str, int]: 

        """
        Property that returns the cfast_factor attribute, that is, the dictionary of the factor (0, +1 or -1) which 
        should be included in the exported results of the PAG forces. 
        """

        return self._cfast_factor
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def ElementIDList(self) -> list[int]: 

        """
        Property that returns the list of the IDs of the N2PElements that make up a plate. 
        """
        
        return [j.ID for j in self.ElementList]
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def ElementInternalIDList(self) -> list[int]: 

        """
        Property that returns the unique internal ID of the N2PElements that make up the plate.  
        """

        return [j.InternalID for j in self.ElementList]
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def NodeList(self) -> list[tuple[N2PNode]]: 

        """
        Property that returns the list of N2PNodes that make up the plate. 
        """
        
        return [j.Nodes for j in self.ElementList]
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def PartID(self) -> list[str]: 

        """
        Property that returns the part ID of eache element that makes up the plate. 
        """

        return [j.PartID for j in self.ElementList]
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def AttachmentID(self) -> int: 

        """
        Property that returns the attachment_id attribute, that is, the plate's internal ID when it goes through the 
        get_attachments() function.
        """
        
        return self._attachment_id
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Intersection(self) -> list[float]: 

        """
        Property that returns the intersection attribute, that is, the point where the bolt pierces the plate. 
        """
    
        return self._intersection
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def DistanceVector(self) -> np.ndarray: 

        """
        Property that returns the distance_vector attribute, that is, the distance between the bolt and the plate's 
        edge as a vector. 
        """
        
        return self._distance_vector
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Distance(self) -> float: 

        """
        Property that returns the distance attribute, that is, the distance between the bolt and the plate's edge. 
        """
        
        return self._distance
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Normal(self) -> list[float]: 

        """
        Property that returns the normal attribute, that is, the direction perpendicular to the plate's plane. 
        """
        
        return self._normal
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def BearingForce(self) -> dict[int, np.ndarray]: 

        """
        Property that returns the bearing_force attribute, that is, the 1D force that the plate experiences.
        """

        return self._bearing_force
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def TranslationalFastenerForces(self) -> dict[int, list[np.ndarray]]: 

        """
        Property that returns the translational_fastener_forces attribute, that is, the 1D force that each fastener 
        experiences. 
        """

        return self._translational_fastener_forces
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def NxBypass(self) -> dict[int, float]: 

        """
        Property that returns the nx_bypass attribute, that is, the bypass load that the plate experiences in the 
        x-axis. 
        """

        return self._nx_bypass
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def NxTotal(self) -> dict[int, float]: 

        """
        Property that returns the nx_total attribute, that is, the total load that the plate experiences in the x-axis. 
        """

        return self._nx_total
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def NyBypass(self) -> dict[int, float]: 

        """
        Property that returns the ny_bypass attribute, that is, the bypass load that the plate experiences in the 
        y-axis. 
        """

        return self._ny_bypass
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def NyTotal(self) -> dict[int, float]: 

        """
        Property that returns the ny_total attribute, that is, the total load that the plate experiences in the y-axis. 
        """

        return self._ny_total
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def NxyBypass(self) -> dict[int, float]: 

        """
        Property that returns the nxy_bypass attribute, that is, the bypass load that the plate experiences in the 
        xy-axis. 
        """

        return self._nxy_bypass
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def NxyTotal(self) -> dict[int, float]: 

        """
        Property that returns the nxy_total attribute, that is, the total load that the plate experiences in the 
        xy-axis. 
        """

        return self._nxy_total
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def MxTotal(self) -> dict[int, float]: 

        """
        Property that returns the mx_total attribute, that is, the total moment that the plate experiences in the 
        x-axis. 
        """

        return self._mx_total
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def MyTotal(self) -> dict[int, float]: 

        """
        Property that returns the my_total attribute, that is, the total moment that the plate experiences in the 
        y-axis. 
        """

        return self._my_total
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def MxyTotal(self) -> dict[int, float]: 

        """
        Property that returns the mxy_total attribute, that is, the total moment that the plate experiences in the 
        xy-axis. 
        """

        return self._mxy_total
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def BypassMax(self) -> dict[int, float]: 

        """
        Property that returns the bypass_max attribute, that is, the maximum bypass load that the plate experiences. 
        """

        return self._bypass_max
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def BypassMin(self) -> dict[int, float]: 

        """
        Property that returns the bypass_min attribute, that is, the minimum bypass load that the plate experiences. 
        """

        return self._bypass_min
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def BypassSides(self) -> dict[int, list[float]]: 

        """
        Property that retuns the bypass_sides attribute, that is, the bypass loads in the north, south, east and west 
        sides of the box. 
        """

        return self._bypass_sides
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def BoxDimension(self) -> float: 

        """
        Property that returns the box_dimension attribute, that is, the length of the side of the box that is used in 
        the bypass loads calculation. 
        """
        
        return self._box_dimension
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def BoxSystem(self) -> list[float]: 

        """
        Property that returns the the reference frame of the box used in the bypass loads calculation, which is the 
        plate's element material reference frame.
        """
        
        return self.CentralElement.MaterialSystemArray
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def BoxPoints(self) -> dict[int, np.ndarray]: 

        """
        Property that returns the box_points attribute, that is, the coordinates of each point that makes up the box 
        used in the bypass loads calculation. 
        """
        
        return self._box_points
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def BoxElements(self) -> dict[int, N2PElement]: 

        """
        Property that returns the box_elements attribute, that is, the N2PElement associated to each point that makes 
        up the box used in the bypass loads calculations.
        """
        
        return self._box_elements
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def BoxFluxes(self) -> dict[int, dict[int, list[float]]]: 

        """
        Property that returns the box_fluxes attribute, that is, the fluxes (in every direction) that every point that 
        makes up the box used in the bypass loads calculation experience. 
        """
        
        return self._box_fluxes
    # ------------------------------------------------------------------------------------------------------------------

    # endregion 
    # region Public methods

    # Method used to obtain the box used in the bypass loads calculations ----------------------------------------------
    def get_bypass_box(self: N2PPlate, model: N2PModelContent, materialFactor = 4.0, areaFactor = 2.5, 
                       maxIterations = 200, projTol = 0.01, errorCounter = 0, maxErrorCounter = 10): 
        
        """
        Method used to obtain a plate's bypass box. 

        Procedure and methodology: 
            - The procedure is based on the crown method, so the fluxes will be calculated using a square-shaped box 
            around the joint in the plate's plane. 
            - Firstly, the box where the calculations are to be made is obtained. Its dimension is 
                    a = 0.4 * areaFactor * materialFactor * Diameter 
            Assuming that the default parameters are used, this dimension is 
                    a = 4 * Diameter
            which is the box dimension used by PAG.
            - Knowing its dimension, the box should be defined with a specific orientation and order. The orientation 
            is defined by the box reference frame, which coincides with the material system of the element where the 
            joint is pierced. This may cause a small variation because the z-axis is defined as the joint's axial 
            direction, and sometimes the material system's z-axis does not coincide with it. 
            - Then, the box system's origin would be placed in the center of the box and the first point would be 
            located in (-a, a) and the other points would be placed in the clockwise direction. 
            - Adjacent elements will be evaluated until the distance from the joint to them is greater to the box's 
            semidiagonal. After this, no more points will be found further away, so the search stops here. If there are 
            still points to be assigned, it is concluded that they lie outside of the edge of the plate and therefore 
            they will be projected. 
            - If all points lie within the free edges, the process is simple. The adjacent elements to the pierced one 
            are evaluated in case that any point lies inside of it, which is done taking into consideration the 
            so-called box tolerance, stopping the iterations when the element that is being analysed is far from the 
            box location. 
            - However, there are two cases where the box point location is not as simple. Firstly, if there are points 
            outside the free edges, they are orthogonally projected onto the mesh. In the FastPPH tool used by Altair, 
            this projection does not always follow the same procedure but, to simplify, in this tool an orthogonal 
            projection is always used. 
            - The second critical case occurs when a box crosses a T-edge or gets out of a surface that does not finish 
            in a free edge. If the box crosses a T-edge, it is considered that all points are located within the free 
            edges and should not be projected. If the box gets out of the borders of a surface, and these borders are 
            not free edges, they are treated as so, and the same procedure is followed as when they were outside of 
            free edges (they are orthogonally projected). 

        Args: 
            model: N2PModelContent 
            materialFactor: float = 4.0 
            areaFactor: float = 2.5 
            maxIterations: int = 200 
            projTol: float = 0.01 

        Calling example: 
            >>> myPlate.get_bypass_box(model, domain) 
        """
        
        boxDimension = 0.4*areaFactor*materialFactor*self.Joint.Diameter
        # The box dimension is obtained as a = 0.4*MF*AF*Diameter. Using the default parameters, it would also be 
        # a = 4*Diameter, as recommended by PAG 
        boxSemiDiag = 0.5*boxDimension*(2**0.5) 
        intersectionPlate = np.array(self.Intersection) 
        self._box_dimension = boxDimension 
        xBox = np.array(self.BoxSystem[0:3])
        yBox = np.array(self.BoxSystem[3:6])
        semiLength = 0.5*boxDimension 
        # The box is created starting from the top left (point 1) and going in a clockwise direction 
        directions = np.array([[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]])
        boxPoints = intersectionPlate + semiLength * (directions[:, 0, None] * xBox + directions[:, 1, None] * yBox)

        boxPointsFound = np.zeros(8, dtype = bool) 
        boxPointsElements = [None] * 8 
        candidateElements = {self.CentralElement}
        seenCandidates = set() 
        minDistance = 0 
        faceElements = self._face_elements
        # Elements in the box are identified 
        for iteration in range(maxIterations): 
            if boxPointsFound.all(): 
                break 
            if minDistance < boxSemiDiag: 
                # Adjacent elements will be evaluated until the distance from the bolt to them is greater than the
                # semidiagonal of the box. After this it is assured that no more points will be found far away and it
                # does not make sense to keep looking. The exception is when the element size is greater than the
                # box. In the case that some points are still be assigned, we can conclude that they lie outside the edge 
                # of the plate and should be projected.
                adjacentElements = set(model.get_elements_adjacent(list(candidateElements)))
                adjacentElements = {k for k in adjacentElements if k in faceElements}
                if len(adjacentElements) < 2: 
                    # If there are not enough adjacent elements, there is a problem with the geometry of the plate (for 
                    # example, the loaded model does not include enough elements near the plates)
                    minDistance = np.inf 
                    errorCounter = errorCounter + 1
                    if errorCounter == maxErrorCounter: 
                        N2PLog.Warning.W546(520)
                        N2PLog.set_console_level("ERROR")
                    N2PLog.Warning.W520(self)
                seenCandidates.update(candidateElements) 
                # Candidate elements list is updated 
                candidateElements = adjacentElements - seenCandidates 
                if not candidateElements: 
                    minDistance = np.inf 
                    errorCounter = errorCounter + 1
                    if errorCounter == maxErrorCounter: 
                        N2PLog.Warning.W546(520)
                        N2PLog.set_console_level("ERROR")
                    N2PLog.Warning.W520(self)
                # Minimum distance is updated 
                candidateNodes = np.array([node.GlobalCoords for elem in candidateElements for node in elem.Nodes])
                if candidateNodes.size: 
                    minDistance = np.min(np.linalg.norm(intersectionPlate - candidateNodes, axis = 1))
                # Points that have not been found yet are searched for in bulk 
                unfoundIndices = np.where(~boxPointsFound)[0]
                if unfoundIndices.size:
                    pointsToCheck = boxPoints[unfoundIndices]
                    for element in candidateElements:
                        found, newPoints, errorCounter = point_in_element(pointsToCheck, element, projTol, True, 
                                                                          errorCounter, maxErrorCounter)
                        foundIndices = unfoundIndices[found]
                        if foundIndices.size:
                            boxPoints[foundIndices] = newPoints[found]
                            boxPointsFound[foundIndices] = True
                            boxPointsElements = [element if i in foundIndices else e 
                                                 for i, e in enumerate(boxPointsElements)]
            else: 
                # It is assumed that points must be projected as the minimum distance from the fastener to the closest 
                # candidate element is greater than the box semidiagonal 
                if boxPointsFound.all(): 
                    break 
                # Since only the plane where the bolt is is considered, T-edges are also considered free edges
                freeEdges = model.get_free_edges(faceElements) 
                A = np.array([edge[1].GlobalCoords for edge in freeEdges])
                B = np.array([edge[2].GlobalCoords for edge in freeEdges])
                segmentVectors = B - A
                
                # Points that have not been found are projected and searched for in bulk 
                unfoundIndices = np.where(~boxPointsFound)[0]
                pointsToProject = boxPoints[unfoundIndices]
                pointVectors = pointsToProject[:, np.newaxis] - A  
                dot1 = np.einsum('ijk,jk->ij', pointVectors, segmentVectors)
                dot2 = np.einsum('ik,ik->i', segmentVectors, segmentVectors)
                projections = np.clip(dot1 / dot2[np.newaxis, :], 0, 1)
                projectedPoints = A + projections[:, :, np.newaxis] * segmentVectors[np.newaxis, :]
                distances = np.linalg.norm(projectedPoints - pointsToProject[:, np.newaxis, :], axis = 2)
                minIndices = np.argmin(distances, axis = 1)

                for idx, edgeIdx in zip(unfoundIndices, minIndices):
                    boxPoints[idx] = projectedPoints[idx % len(unfoundIndices), edgeIdx]
                    boxPointsElements[idx] = freeEdges[edgeIdx][0]
                    boxPointsFound[idx] = True

            # If the maximum number of iterations is reached, a warning shows up
            if iteration == maxIterations - 1: 
                errorCounter = errorCounter + 1
                if errorCounter == maxErrorCounter: 
                        N2PLog.Warning.W546(540)
                        N2PLog.set_console_level("ERROR")
                N2PLog.Warning.W540(self)
                self._error = True 

        self._box_points = {i+1: j for i, j in enumerate(boxPoints)} 
        self._box_elements = {i+1: j for i, j in enumerate(boxPointsElements)}
        return errorCounter
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to obtain the bypass loads of the plate -------------------------------------------------------------- 
    def get_bypass_loads(self: N2PPlate, model: N2PModelContent, results: np.ndarray, loadCaseList: list[N2PLoadCase], 
                         cornerData: bool = False, typeAnalysis: Literal["PAG", "ALTAIR"] = "PAG", 
                         projTol: float = 0.01, errorCounter = 0, maxErrorCounter = 10): 
        
        """
        Method used to obtain the bypass loads of a joint's plates. Maintaining the defauld parameters is highly 
        recommended, although the user is free to change some of them. 

        Args: 
            model: N2PModelContent 
            results: np.ndarray -> results obtained from loads.Results or loads.ResultsCorner. 
            loadCaseList: list[N2PLoadCase] -> list of N2PLoadCases to analyse. 
            cornerData: bool = False -> boolean that shows if there is data in the corners or not. 
            typeAnalysis: Literal["PAG", "ALTAIR"] = "PAG" -> type of analysis to be done. The only difference is in the
            calculation of the momentum fluxes. 
            projTol: float = 0.01 -> tolerance used in the interpolation. 
        Calling example: 
            >>> myPlate.get_bypass_loads(loads.Model, domain, loads.Results, loads.LoadCases, False, "ALTAIR", 0.05) 

        Procedure and methodology: 
            - After the bypass box has been created, the fluxes in each of the points of the boxes must be obtained, in 
            order to calculate the final values for bypass and total loads. There are two options to be analyzed: 

                1. cornerData = True 
                
                If the user asks for results in the corner when running the model and obtaining the corresponding 
                results, these results will be given by node and not by element, giving several values for a node, 
                related to the element where it is. This can be achieved by selecting the CORNER or BILIN describer in 
                the FORCE card. Results will be more accurate if corner data is used, as there are more values to be 
                used. 

                Taking each of the box's points, the same procedure is carried out. Firstly, the results for all nodes 
                that form the element where the box point is are retrieved. They are represented in their element 
                reference frame, so they are transformed into the same reference frame. Once 3 or 4 values for the 
                nodes are obtained (depending on wether the element is a TRIA or QUAD), a bilinear interpolation to the 
                box point from the node locations is used. 

                2. cornerData = False

                The results in the result files are retrieved in the centroid of each element, leading to results that 
                will be less precise, since results in the corners must be approximated instead of actually calculated. 
                This approximation is made by averaging the adjacent elements. Besides this, the same procedure is used 
                as in the previous case. 

            - Finally, all results are transformed into the material reference frame corresponding to the element where 
            the joint is pierced. 
        """

        supportedElements = {"CQUAD4", "CTRIA3"}
        faceElements = set(self._face_elements)
        if cornerData: 
            resultDict = {}
            elementNodal = model.elementnodal()
            boxPointForces = {i: None for i in self.BoxPoints.keys()}
            # Forces and moments are obtained in each box points
            for i in self.BoxPoints.keys(): 
                pointElement = self.BoxElements.get(i) 
                cornerCoordsGlobal = np.array([m.GlobalCoords for m in pointElement.Nodes])
                cornerCoordElem, pointCoordElem = transformation_for_interpolation(cornerCoordsGlobal, 
                                                  pointElement.Centroid, self.BoxPoints.get(i), 
                                                  system_to_matrix(pointElement.MaterialSystemArray))
                elementForces = []
                resultForNode = {j.ID: None for j in pointElement.Nodes}
                for j in pointElement.Nodes: 
                    unsewNode = [k for k in elementNodal.keys() if j.ID == elementNodal.get(k)[1]]
                    unsewElementIDs = [elementNodal.get(k)[2] for k in elementNodal.keys() 
                                       if j.ID == elementNodal.get(k)[1]]
                    unsewElement2 = [k for k in j.Connectivity if (isinstance(k, N2PElement) 
                                                                   and k.TypeElement in supportedElements)]
                    unsewElement2IDs = [k.ID for k in unsewElement2]
                    indexNoElement = [k for k, l in enumerate(unsewElementIDs) if l not in unsewElement2IDs]
                    for k in reversed(indexNoElement): 
                        del unsewElementIDs[k]
                        del unsewNode[k]
                    unsewElement = sorted(unsewElement2, key = lambda x: unsewElementIDs.index(x.ID))
                    # It looks like Altair ignores elements that are not coplanar when obtaining the forces in the box 
                    # points
                    eliminateIndex = [k for k, l in enumerate(unsewElement) if l not in faceElements]
                    # Eliminate elements from lists using the stored indeces.
                    for k in reversed(eliminateIndex): 
                        del unsewNode[k]
                        del unsewElement[k]
                        del unsewElementIDs[k]
                    
                    resultForNodeLC = {k.ID: None for k in loadCaseList}
                    for k, l in enumerate(loadCaseList): 
                        # Results are obtained in the corners 
                        fxC = results[k][0]
                        fyC = results[k][1]
                        fxyC = results[k][2]
                        mxC = results[k][3]
                        myC = results[k][4]
                        mxyC = results[k][5]
                        elementForces = []
                        unsewNodesForces = np.array([[fxC[m], fyC[m], fxyC[m], mxC[m], myC[m], mxyC[m]] 
                                                     for m in unsewNode if not np.isnan(fxC[m])])
                        unsewNodesForcesRot = np.array([rotate_tensor2D(unsewElement[m].ElemSystemArray, self.BoxSystem, 
                                                                        self.BoxSystem[6:9], unsewNodesForces[m]) 
                                                                        for m in range(len(unsewNode))])
                        resultForNodeLC[l.ID] = np.mean(unsewNodesForcesRot, axis = 0)
                    
                    resultForNode[j.ID] = resultForNodeLC 
                keysFirstElem = set(resultForNode[next(iter(resultForNode))].keys()) 
                elementForces = {k: [] for k in keysFirstElem}
                for k in keysFirstElem: 
                    for l in resultForNode.values(): 
                        if k in l: elementForces[k].append(l[k])
                        else: elementForces[k].append(None)
                totalForces, errorCounter = interpolation(pointCoordElem, cornerCoordElem, 
                                                          np.array(list(elementForces.values())), projTol, 
                                                          errorCounter, maxErrorCounter)
                boxPointForces[i] = {loadCaseList[j].ID: k for j,k in enumerate(totalForces)}
            for i, j in boxPointForces.items(): 
                for k, l in j.items(): 
                    if k not in resultDict: resultDict[k] = {} 
                    resultDict[k][i] = l
        else: 
            resultDict = {}
            boxPointForces = {i: None for i in self.BoxPoints.keys()}
            for i, point in self.BoxPoints.items(): 
                pointElement = self.BoxElements.get(i) 
                neighborElementsOld = set(model.get_elements_adjacent([pointElement]))
                neighborElements = {k for k in neighborElementsOld if k in faceElements}
                cornerCoordsGlobal = np.array([l.GlobalCoords for l in pointElement.Nodes])
                cornerCoordElem, pointCoordElem = transformation_for_interpolation(cornerCoordsGlobal, 
                                                  pointElement.Centroid, point, 
                                                  system_to_matrix(pointElement.MaterialSystemArray))
                elementForces = []
                for l in pointElement.Nodes: 
                    nodeForces = []
                    trueElements = {m for m in neighborElements if l in m.Nodes}
                    for m in trueElements: 
                        n = m.InternalID 
                        neighborForces = results[:,3:,n]
                        if np.isnan(neighborForces[0,0]): 
                            continue
                        nodeForces.append(self.__rotate_forces(neighborForces, m.ElemSystemArray, self.BoxSystem))
                    if nodeForces == []: 
                        nodeForces = [[[np.nan for _ in range(6)] for w in range(len(loadCaseList))]]
                    elementForces.append(np.mean(np.array(nodeForces), axis = 0)) 
                totalForces, errorCounter = interpolation(pointCoordElem, cornerCoordElem, 
                                                          np.array(elementForces).swapaxes(1,0), projTol, errorCounter, 
                                                          maxErrorCounter)
                boxPointForces[i] = {loadCaseList[j].ID: k for j,k in enumerate(totalForces)}
            for i, j in boxPointForces.items(): 
                for k, l in j.items(): 
                    if k not in resultDict: 
                        resultDict[k] = {} 
                    resultDict[k][i] = l.T 
        self._box_fluxes.update(resultDict)
        side = {1: [1, 2, 3], 2: [3, 4, 5], 3: [5, 6, 7], 4: [7, 8, 1]}
        loadCaseList = np.array(list(resultDict.keys()))
        bypassForces = np.mean(np.array([[[[j[k][u] for k in side[v]] for j in resultDict.values()] for u in range(6)] 
                                         for v in [3,1,4,2]]).T, axis = 0)
        self._bypass_sides.update({i: bypassForces[n] for n,i in enumerate(loadCaseList)})
        nxBypassPrev = bypassForces[:,0,2:]
        nxBypass = np.array([min(nxBypassPrev[n], key = abs) for n in range(len(loadCaseList))])
        self._nx_bypass.update({i: nxBypass[n] for n,i in enumerate(loadCaseList)})
        self._nx_total.update({i: max(nxBypassPrev[n], key = abs) for n,i in enumerate(loadCaseList)})
        nyBypassPrev = bypassForces[:,1,:2]
        nyBypass = np.array([min(nyBypassPrev[n], key = abs) for n in range(len(loadCaseList))])
        self._ny_bypass.update({i: nyBypass[n] for n,i in enumerate(loadCaseList)})
        self._ny_total.update({i: max(nyBypassPrev[n], key = abs) for n,i in enumerate(loadCaseList)})
        nxyBypassPrev = bypassForces[:,2]
        nxyBypass = np.array([min(nxyBypassPrev[n], key = abs) for n in range(len(loadCaseList))])
        self._nxy_bypass.update({i: nxyBypass[n] for n,i in enumerate(loadCaseList)})
        self._nxy_total.update({i: max(nxyBypassPrev[n], key = abs) for n,i in enumerate(loadCaseList)})
        mxTotalPrev = bypassForces[:,3,2:]
        myTotalPrev = bypassForces[:,4,:2]
        mxyTotalPrev = bypassForces[:,5]
        if typeAnalysis == "PAG": 
            self._mx_total.update({i: max(mxTotalPrev[n], key = abs) for n,i in enumerate(loadCaseList)})
            self._my_total.update({i: max(myTotalPrev[n], key = abs) for n,i in enumerate(loadCaseList)})
            self._mxy_total.update({i: max(mxyTotalPrev[n], key = abs) for n,i in enumerate(loadCaseList)})
        else: 
            self._mx_total.update({i: -np.mean(mxTotalPrev[n]) for n,i in enumerate(loadCaseList)})
            self._my_total.update({i: -np.mean(myTotalPrev[n]) for n,i in enumerate(loadCaseList)})
            self._mxy_total.update({i: -np.mean(mxyTotalPrev[n]) for n,i in enumerate(loadCaseList)})  
        u = 0.5*(nxBypass + nyBypass)
        v = (0.5*(nxBypass - nyBypass)**2 + (nxyBypass)**2)**0.5
        self._bypass_max.update({i: u[n]+v[n] for n,i in enumerate(loadCaseList)})
        self._bypass_min.update({i: u[n]-v[n] for n,i in enumerate(loadCaseList)})
        return errorCounter
    # ------------------------------------------------------------------------------------------------------------------

    # endregion 
    # region Private methods 

    # Method used to quickly rotate a force in get_bypass_loads() ------------------------------------------------------
    def __rotate_forces(self, f, elemSystem, matSystem): 

        """
        Method used to rotate N vectors with 6 components each representing force and momentum fluxes. 

        Args: 
            f: np.ndarray -> vector (of size Nx6) to be rotated. 
            elemSystem: np.ndarray -> 9x1 vector of the origin reference frame.
            matSystem: np.ndarray -> 9x1 vector of the destination reference frame.

        Returns: 
            fRot: np.ndarray -> vector (of size Nx6) rotated.

        Calling example: 
            >>> f = np.array([np.random.rand(6) for _ in range(25)])
            >>> elemSystem = element.ElemSystemArray
            >>> matSystem = plate.BoxSystem
            >>> plate.__rotate_force(f, elemSystem, matSystem)
        """

        matSystem = np.array(matSystem) 
        elemSystem = np.array(elemSystem) 
        xMat = matSystem[0:3]
        xElem = elemSystem[0:3]
        yElem = elemSystem[3:6]
        zElem = elemSystem[6:9]
        projX = xMat - zElem*np.dot(xMat, zElem) 
        projX = projX/np.linalg.norm(projX) 
        alpha = np.arctan2(np.dot(projX, yElem), np.dot(projX, xElem))
        c = np.cos(alpha) 
        s = np.sin(alpha)
        R = np.array([[c, s, 0], 
                      [-s, c, 0], 
                      [0, 0, 1]])
        N = len(f) 
        F = np.zeros((N, 3, 3))
        M = np.zeros((N, 3, 3))
        F[:, 0, 0] = f[:, 0]
        F[:, 1, 1] = f[:, 1]
        F[:, 1, 0] = F[:, 0, 1] = f[:, 2]
        M[:, 0, 0] = f[:, 3]
        M[:, 1, 1] = f[:, 4]
        M[:, 0, 1] = M[:, 1, 0] = f[:, 5]
        FRot = R@F@R.T
        MRot = R@M@R.T 
        fRot = np.zeros((len(f), 6))
        fRot[:, 0] = FRot[:, 0, 0]
        fRot[:, 1] = FRot[:, 1, 1]
        fRot[:, 2] = FRot[:, 0, 1]
        fRot[:, 3] = MRot[:, 0, 0]
        fRot[:, 4] = MRot[:, 1, 1]
        fRot[:, 5] = MRot[:, 0, 1]
        return fRot 