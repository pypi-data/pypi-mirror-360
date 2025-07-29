# Clase Increment de Python --------------------------------------------------------------------------------------------
class N2PIncrement:
    """
    Class which contains the information associated to an increment/frame of a N2PLoadCase instance.
    """

    __slots__ = (
        "__info"
    )

    # Constructor de N2PIncrement --------------------------------------------------------------------------------------
    def __init__(self, info):
        self.__info = info
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el nombre del incremento ---------------------------------------------------------------------
    @property
    def Name(self) -> str:
        """Name of the Increment"""
        return(str(self.__info.Name))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el valor del autovalor real ------------------------------------------------------------------
    @property
    def RealEigenvalue(self) -> float:
        """Real Eigenvalue of the increment"""
        return(float(self.__info.EigReal))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el valor del autovalor imaginario ------------------------------------------------------------
    @property
    def ImaginaryEigenvalue(self) -> float:
        """Imaginary Eigenvalue of the increment"""
        return(float(self.__info.EigImg))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el ID del incremento en el caso de carga -----------------------------------------------------
    @property
    def ID(self) -> int:
        """Solver ID of the Increment"""
        return(int(self.__info.ID))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el valor del incremento ----------------------------------------------------------------------
    @property
    def Time(self) -> float:
        ''' Returns the value of the increment/frame'''
        return(float(self.__info.Time))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el tipo de Solucion --- ----------------------------------------------------------------------
    @property
    def Solution(self) -> str:
        """Returns the value of the Solution name of the Increment"""
        return(str(self.__info.Solution))
    # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PIncrement({self.ID}: \"{self.Name}\")"
    # ------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------


