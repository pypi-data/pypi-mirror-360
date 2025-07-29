# Clase Section de Python ----------------------------------------------------------------------------------------------
class N2PSection:
    """Class which contains the information associated to a section of a :class:`N2PComponent` instance.
    """

    __slots__ = (
        "__name",
        "__number"
    )
    
    # Constructor de N2PSection ----------------------------------------------------------------------------------------
    def __init__(self, name, number):
        """Python Section Constructor.

        Args:
            name: str -> name of the section.
            number: int -> number associated to the section.

        Returns:
            section: N2PSection

        """
        self.__name = name
        self.__number = number
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el nombre de la seccion ----------------------------------------------------------------------
    @property
    def Name(self) -> str:
        """Returns the name of the section"""
        return(str(self.__name))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el numero asociado a la seccion --------------------------------------------------------------
    @property
    def InternalNumber(self) -> int:
        """Returns the number associated to the section"""
        return(int(self.__number))
    # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PSection(\'{self.Name}\')"
    # ------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
