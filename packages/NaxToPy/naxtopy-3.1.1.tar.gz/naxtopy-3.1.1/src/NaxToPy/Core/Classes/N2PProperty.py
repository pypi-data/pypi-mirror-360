"""Module with the class N2PProperty and all its derivated class"""

from typing import Union
from abc import ABC
import math
from NaxToPy.Core.Errors.N2PLog import N2PLog
import numpy as np
from NaxToModel import PropType


failuredict = {0: "UNKNOWN",
               1: "HILL",
               2: "HOFF",
               3: "TASI",
               4: "STRN",
               5: "HASH",
               6: "PUCK",
               7: "STRS"}


# Clase base para el resto de propiedades ------------------------------------------------------------------------------
class N2PProperty(ABC):
    """Abstract base class for all properties types. Other properties classes inherit from this class."""

    __slots__ = (
        "__info",
        "__model"
    )

    def __init__(self, information, model_father):
        """
        Constructor of the class N2PProperty. As Abaqus don't have ids for the props
        """

        self.__info = information
        self.__model = model_father

    @property
    def ID(self) -> int:
        """Solver Index for the Property"""
        if self.__info.ID is None or self.__info.ID == 0:
            N2PLog.Error.E209(self.Name)
        return self.__info.ID

    @property
    def PartID(self) -> str:
        """Part where the property is defined"""
        if self.__info.PartID is None:
            N2PLog.Error.E210(self.Name)
        return self.__model._N2PModelContent__partIDtoStr.get(self.__info.PartID, -1)

    @property
    def InternalID(self) -> int:
        """Index used by NaxToPy to identify the property"""
        return self.__info.InternalID

    @property
    def Name(self) -> str:
        """Name of the property. It is used by Abaqus"""
        return self.__info.Name

    @property
    def PropertyType(self) -> str:
        """Type of property. Example 1: "PCOMP". Example2: "SHELL SECTION" """
        return self.__info.PropertyType.ToString()

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        if self.__model.Solver == "Abaqus" or self.__model.Solver == "InputFileAbaqus":
            reprs = f"N2PProperty(\'{self.Name}\', \'{self.PropertyType}\')"
        else:
            reprs = f"N2PProperty({self.ID}, \'{self.PropertyType}\')"
        return reprs
    # ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


# Clase para definir propiedades de compuestos -------------------------------------------------------------------------
class N2PComp(N2PProperty):
    """
    Class for defining compound properties. It derives from N2PProperty.
    """

    def __init__(self, information, model_father):
        """
        Constructor of the class N2PComp. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    @property
    def NumPiles(self) -> int:
        """Number of plies of the laminate"""
        return self.__info__.NumPiles

    @property
    def IsSymmetric(self) -> bool:
        """`True` if it is Symmetric. `False` if it is not"""
        return self.__info__.IsSymetric

    @property
    def NSM(self) -> float:
        "Non Structural Mass"
        return self.__info__.NSM

    @property
    def AllowShear(self) -> float:
        """Shear allowable"""
        return self.__info__.AllowShear

    @property
    def FailTh(self) -> str:
        """Fail Theory"""
        return self.__info__.FailTh.ToString()

    @property
    def DampCoef(self) -> float:
        """Damping Coefficient"""
        return self.__info__.DampCoef

    @property
    def MatID(self) -> tuple[tuple[int, str]]:
        """Tuple with the solver tuple of thr id and part of the material for each ply of the laminate"""
        part = self.PartID
        if self.__model__.Solver == "Abaqus" or self.__model__.Solver == "InputFileAbaqus":
            return tuple((self.__model__._N2PModelContent__materialsID[mat], part) for mat in self.__info__.Mat)
        return tuple((mat, part) for mat in self.__info__.Mat)

    @property
    def Thickness(self) -> tuple[float]:
        """Tuple with the thickness for each ply of the laminate"""
        return tuple(self.__info__.Thickness)

    @property
    def Theta(self) -> tuple[float]:
        """Tuple with the orientation angle for each ply of the laminate"""
        return tuple(self.__info__.Theta)

    @property
    def SOut(self) -> tuple[bool]:
        """Tuple with the stress requirement for each ply of the laminate"""
        return tuple(self.__info__.SOut)

    @property
    def Plies(self) -> list[tuple]:
        """
        It returns a list of tuple. A tuple for a ply. Plies have four data: (MatID, Thickness, Theta, SOut)
        """
        return [(self.MatID[i], self.Thickness[i], self.Theta[i]) for i in range(self.NumPiles)]

    @property
    def EqQMatrix(self) -> list:
        """
        Returns the lamina membrane stiffness matrix (Q-Bar).
        | σx |       |   εx  | \n
        | σy | = [Q]*|   εy  | \n
        | τxy|       | γxy/2 |
        """

        q11_t = 0
        q12_t = 0
        q22_t = 0
        q16_t = 0
        q26_t = 0
        q66_t = 0

        t_thick = sum(self.Thickness) #! is self.Thickness a numpy array?

        for i in range(self.NumPiles):
            c = math.cos(math.radians(self.Theta[i]))
            s = math.sin(math.radians(self.Theta[i]))

            thick = self.Thickness[i]
            rel_thick = thick/t_thick

            mat = self.__model__._N2PModelContent__material_dict[self.MatID[i]]

            s11 = 1 / mat.YoungX
            s22 = 1 / mat.YoungY
            s12 = (-1) * mat.PoissonXY / mat.YoungX
            s66 = 1 / mat.ShearXY if mat.ShearXY != 0.0 else mat.YoungX/(2*(1+mat.PoissonXY))

            # Calculate the terms of the reduced stiffness matrix Q in the laminae coordinate system
            q11 = s22 / (s11 * s22 - s12 ** 2)
            q12 = (-1) * s12 / (s11 * s22 - s12 ** 2)
            q22 = s11 / (s11 * s22 - s12 ** 2)
            q66 = 1 / s66

            # Calculate the terms of the reduced stiffness matrix Q' in the laminate coordinate system
            q11_t += (q11 * c ** 4 + 2 * (q12 + 2 * q66) * s ** 2 * c ** 2 + q22 * s ** 4) * rel_thick #! why multiply by the thickness
            q12_t += ((q11 + q22 - 4 * q66) * s ** 2 * c ** 2 + q12 * (s ** 4 + c ** 4)) * rel_thick
            q22_t += (q11 * s ** 4 + 2 * (q12 + 2 * q66) * s ** 2 * c ** 2 + q22 * c ** 4) * rel_thick
            q16_t += ((q11 - q12 - 2 * q66) * s * c ** 3 + (q12 - q22 + 2 * q66) * s ** 3 * c) * rel_thick
            q26_t += ((q11 - q12 - 2 * q66) * s ** 3 * c + (q12 - q22 + 2 * q66) * s * c ** 3) * rel_thick
            q66_t += ((q11 + q22 - 2 * q12 - 2 * q66) * s ** 2 * c ** 2 + q66 * (s ** 4 + c ** 4)) * rel_thick

        Q = [[q11_t, q12_t, q16_t],
             [q12_t, q22_t, q26_t],
             [q16_t, q26_t, q66_t]]

        return Q
# ----------------------------------------------------------------------------------------------------------------------
    
    @property
    def EqQBenMatrix(self) -> list:
        """ Returns the lamina bending stiffness matrix. It is calculated from the D matrix.
        """
        _, _, D = self.ABDMatrix

        h3 = sum(self.Thickness)**3
        aux = 12*(D[0,0] * D[1,1] - D[0,1]**2)/(h3 * (1 - D[0,1]**2 / (D[0,0] * D[1,1])) )

        q11 = aux / D[1,1]
        q22 = aux / D[0,0]
        q12 = aux * D[0,1] / (D[0,0] * D[1,1])
        q66 = 12 * D[2,2] / h3

        q13 = q66 * D[0,2] / D[2,2]
        q23 = q66 * D[1,2] / D[2,2]

        return [[q11, q12, q13],
                [q12, q22, q23],
                [q13, q23, q66]]

    def QMatrix(self, i) -> np.ndarray:
        """
        Returns the lamina stiffness matrix (Q-Bar) as a numpy 2D array
        | σ1 |       |   ε1  |
        | σ2 | = [Q]*|   ε2  |
        | τ12|       | γ12/2 |
        
        """                

        c = np.cos(np.radians(self.Theta[i]))   
        s = np.sin(np.radians(self.Theta[i]))   

        mat = self.__model__.MaterialDict[self.MatID[i]]

        s11 = 1 / mat.YoungX
        s22 = 1 / mat.YoungY
        s12 = (-1) * mat.PoissonXY / mat.YoungX
        shear = mat.ShearXY if mat.ShearXY != 0.0 else mat.YoungX/(2*(1+mat.PoissonXY))
        s66 = 1 / shear

        # Calculate the terms of the reduced stiffness matrix Q in the lamina, principal axis, coordinate system
        q11 = s22 / (s11 * s22 - s12 ** 2)
        q12 = (-1) * s12 / (s11 * s22 - s12 ** 2)
        q22 = s11 / (s11 * s22 - s12 ** 2)
        q66 = 1 / s66

        Q = np.array([[q11, q12, 0],[q12,q22,0],[0,0,q66]])

        # Calculate the terms of the reduced stiffness matrix Q' in the laminate, general, coordinate system
       
        # Calculate matrix of rotation, [T]

        T = np.array([[c**2, s**2,2*s*c],
                      [s**2,c**2,-2*s*c],
                      [-s*c,s*c,c**2-s**2]])

        try:
            T_inv = np.linalg.inv(T)
        except Exception as e:
            msg = N2PLog.Error.E315()
            raise Exception(msg)

        # From Jones pg50-51: [sigma] = [T]**(-1)*[Q]*[T]**(-1) [eps] = [Q_bar]*[eps]

        Q_bar = T_inv @ Q @ np.transpose(T_inv)

        return Q_bar

    @property
    def EqMemProps(self) -> tuple[float, float, float, float]:
        """Calculate the Equivalent Membrane Properties of the laminate using A matrix.
        
        Returns:
            tuple[float, float, float, float]: A tuple containing (Ex, Ey, nu, G).
            
            - Ex: Equivalent Membrane modulus in the x-direction.
            - Ey: Equivalent Membrane modulus in the y-direction.
            - nu: Equivalent Membrane Poisson's ratio.
            - G: Equivalent Membrane shear modulus.
        
        Example:
            >>> pcomp: n2p.AllClasses.N2PComp = model.PropertyDict((10001, "0"))
            >>> Ex, Ey, nu, G = pcomp.EqMemProps()
        """

        A, _, _ = self.ABDMatrix

        total_thickness = sum(self.Thickness)
        determinant = A[0, 0] * A[1, 1] - A[0, 1] ** 2

        Ex = determinant / (A[1, 1] * total_thickness)
        Ey = determinant / (A[0, 0] * total_thickness)
        nu = A[0, 1] / A[1, 1]
        G = A[2, 2] / total_thickness

        return Ex, Ey, nu, G
    
    @property
    def EqBenProps(self) -> tuple[float, float, float, float]:
        """Calculate the Equivalent Bending Properties of the laminate using D matrix
        
        Returns:
            tuple[float, float, float, float]: A tuple containing (Ex, Ey, nu, G).
            
            - Ex: Equivalent Bending modulus in the x-direction.
            - Ey: Equivalent Bending modulus in the y-direction.
            - nu: Equivalent Bending Poisson's ratio.
            - G: Equivalent Bending shear modulus.
        
        Example:
            >>> pcomp: n2p.AllClasses.N2PComp = model.PropertyDict((20001, "0"))
            >>> Ex, Ey, nu, G = pcomp.EqBenProps()
        """

        _, _, D = self.ABDMatrix

        total_thickness_cube = sum(self.Thickness)**3
        determinant = 12*(D[0, 0] * D[1, 1] - D[0, 1] ** 2)

        Ex = determinant / (D[1, 1] * total_thickness_cube)
        Ey = determinant / (D[0, 0] * total_thickness_cube)
        nu = D[0, 1] / D[1, 1]
        G = D[2, 2] / total_thickness_cube

        return Ex, Ey, nu, G

    @property
    def ABDMatrix(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]: 
        """
        Calculate extensional (A), coupling (B), and bending (D) stiffness matrices

        Returns A, B, C (numpy 2D arrays) of the laminate
        """

        # Nótese que las unidades de las matrices de rigidez ABD deben ser consistentes: A [N/m], B [N] y D [N·m].

        A = np.zeros([3, 3], float)
        B = np.zeros([3, 3], float)
        D = np.zeros([3, 3], float)

        if self.NumPiles < 0:               # SYMMETRIC LAMINATE 
            Nply = abs(self.NumPiles)       # in this case Nply = half the real number of plies     
            t_thick = sum(self.Thickness)*2
            low_reference = - sum(self.Thickness)
            iterplies = np.pad(np.arange(0,Nply), (0,Nply), 'symmetric')  # e.g.: transforms [0,1,2] in [0,1,2,2,1,0]
        else:                               # NON-SYMMETRIC LAMINATE
            Nply = self.NumPiles            # in this case Nply 0 real number of plies
            t_thick = sum(self.Thickness)
            low_reference = - sum(self.Thickness) / 2
            iterplies = np.arange(0, Nply)
        
        for i in iterplies:
            
            thick = self.Thickness[i]  # tener en cuenta caso simetrico
            centroid = low_reference + thick/2            

            Q_bar = self.QMatrix(i)  # get Q_bar of the lamina in the laminate coordinate system

            # Calculate A, B, C matrices in the laminate coordinate system
            A += Q_bar*thick  # extensional_matrix
            B += Q_bar * centroid * thick  # bending_matrix
            D += Q_bar * (centroid**2 * thick + (thick**3)/12)  # coupling_matrix

            low_reference += thick

        return A, B, D


# Clase para definir propiedades de tipo placa -------------------------------------------------------------------------
class N2PShell(N2PProperty):
    """
    Class for defining shell properties. It derives from N2PProperty.
    """

    def __init__(self, information, model_father):
        """
        Constructor of the class N2PShell. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    @property
    def MatMemID(self) -> Union[tuple[int, str], tuple[str, str]]:
        """Material index for the membrane behavior"""
        if self.__model__.Solver == "Abaqus" or self.__model__.Solver == "InputFileAbaqus":
            return (self.__model__._N2PModelContent__materialsID[self.__info__.MatMemID], "ASSEMBLY")
        return (self.__info__.MatMemID, self.PartID)

    @property
    def MatBenID(self) -> Union[tuple[int, str], tuple[str, str]]:
        """Material index for the bending behavior"""
        if self.__model__.Solver == "Abaqus" or self.__model__.Solver == "InputFileAbaqus":
            return (self.__model__._N2PModelContent__materialsID[self.__info__.MatBenID], "ASSEMBLY")
        return (self.__info__.MatBenID, self.PartID)

    @property
    def MatSheID(self) -> Union[tuple[int, str], tuple[str, str]]:
        """Material index for the shell behavior"""
        if self.__model__.Solver == "Abaqus" or self.__model__.Solver == "InputFileAbaqus":
            return (self.__model__._N2PModelContent__materialsID[self.__info__.MatSheID], "ASSEMBLY")
        return (self.__info__.MatSheID, self.PartID)

    @property
    def Thickness(self) -> float:
        """Thickness of the shell"""
        return self.__info__.Thickness

    @property
    def BenMR(self) -> float:
        """Bending Moment of Inertia Ratio, 12*I/T**3."""
        return self.__info__.BenMR

    @property
    def TrShThickness(self) -> float:
        """Transverse Shear Thickness Ratio, Ts/T."""
        return self.__info__.TrShThickness

    @property
    def NSM(self) -> float:
        """Nonstructural mass per unit area"""
        return self.__info__.NSM

    @property
    def FiberDist(self) -> tuple[float, float]:
        """Fiber distances for stress calculations. The positive direction is determined by the right-hand rule, and the
        order in which the grid points are listed on the connection entry"""
        return tuple(self.__info__.FiberDist)
    
    @property
    def MatCouplID(self) -> Union[tuple[int, str], tuple[str, str]]:
        """Material identification number for membrane-bending coupling"""
        if self.__model__.Solver == "Abaqus" or self.__model__.Solver == "InputFileAbaqus":
            return (self.__model__._N2PModelContent__materialsID[self.__info__.MatCoupl], "ASSEMBLY")
        return (self.__info__.MatCoupl, self.PartID)
# ----------------------------------------------------------------------------------------------------------------------


# Clase para definir propiedades de tipo solido ------------------------------------------------------------------------
class N2PSolid(N2PProperty):
    """
    Class for defining solid properties. It derives from N2PProperty.
    """

    def __init__(self, information, model_father):
        """
        Constructor of the class N2PSolid. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    @property
    def MatID(self) -> Union[tuple[int, str], tuple[str, str]]:
        """Index of the material of the solid property"""
        if self.__model__.Solver == "Abaqus" or self.__model__.Solver == "InputFileAbaqus":
            return (self.__model__._N2PModelContent__materialsID[self.__info__.MatID], "ASSEMBLY")
        return (self.__info__.MatID, self.PartID)

    @property
    def Cordm(self) -> int:
        """Identification number of the material coordinate system."""
        return self.__info__.Cordm

    @property
    def IntNet(self) -> str:
        """Integration Network."""
        return self.__info__.IntNet.strip()

    @property
    def LocStrssOut(self) -> str:
        """Location selection for stress output."""
        return self.__info__.LocStrssOut.strip()

    @property
    def IntSch(self) -> str:
        """Integration Scheme."""
        return self.__info__.IntSch.strip()

    @property
    def Fluid(self) -> str:
        """Fluid Element Flag."""
        return self.__info__.Fluid


class N2PRod(N2PProperty):
    """
    Class for defining Rod or Truss properties. It derives from N2PProperty.
    """

    def __init__(self, information, model_father):
        """
        Constructor of the class N2PRod. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    @property
    def MatID(self) -> Union[tuple[int, str], tuple[str, str]]:
        """Material identification number."""
        if self.__model__.Solver == "Abaqus" or self.__model__.Solver == "InputFileAbaqus":
            return (self.__model__._N2PModelContent__materialsID[self.__info__.MatID], "ASSEMBLY")
        return (self.__info__.MatID, self.PartID)

    @property
    def Area(self) -> float:
        """Area of the rod|truss."""
        return self.__info__.Area

    @property
    def J(self) -> float:
        """Torsinon Constant"""
        return self.__info__.TorsinonConstant

    @property
    def CoefTorsion(self) -> float:
        """Torsional Coeficient. Abv as C. It is used to calculate the stress: tau = (C*Moment)/J"""
        return self.__info__.CoefTorsion

    @property
    def NSM(self) -> float:
        """Nonstructural mass per unit area"""
        return self.__info__.NSM


class N2PBeam(N2PProperty):
    """
    Class for defining PBEAM, PBAR and Beam section form Abaqus. It derives from N2PProperty.
    """
    def __init__(self, information, model_father):
        """
        Constructor of the class N2PBeam. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    @property
    def MatID(self) -> Union[tuple[int, str], tuple[str, str]]:
        """Material identification number."""
        mat_id = self.__info__.MatID
        if self.__model__.Solver == "Abaqus" or self.__model__.Solver == "InputFileAbaqus":
            return (self.__model__._N2PModelContent__materialsID[mat_id], "ASSEMBLY")
        elif mat_id == -1:
            return N2PLog.Warning.W702()
        return (mat_id, self.PartID)

    @property
    def Area(self) -> list:
        """Area of bar|beam at each cross-section."""
        return list(self.__info__.Area)

    @property
    def NumSeg(self) -> int:
        """Number of Segments. Only for BEAMS. For BARs it will be 0 always."""
        return self.__info__.NumSeg

    @property
    def I1(self) -> list:
        """Area moment inertia in plane 1 about the neutral axis at each cross-section"""
        return list(self.__info__.I1)

    @property
    def I2(self) -> list:
        """Area moment inertia in plane 2 about the neutral axis at each cross-section"""
        return list(self.__info__.I2)

    @property
    def I12(self) -> list:
        """Area moment inertia 12 at each cross-section (I1 * I2 > I12)"""
        return list(self.__info__.I12)

    @property
    def J(self) -> list:
        """Torsion Constant"""
        return list(self.__info__.TorsinonConstant)

    @property
    def FractionalDistance(self) -> list:
        """Fractional distance of the intermediate station from end A."""
        return list(self.__info__.FractionalDistance)

    @property
    def NSM(self) -> list:
        """Nonstructural mass per unit area"""
        return list(self.__info__.NSM)

    @property
    def K1(self) -> float:
        """Shear stiffness factor K in K*A*G for plane 1"""
        return self.__info__.K1

    @property
    def K2(self) -> float:
        """Shear stiffness factor K in K*A*G for plane 1"""
        return self.__info__.K2

    @property
    def NSIA(self) -> float:
        """Nonstructural mass moment of inertia per unit length about nonstructural mass center of gravity at end A."""
        return self.__info__.NSIA

    @property
    def NSIB(self) -> float:
        """Nonstructural mass moment of inertia per unit length about nonstructural mass center of gravity at end B."""
        return self.__info__.NSIB

class N2PBush(N2PProperty):
    """
    Class for defining PBUSH form Optistruct/Nastran. It derives from N2PProperty.
    """
    def __init__(self, information, model_father):
        """
        Constructor of the class N2PBush. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father
        self.__info__.PropertyType = PropType.PBUSH

    @property
    def Stiffness(self) -> list[float]:
        """
        List with the stiffnesses [K1, K2, K3, K4, K5, K6]
        """
        return self.__info__.Stiffness
    
    @property
    def ForceVelDamp(self) -> list[float]:
        """
        List with the Force-per-Velocity Damping [B1, B2, B3, B4, B5, B6]
        """
        return self.__info__.ForceVelDamp
    
    @property
    def StrDamp(self) -> float:
        """
        List with the Structural Damping [GE1, GE2, GE3, GE4, GE5, GE6]
        """
        return self.__info__.StrDamp
    
    @property
    def SA(self) -> float:
        """
        Stress recovery coefficient in the translational component (K1, K2, K3)
        """
        return self.__info__.SA
    
    @property
    def ST(self) -> float:
        """
        Stress recovery coefficient in the rotational component (K4, K5, K6)
        """
        return self.__info__.ST
    
    @property
    def EA(self) -> float:
        """
        Strain recovery coefficient in the translational component (K1, K2, K3)
        """
        return self.__info__.EA
    
    @property
    def ET(self) -> float:
        """
        Strain recovery coefficient in the rotational component (K4, K5, K6)
        """
        return self.__info__.ET
    

class N2PFast(N2PProperty):
    """
    Class for defining PFAST form Optistruct/Nastran. It derives from N2PProperty.
    """
    def __init__(self, information, model_father):
        """
        Constructor of the class N2PFAST. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father
    
    @property
    def Diameter(self) -> float:
        """
        Diameter of the fastener
        """
        return self.__info__.Diameter
    
    @property
    def StiffCoordSys(self) -> int:
        """
        Stiffness Coordinate System
        """
        return self.__info__.StiffCoordSys
    
    @property
    def CoordAbs(self) -> bool:
        """
        Flag that indicate if the coordinate system is relative (flase) or absolute (true)
        """
        return self.__info__.CoordAbs
    
    @property
    def Stiffness(self) -> list[float]:
        """
        List with the Displacements stiffnesses [KT1, KT2, KT3]
        """
        return list(self.__info__.Stiffness)
    
    @property
    def RotStiff(self) -> list[float]:
        """
        List with the Rotational stiffnesses [KR1, KR2, KR3]
        """
        return list(self.__info__.RotStiff)
    
    @property
    def Mass(self) -> float:
        """
        Lumped mass of the fastener
        """
        return  self.__info__.Mass
    
    @property
    def StrDamp(self) -> float:
        """
        Structural Damping
        """
        return  self.__info__.StrDamp
    
    @property
    def TExp(self) -> float:
        """
        Thermal Expansion Coeficient
        """
        return  self.__info__.TExp
    
    @property
    def TRef(self) -> float:
        """
        Reference Temperature
        """
        return self.__info__.TRef
    
    @property
    def CoinLen(self) -> float:
        """
        Length of a CFAST with coincident grids
        """
        return self.__info__.CoinLen
    
class N2PMass(N2PProperty):
    """
    Class for defining mass. It derives from N2PProperty.
    """
    def __init__(self, information, model_father):
        """
        Constructor of the class N2PMass. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    @property
    def Mass(self) -> float:
        """
        Value of scalar mass
        """
        return self.__info__.Mass
    
class N2PElas(N2PProperty):
    """
    Class that specifies the stiffness, damping coefficient, and stress coefficient of a scalar elastic (spring) element. PELAS from Optistruct/Nastran
    """
    def __init__(self, information, model_father):
        """
        Constructor of the class N2PElas. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father


    @property
    def K(self) -> float:
        """
        Stiffness Value
        """
        return self.__info__.K
    
    @property
    def GE(self) -> float:
        """
        Structural Damping
        """
        return self.__info__.GE
    
    @property
    def S(self) -> float:
        """
        Stress coefficient
        """
        return self.__info__.S
    
class N2PGap(N2PProperty):
    """
    Class that specifies the PGAP from Optistruct/Nastran
    """
    def __init__(self, information, model_father):
        """
        Constructor of the class N2PGap. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father
        self.__info__.PropertyType = PropType.PGAP

    @property
    def InitGap(self) -> float:
        """
        Initial gap opening
        """
        return self.__info__.InitGap
    
    @property
    def PreLoad(self) -> float:
        """
        Preload
        """
        return self.__info__.PreLoad
    
    @property
    def KA(self) -> float:
        """
        Axial stiffness for the closed gap
        """
        return self.__info__.KA
    
    @property
    def KB(self) -> float:
        """
        Axial stiffness for the open gap
        """
        return self.__info__.KB
    
    @property
    def KT(self) -> float:
        """
        Transverse stiffness when the gap is closed
        """
        return self.__info__.KT
    
    @property
    def MU1(self) -> float:
        """
        Coefficient of static friction for the adaptive gap element or coefficient of friction in the "y" transverse direction for the nonadaptive gap element.
        """
        return self.__info__.MU1
    
    @property
    def MU2(self) -> float:
        """
        Coefficient of kinetic friction for the adaptive gap element or coefficient of friction in the z transverse direction for the nonadaptive gap element.
        """
        return self.__info__.MU2
    
    @property
    def TMax(self) -> float:
        """
        Maximum allowable penetration used in the adjustment of penalty values. The positive value activates the penalty value adjustment
        """
        return self.__info__.TMax
    
    @property
    def MAR(self) -> float:
        """
        Maximum allowable adjustment ratio for adaptive penalty values KA and KT
        """
        return self.__info__.MAR
    
    @property
    def TRMin(self) -> float:
        """
        Fraction of TMAX defining the lower bound for the allowable penetration
        """
        return self.__info__.TRMin
    

class N2PWeld(N2PProperty):
    """
    Class that specifies the property of the connector element CWELD
    """
    def __init__(self, information, model_father):
        """
        Constructor of the class N2PWeld. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    @property
    def MatID(self) -> Union[tuple[int, str], tuple[str, str]]:
        """
        Material identification number.
        """
        if self.__model__.Solver == "Abaqus" or self.__model__.Solver == "InputFileAbaqus":
            return (self.__model__._N2PModelContent__materialsID[self.__info__.MatID], "ASSEMBLY")
        return (self.__info__.MatID, self.PartID)
    
    @property
    def Diameter(self) -> float:
        """
        Diameter of the connector
        """
        return self.__info__.Diameter
    
    @property
    def MSET(self) -> bool:
        """
        Flag to eliminate m-set degrees-of-freedom (DOFs). Active ONLY for "PARAM,OLDWELD,YES".
        """
        return self.__info__.MSET

    @property
    def Type(self) -> str:
        """
        Type of connection
        """
        return str(self.__info__.Type.ToString())
    
    @property
    def MinLength(self) -> float:
        """
        Smallest ratio of length to diameter for stiffness calculation
        """
        return self.__info__.MinLength
    
    @property
    def MaxLength(self) -> float:
        """
        Largest ratio of length to diameter for stiffness calculation
        """
        return self.__info__.MaxLength

class N2PBeamL(N2PProperty):
    """
    Class representing the beam properties (equivalent to N2BeamL in C#).
    It derives from N2PProperty.
    """
    def __init__(self, information, model_father):
        """
        Constructor for N2PBeamL, mapping the properties from the C# class.
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    @property
    def MatID(self) -> Union[tuple[int, str], tuple[str, str]]:
        """
        Material identification number.
        """
        if self.__model__.Solver == "Abaqus" or self.__model__.Solver == "InputFileAbaqus":
            return (self.__model__._N2PModelContent__materialsID[self.__info__.MatID], "ASSEMBLY")
        return (self.__info__.MatID, self.PartID)
    
    @property
    def Group(self) -> str:
        """
        Cross-section group
        """
        return self.__info__.Group
    
    @property
    def Type(self) -> str:
        """
        Cross-section shape
        """
        return str(self.__info__.Type.ToString())
    
    @property
    def DIM(self) -> list[list[float]]:
        """
        Cross-section dimensions at end A [i, 0], intermediate station j [i, j] and end B [i, -1], where i is the dimension.
        """
        return list(self.__info__.DIM)
    
    @property
    def NSM(self) -> list[float]:
        """
        Nonstructural mass per unit area
        """
        return self.__info__.NSM
    
    @property
    def StressOut(self) -> bool:
        """
        Stress output request option for intermediate station j and end B.
        """
        return self.__info__.StressOut
    
    @property
    def FractionalDistance(self) -> list[float]:
        """
        Fractional distance of the intermediate station from end A
        """
        return self.__info__.FractionalDistance
    

class N2PPropMisc(N2PProperty):
    """
    Class representing the undefined properties (equivalent to N2MatMisc in C#).
    It derives from N2PProperty.
    """
    def __init__(self, information, model_father):
        """
        Constructor for N2PMatMisc, mapping the properties from the C# class.
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    @property
    def QualitiesDict(self) -> dict[str, float]:
        """
        Dictionary with the material properties and their values.
        """
        return self.__info__.QualitiesDict