"""Script for the definition of the class Property and its child classes."""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

import numpy as np
import math as math
from abc import ABC, abstractmethod
from NaxToPy import N2PLog
from NaxToPy.Core.Classes.N2PProperty import N2PProperty
from NaxToPy.Core.Classes.N2PMaterial import N2PMaterial
from NaxToPy.Core.N2PModelContent import N2PModelContent
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Modules.common.material import Orthotropic, Isotropic

class Property:
    """
    Base class for managing properties common to all FEM property types.
    
    """

    __slots__ = (
        '_n2p_property',
        '_n2p_material',
        '_name',
        '_id',
        '_type'
    )

    def __init__(self, n2p_property: N2PProperty = None, n2p_material: dict = None):
        """
        Initialize the property from an N2PProperty instance.
        
        Args:
            : External source object containing property data.
        """
        if isinstance(n2p_property, N2PProperty) and isinstance(n2p_material, dict):
            self._n2p_property = n2p_property
            self._name = n2p_property.Name
            self._id = n2p_property.ID
            self._type = n2p_property.PropertyType
            self._n2p_material = n2p_material
        #else:
            #N2PLog.Warning.W801()
    
    
    # Getters ------------------------------------------------------------------------------------------------------------
    # Method to obtain the name attribute of the Property ----------------------------------------------------------------
    @property
    def Name(self):
        return self._name
    # --------------------------------------------------------------------------------------------------------------------
    
    # Method to obtain the id attribute of the Property ------------------------------------------------------------------
    @property
    def ID(self):
        return self._id
    # --------------------------------------------------------------------------------------------------------------------

    # Method to obtain the type attribute of the Property ----------------------------------------------------------------
    @property
    def Type(self):
        return self._type
    # --------------------------------------------------------------------------------------------------------------------


#Subclass for Composite Laminates property -------------------------------------------------------------------------------
class CompositeShell(Property):
    """
    Class for PCOMP property, representing a composite laminate.

    Attributes:
        _mat_IDs -> List of Material ID for each ply of the laminate.
        _thicknesses -> List of thicknesses for each ply of the laminate.
        _num_plies -> Total number of plies composing the laminate.
        _theta -> List of theta angles - orientation wrt XY directions - for each ply of the laminate.
        _ABD_matrix -> Array representing each component of the Global Stiffness Matrix of the laminate, 
                       considering Normal, Bending Loads and the coupling effects.
        _bearingAllowable -> Bearing allowable of the laminate     
        _OHTAllowable -> Open Hole Tension Strains allowable of the laminate [Strength]
        _OHCAllowable -> Open Hole Compression Strains allowable of the laminate [Strength]
        _FHTAllowable -> Filled Hole Tension Strains allowable of the laminate [Strength]
        _FHCAllowable -> Filled Hole Compression Strains allowable of the laminate [Strength]
        _CAIAllowable -> Compression After Impact Strength allowable of the laminate [Strength]
        _PlainTensionAllowable -> Plain Tension Strength allowable of the laminate [Strength]
        _PlainCompressionAllowable -> Plain Compression Strength allowable of the laminate [Strength]
        _PTAllowable -> Pull Through strength allowable of the laminate [Strength]


    CompositeShell instances can be intitialised both automatically from N2PProperty instances or manualy from user-input.

    When instancing from user input. The following atributes are requested:
        - NumPlies : int 
        - MatIDs : list[tuple(MatID, PartID)]
        - thicknesses : list[float]
        - theta : list[float]
        - MaterialDict : dict{N2PMaterial}     
        - simmetry (optional) : bool                 
    
    It is mandatory that NumPlies is set in first place. Other attributes might be set with no order.
    
    EXAMPLE
        laminate = CompositeShell()
        laminate.NumPlies = 6
        laminate.PartIDs = '0'
        laminate.MatIDs = [(11100000,'0'),(11100000,'0'),(11100000,'0'),(11100000,'0'),(11100000,'0'),(11100000,'0')]
        laminate.thicknesses = [0.1,0.1,0.1,0.1,0.1,0.1]
        laminate.theta = [0,45,0,90,0,-45]
        model = n2p.load_model(r"")
        laminate.MaterialDict = model.MaterialDict
        laminate.simmetry = True

        *** Every given list must have the same length as the number of plies of the laminate. Otherwise, instance will not be created.
    
    """
    __slots__ = (
        '_n2p_property',
        '_n2p_material_dict',
        '_name',
        '_id',
        '_type',
        '_mat_IDs',
        '_part_IDs',
        '_thicknesses',
        '_num_plies',
        '_simmetry',
        '_theta',
        '_ABDMATRIX',
        '_ABDmatrix_card',
        '_EqMemProps',
        '_EqBenProps',                
        '_laminate',        
        '_bearingAllowable',
        '_OHTAllowable',
        '_OHCAllowable',
        '_FHTAllowable',
        '_FHCAllowable',
        '_CAIAllowable',
        '_PlainTensionAllowable',
        '_PlainCompressionAllowable',
        '_PTAllowable'
    )

    def __init__(self, n2p_property: N2PProperty = None, n2p_material_dict: dict = None):
        """
        Initialize PCOMP-specific attributes from the external source.
        """

        super().__init__(n2p_property, n2p_material_dict)


        self._ABDMATRIX = None
        self._n2p_material_dict = n2p_material_dict

        if n2p_property is not None:
            if n2p_property.PropertyType in ('PCOMP', 'CompositeShellSection'):
                self._mat_IDs = n2p_property.MatID
                self._part_IDs = n2p_property.PartID
                self._thicknesses = n2p_property.Thickness
                self._num_plies = abs(n2p_property.NumPiles)
                self._simmetry = n2p_property.IsSymmetric
                self._theta = n2p_property.Theta
                self._ABDmatrix_card = n2p_property.ABDMatrix
                self._EqMemProps = n2p_property.EqMemProps
                self._EqBenProps = n2p_property.EqBenProps
                self._bearingAllowable = None
                self._OHTAllowable = None
                self._OHCAllowable = None
                self._FHTAllowable = None
                self._FHCAllowable = None
                self._CAIAllowable = None
                self._PlainTensionAllowable = None
                self._PlainCompressionAllowable = None 
                self._PTAllowable = None   

                # Initialize laminae layers --------------------------------------------------------------------------------------
                self._laminate = self._initialize_laminae()

                # Apply Simmetry to the laminate ---------------------------------------------------------------------------------
                if self._simmetry == True:
                    self._apply_symmetry()

                self._ABDMATRIX = self._ABDMatrix()
            else:
                N2PLog.Warning.W801() #WARNING raised when trying to assign a non composite property to CompositeShell subclass
        else:
            self._mat_IDs = []
            self._part_IDs = []
            self._thicknesses = []
            self._num_plies = 0
            self._simmetry = False
            self._theta = []
            self._EqMemProps = None
            self._EqBenProps = None
            self._bearingAllowable = None
            self._OHTAllowable = None
            self._OHCAllowable = None
            self._FHTAllowable = None
            self._FHCAllowable = None
            self._CAIAllowable = None
            self._PlainTensionAllowable = None
            self._PlainCompressionAllowable = None
            self._PTAllowable = None
            self._laminate = []



    def _can_initialize_laminae(self):
        """
        Check if all required attributes are assigned before initialising laminae instances.
        """
        return all([
            self._mat_IDs, 
            self._thicknesses, 
            self._theta, 
            self._num_plies > 0, 
            self._n2p_material_dict  # Asegura que hay materiales disponibles
        ])

    def _initialize_laminae(self):
        """
        Initialize laminae layers for the laminate. Reading data from FEM Model input.
        
        Memorization is implemented to avoid redundant instances.
        """

        if not self._can_initialize_laminae():
            return[]

        lamina_cache = {}
        Laminate = []

        for i in range(abs(self._num_plies)):
            mat_id = self._mat_IDs[i]
            lamina = Laminae(i + 1, mat_id, self._thicknesses[i], self._theta[i], self._n2p_material_dict[self._mat_IDs[i]])
            Laminate.append(lamina)
            if mat_id not in lamina_cache:
                lamina_cache[mat_id] = lamina

        return Laminate

    def _can_apply_symmetry(self):
        """
        Check if all required attributes are assigned before applying symmetry.
        """
        return all([
            self._simmetry == True,
            self._mat_IDs, 
            self._thicknesses, 
            self._theta, 
            self._num_plies > 0, 
            self._laminate,
            self._n2p_material_dict  # Asegura que hay materiales disponibles
        ])
    
    def _apply_symmetry(self):
        """
        Apply symmetry to the laminate by duplicating and reversing the existing plies. 
        Updates the _mat_IDs, _thicknesses, _theta, and _laminae lists.
        """
        if not self._can_apply_symmetry():
            return  # No hacer nada si los atributos aún no están definidos
        
        # Extender listas con los valores invertidos
        half_count = len(self._mat_IDs)
        self._mat_IDs += self._mat_IDs[half_count - 1::-1]
        self._thicknesses += self._thicknesses[half_count - 1::-1]
        self._theta += self._theta[half_count - 1::-1]

        # Actualizar número de plies
        self._num_plies = len(self._mat_IDs)

        # Recalcular laminado
        self._laminate += [
            Laminae(i + half_count + 1, self._mat_IDs[i], self._thicknesses[i], self._theta[i], self._n2p_material_dict[self._mat_IDs[i]])
            for i in range(half_count - 1, -1, -1)
        ]

    def _ABDMatrix(self):
        """
        Method to compute the equivalent QMatrix f the laminate.
        """
        # A = np.zeros([3,3], float)
        # B = np.zeros([3, 3], float)
        # D = np.zeros([3, 3], float)

        # t_thickness = sum(self._thicknesses)
        # Nply = self._num_plies
        # if self._simmetry == True:
        #     low_reference = - sum(self._thicknesses)
        # else:
        #     low_reference = - sum(self._thicknesses) / 2

        # for i in range(self._num_plies):

        #     thickness = self._thicknesses[i]
        #     centroid = low_reference + thickness/2

        #     A += self._laminate[i]._Qbar * thickness
        #     B += self._laminate[i]._Qbar *centroid * thickness
        #     D += self._laminate[i]._Qbar * (centroid**2 * thickness+(thickness**3)/12)

        #     low_reference += thickness
            
        # return A, B, D
    
        # Initialize matrices
        A = np.zeros((3, 3), dtype=float)
        B = np.zeros((3, 3), dtype=float)
        D = np.zeros((3, 3), dtype=float)

        # Compute total thickness
        t_thickness = np.sum(self._thicknesses)
        low_reference = -t_thickness if self._simmetry else -t_thickness / 2

        # Convert lists to NumPy arrays for vectorized calculations
        thicknesses = np.array(self._thicknesses)
        centroids = low_reference + np.cumsum(thicknesses) - thicknesses / 2
        Qbar_matrices = np.array([lamina._Qbar for lamina in self._laminate])

        # Compute A, B, and D matrices in a vectorized manner
        A = np.sum(Qbar_matrices * thicknesses[:, None, None], axis=0)
        B = np.sum(Qbar_matrices * (centroids * thicknesses)[:, None, None], axis=0)
        D = np.sum(Qbar_matrices * ((centroids**2 * thicknesses + thicknesses**3 / 12)[:, None, None]), axis=0)

        return A, B, D
    
    def EqMemProps(self):

        """Calculate the Homogenized Membrane Properties of the laminate using A matrix.

        Returns:
            tuple[float, float, float, float]: A tuple containing (Ex, Ey, nu, G).

            - Ex: Equivalent Membrane modulus in the x-direction.
            - Ey: Equivalent Membrane modulus in the y-direction.
            - nu: Equivalent Membrane Poisson's ratio.
            - G: Equivalent Membrane shear modulus.

        Example:
            >>> CompositeShell: user_laminate = CompositeShell()
            >>>                 user_laminate.NumPlies = 6
            >>>                 user_laminate.PartIDs = '0'
            >>>                 user_laminate.MatIDs = [(11211000,'0'),(11211000,'0'),(11211000,'0'),(11211000,'0'),(11211000,'0'),(11211000,'0')]
            >>>                 user_laminate.thicknesses = [0.1,0.1,0.1,0.1,0.1,0.1]
            >>>                 user_laminate.theta = [0,45,0,90,0,-45]
            >>>                 user_laminate.MaterialDict = model_test.MaterialDict
            >>> Ex, Ey, nu, G = user_laminate.EqMemProps()
        """

        A, _, _ = self._ABDMatrix()

        total_thickness = sum(self._thicknesses)
        determinant = A[0, 0] * A[1, 1] - A[0, 1] ** 2

        Ex = determinant / (A[1, 1] * total_thickness)
        Ey = determinant / (A[0, 0] * total_thickness)
        nu = A[0, 1] / A[1, 1]
        G = A[2, 2] / total_thickness

        return Ex, Ey, nu, G

    def EqBenProps(self):

        """Calculate the Homogenized Bending Properties of the laminate using D matrix.

        Returns:
            tuple[float, float, float, float]: A tuple containing (Ex, Ey, nu, G).

            - Ex: Equivalent Bending modulus in the x-direction.
            - Ey: Equivalent Bending modulus in the y-direction.
            - nu: Equivalent Bending Poisson's ratio.
            - G: Equivalent Bending shear modulus.

        Example:
            >>> CompositeShell: user_laminate = CompositeShell()
            >>>                 user_laminate.NumPlies = 6
            >>>                 user_laminate.PartIDs = '0'
            >>>                 user_laminate.MatIDs = [(11211000,'0'),(11211000,'0'),(11211000,'0'),(11211000,'0'),(11211000,'0'),(11211000,'0')]
            >>>                 user_laminate.thicknesses = [0.1,0.1,0.1,0.1,0.1,0.1]
            >>>                 user_laminate.theta = [0,45,0,90,0,-45]
            >>>                 user_laminate.MaterialDict = model_test.MaterialDict
            >>> Ex, Ey, nu, G = user_laminate.EqBenProps()
        """

        _, _, D = self._ABDMatrix()

        total_thickness_cube =  sum(self._thicknesses)**3
        determinant = 12*(D[0, 0] * D[1, 1] - D[0, 1] ** 2)

        Ex = determinant / (D[1, 1] * total_thickness_cube)
        Ey = determinant / (D[0, 0] * total_thickness_cube)
        nu = D[0, 1] / D[1, 1]
        G = D[2, 2] / total_thickness_cube

        return Ex, Ey, nu, G

    
    # Getters -------------------------------------------------------------------------------------------------------------
    # Method to obtain the PartID associated to the property ---------------------------------------------------------------
    @property
    def PartIDs(self) -> str:
        """ Return the part ID of the element."""
        return self._part_IDs
    
    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain list of Material IDs for each ply of the laminate --------------------------------------------------
    @property
    def MatIDs(self) -> list[tuple]:
        """ Return the list of tuples which defines the material for each 
        ply of the laminate. """
        return self._mat_IDs

    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the orientation of each ply in the laminate --------------------------------------------------------
    @property
    def theta(self)-> list:
        """Return the list of theta angles."""
        return self._theta
    
    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the thicknesses of each ply in the laminate --------------------------------------------------------    
    @property 
    def thicknesses(self) -> list:
        """Return the list of theta angles."""
        return self._thicknesses

    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the number of plies of the laminate ----------------------------------------------------------------
    @property
    def NumPlies(self) -> int:
        """ Return the number of plies of the laminate."""
        return self._num_plies
    
    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the simmetry condition of the laminate -------------------------------------------------------------
    @property
    def simmetry(self) -> bool:
        """ Return the simmetry condition of the laminate."""
        return self._simmetry
    
    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the detailed Laminate - in terms of Lamina instance containing material properties for each ply ----
    @property
    def Laminate(self)-> list:
        """Return the list of laminae objects."""
        return self._laminate

    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Bearing allowable of the laminate --------------------------------------------------------------
    @property
    def BearingAllowable(self) -> float:
        """
        Property that returns the Bearing Allowable of the laminate.
        """
        return self._bearingAllowable
    
    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Open Hole Tension Strength Strains allowable of the laminate -------------------------------------------
    @property
    def OHTAllowable(self) -> float:
        """
        Property that returns the Open Hole Tension Strength Strains allowable of the laminate.
        """
        return self._OHTAllowable

    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Open Hole Compression Strength Strains allowable of the laminate ---------------------------------------
    @property
    def OHCAllowable(self) -> float:
        """
        Property that returns the Open Hole Compression Strength Strains allowable of the laminate.
        """
        return self._OHCAllowable
        
    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Filled Hole Tension Strength Strains allowable of the laminate -----------------------------------------
    @property
    def FHTAllowable(self) -> float:
        """
        Property that returns the Filled Hole Tension Strength Strains allowable of the laminate.
        """
        return self._FHTAllowable
        
    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Filled Hole Compression Strength Strains allowable of the laminate -------------------------------------
    @property
    def FHCAllowable(self) -> float:
        """
        Property that returns the Filled Hole Compression Strength Strains allowable of the laminate.
        """
        return self._FHCAllowable
    
    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Compression After Impact Strength allowable of the laminate ------------------------------------        
    @property
    def CAIAllowable(self) -> float:
        """
        Property that returns the Compression After Impact Strength allowable of the laminate.
        """
        return self._CAIAllowable
        
    # ---------------------------------------------------------------------------------------------------------------------

    #Method to obtain the Plain Tension Strength allowable of the laminate ------------------------------------------------
    @property
    def PlainTensionAllowable(self) -> float:
        """
        Property that returns the Plain Tension Strength allowable of the laminate.
        """
        return self._PlainTensionAllowable
        
    @property
    def PlainCompressionAllowable(self) -> float:
        """
        Property that returns the Plain Compression Strength allowable of the laminate.
        """
        return self._PlainCompressionAllowable
    
    @property
    def PTAllowable(self) -> float:
        """
        Property that returns the Pull Through Strength allowable of the laminate.
        """
        return self._PTAllowable
    
    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the total Thickness of the Laminate ----------------------------------------------------------------             
    @property
    def Thickness(self):
        return sum(self._thicknesses)

    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Material Dict given from user -------------------------------------------------------------------
    @property
    def MaterialDict(self):
        """
        Property that returns that N2PMaterial instances given from user input.
        """
        return self._n2p_material_dict
    
    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Material Dict given from user -------------------------------------------------------------------
    @property
    
    def Thickness(self):
        """
        Property that returns the total thickness of the laminate.
        """
        return sum(self._thicknesses)
    
    # ---------------------------------------------------------------------------------------------------------------------

    # Method to obtain the ABDMatrix of the laminate
    @property
    def ABDMatrix(self):
        """
        Property that returns the ABDMatrix of the laminate
        """
        return self._ABDMATRIX

    # ---------------------------------------------------------------------------------------------------------------------

    
    # Setters -------------------------------------------------------------------------------------------------------------   
    # ---------------------------------------------------------------------------------------------------------------------
    @NumPlies.setter
    def NumPlies(self, value: int):
        if type(value) == int:
            self._num_plies = value
        else:
            raise Exception("NumPlies must be an integer")
        
        if self._can_initialize_laminae():
            self._laminate = self._initialize_laminae()

        if self._can_apply_symmetry():
            self._apply_symmetry()   
        
    # ----------------------------------------------------------------------------------------------------------
    
    @MatIDs.setter
    def MatIDs(self, value: list[tuple]):
        if not isinstance(value, list):
            raise TypeError("MatIDs must be a list of tuples")

        if not all(isinstance(item, tuple) for item in value):
            raise TypeError("All elements in MatIDs must be tuples")

        if len(value) != self._num_plies:
            raise ValueError("List length must be the same as the number of plies")
        self._mat_IDs = value

        if self._can_initialize_laminae():
            self._laminate = self._initialize_laminae()

        if self._can_apply_symmetry():
            self._apply_symmetry()

    # ----------------------------------------------------------------------------------------------------------        
    
    @PartIDs.setter
    def PartIDs(self, value: str):
        if not isinstance(value, str):
            raise TypeError("PartID must be a string")
        self._part_IDs = value

    # ----------------------------------------------------------------------------------------------------------     
    
    @thicknesses.setter
    def thicknesses(self, value):
        if not isinstance(value, (list, tuple)):
            raise TypeError("thicknesses must be a list")

        if len(value) != self._num_plies:
            raise ValueError("List length must be the same as the number of plies")
        self._thicknesses = value

        if self._can_initialize_laminae():
            self._laminate = self._initialize_laminae()

        if self._can_apply_symmetry():
            self._apply_symmetry()

    # ---------------------------------------------------------------------------------------------------------- 
   
    @theta.setter
    def theta(self, value):
        if not isinstance(value, (list, tuple)):
            raise TypeError("theta must be a list")

        if len(value) != self._num_plies:
            raise ValueError("List length must be the same as the number of plies")
        self._theta = value

        if self._can_initialize_laminae():
            self._laminate = self._initialize_laminae()

        if self._can_apply_symmetry():
            self._apply_symmetry()

    # ---------------------------------------------------------------------------------------------------------- 
    
    @simmetry.setter
    def simmetry(self, value:bool):
        if not isinstance(value, bool):
            raise TypeError("simmetry must be a bool (True/False)")
        self._simmetry = value

        if self._can_initialize_laminae():
            self._laminate = self._initialize_laminae()

        if self._can_apply_symmetry():
            self._apply_symmetry()
        
    # ----------------------------------------------------------------------------------------------------------
    
    @MaterialDict.setter
    def MaterialDict(self, value: dict):
        if type(value) == dict:
            self._n2p_material_dict = value
        else:
            raise Exception("MaterialDict must be a dict of N2PMaterial instances")
        
        if self._can_initialize_laminae():
            self._laminate = self._initialize_laminae()

        if self._can_apply_symmetry():
            self._apply_symmetry()

    # ----------------------------------------------------------------------------------------------------------     
    
    @BearingAllowable.setter
    def BearingAllowable(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._bearingAllowable = value
        else:
            raise Exception("BearingAllowable must be a float")    
    # ---------------------------------------------------------------------------------------------------------- 
    @OHTAllowable.setter
    def OHTAllowable(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._OHTAllowable = value
        else:
            raise Exception("OHTAllowable must be a float")
            
    # ----------------------------------------------------------------------------------------------------------         
    
    @OHCAllowable.setter
    def OHCAllowable(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._OHCAllowable = value
        else:
            raise Exception("OHCAllowable must be a float")
            
    # ----------------------------------------------------------------------------------------------------------         
    
    @FHTAllowable.setter
    def FHTAllowable(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._FHTAllowable = value
        else:
            raise Exception("FHTAllowable must be a float")
           
    # ----------------------------------------------------------------------------------------------------------          
    
    @FHCAllowable.setter
    def FHCAllowable(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._FHCAllowable = value
        else:
            raise Exception("FHCAllowable must be a float")
            
    # ----------------------------------------------------------------------------------------------------------         
    
    @CAIAllowable.setter
    def CAIAllowable(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._CAIAllowable = value
        else:
            raise Exception("CAIAllowable must be a float")    
        
    @PlainTensionAllowable.setter
    def PlainTensionAllowable(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._PlainTensionAllowable = value
        else:
            raise Exception("PlainTensionAllowable must be a float")    
        
    @PlainCompressionAllowable.setter
    def PlainCompressionAllowable(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._PlainCompressionAllowable = value
        else:
            raise Exception("PlainCompressionAllowable must be a float")   
        
    @PTAllowable.setter
    def PTAllowable(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._PTAllowable = value
        else:
            raise Exception("PTAllowable must be a float")

    @Laminate.setter
    def Laminate(self, value: list):
        # if type(value) == list[Laminae]:
        if type(value) == list:
            self._laminate = value
        else:
            raise Exception("Laminate must be a list of Laminae")
        
    @ABDMatrix.setter
    def ABDMatrix(self, value):
        self._ABDMATRIX = value

    @ABDMatrix.setter
    def ABDMatrix(self, value):
        # if type(value) == list[Laminae]:
        self._ABDMATRIX = value



    def QMatrix(self,i):

        """
        Delegate method from N2PProperty Core class to compute Reduced Stiffness Matrix in each ply of the laminate.
        """
        
        if self._n2p_property.IsSymmetric:
            i = int(len(self.theta)/2 - (i -(len(self.theta)/2 -1))) if i >= len(self.theta)/2 else int(i)
        return self._n2p_property.QMatrix(i)
    


    # def __repr__(self):
    #     return (f"CompositeShell(PropID={self._id}, num_plies={self._num_plies})")
    


#Subclass for Shell property ------------------------------------------------------------------------------------------
class Shell(Property):

    """Class for defining shell properties. It derives from Property
        
        Attributes:
        MatMem_ID   -> shell material identification number for membrane. tuple (Material ID, 'Part ID') 
        MatBen_ID   -> shell material identification number for bending. tuple (Material ID, 'Part ID')  
        MatShe_ID   -> shell material identification number for trasnverse shear. tuple (Material ID, 'Part ID')
        MatCoup_ID  -> shell material identification number for membrane-bending coupling. tuple (Material ID, 'Part ID')
        Part_ID     -> shell part ID.
        Thickness   -> Total thickness of the shell.
        Ben_ratio   -> Bending moment of inertia ratio of the shell.
        Tst_ratio   -> Transverse shear thickness ratio of the shell. 
        Fbru_e2d    -> Ultimate Bearing allowable of the shell for e/D = 2 [Strength]
        Fbru_e1p5d  -> Ultimate Bearing allowable of the shell for e/D = 1.5 [Strength]
        Ftu         -> Ultimate Tension allowable of the shell [Strength]
        Fcu         -> Ultimate Compression allowable of the shell [Strength]
        Fsu         -> Ultimate Shear allowable of the shell [Strength]                        
    
    """
    __slots__ = (
        '_n2p_property',
        '_n2p_material',
        '_matMem_ID',
        '_matBen_ID',
        '_matShe_ID',
        '_matCoup_ID',
        '_part_ID',
        '_thickness',
        '_ben_ratio',
        '_tst_ratio',
        '_fbru_e2d',
        '_fbru_e1p5d',        
        '_ftu',
        '_fcu',
        '_fsu'
    )

    def __init__(self, n2p_property: N2PProperty, n2p_material: dict):
        """
        Initialize SHELL-specific attributes from the external source.
        """
        super().__init__(n2p_property, n2p_material)
        if n2p_property:
            self._n2p_property = n2p_property
            if n2p_property.PropertyType in ['PSHELL','ShellSection','HomogeneousShellSection']:
                    
                # Specific PSHELL attributes --------------------------------------------------------------------------------------
                self._matMem_ID = n2p_property.MatMemID
                self._matBen_ID = n2p_property.MatBenID
                self._matShe_ID = n2p_property.MatSheID
                self._matCoup_ID = n2p_property.MatCouplID
                self._part_ID = n2p_property.PartID
                self._thickness = n2p_property.Thickness
                self._ben_ratio = n2p_property.BenMR
                self._tst_ratio = n2p_property.TrShThickness
                # Specific PSHELL attributes for module calculation (allowable values)---------------------------------------------
                self._fbru_e2d = None
                self._fbru_e1p5d = None              
                self._ftu = None
                self._fcu = None
                self._fsu = None                

            else:
                N2PLog.Error.E806() #error raised when trying to assign a non shell property to Shell subclass
        else:
            N2PLog.Error.E805()  

    def __repr__(self):
        return (f"Shell(PropID={self._id}, thickness={self._thickness})")
    

    # Getters ---------------------------------------------------------------------------------------------------  
    @property
    def MatBenID(self):
        """Property that returns the matBen ID"""
        return self._matBen_ID

    @property
    def MatCoupID(self):
        """Property that returns the matCoup ID"""
        return self._matCoup_ID

    @property
    def MatMemID(self):
        """Property that returns the matMem ID"""
        return self._matMem_ID

    @property
    def MatSheID(self):
        """Property that returns the matShe ID"""
        return self._matShe_ID

    @property
    def Thickness(self):
        """Property that returns the shell thickness"""
        return self._thickness

    @property
    def BenMR(self):
        """Property that returns the BenMR"""
        return self._matBen_ID

    @property
    def TrShThickness(self):
        """Property that returns the tst ratio"""
        return self._tst_ratio

    @property
    def Fbru_e2d(self):
        """Property that returns the Ultimate Bearing Strength allowable of the shell for e/D = 2 [Strength]"""
        return self._fbru_e2d    
     
    @property
    def Fbru_e1p5d(self):
        """Property that returns the Ultimate Bearing Strength allowable of the shell for e/D = 1.5 [Strength]"""
        return self._fbru_e1p5d  
      
    @property
    def Ftu(self):
        """Property that returns the Ultimate Tension Strength allowable of the shell [Strength]"""
        return self._ftu            
    
    @property
    def Fcu(self):
        """Property that returns the Ultimate Compression Strength allowable of the shell [Strength]"""
        return self._fcu       
    
    @property
    def Fsu(self):
        """Property that returns the Ultimate Shear Strength allowable of the shell [Strength]"""
        return self._fsu        

    # Setters ---------------------------------------------------------------------------------------------------            
    @Fbru_e2d.setter
    def Fbru_e2d(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._fbru_e2d = value
        else:
            raise Exception("Fbru_e2d must be a float")              
        
    @Fbru_e1p5d.setter
    def Fbru_e1p5d(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._fbru_e1p5d = value
        else:
            raise Exception("Fbru_e1p5d must be a float")      

    @Ftu.setter
    def Ftu(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._ftu = value
        else:
            raise Exception("Ftu must be a float")      

    @Fcu.setter
    def Fcu(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._fcu = value
        else:
            raise Exception("Fcu must be a float")             

    @Fsu.setter
    def Fsu(self, value: float):

        # If "value" is a float, it is stored.
        if type(value) == float:
            self._fsu = value
        else:
            raise Exception("Fsu must be a float")      


#Subclass for Solid property ------------------------------------------------------------------------------------------
class CompSolid(Property):
    """Class for homogeneous solid properties. Not implemented yet"""

    def __init__(self):
        print("Class not implemented yet")


class Laminae:
    """
    Class representing a single layer (lamina) in a composite laminate.

    Attributes:
        lamina_id (int): Identifier for the lamina.
        mat_id (int): Identifier for the material associated to the lamina.
        thickness (float): Thickness of the lamina.
        theta (float): Orientation angle of the lamina in degrees.
        Ex, Ey, Nuxy (float): Mechanical properties of the lamina derived from the material.
        Xt, Xc, Yt, Yc, S (float): Strength properties of the lamina derived from the material.
        
    """
    __slots__ = (
    '_lamina_id',
    '_mat_ID',
    '_thickness',
    '_theta',
    '_material',
    '_Ex',
    '_Ey',
    '_Nuxy',
    '_Nuyx',
    '_G',
    '_Qmatrix',
    '_Qbar',
    '_isActive'
)

    def __init__(self, lamina_ID: int = None, mat_ID: int = None, thickness: float = None, theta: float = None, n2p_material: N2PMaterial = None):


        """
        Initialize a single layer of the laminate.

        Args:
            lamina_ID (int): Unique identifier for the lamina.
            mat_ID (int): Identifier for the associated material.
            thickness (float): Thickness of the lamina.
            theta (float) Orientation angle of the lamina in degrees.

        Instances will be initialised from N2PMaterial instances when creating CompositeShell instances from FEM Models.

        User has the option to create empty Laminae instances.
        """


        self._lamina_id = lamina_ID if lamina_ID is not None else -1
        self._mat_ID = mat_ID if mat_ID is not None else -1
        self._thickness = thickness if thickness is not None else 0.0
        self._theta = theta if theta is not None else 0.0
        self._material = None
        self._isActive = True
        self._Ex = None
        self._Ey = None
        self._Nuxy = None
        self._Nuyx = None
        self._G = None
        self._Qmatrix = None
        self._Qbar = None

        # Initialize material properties using the Orthotropic(Material) class -----------------------------------------
        if n2p_material is not None:
            self._material = self._initialize_material_properties(n2p_material)

    def _initialize_material_properties(self, n2p_material: N2PMaterial):
        """
        Initialize mechanical properties from a material instance.

        Args:
            n2p_material (N2PMaterial): source object representing the material data
        """

        material = Orthotropic(n2p_material)                          # Create an orthotropic instance from an N2PMaterial

        # # Validate material is orthotropic -----------------------------------------------------------------------------    
        if not isinstance(material, Orthotropic):
            raise TypeError(f"Material ID {self._mat_ID} is not an orthotropic material")

        # Assign  mechanical properties to our Lamainae instances from Orthotropic instances ----------------------------
        self._Ex = material.YoungX
        self._Ey = material.YoungY
        self._Nuxy = material.PoissonXY
        self._Nuyx = (self._Ey/self._Ex)*self._Nuxy
        self._G = material.ShearXY
        # self._Xt = material.Allowables.XTensile
        # self._Xc = material.Allowables.XCompressive
        # self._Yt = material.Allowables.YTensile
        # self._Yc = material.Allowables.YCompressive
        # self._S = material.Allowables.Shear
        self._Qmatrix, self._Qbar = self.compute_Qmatrix()

        return material

    def compute_Qmatrix(self):
        """
        Method to compute stiffness matrix Q in local axis system using material properties from each lamina
        """
        
        # Factor initialisation -----------------------------------------------------------------------------------------

        Q11 = self._Ex / (1 - self._Nuxy*self._Nuyx)
        Q12 = self._Nuxy*self._Ey/(1 - self._Nuxy*self._Nuyx)
        Q22 = self._Ey / (1 - self._Nuxy*self._Nuyx)
        Q66 = self._G

        Q = np.array([

            [Q11, Q12, 0],
            [Q12, Q22, 0],
            [0, 0, Q66]
        ])

        """
        Once local Qmatrix is obtained, computations extend to the global axis of the laminate. Theta angle for
        each ply is taken into consideration for matrix rotation.
        """ 

        theta = self._theta
        cos_t = math.cos(np.radians(theta))
        sin_t = math.sin(np.radians(theta))
        T = np.array([
                    [cos_t**2, sin_t**2, 2*cos_t*sin_t],
                    [sin_t**2, cos_t**2, -2*cos_t*sin_t],
                    [-sin_t*cos_t, sin_t*cos_t, cos_t**2 - sin_t**2]
                    ])


        T_inv = np.linalg.inv(T)
        Q_bar = T_inv @ Q @T_inv.T


        return Q, Q_bar

    def copy(self):
        """
        Method to create a maual copy of laminae instances
        """
        return Laminae(self.lamina_id, self.mat_id, self.thickness, self.theta, self._material)



    # Getters ----------------------------------------------------------------------------------------------------------
    # Method to obtain the lamina id with regard to full laminate. -----------------------------------------------------
    @property
    def lamina_ID(self):
        return self._lamina_id

    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the material id of the lamina. ------------------------------------------------------------------
    @property
    def mat_ID(self):
        return self._mat_ID

    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the thickness of the lamina. --------------------------------------------------------------------
    @property
    def thickness(self):
        return self._thickness

    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the fiber orientation of the lamina. ------------------------------------------------------------
    @property
    def theta(self):
        return self._theta
    
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Young modulus in the x direction - which is also considered as fiber direction. -------------
    @property
    def Ex(self):
        return self._Ex
    
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Young modulus in the y direction - which is also considered as transverse fiber direction. --
    @property
    def Ey(self):
        return self._Ey
    
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Poisson coefficient in xy direction - ie longitudinal/transverse fiber direction. ---------------
    @property
    def Nuxy(self):
        return self._Nuxy
    
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Poisson coefficient in xy direction - ie longitudinal/transverse fiber direction. ---------------
    @property
    def Nuyx(self):
        return self._Nuyx

    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Shear Modulus in xy direction - ie longitudinal/transverse fiber direction. ---------------
    @property
    def ShearXY(self):
        return self._G

    # ------------------------------------------------------------------------------------------------------------------
    
    # Method to obtain the Tensile allowable (stress) in X direction - fiber direction. --------------------------------
    @property
    def Xt(self):
        return self._Xt
    
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Compressive allowable (stress) in X direction - fiber direction. ----------------------------
    @property
    def Xc(self):
        return self._Xc
    
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Tensile allowable (stress) in Y direction - transverse fiber direction. ---------------------
    @property
    def Yt(self):
        return self._Yt
    
    # ------------------------------------------------------------------------------------------------------------------

    # Method to the obtain Compressive allowable (stress) in Y direction - transverse fiber direction. -----------------
    @property
    def Yc(self):
        return self._Yc
    
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Shear allowable (stress). -------------------------------------------------------------------
    @property
    def S(self):
        return self._S
    
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Reduced Stiffness Matrix - local axis - of the lamina. ---------------------------------------------------------
    @property
    def Qmatrix(self):
        return self._Qmatrix
    
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Reduced Stiffness Matrix - global axis - of the lamina. ---------------------------------------------------------
    @property
    def QBar(self):
        return self._Qbar

    # ------------------------------------------------------------------------------------------------------------------

    # Method to Activate - Deactivate the lamina stiffness-wise - i.e when the laina fails under loading condition. ----
    @property
    def isActive(self):
        return self._isActive

    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the material instance of the lamina -------------------------------------------------------------
    @property
    def material(self):
        return self._material

    # ------------------------------------------------------------------------------------------------------------------


    # Setters ----------------------------------------------------------------------------------------------------------

    @lamina_ID.setter
    def lamina_ID(self, value: int):
        if type(value) == int:
            self._lamina_id = value
        else:
            raise Exception("lamina_ID must be an integer")

    @mat_ID.setter
    def mat_ID(self, value: tuple):
        if type(value) == tuple:
            self._mat_ID = value
        else:
            raise Exception("mat_ID must be an integer")

    @thickness.setter
    def thickness(self, value: float):
        if type(value) == float:
            self._thickness = value
        else:
            raise Exception("thickness must be a float")

    @theta.setter
    def theta(self, value: int):
        if type(value) == float:
            self._theta = value
        else:
            raise Exception("theta must be a float") 
        
    @material.setter
    def material(self, value: Orthotropic):
        if type(value) == Orthotropic:
            self._material = value
        else:
            raise Exception("material must be Orthotropic")
    
    @Ex.setter
    def Ex(self, value: float):
        if type(value) == float:
            self._Ex = value
        else: 
            raise Exception("Ex must be a float")
        
    @Ey.setter
    def Ey(self, value: float):
        if type(value) == float:
            self._Ey = value
        else: 
            raise Exception("Ey must be a float")

    @Nuxy.setter
    def Nuxy(self, value: float):
        if type(value) == float:
            self._Nuxy = value
        else: 
            raise Exception("Nuxy must be a float")    
            
            
    @Nuyx.setter
    def Nuyx(self, value: float):
        if type(value) == float:
            self._Nuyx = value
        else: 
            raise Exception("Nuyx must be a float")

    @ShearXY.setter
    def ShearXY(self, value: float):
        if type(value) == float:
            self._G = value
        else: 
            raise Exception("Nuyx must be a float")      
        
    @Qmatrix.setter
    def Qmatrix(self, value):
        self._Qmatrix = value

    @QBar.setter
    def QBar(self, value):
        self._Qbar = value


    @isActive.setter
    def isActive(self, value:bool):
        if not isinstance(value, bool):
            raise Exception('isActive must be a bool')

        if self._isActive == value:  # Skip recomputation if no change
            return  

        self._isActive = value
        if not self._isActive:
            self._Qmatrix = np.zeros((3, 3))
            self._Qbar = np.zeros((3, 3))
        else:
            self._Qmatrix, self._Qbar = self.compute_Qmatrix()

            
        # if self.isActive == value:  # Skip recomputation if no change
        #     return  

        # self.isActive = value
        # if not self.isActive:
        #     self._Qmatrix = np.zeros((3, 3))
        #     self._Qbar = np.zeros((3, 3))

    #------------------------------------------------------------------------------------------------------------------
    def __repr__(self):
        return (f"{self._mat_ID[0]}, {self._theta}, {self._thickness}")


class IsotropicShell:
    def __init__(self, thickness: float, isotropic_mat: Isotropic):
        self._material = isotropic_mat
        self._thickness = thickness
        self._young = isotropic_mat.Young
        self._shear = isotropic_mat.Shear
        self._poisson = isotropic_mat.Poisson
        self._allowables = isotropic_mat.Allowables

    @property
    def Thickness(self):
        return self._thickness

    @property
    def Young(self):
        return self._young

    @property
    def Shear(self):
        return self._shear

    @property
    def Poisson(self):
        return self._poisson

    @property
    def Allowables(self):
        return self._allowables

class Core:

    def __init__(self, index_core: int, core_type: str, n2p_property: N2PProperty, material_dict: dict):

        if isinstance(n2p_property, N2PProperty) and isinstance(material_dict, dict):
            self._n2p_property = n2p_property
            mat_ID = self._n2p_property.MatID[index_core]
            self._material = material_dict[mat_ID]
            self._core_type = core_type
            self._thickness = self._n2p_property.Thickness[index_core]
        else:
            raise Exception(
                'Property must be a "N2PProperty" instance and material_dict must be a dict from FEM model')

    @property
    def Material(self):
        return self._material

    @property
    def CoreType(self):
        return self._core_type

    @property
    def Thickness(self):
        return self._thickness

class Sandwich:

    def __init__(self, core_type, n2p_property: N2PProperty = None, n2p_material: dict = None,
                 mat_dict: dict = None):
        # Check that the sandwich structure comes from a PCOMP and initialize it
        if isinstance(n2p_property, N2PProperty) and isinstance(n2p_material, dict):
            self._n2p_property = n2p_property
            self._name = n2p_property.Name
            self._id = n2p_property.ID
            self._core_type = core_type
            self._n2p_material = n2p_material
            self._materials = mat_dict
        else:
            N2PLog.Warning.W801()

        # Find the core (layer with maximum thickness)
        index_core = self._n2p_property.Thickness.index(max(self._n2p_property.Thickness))
        core_thickness = self._n2p_property.Thickness[index_core]  # Core thickness

        # Check that core is oriented to 0 degrees (otherwise raise an error)
        if self._n2p_property.Theta[index_core] != 0:
            msg = N2PLog.Critical.C960()
            raise Exception(msg)

        # Retrieve the properties from the upper and lower facesheets of the sandwich and store it on CompositeShell
        lower_thickness = []
        lower_matIDs = []
        lower_theta = []

        # Initialize core
        self._core = Core(index_core, self._core_type, self._n2p_property, self._materials)

        for layer in range(index_core):
            lower_thickness.append(self._n2p_property.Thickness[layer])
            lower_matIDs.append(self._n2p_property.MatID[layer])
            lower_theta.append(self._n2p_property.Theta[layer])

        upper_thickness = []
        upper_matIDs = []
        upper_theta = []

        for layer in range(index_core + 1, len(self._n2p_property.Thickness)):
            upper_thickness.append((self._n2p_property.Thickness[layer]))
            upper_matIDs.append(self._n2p_property.MatID[layer])
            upper_theta.append(self._n2p_property.Theta[layer])

        if len(lower_matIDs) == 1:  # Isotropic lower face
            self._lower_face = IsotropicShell(lower_thickness[0], mat_dict[lower_matIDs[0]])
        else:
            # Initialize upper and lower face as instances from CompositeShell
            self._lower_face = CompositeShell()
            self._lower_face._num_plies = index_core
            self._lower_face.MaterialDict = n2p_material
            self._lower_face.MatIDs = lower_matIDs
            self._lower_face.theta = lower_theta
            self._lower_face.thicknesses = lower_thickness
            self._lower_face.Laminate = self._lower_face._initialize_laminae()

        if len(upper_matIDs) == 1:  # Isotropic upper face
            self._upper_face = IsotropicShell(upper_thickness[0], mat_dict[upper_matIDs[0]])
        else:
            self._upper_face = CompositeShell()
            self._upper_face._num_plies = len(self._n2p_property.Thickness) - (index_core + 1)
            self._upper_face.MaterialDict = n2p_material
            self._upper_face.MatIDs = upper_matIDs
            self._upper_face.theta = upper_theta
            self._upper_face.thicknesses = upper_thickness
            self._upper_face.Laminate = self._lower_face._initialize_laminae()



    @property
    def SandwichCore(self):
        return self._core

    @property
    def UpperFace(self):
        return self._upper_face

    @property
    def LowerFace(self):
        return self._lower_face

    # ------------------------------------------------------------------------------------------------------------------
