from NaxToPy.Core import N2PModelContent
from NaxToPy.Modules.static.fasteners._N2PFastenerAnalysisDeprecated.Core.Classes.ARPlateElements import ARPlateElements
import numpy as np


class ARPlate:
    """Each instance ARPlate is a box containing all data relative to the plate.

    Attributes:
        Elements: tuple[N2PElement]
        DistanceToEdge: float
        IntersectionPoint: ndarray
        Normal: ndarray
        ElementIDs: list[int]

        Element1DIDsJoined: list[list]
        F_1D_PlatesOrganisation: dict
        F_1D_Altair: dict

        BoxDimension: float
        NxBypass: dict 
        NxTotal: dict 
        NyBypass: dict
        NyTotal: dict 
        NxyBypass: dict 
        NxyTotal: dict 
        MxTotal: dict 
        MyTotal: dict 
        MxyTotal: dict 
        BypassMaxPpal: dict
        BypassMinPpal: dict
        

        """

    def __init__(self, plate_elements: list[ARPlateElements], id: int):

        self.ID = id

        self.Elements: list = plate_elements
        self.DistanceToEdge: float = None
        self.IntersectionPoint: np.ndarray = None
        self.Normal: np.ndarray = None
        self.ElementIDs: list = []
        self.Element1DIDsJoined: list = []

        self.F_1D_PlatesOrganisation: dict = {}
        self.F_1D_Altair: dict = {}
        self.BoxDimension: float = None
        self.BoxSystem: list = []

        for element in self.Elements:
            self.ElementIDs.append(element.ID)

        self.NxBypass: dict = {}
        self.NxTotal: dict = {}
        self.NyBypass: dict = {}
        self.NyTotal: dict = {}
        self.NxyBypass: dict = {}
        self.NxyTotal: dict = {}
        self.MxTotal: dict = {}
        self.MyTotal: dict = {}
        self.MxyTotal: dict = {}
        self.BoxPoints: dict = {}
        self.BoxFluxes: dict = {}
        self.BypassMaxPpal: dict = {}
        self.BypassMinPpal: dict = {}
        

        self.serialized = False

    def serialize(self):
        '''
        Serialize method substitutes all N2P objects by integer or tuple IDs so that ARPlate can be serialized by pickle.
        ARPlateElements  serialize methods all called.

        Returns: None
        '''
        if not self.serialized:
            for element in self.Elements:
                element.serialize()

            self.serialized = True


    def deserialize(self, model: N2PModelContent):
        '''
        Deserialize method rebuilds ARPlate using the model and the IDs left by the serialize method.
        ARPlateElements deserialize methods all called.

        Returns: None
        '''
        if self.serialized:
            for element in self.Elements:
                element.deserialize(model)

            self.serialized = False