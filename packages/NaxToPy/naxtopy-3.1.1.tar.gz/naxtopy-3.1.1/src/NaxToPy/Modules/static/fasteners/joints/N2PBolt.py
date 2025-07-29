# region Imports 

"""
Class that represents a single bolt, which is the union of one or several fasteners in the model. 
"""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

from __future__ import annotations
from typing import TYPE_CHECKING

from NaxToPy.Core.Classes.N2PAbaqusInputData import * 
from NaxToPy.Core.Classes.N2PElement import N2PElement 
from NaxToPy.Core.Classes.N2PNastranInputData import * 
from NaxToPy.Core.Classes.N2PNode import N2PNode 
if TYPE_CHECKING:
    from NaxToPy.Modules.static.fasteners.joints.N2PJoint import N2PJoint

# endregion 
# region N2PBolt 

class N2PBolt: 

    """
    Class that represents a single bolt, which is the union of one or several fasteners in the model. 

    Properties: 
        ID: int -> bolt's internal identificator. 
        OneDimElemsIDList: list[int] -> list of the internal IDs of N2PElements that make up the bolt. 
        Cards: list[N2PCard] -> list of the cards of the N2PElements that make up the bolt. 
        Type: str -> type of bolt. 
        Joint: N2PJoint -> N2PJoint associated to the N2PBolt. 
        ElementList: list[N2PElement] -> list of all N2PElements associated to the N2PBolt. 
        ElementIDList: list[int] -> list of the solver IDs of all elements associated to the bolt. 
        ElementInternalIDList: list[int] -> list of the internal IDs of all elements associated to the bolt. 
        NodeList: list[N2PNode] -> list[tuple[N2PNode]] -> list of all N2PNodes associated to the bolt. 
        PartID: str -> part ID of the bolt (precisely, of the first element that makes up the bolt). 
        AxialForce: dict[int, dict[int, float]] -> dictionary in the form {Load Case ID: Bolt Element ID: F} of the 
        joint's axial force. 
        ShearForce: dict[int, dict[int, float]] -> dictionary in the form {Load Case ID: Bolt Element ID: F} of the 
        joint's shear force. 
        MaxAxialForce: dict[int, dict[int, float]] -> dictionary in the form {Load Case ID: F} of the joint's maximum 
        axial force. 
        LoadAngle: dict[int, dict[int, float]] -> dictionary in the form {Load Case ID: Bolt Element ID: Angle} of the 
        joint's load angle in degrees. 
    """

    __slots__ = ("__info__", 
                 "__input_data_father__", 
                 "_id", 
                 "_one_dim_elems_id_list", 
                 "_cards", 
                 "_type", 
                 "_joint", 
                 "_element_list", 
                 "_axial_force", 
                 "_shear_force", 
                 "_max_axial_force", 
                 "_load_angle")

    # N2PBolt constructor ----------------------------------------------------------------------------------------------
    def __init__(self, info, input_data_father): 
        self.__info__ = info 
        self.__input_data_father__ = input_data_father 

        self._id: int = int(self.__info__.ID)
        self._one_dim_elems_id_list: list[int] = list(self.__info__.OneDimElemsIdList)
        self._cards: list[N2PCard] = [self.__input_data_father__._N2PNastranInputData__dictcardscston2p[i] 
                                      for i in self.__info__.Cards if self.__info__.Cards[0] is not None]
        self._type: str = self.__info__.Type.ToString() 

        self._joint: N2PJoint = None
        self._element_list: list[N2PElement] = None 

        self._axial_force: dict[int, dict[int, float]] = {}
        self._shear_force: dict[int, dict[int, float]] = {} 
        self._max_axial_force: dict[int, float] = {} 
        self._load_angle: dict[int, dict[int, float]] = {} 
    # ------------------------------------------------------------------------------------------------------------------

    # endregion 
    # region Getters 

    # Getters ----------------------------------------------------------------------------------------------------------
    @property 
    def ID(self) -> int: 

        """
        Property that returns the id attribute, that is, the bolt's internal identificator. 
        """

        return self._id 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def OneDimElemsIDList(self) -> list[int]: 

        """
        Property that returns the one_dim_elems_id_list attribute, that is, the list of the internal IDs of all 
        N2PElements that make up the N2PBolt. 
        """

        return self._one_dim_elems_id_list
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def Cards(self) -> list[N2PCard]: 

        """
        Property that returns the cards attribute, that is, the list of N2PCards associated to the N2PElements that 
        make up the bolt.
        """

        return self._cards
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Type(self) -> str: 

        """
        Property that returns the type attribute, that is, what type of elements make up the bolt.
        """

        return self._type 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Joint(self) -> N2PJoint: 

        """
        Property that returns the joint attribute, that is, the N2PJoint associated to the bolt. 
        """

        return self._joint
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def ElementList(self) -> list[N2PElement]: 

        """
        Property that returns the element_list attribute, that is, the list of all N2PElements that compose the bolt. 
        """

        return self._element_list 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def ElementIDList(self) -> list[int]: 

        """
        Property that returns the list of the solver IDs of all N2PElements that compose the bolt. 
        """

        return [j.ID for j in self.ElementList]
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def ElementInternalIDList(self) -> list[int]: 

        """
        Property that returns the list of the internal IDs of all N2PElements that compose the bolt. 
        """

        return [j.InternalID for j in self.ElementList]
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def NodeList(self) -> list[tuple[N2PNode]]: 

        """
        Property that returns the list of all N2PNodes that compose the bolt. 
        """

        return [j.Nodes for j in self.ElementList]
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def PartID(self) -> str: 

        """
        Property that returns the part ID of the bolt. 
        """

        return self.ElementList[0].PartID
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def AxialForce(self) -> dict[int, dict[int, float]]: 

        """
        Property that returns the axial_force attribute, that is, the bolt's shear force.
        """
        
        return self._axial_force
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def ShearForce(self) -> dict[int, dict[int, float]]: 

        """
        Property that returns the shear_force attribute, that is, the bolt's shear force.
        """
        
        return self._shear_force
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def MaxAxialForce(self) -> dict[int, float]: 

        """
        Property that returns the max_axial_force attribute, that is, the maximum axial force sustained by the bolt. 
        """

        return self._max_axial_force
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def LoadAngle(self) -> dict[int, dict[int, float]]: 

        """
        Property that returns the load_angle attribute, that is, the bolt's load angle in degrees. 
        """

        return self._load_angle
    # ------------------------------------------------------------------------------------------------------------------