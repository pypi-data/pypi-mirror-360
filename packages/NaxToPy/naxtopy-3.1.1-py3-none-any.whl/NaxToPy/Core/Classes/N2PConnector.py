from NaxToPy.Core.Classes.N2PNode import N2PNode


class N2PConnector:
    """
    Class of Connectors for NaxToPy. In the module, elements and connectors are separate classes.
    """

    __slots__ = (
        "__info",
        "__model"
    )

    def __init__(self, info, model_father):
        """
        Python Connector constructor
        """
        self.__info = info
        self.__model = model_father

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el ID conector -------------------------------------------------------------------------------
    @property
    def ID(self) -> int:
        """
        ID of the connector.
        """
        return(int(self.__info.ID))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el ID de la parte del conector ---------------------------------------------------------------
    @property
    def PartID(self) -> str:
        """
        Part ID of the connector.
        """
        return(self.__model._N2PModelContent__partIDtoStr.get(self.__info.Part, -1))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el tipo de conector --------------------------------------------------------------------------
    @property
    def TypeConnector(self) -> str:
        """
        Connector type.
        """
        return str(self.__info.tipo)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los nodos (N2PNode) libres/independientes conector -------------------------------------------
    @property
    def FreeNodes(self) -> list[N2PNode]:
        """
        Free Nodes of the connector.
        """
        # Devuelve el ID interno (el de VTK) de los nodos, no el solver. Entro con ese id en el diccionario de VTK a
        # Solver(ID, partID). Con la tupla entro en el diccionario de nodos para sacar el objeto N2PNode.
        # Todo dentro de una comprension de lista.
        listaobjetos = [ list(self.__model._N2PModelContent__node_dict)[node]
                        for node in list(self.__info.pointsIndep) ]
        return listaobjetos
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los nodos (N2PNode) esclavos/dependientes del conector ---------------------------------------
    @property
    def SlaveNodes(self) -> list[N2PNode]:
        """
        Slaves Nodes of the connector.
        """
        listaobjetos = [list(self.__model._N2PModelContent__node_dict)[node]
                        for node in list(self.__info.pointsDep)]
        return listaobjetos
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los nodos (N2PNode) del conector en caso de ser del tipo MPC o RSPLINE -----------------------
    @property
    def GridIDs(self) -> list[N2PNode]:
        """
        Nodes (:class:`N2PNode`) of the connector in case it is of type MPC or RSPLINE.
        """
        listaobjetos = [ list(self.__model._N2PModelContent__node_dict)[node]
                        for node in list(self.__info.gridIDs) ]
        return listaobjetos
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el id interno (o VTK) del conector -----------------------------------------------------------
    @property
    def InternalID(self) -> int:
        """
        Internal ID of the connector.
        """
        return (int(self.__info.VTKindice))
    # ------------------------------------------------------------------------------------------------------------------
    
    # Metodo para obtener el id del nodo de referencia en caso de que el conector sea RBE3 o COUPLING
    @property
    def RefGrid(self) -> N2PNode:
        """
        Reference node ID in case the connector is of type RBE3 or COUPLING.
        """
        return list(self.__model._N2PModelContent__node_dict)[int(self.__info.refGrid)]
    # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PConnector({self.ID}, \'{self.PartID}\', \'{self.TypeConnector}\')"
    # ------------------------------------------------------------------------------------------------------------------
