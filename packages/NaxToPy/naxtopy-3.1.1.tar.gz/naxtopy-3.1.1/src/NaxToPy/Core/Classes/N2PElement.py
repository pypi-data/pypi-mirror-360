import array
from typing import Union

from NaxToPy.Core.Classes.N2PNode import N2PNode
from NaxToModel import N2ElementsCoordinateSystems

# Clase Element de Python
class N2PElement:
    """
    Class with the information of an element.
    """

    __slots__ = (
        "__info",
        "__model"
    )

    def __init__(self, info, model_father):
        """
        Python Element constructor.
        """

        self.__info = info
        self.__model = model_father

    # Metodo para obtener ID interno del elemento ----------------------------------------------------------------------
    @property
    def InternalID(self) -> int:
        """
        Internal ID of the element.
        """
        return(int(self.__info.VTKindice))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el id del elemento ---------------------------------------------------------------------------
    @property
    def ID(self) -> int:
        """
        ID of the element.
        """
        return(int(self.__info.ID))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener la parte del elemento ------------------------------------------------------------------------
    @property
    def PartID(self) -> str:
        """
        Part ID of the element.
        """
        return(self.__model._N2PModelContent__partIDtoStr.get(self.__info.partID, -1))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener tipo de elemento -----------------------------------------------------------------------------
    @property
    def TypeElement(self) -> str:
        """
        Type of the element.
        """
        return(self.__model._N2PModelContent__elementTypeIDtoStr.get(self.__info.typeElementSolver, -1))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener la propiedad del elemento --------------------------------------------------------------------
    @property
    def Prop(self) -> Union[tuple[int, str], tuple[str, str]]:
        """
        Property of the element.
        """
        id_prop = int(self.__info.prop)
        if self.__model.Solver == "Abaqus":
            id_prop = self.__model._N2PModelContent__propertyIDtoStr.get(id_prop)
            part = "ASSEMBLY"
        elif self.__model.Solver == "InputFileAbaqus":
            id_prop = self.__model._N2PModelContent__propertyIDtoStr.get(id_prop)
            part = self.PartID
        else:
            part = self.PartID
        return (id_prop, part)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el tipo de elemento interno ------------------------------------------------------------------
    @property
    def InternalElemType(self) -> int:
        """
        Internal element type.
        """
        return(int(self.__info.typeElementVTK))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener nNodes del elemento --------------------------------------------------------------------------
    @property
    def NumNodes(self) -> int:
        """
        Number of nodes of the element.
        """
        return(int(self.__info.nNodes))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los nodos del elemento como N2PNode ----------------------------------------------------------
    @property
    def Nodes(self) -> tuple[N2PNode]:
        """
        Nodes (:class:`N2PNode`) of the element.
        """
        aux = list(self.__info.nodeList)
        retornar = tuple()
        for nodo in aux:
            retornar += (self.__model._N2PModelContent__node_dict.get((nodo, self.__info.partID), -1) ,)
        return(retornar)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los ids de los nodos del elemento ------------------------------------------------------------
    @property
    def NodesIds(self) -> tuple:
        """
        Nodes IDs of the element.
        """
        return(tuple(self.__info.nodeList))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el angulo material del elemento --------------------------------------------------------------
    @property
    def AngleMat(self) -> float:
        """
        Angle of the material of the element.
        """
        return(float(self.__info.angleMaterial))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para el sistema de coordenadas elemento -------------------------------------------------------------------
    @property
    def ElemSystemArray(self) -> list[float, ...]:  # En el futuro se puede crear una clase N2PElemSys
        """
        Returns an array with the position of the three vectors that define the element system of the element:
        [x1, x2, x3, y1, y2, y3, z1, z2, z3]
        """
        systems = self.__model._elements_coord_sys()
        return [systems[self.InternalID, i] for i in range(9)]
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para el sistema de material elemento ----------------------------------------------------------------------
    @property
    def MaterialSystemArray(self) -> list[float, ...]:
        """
        Returns list with the position of the three vectors that define the material system of the element:
        [x1, x2, x3, y1, y2, y3, z1, z2, z3]
        """
        mastsys = N2ElementsCoordinateSystems.GetElementMaterialSystem(self.__model._N2PModelContent__vzmodel,
                                                                       self.InternalID)
        if mastsys is not None:
            return list(mastsys)
        else:
            return None
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para el sistema de material elemento ----------------------------------------------------------------------
    @property
    def Centroid(self) -> list[float, ...]:
        """
        Returns list with the centroid of the element: [x, y, z]
        """
        all_centroids = self.__model._N2PModelContent__vzmodel.ElementCentroids
        iid = self.InternalID
        return [all_centroids[iid, i] for i in range(3)]
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para el sistema de usuario del elemento -------------------------------------------------------------------
    @property
    def UserSystemArray(self) -> list[float, ...]:
        """
        Returns list with the position of the three vectors that define the user system of the element:
        [x1, x2, x3, y1, y2, y3, z1, z2, z3]

        If no user systems for elements are defined yet, it returns None.
        """
        user_system_array = self.__model._N2PModelContent__vzmodel.ElementUserCoordinateSystems
        if not user_system_array:
            return None
        return [user_system_array[self.InternalID, i] for i in range(9)]
    # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PElement({self.ID}, \'{self.PartID}\')"
    # ------------------------------------------------------------------------------------------------------------------
