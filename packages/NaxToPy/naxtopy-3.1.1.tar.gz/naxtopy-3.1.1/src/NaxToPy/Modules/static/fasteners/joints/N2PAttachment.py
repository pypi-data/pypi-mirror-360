# region Imports 

"""
Class that represents a single attachment, which is a series of N2PJoints that join the same region of the model. 
"""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

from __future__ import annotations
import numpy as np 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from NaxToPy.Modules.static.fasteners.joints.N2PPlate import N2PPlate 
    from NaxToPy.Modules.static.fasteners.joints.N2PJoint import N2PJoint

# endregion 
# region N2PAttachment

class N2PAttachment: 

    """
    Class that represents a single attachment, which is a series of N2PJoints that join the same region of the model. 

    Properties: 
        ID: int 
        AttachedPlatesIDList: list[int] -> list of the attached N2PPlates' element's solver ID.
        AttachedPlateList: list[N2PPlate] -> list of the attached N2PPlates. 
        JointsList: list[N2PJoint] -> list of the attached N2PJoints. 
        Pitch: float -> minimum distance from an N2PJoint to its neighbours. 
    """

    __slots__ = ("_id", 
                 "_attached_plates_id_list", 
                 "_attached_plates_list", 
                 "_joints_list", 
                 "_pitch")

    # N2PAttachment constructor ----------------------------------------------------------------------------------------
    def __init__(self, id): 
        self._id: int = id 
        self._attached_plates_id_list: list[int] = None 
        self._attached_plates_list: list[N2PPlate] = None 
        self._joints_list: list[N2PJoint] = [] 
        self._pitch: float = None 
    # ------------------------------------------------------------------------------------------------------------------
        
    # region Getters 

    # Getters ----------------------------------------------------------------------------------------------------------
    @property 
    def ID(self) -> int: 
        
        """
        Property that returns the id attribute, that is, the N2PAttachment's ID. 
        """
        
        return self._id 
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def AttachedPlatesIDList(self) -> list[int]: 

        """
        Property that returns the attached_plates_id_list attribute, that is, the list of the solver IDs of all 
        elements in the attached plates. 
        """

        return self._attached_plates_id_list
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def AttachedPlateList(self) -> list[N2PPlate]: 

        """
        Property that returns the attached_plates_list attribute, that is, the list of all attached N2PPlates. 
        """

        return self._attached_plates_list
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def JointsList(self) -> list[N2PJoint]: 

        """
        Property that returns the joints attribute, that is, the list of all N2PJoints. 
        """

        return self._joints_list
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Pitch(self) -> float: 

        """
        Property that returns the pitch attribute, that is, the attachment's pitch. 
        """

        return self._pitch
    # ------------------------------------------------------------------------------------------------------------------
    
    # endregion 
    # region Public methods 

    # Method used to obtain the attachment's pitch ---------------------------------------------------------------------
    def get_pitch(self): 

        """
        Method used to obtain the attachment's pitch, that is, the minimum distance from an N2PJoint to its neighbours. 

        Calling example: 
            >>> jointPitch = myAttachment.get_pitch()
        """

        numPoints = len(self.AttachedPlateList) 
        distances = np.zeros((numPoints,numPoints)) 
        # The distance from a plate to itself is set to infinity so that it does not affect the pitch calculation 
        np.fill_diagonal(distances, np.inf) 
        for i in range(numPoints): 
            pi = self.AttachedPlateList[i]
            for j in range(i+1, numPoints): 
                pj = self.AttachedPlateList[j]
                # The distance from a plate to another plate in the same joint is also set to infinity 
                if pi.Joint == pj.Joint: 
                    distances[i, j] = distances[j, i] = np.inf 
                # The distance from a plate to another plate in another joint is actually calculated
                else: 
                    distances[i, j] = distances[j, i] = np.linalg.norm(np.array(pi.Intersection) - \
                                                                       np.array(pj.Intersection)) 
        # Each plate's pitch is calculated as the minimum in the rows/columns of the matrix 
        distance = np.min(distances, axis = 0)
        for i, j in enumerate(self.AttachedPlateList): 
            # A joint's pitch will be the minimum pitch of its plate's pitches
            if not j.Joint.Pitch: 
                j._joint._pitch = float(distance[i])
            elif float(distance[i]) < j.Joint.Pitch: 
                j._joint._pitch = float(distance[i])
        # The attachment's pitch will be the minimum of its joint's pitches 
        self._pitch = float(np.min(distance))
    # -------------------------------------------------------------------------------------------------------------------