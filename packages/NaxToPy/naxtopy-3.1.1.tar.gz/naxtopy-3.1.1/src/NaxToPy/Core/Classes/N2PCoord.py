class N2PCoord(object):
    """
    Class with the information of a coordinate system.
    """

    __slots__ = (
        "__info",
        "__model"
    )

    def __init__(self, info, model_father):
        """
        Constructor of the class N2PCoord.
        """

        self.__info = info
        self.__model = model_father
    #-------------------------------------------------------------------------------------------------------------------

    # Método para obtener el ID del Sistema de Coordenadas -------------------------------------------------------------
    @property
    def ID(self) -> int:
        """
        ID of the Coordinate System.
        """
        return int(self.__info.ID)
    # ------------------------------------------------------------------------------------------------------------------


    # @property
    # def PartID(self) -> str:
    #     try:
    #         partid = int(self.__info.partID)
    #     except:
    #         partid = 0
    #     return self.__model__._N2PModelContent__partIDtoStr.get(self.__info.Part, -1)
    
    # Método para obtener el Sistema de Coordenadas --------------------------------------------------------------------
    @property
    def TypeSys(self) -> str:
        """
        Type of Coordinate System.
        """
        return str(self.__info.type)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el Origen del Sistema de Coordenadas ---------------------------------------------------------
    @property
    def Origin(self) -> tuple:
        """
        Origin of the Coordinate System.
        """
        return tuple(self.__info.origen)
    # ------------------------------------------------------------------------------------------------------------------
    
    # Método para obtener el eje X del Sistema de Coordenadas ----------------------------------------------------------
    @property
    def Xaxis(self) -> tuple:
        """
        X Axis of the Coordinate System.
        """
        return tuple(self.__info.xAxis)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el eje Y del Sistema de Coordenadas ----------------------------------------------------------
    @property
    def Yaxis(self) -> tuple:
        """
        Y Axis of the Coordinate System.
        """
        return tuple(self.__info.yAxis)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener el eje Z del Sistema de Coordenadas ----------------------------------------------------------
    @property
    def Zaxis(self) -> tuple:
        """
        Z Axis of the Coordinate System.
        """
        return tuple(self.__info.zAxis)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para obtener la descripción del Sistema de Coordenadas ----------------------------------------------------
    @property
    def Description(self) -> str:
        """
        Description of the Coordinate System.
        """
        return str(self.__info.description)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para comprobar si el Sistema de Coordenadas es Global -----------------------------------------------------
    @property
    def IsGlobal(self) -> bool:
        """
        Verify if the Coordinate System is Global.
        """
        return bool(self.__info.is_global)
    # ------------------------------------------------------------------------------------------------------------------

    # Método para comprobar si el Sistema de Coordenadas es definido por el usuario ------------------------------------
    @property
    def IsUserDefined(self) -> bool:
        """
        Verify if the Coordinate System is User Defined.
        """
        return bool(self.__info.is_user_defined)
    # ------------------------------------------------------------------------------------------------------------------
    
    # Método obtener el nombre del Sistema de Coordenadas --------------------------------------------------------------
    @property
    def Name(self) -> str:
        """
        Name of the Coordinate System.
        """
        return self.__info.Name
    # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PCoord({self.ID}, \'{self.Name}\', \'{self.TypeSys}\')"
    # ------------------------------------------------------------------------------------------------------------------
