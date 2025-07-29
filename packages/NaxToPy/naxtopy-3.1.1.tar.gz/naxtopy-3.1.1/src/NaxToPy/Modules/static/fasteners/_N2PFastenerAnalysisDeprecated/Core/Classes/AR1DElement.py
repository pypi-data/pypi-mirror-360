from NaxToPy.Core.Classes import N2PElement
class AR1DElement:
    """Each instance AR1DElement is a box containing information of the Element, Property and Card of a CFAST,
    ... element

    Attributes:
        ID: int
        GA: N2PNode
        GB: N2PNode
        ConnectionPlateA: M2PNode
        ConnectionPlateB: M2PNode
        Elements2DTop: list
        Elements2DBottom: list
        D: float
        InternalID: int

        F_ElementLocalSystem: dict
        F_shear: dict
        F_axial: dict
        LoadAngle: dict
        F_BottomPlateSystem: dict
        F_TopPlateSystem: dict


    """

    def __init__(self, n2pelement: N2PElement,  n2pcard, n2pproperty, top_plate_id: int, bottom_plate_id: int):

        self.Element = n2pelement
        self.Property = n2pproperty
        self.Card = n2pcard

        ##########################################################
        self.ID = self.Element.ID
        self.GA = self.Element.Nodes[0]
        self.GB = self.Element.Nodes[1]
        self.ConnectionPlateA = None
        self.ConnectionPlateB = None

        # At the moment this method to extract the plate elements is connected to is only valid for CFAST. In the
        # future, a more flexible method will need to be implemented.
        self.TopPlateID = top_plate_id
        self.BottomPlateID = bottom_plate_id

        self.InternalID = self.Element.InternalID

        ### FORCES IN ELEMENT1D ELEMENT SYSTEM
        self.F_ElementLocalSystem: dict = {}
        self.F_shear: dict = {}
        self.F_axial: dict = {}

        ### FORCES IN 1ST PLATE OF BOLT MATERIAL SYSTEM
        self.LoadAngle: dict = {}


        ### FOR FASTPPH CSV
        self.F_BottomPlateSystem: dict = {}
        self.F_TopPlateSystem: dict = {}



        self.serialized = False



    ####################################################################################################################
    ### CLASS METHODS
    ####################################################################################################################

    def serialize(self):
        '''
        Serialize method substitutes all N2P objects by integer or tuple IDs so that AR1DElement can be serialized by pickle.

        Returns: None
        '''
        if not self.serialized:
            self.Element = self.Element.ID
            self.Property = (self.Property.CharName, self.Property.PID)
            self.Card = (self.Card.CharName, self.Card.EID)
            self.GA = self.GA.ID
            self.GB = self.GB.ID

            self.serialized: bool = True
    def deserialize(self, model: N2PElement):
        '''
        Deserialize method rebuilds AR1DElement using the model and the IDs left by the serialize method.

        Returns: None
        '''
        if self.serialized:
            self.Element = model.get_elements((self.Element, 0))
            self.Property = [card for card in model.ModelInputData.get_cards_by_field([str(self.Property[1])], 0, 1) if card.CharName == self.Property[0]][0]
            self.Card = [card for card in model.ModelInputData.get_cards_by_field([str(self.Card[1])], 0, 1) if card.CharName == self.Card[0]][0]
            self.GA = model.get_nodes((self.GA,0))
            self.GB = model.get_nodes((self.GB,0))

            self.serialized = False