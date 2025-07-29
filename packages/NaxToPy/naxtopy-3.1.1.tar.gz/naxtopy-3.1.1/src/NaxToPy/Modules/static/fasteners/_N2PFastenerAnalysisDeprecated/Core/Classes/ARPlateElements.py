from NaxToPy.Core.Classes import N2PElement, N2PProperty, N2PMaterial
from NaxToPy.Core import N2PModelContent
import NaxToPy as N2P

class ARPlateElements:
    """Each instance ARPlateElements is a box containing information of the Element, Property and Material of a plate
    element.

    Attributes:
        Element: N2PElement
        Property: N2PProperty
        Material: N2PMaterial
        ID: int

        """

    def __init__(self, n2pelement: N2PElement, n2pproperty: N2PProperty, n2pmaterial: N2PMaterial):
        if not (n2pelement.TypeElement == "CQUAD4" or n2pelement.TypeElement == "CTRIA3"):
            N2P.N2PLog.Warning.W519(n2pelement)

        self.Element = n2pelement
        self.Property = n2pproperty
        self.Material = n2pmaterial
        self.ID = self.Element.ID

        self.serialized: bool = False


    def serialize(self):
        '''
        Serialize method substitutes all N2P objects by integer or tuple IDs so that ARPlateElements can be serialized by pickle.

        Returns: None
        '''
        if not self.serialized:
            self.Element = self.Element.ID
            self.Property = self.Property.ID
            self.Material = self.Material.ID

            self.serialized = True

    def deserialize(self, model: N2PModelContent):
        '''
         Deserialize method rebuilds ARPlateElements using the model and the IDs left by the serialize method.

         Returns: self
         '''
        if self.serialized:
            self.Element = model.get_elements((self.Element, 0))
            self.Property = model.PropertyDict.get(self.Property)
            self.Material = model.MaterialDict.get(self.Material)

            self.serialized = False