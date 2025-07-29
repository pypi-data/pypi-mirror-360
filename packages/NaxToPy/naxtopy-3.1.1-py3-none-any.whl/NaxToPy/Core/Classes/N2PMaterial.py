from abc import ABC
from typing import Union

# ----------------------------------------------------------------------------------------------------------------------
class N2PMaterial(ABC):
    """
    Base abstract class for materials. The material classes inherit from this base class. The type of materials that
    are now supported are:

        - N2PMatE:  Elastic, linear isotropic material.
        - N2PMatA:  Elastic, linear anisotropic material.
        - N2PMatO:  Elastic, linear orthotropic material.
        - N2PMatT:  Material with Thermal properties ut not mechanical.
        - N2PMatTA: Anisotropic material with Thermal properties but not mechanical.
        - N2PMatI:  Orthotropic material for Isoparametric shell elements.
        - N2PMatIS: Anisotropic material for Solid Isoparametric elements.
        - N2PMatF:  Fluid material property definition.
    """

    def __init__(self, information, model_father):

        self.__info__ = information
        self.__model__ = model_father

    # Metodo para obtener el id solver del material --------------------------------------------------------------------
    @property
    def ID(self) -> Union[str, int]:
        """
        ID of the material.
        """
        if self.__model__.Solver == "Abaqus" or self.__model__.Solver == "InputFileAbaqus":
            return self.__info__.Name
        else:
            return self.__info__.ID
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener la parte solver del material -----------------------------------------------------------------
    @property
    def PartID(self) -> str:
        """
        Part ID of the material.
        """
        return(self.__model__._N2PModelContent__partIDtoStr.get(self.__info__.PartID, -1))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el id VTK del material -----------------------------------------------------------------------
    @property
    def InternalID(self) -> int:
        """
        Internal ID of the material.
        """
        return(int(self.__info__.InternalID))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el tipo del material -------------------------------------------------------------------------
    @property
    def MatType(self) -> str:
        """
        Material Type.
        """
        return self.__info__.MatType.ToString()
    # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        if self.__model__.Solver == "Abaqus" or self.__model__.Solver == "InputFileAbaqus":
            reprs = f"N2PMaterial(\'{self.ID}\', \'{self.MatType}\')"
        else:
            reprs = f"N2PMaterial({self.ID}, \'{self.MatType}\')"
        return reprs
    # ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
class N2PMatE(N2PMaterial):
    """
    Class for Elastic, linear and isotropic material.
    """
    
    def __init__(self, information, model_father):

        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    # Metodo para obtener el modulo elástico del material --------------------------------------------------------------
    @property
    def Young(self) -> float:
        ''' Returns the elastic or Young's modulus of the material.'''
        return(float(self.__info__.Young))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el modulo cortante del material --------------------------------------------------------------
    @property
    def Shear(self) -> float:
        ''' Returns the shear modulus of the material.'''
        return(float(self.__info__.Shear))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el modulo de Poisson del material ------------------------------------------------------------
    @property
    def Poisson(self) -> float:
        ''' Returns the Poisson modulus of the material.'''
        return(float(self.__info__.Poisson))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener la densidad del material ---------------------------------------------------------------------
    @property
    def Density(self) -> float:
        ''' Returns the density of the material.'''
        return(float(self.__info__.Density))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el coeficiente de expansion térmica del material ---------------------------------------------
    @property
    def TExp(self) -> float:
        ''' Returns the thermal expansion coefficient of the material.'''
        return(float(self.__info__.TExp))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener la temperatura de referencia del material ----------------------------------------------------
    @property
    def TRef(self) -> float:
        ''' Returns the reference temperature of the material.'''
        return(float(self.__info__.TRef))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el coeficiente de amortiguamiento estructural del material -----------------------------------
    @property
    def GE(self) -> float:
        ''' Returns the structural damping coefficient of the material.'''
        return(float(self.__info__.GE))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el esfuerzo limite a tension del material ----------------------------------------------------
    @property
    def ST(self) -> float:
        ''' Returns the stress limit for tension of the material.'''
        return(float(self.__info__.ST))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el esfuerzo limite a compresion del material -------------------------------------------------
    @property
    def SC(self) -> float:
        ''' Returns the stress limit for compression of the material.'''
        return(float(self.__info__.SC))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el esfuerzo limite a cortadura del material --------------------------------------------------
    @property
    def SS(self) -> float:
        ''' Returns the stress limit for shear of the material.'''
        return(float(self.__info__.SS))
    # ------------------------------------------------------------------------------------------------------------------
    
    # Metodo para obtener id del sistema de coordenadas del material ---------------------------------------------------
    @property
    def MCSID(self) -> int:
        ''' Returns the id of the coordinate system of the material.'''
        return(int(self.__info__.MCSID))
    # ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
class N2PMatMisc(N2PMaterial):
    """
    Class with the materials that are not yet defined.
    """

    def __init__(self, information, model_father):
        """
        Constructor of the N2PMatMisc: Class with the materials that are not yet defined
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father


    @property
    def QualitiesDict(self) -> dict:
        """
        Returns a dictionary with the name of the properties as key and its values
        """
        return dict(self.__info__.QualitiesDict)
    # ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
class N2PMatI(N2PMaterial):
    """
    Class for orthotropic material for Isoparametric shell elements.
    """

    __slots__ = (
        "__info",
        "__model"
    )

    def __init__(self, information, model_father):
        super().__init__(information, model_father)
        self.__info = information
        self.__model = model_father

    # Metodo para obtener el modulo elástico del material --------------------------------------------------------------
    @property
    def YoungX(self) -> float:
        """Returns the elastic modulus in X material coordinate direction, also fiber direction."""
        return (float(self.__info.YoungX))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el modulo elástico del material --------------------------------------------------------------
    @property
    def YoungY(self) -> float:
        """Returns the elastic modulus in Y material coordinate direction."""
        return (float(self.__info.YoungY))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el modulo cortante del material --------------------------------------------------------------
    @property
    def ShearXY(self) -> float:
        """In-plane shear modulus of the material."""
        return (float(self.__info.ShearXY))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el modulo cortante del material --------------------------------------------------------------
    @property
    def ShearXZ(self) -> float:
        """Tranverse shear modulus of the material in plane XZ"""
        return (float(self.__info.ShearXZ))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el modulo cortante del material --------------------------------------------------------------
    @property
    def ShearYZ(self) -> float:
        """Tranverse shear modulus of the material in plane YZ"""
        return (float(self.__info.ShearYZ))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el modulo de Poisson del material ------------------------------------------------------------
    @property
    def PoissonXY(self) -> float:
        """Poisson's ratio of the material. NOTE: PoissonXY = 1/PoissonYX"""
        return (float(self.__info.PoissonXY))

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener la densidad del material ---------------------------------------------------------------------
    @property
    def Density(self) -> float:
        """Returns the density of the material."""
        return (float(self.__info.Density))

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el coeficiente de expansion térmica del material ---------------------------------------------
    @property
    def TExpX(self) -> float:
        """Thermal expansion coefficient in X direction of the material (fiber direction)"""
        return (float(self.__info.TExpX))
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def TExpY(self) -> float:
        """Thermal expansion coefficient in Y direction of the material"""
        return (float(self.__info.TExpY))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener la temperatura de referencia del material ----------------------------------------------------
    @property
    def TRef(self) -> float:
        """Returns the reference temperature of the material."""
        return (float(self.__info.TRef))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener la temperatura de referencia del material ----------------------------------------------------
    @property
    def Xc(self) -> float:
        """Longitudinal Compressive Strength"""
        return (float(self.__info.Xc))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener la temperatura de referencia del material ----------------------------------------------------
    @property
    def Xt(self) -> float:
        """Longitudinal Tensile Strength"""
        return (float(self.__info.Xt))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener la temperatura de referencia del material ----------------------------------------------------
    @property
    def Yc(self) -> float:
        """Transverse Compressive Strength"""
        return (float(self.__info.Yc))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener la temperatura de referencia del material ----------------------------------------------------
    @property
    def Yt(self) -> float:
        """Transverse Tensile Strength"""
        return (float(self.__info.Yt))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener la temperatura de referencia del material ----------------------------------------------------
    @property
    def SC(self) -> float:
        """Shear Strength"""
        return (float(self.__info.SC))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el coeficiente de amortiguamiento estructural del material -----------------------------------
    @property
    def GE(self) -> float:
        """Returns the structural damping coefficient of the material."""
        return (float(self.__info.GE))
    # ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
