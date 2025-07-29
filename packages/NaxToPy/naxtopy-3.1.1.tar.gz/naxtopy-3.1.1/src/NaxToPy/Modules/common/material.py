"""Script for the definition of the class Material and its child classes."""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

from NaxToPy import N2PLog
from NaxToPy.Core.Classes.N2PMaterial import N2PMaterial
import numpy as np

class Plastic:
    """
    Base Class Plastic
    """
    __slots__ = (
        "_data_table_plastic",
        "_data_table_stress",
        "_data_table_strain",
        "_stress",
        "_strain"
    )

    def __init__(self):
        self._data_table_plastic: np.array = None
        self._data_table_stress: np.array = None
        self._data_table_strain: np.array = None

        self._stress: float = None
        self._strain: float = None

    # Getters ----------------------------------------------------------------------------------------------------------
    # Method to obatin the Table Data ----------------------------------------------------------------------------------
    @property
    def Data_table(self) -> np.array:
        """
        Returns the data table of the stress/strain curve
        """
        return self._data_table_plastic
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Stress which is going to be used to calculate -----------------------------------------------
    @property
    def Stress(self) -> float:
        """
        Returns the stress which is going to be used to calculate
        """
        return self._stress
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Strain which is going to be used to calculate -----------------------------------------------
    @property
    def Strain(self) -> float:
        """
        Returns the strain which is going to be used to calculate
        """
        return self._strain
    # ------------------------------------------------------------------------------------------------------------------

    # Setters ----------------------------------------------------------------------------------------------------------
    @Data_table.setter
    def Data_table(self, value:np.array) -> None:
        self._data_table_plastic = value
        self._data_table_stress = self._data_table_plastic[:,0]
        self._data_table_strain = self._data_table_plastic[:,1]
    # ------------------------------------------------------------------------------------------------------------------

    @Stress.setter
    def Stress(self, value:float) -> None:
        self._stress = value
        self._strain = self.interpolate()
    # ------------------------------------------------------------------------------------------------------------------

    @Strain.setter
    def Strain(self, value: float) -> None:
        self._strain = value
        self._stress = self.interpolate()
    # ------------------------------------------------------------------------------------------------------------------

    def interpolate(self):
        if self._data_table_stress is None or self._data_table_strain is None:
            pass
        
        if self._strain is not None and self._stress is None:
            interpolation_function = interp1d(self._data_table_strain, self._data_table_stress, kind='linear')
            return interpolation_function(self._strain)
        elif self._strain is None and self._stress is not None:
            interpolation_function = interp1d(self._data_table_stress,self._data_table_strain, kind='linear')
            return interpolation_function(self._stress)
        else:
            pass



class Allowables:
    """
    Base Class Allowables
    """
    __slots__ = (
        "_shear",
        "_ultimate_stress",
        "_ultimate_strain",
        "_fatigue_limit"
    )

    def __init__(self):
        self._shear: float = None
        self._ultimate_stress: float = None
        self._ultimate_strain: float = None
        self._fatigue_limit: float = None
    
    # Getters ----------------------------------------------------------------------------------------------------------
    # Method to obtain Allowable Shear ---------------------------------------------------------------------------------
    @property
    def Shear(self) -> float:
        """Returns the Allowable Shear"""
        return self._shear
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the ultime stress -------------------------------------------------------------------------------
    @property
    def Ultimate_Stress(self) -> float:
        """Returns the ultimate stress of the material"""
        return self._ultimate_stress
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the ultimate strain -----------------------------------------------------------------------------
    @property
    def Ultimate_Strain(self) -> float:
        """Returns the ultimae strain of the material"""
        return self._ultimate_strain
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Fatigue Limit -------------------------------------------------------------------------------
    @property
    def Fatigue_Limit(self) -> float:
        """Returns the fatigue limit of the material"""
        return self._fatigue_limit
    # ------------------------------------------------------------------------------------------------------------------


    # Setters ----------------------------------------------------------------------------------------------------------
    @Shear.setter
    def Shear(self, value: float) -> None:
        self._shear = value
    # ------------------------------------------------------------------------------------------------------------------
    @Ultimate_Stress.setter
    def Ultimate_Stress(self, value:float) -> None:
        self._ultimate_stress = value
    # ------------------------------------------------------------------------------------------------------------------

    @Ultimate_Strain.setter
    def Ultimate_Strain(self, value:float) -> None:
        self._ultimate_strain = value
    # ------------------------------------------------------------------------------------------------------------------
    @Fatigue_Limit.setter
    def Fatigue_Limit(self, value: float) -> None:
        self._fatigue_limit = value
    # ------------------------------------------------------------------------------------------------------------------



class AllowablesISO(Allowables):
    __slots__ = (
        '_ro_exponent',
        '_proof_stress',
        '_ultimate_stress',
        '_ultimate_strain',
        '_shared_yield_stress',
        '_shared_yield_shear',
        '_shared_yield_compression'
    )




    def __init__(self):
        super().__init__()
        self._ro_exponent: float = None
        self._proof_stress: float = None
        self._ultimate_stress: float = None
        self._ultimate_strain: float = None
        self._shared_yield_stress: float = None
        self._shared_yield_shear: float = None
        self._shared_yield_compression: float = None

    # Getters ----------------------------------------------------------------------------------------------------------
    # Method to obtain the Ramberg-Osgood exponent ---------------------------------------------------------------------
    @property
    def RO_exponent(self) -> float:
        """Returns the Ramberg-Osgood exponent"""
        return self._ro_exponent
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Proof Stress --------------------------------------------------------------------------------
    @property
    def Proof_Stress(self) -> float:
        """Returns the proof stress"""
        return self._proof_stress
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Yield Stress --------------------------------------------------------------------------------
    @property
    def Yield_stress(self) -> float:
        """Returns the Yield Stress"""
        return self._shared_yield_stress
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Yield shear -------------------------------------------------------------------------------------
    @property
    def Yield_shear(self) -> float:
        """Returns the Yield Shear"""
        return self._shared_yield_shear
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Yield Compression -------------------------------------------------------------------------------
    @property
    def Yield_compression(self) -> float:
        """Returns the Yield Compression"""
        return self._shared_yield_compression
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Allowable Stress ----------------------------------------------------------------------------
    @property
    def Ultimate_stress(self) -> float:
        """Returns the allowable stress. This is the ultimate stress with a safety factor"""
        return self._ultimate_stress
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Allowable Strain ----------------------------------------------------------------------------
    @property
    def Ultimate_strain(self) -> float:
        """Returns the Allowable Strain"""
        return self._ultimate_strain
    # ------------------------------------------------------------------------------------------------------------------


    # Setters ----------------------------------------------------------------------------------------------------------
    @RO_exponent.setter
    def RO_exponent(self, value: float) -> None:
        self._ro_exponent = value
    # ------------------------------------------------------------------------------------------------------------------

    @Proof_Stress.setter
    def Proof_Stress(self, value: float) -> None:
        self._proof_stress = value
    # ------------------------------------------------------------------------------------------------------------------

    @Yield_stress.setter
    def Yield_stress(self, value:float) -> None:
        self._shared_yield_stress = value
    # ------------------------------------------------------------------------------------------------------------------

    @Yield_shear.setter
    def Yield_shear(self, value:float) -> None:
        self._shared_yield_shear = value
    # ------------------------------------------------------------------------------------------------------------------

    @Yield_compression.setter
    def Yield_compression(self, value: float) -> None:
        self._shared_yield_compression = value
    # ------------------------------------------------------------------------------------------------------------------

    @Ultimate_stress.setter
    def Ultimate_stress(self, value: float) -> None:
        self._ultimate_stress = value
    # ------------------------------------------------------------------------------------------------------------------

    @Ultimate_strain.setter
    def Ultimate_strain(self, value: float) -> None:
        self._ultimate_strain = value
    # ------------------------------------------------------------------------------------------------------------------


class AllowablesORTO(Allowables):
    __slots__ = (
        '_ztensile',
        '_zcompressive',
        '_shearxz',
        '_shearyz',
        '_ilss',
        '_shared_xcompressive',
        '_shared_ycompressive',
        '_shared_xtensile',
        '_shared_ytensile',
        '_shared_shear'
    )


    def __init__(self):
        super().__init__()
        self._ztensile: float = None
        self._zcompressive: float = None
        self._shearxz: float = None
        self._shearyz: float = None
        self._ilss: float = None
        self._shared_xcompressive: float = None
        self._shared_ycompressive: float = None
        self._shared_xtensile: float = None
        self._shared_ytensile: float = None
        self._shared_shear: float = None
    # Getters ----------------------------------------------------------------------------------------------------------
    # Method to obtain Allowable Compression in X ----------------------------------------------------------------------
    @property
    def XCompressive(self) -> float:
        """Returns the Allowable Compression in X"""
        return self._shared_xcompressive
    # ------------------------------------------------------------------------------------------------------------------
    
    # Method to obtain Allowable Compression in Y ----------------------------------------------------------------------
    @property
    def YCompressive(self) -> float:
        """Returns the Allowable Compression in Y"""
        return self._shared_ycompressive
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Allowable Compression in Z ----------------------------------------------------------------------
    @property
    def ZCompressive(self) -> float:
        """Returns the Allowable Compression in Z"""
        return self._zcompressive
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Allowable Tension in X --------------------------------------------------------------------------
    @property
    def XTensile(self) -> float:
        """Returns the Allowable Tension in X"""
        return self._shared_xtensile
    # ------------------------------------------------------------------------------------------------------------------
    
    # Method to obtain Allowable Tension in Y --------------------------------------------------------------------------
    @property
    def YTensile(self) -> float:
        """Returns the Allowable Tension in Y"""
        return self._shared_ytensile
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Allowable Tension in Z --------------------------------------------------------------------------
    @property
    def ZTensile(self) -> float:
        """Returns the Allowable Tension in Z"""
        return self._ztensile
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Shear Allowable in the plane XY ---------------------------------------------------------------------------
    @property
    def Shear(self) -> float:
        """Returns the Shear in the plane XY"""
        return self._shared_shear
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Shear in the plane XZ ---------------------------------------------------------------------------
    @property
    def ShearXZ(self) -> float:
        """Returns the Shear in the plane XZ"""
        return self._shearxz
    # ------------------------------------------------------------------------------------------------------------------
    
    # Method to obtain Shear in the plane YZ ---------------------------------------------------------------------------
    @property
    def ShearYZ(self) -> float:
        """Returns the Shear in the plane YZ"""
        return self._shearyz
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain Shear in the plane YZ ---------------------------------------------------------------------------
    @property
    def ILSS(self) -> float:
        """Returns the ILLS (Interlaminar Shear Strength = f13)"""
        return self._ilss
    # ------------------------------------------------------------------------------------------------------------------    



    # Setters ----------------------------------------------------------------------------------------------------------
    @XCompressive.setter
    def XCompressive(self, value: float) -> None:
        self._shared_xcompressive = value
    # ------------------------------------------------------------------------------------------------------------------

    @YCompressive.setter
    def YCompressive(self, value: float) -> None:
        self._shared_ycompressive = value
    # ------------------------------------------------------------------------------------------------------------------

    @ZCompressive.setter
    def ZCompressive(self, value: float) -> None:
        self._zcompressive = value
    # ------------------------------------------------------------------------------------------------------------------

    @XTensile.setter
    def XTensile(self, value: float) -> None:
        self._shared_xtensile = value
    # ------------------------------------------------------------------------------------------------------------------

    @YTensile.setter
    def YTensile(self, value: float) -> None:
        self._shared_ytensile = value

    @Shear.setter
    def Shear(self, value: float) -> None:
        self._shared_shear = value
    # ------------------------------------------------------------------------------------------------------------------

    @ZTensile.setter
    def ZTensile(self, value: float) -> None:
        self._ztensile = value
    # ------------------------------------------------------------------------------------------------------------------

    @ShearXZ.setter
    def ShearXZ(self, value:float) -> None:
        self._shearxz = value
    # ------------------------------------------------------------------------------------------------------------------

    @ShearYZ.setter
    def ShearYZ(self, value:float) -> None:
        self._shearyz = value
    # ------------------------------------------------------------------------------------------------------------------

    @ILSS.setter
    def ILSS(self, value:float) -> None:
        self._ilss = value
    # ------------------------------------------------------------------------------------------------------------------    








class Material:
    """
    Base class Material.

    """
    __slots__ = ('_n2p_material', '_id', '_plastic')

    def __init__(self, n2p_material: N2PMaterial = None):
        """
        Dual constructor:
        - If a N2PMaterial is given, the reference is keeped.
        - User can modify an instance, except of the anisotropic case.

        """
        if isinstance(n2p_material,N2PMaterial):
            self._n2p_material = n2p_material
            self._id = n2p_material.ID
            self._plastic = None
        else:
            N2PLog.Error.E656()
    # Getters ----------------------------------------------------------------------------------------------------------
    # Method to obtain the plastic attributes of the material ----------------------------------------------------------
    @property
    def Plastic (self) -> Plastic:
        """Returns the plastic class asociated"""
        if self._plastic:
            return self._plastic
        else:
            N2PLog.Error.E657()
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the N2PMaterial ---------------------------------------------------------------------------------
    @property
    def N2PMaterial_original (self) -> N2PMaterial:
        """Returns the N2PMaterial"""
        return self._n2p_material
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the ID of the material -------------------------------------------------------------------------
    @property
    def ID(self) -> int:
        """Returns the ID of the material"""
        return self._id
    # ------------------------------------------------------------------------------------------------------------------
    

    # Setters ----------------------------------------------------------------------------------------------------------
    @Plastic.setter
    def Plastic(self, value) -> None:
        if isinstance(value,Plastic):
            self._plastic = value
        else:
            N2PLog.Error.E658()
    # ------------------------------------------------------------------------------------------------------------------
    @N2PMaterial_original.setter
    def N2PMaterial_original(self,value) -> None:
        if isinstance(value,N2PMaterial):
            self._n2p_material = value
        else:
            N2PLog.Error.E656()
    # ------------------------------------------------------------------------------------------------------------------



# Subclass for isotropic materials
class Isotropic(Material):
    """
    Class for isotropic materials.

    Attributes:
        _young -> Young's modulus of the material.
        _poisson -> Poisson's ratio of the material.
        _density -> Density of the material.
        _shear -> Shear modulus of the material.
        _texp -> Thermal expansion coefficient of the material.
        _tref -> Reference temperature of the material.
        _ge -> Structural damping coefficient of the material.


    """
    __slots__ = (
        '_n2p_material',
        '_id',
        '_young',
        '_poisson',
        '_density',
        '_shear',
        '_texp',
        '_tref',
        '_ge',
        '_allowableISO',
    )

    def __init__(self, n2p_material:N2PMaterial):
        """
        Dual construcotr
        - If a N2PMaterial is given, initialises from its attributes.
        - If not, allowable to introduce parameters directly.

        """
        super().__init__(n2p_material)

        if n2p_material:
            if isinstance(n2p_material,N2PMaterial):
                self._n2p_material = n2p_material
                if n2p_material.MatType == 'MAT1' or n2p_material.MatType == 'ISOTROPIC':
                    self._young = n2p_material.Young
                    self._poisson = n2p_material.Poisson
                    self._density = n2p_material.Density
                    self._shear = n2p_material.Shear
                    self._texp = n2p_material.TExp
                    self._tref = n2p_material.TRef
                    self._ge = n2p_material.GE
                    self._allowableISO = AllowablesISO()

                    self._allowableISO._shared_yield_stress = n2p_material.ST
                    self._allowableISO._shared_yield_shear = n2p_material.SS
                    self._allowableISO._shared_yield_compression = n2p_material.SC
                else:
                    N2PLog.Error.E650()
            else:
                N2PLog.Error.E656()


    # Getters ----------------------------------------------------------------------------------------------------------
    # Method to obtain the Yield Stress of the material ----------------------------------------------------------------
    @property
    def Yield_stress(self) -> float:
        """Returns the Yield Stress"""
        return AllowablesISO._shared_yield_stress
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Yield Shear of the material -----------------------------------------------------------------
    @property
    def Yield_shear(self) -> float:
        """Returns the Yield Shear"""
        return AllowablesISO._shared_yield_shear
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the Yield Compression of the material -----------------------------------------------------------
    @property
    def Yield_compression(self) -> float:
        """Returns the Yield Compression"""
        return AllowablesISO._shared_yield_compression
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the allowables of the material ------------------------------------------------------------------
    @property
    def Allowables (self) -> AllowablesISO:
        """Returns the Allowables of the material"""
        if self._allowableISO:
            return self._allowableISO
        else:
            N2PLog.Error.E659()
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the elastic's modulus of the material -----------------------------------------------------------
    @property
    def Young(self) -> float:
        """Returns the Young's modulus of the material."""
        return self._young
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the poisson's ratio of the material -------------------------------------------------------------
    @property
    def Poisson(self) -> float:
        """Returns the Poisson's ratio of the material."""
        return self._poisson
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the density of the material ---------------------------------------------------------------------
    @property
    def Density(self) -> float:
        """Returns the Density of the material."""
        return self._density
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the shear's modulus of the material -------------------------------------------------------------
    @property
    def Shear(self) -> float:
        """Returns the Shear modulus of the material."""
        return self._shear
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the thermal expansion coefficient of the material -----------------------------------------------
    @property
    def TExp(self) -> float:
        """Returns the thermal expansion coefficient of the material."""
        return self._texp
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the reference temperature of the material -------------------------------------------------------
    @property
    def TRef(self) -> float:
        """Returns the reference temperature of the material."""
        return self._texp
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the structural damping coefficient of the material ----------------------------------------------
    @property
    def GE(self) -> float:
        """Returns the structural damping coefficient of the material."""
        return self._ge
    # ------------------------------------------------------------------------------------------------------------------



    # Setters ----------------------------------------------------------------------------------------------------------
    @Yield_stress.setter
    def Yield_stress(self, value: float) -> None:
        AllowablesISO._shared_yield_stress = value
    # ------------------------------------------------------------------------------------------------------------------

    @Yield_shear.setter
    def Yield_shear(self, value: float) -> None:
        AllowablesISO._shared_yield_shear = value
    # ------------------------------------------------------------------------------------------------------------------

    @Yield_compression.setter
    def Yield_compression(self, value:float) -> None:
        AllowablesISO._shared_yield_compression = value
    # ------------------------------------------------------------------------------------------------------------------

    @Young.setter
    def Young(self, value: float) -> None:
        self._young = value
    # ------------------------------------------------------------------------------------------------------------------

    @Poisson.setter
    def Poisson(self, value: float) -> None:
        self._poisson = value
    # ------------------------------------------------------------------------------------------------------------------

    @Density.setter
    def Density(self, value: float) -> None:
        self._density = value
    # ------------------------------------------------------------------------------------------------------------------

    @Shear.setter
    def Density(self, value: float) -> None:
        self._shear = value
    # ------------------------------------------------------------------------------------------------------------------

    @TExp.setter
    def TExp(self, value: float) -> None:
        self._texp = value
    # ------------------------------------------------------------------------------------------------------------------

    @TRef.setter
    def TRef(self, value: float) -> None:
        self._tref = value
    # ------------------------------------------------------------------------------------------------------------------

    @GE.setter
    def GE(self, value: float) -> None:
        self._ge = value
    # ------------------------------------------------------------------------------------------------------------------

    @Allowables.setter
    def Allowables(self, value) -> None:
        if isinstance(value,AllowablesISO):
            self._allowableISO = value
        else:
            N2PLog.Error.E670()

    def __repr__(self):
        return (f"Isotropic({self.ID},'0')")
    # ------------------------------------------------------------------------------------------------------------------








class Orthotropic(Material):
    """
    Class for Orthotropic materials.

    Attributes:
        _youngx -> Young's modulus in X direction of the material.
        _youngy -> Young's modulus in Y direction of the material.
        _poissonxy -> Poisson's ratio of the material.
        _shearxy -> Shear modulus in XY plane of the material.
        _shearxz -> Shear modulus in XZ plane of the material.
        _shearyz -> Shear modulus in YZ plane of the material.
        _density -> Density of the material.
        _texpx -> Thermal expansion coefficient in X direction of the material.
        _texpy -> Thermal expansion coefficient in Y direction of the material.
        _tref -> Reference temperature of the material.
        _ge -> Structural damping coefficient of the material.

    """
    __slots__ = (
        '_n2p_material',
        '_youngx',
        '_youngy',
        '_youngz',
        '_poissonxy',
        '_poissonxz',
        '_poissonyz',
        '_shearxy',
        '_shearxz',
        '_shearyz',
        '_density',
        '_texpx',
        '_texpy',
        '_tref',
        '_ge',
        '_allowableORTO',
        '_mu21',
        '_mu2',
        '_b21',
        '_b2',
    )


    def __init__(self, n2p_material: N2PMaterial):

        super().__init__(n2p_material)

        if n2p_material:
            if isinstance(n2p_material,N2PMaterial):
                self._n2p_material = n2p_material
                # Si es un MAT8 de NASTRAN entra en el if
                if n2p_material.MatType in ['MAT8','ORTHOTROPIC','LAMINA']:
                    self._youngx = n2p_material.YoungX
                    self._youngy = n2p_material.YoungY
                    self._poissonxy = n2p_material.PoissonXY
                    self._shearxy = n2p_material.ShearXY
                    self._shearxz = n2p_material.ShearXZ
                    self._shearyz = n2p_material.ShearYZ
                    self._density = n2p_material.Density
                    self._texpx = n2p_material.TExpX
                    self._texpy = n2p_material.TExpY
                    self._tref = n2p_material.TRef
                    self._ge = n2p_material.GE
                    self._youngz = None
                    self._poissonyz = None
                    self._poissonxz = None
                    self._mu21 = None
                    self._mu2 = None
                    self._b21 = None
                    self._b2 = None
                    self._allowableORTO = AllowablesORTO()
                    self._allowableORTO._shared_xcompressive = n2p_material.Xc
                    self._allowableORTO._shared_ycompressive = n2p_material.Yc
                    self._allowableORTO._shared_xtensile = n2p_material.Xt
                    self._allowableORTO._shared_ytensile = n2p_material.Yt
                    self._allowableORTO._shared_shear = n2p_material.SC

                # En Abaqus, los materiales ortotropicos pueden estar definidos mediante ENGINEERING_CONSTANTS, LAMINA
                # o ORTHOTROPIC
                elif n2p_material.MatType == 'UNDEF':
                    if n2p_material.QualitiesDict['Elastic type'] == 'ENGINEERING_CONSTANTS':
                        self._youngx = n2p_material.QualitiesDict['E1']
                        self._youngy = n2p_material.QualitiesDict['E2']
                        self._youngz = n2p_material.QualitiesDict['E3']
                        self._poissonxy = n2p_material.QualitiesDict['v12']
                        self._poissonxz = n2p_material.QualitiesDict['v13']
                        self._poissonyz = n2p_material.QualitiesDict['v23']
                        self._shearxy = n2p_material.QualitiesDict['G12']
                        self._shearxz = n2p_material.QualitiesDict['G13']
                        self._shearyz = n2p_material.QualitiesDict['G23']
                        self._tref = n2p_material.QualitiesDict['Temperature']

                else:
                    N2PLog.Error.E651()
            else:
                N2PLog.Error.E656()

    # Getters ----------------------------------------------------------------------------------------------------------
    # Method to obtain the allowables of the material ------------------------------------------------------------------
    @property
    def Allowables (self) -> AllowablesORTO:
        """Returns the Allowables of the material"""
        if self._allowableORTO:
            return self._allowableORTO
        else:
            N2PLog.Error.E659()
    # ------------------------------------------------------------------------------------------------------------------
    # Method to obtain the elastic's modulus in X of the material ------------------------------------------------------
    @property
    def YoungX(self) -> float:
        """Returns the elastic modulus in X material coordinate direction, also fiber direction."""
        return self._youngx
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the elastic's modulus in Y of the material ------------------------------------------------------
    @property
    def YoungY(self) -> float:
        """Returns the elastic modulus in Y material coordinate direction."""
        return self._youngy
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the elastic's modulus in Z of the material ------------------------------------------------------
    @property
    def YoungZ(self) -> float:
        """Returns the elastic modulus in Z material coordinate direction."""
        return self._youngz
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the shear's modulus in plane XY of the material -------------------------------------------------
    @property
    def ShearXY(self) -> float:
        """In-plane shear modulus of the material."""
        return self._shearxy
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the shear's modulus in plane XZ of the material -------------------------------------------------
    @property
    def ShearXZ(self) -> float:
        """Tranverse shear modulus of the material in plane XZ"""
        return self._shearxz
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the shear's modulus in plane YZ of the material -------------------------------------------------
    @property
    def ShearYZ(self) -> float:
        """Tranverse shear modulus of the material in plane YZ"""
        return self._shearyz
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the poisson's ratio of the material -------------------------------------------------------------
    @property
    def PoissonXY(self) -> float:
        """Poisson's ratio of the material in plane XY"""
        return self._poissonxy

    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the poisson's ratio of the material -------------------------------------------------------------
    @property
    def PoissonXZ(self) -> float:
        """Poisson's ratio of the material in plane XZ"""
        return self._poissonxz

    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the poisson's ratio of the material -------------------------------------------------------------
    @property
    def PoissonYZ(self) -> float:
        """Poisson's ratio of the material in plane YZ"""
        return self._poissonyz

    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the density of the material ---------------------------------------------------------------------
    @property
    def Density(self) -> float:
        """Returns the density of the material."""
        return self._density

    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the thermal expansion coefficient in X of the material ------------------------------------------
    @property
    def TExpX(self) -> float:
        """Thermal expansion coefficient in X direction of the material (fiber direction)"""
        return self._texpx
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the thermal expansion coefficient in X of the material ------------------------------------------
    @property
    def TExpY(self) -> float:
        """Thermal expansion coefficient in Y direction of the material"""
        return self._texpy
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the reference temperature of the material -------------------------------------------------------
    @property
    def TRef(self) -> float:
        """Returns the reference temperature of the material."""
        return self._tref
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the structural damping coefficient of the material ----------------------------------------------
    @property
    def GE(self) -> float:
        """Returns the structural damping coefficient of the material."""
        return self._ge
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the inter fiber friction property in transverse-longitudinal direction (fiber-wise) -----------------------------------------------------
    @property
    def mu21(self) -> float:
        """ Returns inter fiber friction property in transverse-longitudinal direction. """
        return self._mu21
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the inter fiber friction property in transverse direction (fiber-wise) -----------------------------------------------------
    @property
    def mu2(self) -> float:
        """ Returns inter fiber friction property in transverse direction.
        """
        return self._mu2
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the inter fiber friction coefficient in transverse-longitudinal direction (fiber-wise) -----------------------------------------------------
    @property
    def b21(self) -> float:
        """ Returns inter fiber friction coefficient in transverse-longitudinal direction.
        """
        self._b21 = self.mu21
        return self._b21    
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the inter fiber friction coefficient in transverse direction (fiber-wise) -----------------------------------------------------
    @property
    def b2(self) -> float:
        """ Returns inter fiber friction coefficient in transverse-longitudinal direction.
        """
        self._b2 = 1/(1-self.mu2)
        return self._b2
    

    # Setters ----------------------------------------------------------------------------------------------------------
    @YoungX.setter
    def YoungX(self, value: float) -> None:
        self._youngx = value
    # ------------------------------------------------------------------------------------------------------------------

    @YoungY.setter
    def YoungY(self, value: float) -> None:
        self._youngy = value
    # ------------------------------------------------------------------------------------------------------------------

    @YoungZ.setter
    def YoungZ(self, value: float) -> None:
        self._youngz = value
    # ------------------------------------------------------------------------------------------------------------------

    @ShearXY.setter
    def ShearXY(self, value: float) -> None:
        self._shearxy = value
    # ------------------------------------------------------------------------------------------------------------------

    @ShearXZ.setter
    def ShearXZ(self, value: float) -> None:
        self._shearxz = value
    # ------------------------------------------------------------------------------------------------------------------

    @ShearYZ.setter
    def ShearYZ(self, value: float) -> None:
        self._shearyz = value
    # ------------------------------------------------------------------------------------------------------------------

    @PoissonXY.setter
    def PoissonXY(self, value: float) -> None:
        self._poissonxy = value
    # ------------------------------------------------------------------------------------------------------------------

    @PoissonXZ.setter
    def PoissonXZ(self, value: float) -> None:
        self._poissonxz = value
    # ------------------------------------------------------------------------------------------------------------------

    @PoissonYZ.setter
    def PoissonYZ(self, value: float) -> None:
        self._poissonyz = value
    # ------------------------------------------------------------------------------------------------------------------

    @Density.setter
    def Density(self, value: float) -> None:
        self._density = value
    # ------------------------------------------------------------------------------------------------------------------

    @TExpX.setter
    def TExpX(self, value: float) -> None:
        self._texpx = value
    # ------------------------------------------------------------------------------------------------------------------

    @TExpY.setter
    def TExpY(self, value: float) -> None:
        self._texpy = value
    # ------------------------------------------------------------------------------------------------------------------

    @TRef.setter
    def TRef(self, value: float) -> None:
        self._tref = value
    # ------------------------------------------------------------------------------------------------------------------

    @GE.setter
    def GE(self, value: float) -> None:
        self._ge = value
    # ------------------------------------------------------------------------------------------------------------------

    @Allowables.setter
    def Allowables(self, value) -> None:
        if isinstance(value,AllowablesORTO):
            self._allowableORTO = value
        else:
            N2PLog.Error.E671()

    def __repr__(self):
        return (f"Orthotropic({self.ID},'0')")
    # ------------------------------------------------------------------------------------------------------------------

    @mu21.setter
    def mu21(self, value) -> None:
        self._mu21 = value
    # ------------------------------------------------------------------------------------------------------------------

    @mu2.setter
    def mu2(self, value) -> None:
        self._mu2 = value









# class Anisotropic(Material):
#     """
#     Class for Anisotropic materials. Actually is impossible to construct a Anisotropic material froma a N2PMaterial.

#     Attributes:
#         _g11 -> Component 11 of the material property matrix.
#         _g12 -> Component 12 of the material property matrix.
#         _g13 -> Component 13 of the material property matrix.
#         _g22 -> Component 22 of the material property matrix.
#         _g23 -> Component 23 of the material property matrix.
#         _g33 -> Component 33 of the material property matrix.
#         _density -> Density of the material.
#         _texpx -> Thermal expansion coefficient in X direction of the material.
#         _texpy -> Thermal expansion coefficient in Y direction of the material.
#         _texpz -> Thermal expansion coefficient in Z direction of the material.
#         _tref -> Reference temperature of the material.
#         _ge -> Structural damping coefficient of the material.
#         _mcsid -> Material coordinate system identification number.
#         _ge11 -> Component 11 of the material structural damping matrix.
#         _ge12 -> Component 12 of the material structural damping matrix.
#         _ge13 -> Component 13 of the material structural damping matrix.
#         _ge22 -> Component 22 of the material structural damping matrix.
#         _ge23 -> Component 23 of the material structural damping matrix.
#         _ge33 -> Component 33 of the material structural damping matrix.

#     """
#     def __init__(self, n2p_material: N2PMaterial, G11: float = None, G12: float = None, G13: float = None,
#                 G22: float = None, G23: float = None, G33: float = None, Density: float = None, TExpX: float = None,
#                 TExpY: float = None, TExpZ: float = None, TRef: float = None, GE: float = None, MCSID: float = None,
#                 GE11: float = None, GE12: float = None, GE13: float = None, GE22: float = None, GE23: float = None,
#                 GE33: float = None):

#         super().__init__(n2p_material)

#         self._g11 = G11
#         self._g12 = G12
#         self._g13 = G13
#         self._g22 = G22
#         self._g23 = G23
#         self._g33 = G33
#         self._density = Density
#         self._texpx = TExpX
#         self._texpy = TExpY
#         self._texpz = TExpZ
#         self._tref = TRef
#         self._ge = GE
#         self._mcsid = MCSID
#         self._ge11 = GE11
#         self._ge12 = GE12
#         self._ge13 = GE13
#         self._ge22 = GE22
#         self._ge23 = GE23
#         self._ge33 = GE33

#     # Getters ----------------------------------------------------------------------------------------------------------
#     # Method to obtain the component 11 of property matrix -------------------------------------------------------------
#     @property
#     def G11(self) -> float:
#         """Returns the element 11 of the property matrix"""
#         return self._g11
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the component 12 of property matrix -------------------------------------------------------------
#     @property
#     def G12(self) -> float:
#         """Returns the element 12 of the property matrix"""
#         return self._g12
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the component 13 of property matrix -------------------------------------------------------------
#     @property
#     def G13(self) -> float:
#         """Returns the element 13 of the property matrix"""
#         return self._g13
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the component 22 of property matrix -------------------------------------------------------------
#     @property
#     def G22(self) -> float:
#         """Returns the element 22 of the property matrix"""
#         return self._g22
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the component 23 of property matrix -------------------------------------------------------------
#     @property
#     def G23(self) -> float:
#         """Returns the element 23 of the property matrix"""
#         return self._g23
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the component 33 of property matrix -------------------------------------------------------------
#     @property
#     def G33(self) -> float:
#         """Returns the element 33 of the property matrix"""
#         return self._g33
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the density of the material ---------------------------------------------------------------------
#     @property
#     def Density(self) -> float:
#         """Returns the density of the material"""
#         return self._density
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the thermal expansion coefficient in X ----------------------------------------------------------
#     @property
#     def TExpX(self) -> float:
#         """Returns the thermal expansion coefficient in X"""
#         return self._texpx
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the thermal expansion coefficient in Y ----------------------------------------------------------
#     @property
#     def TExpY(self) -> float:
#         """Returns the thermal expansion coefficient in Y"""
#         return self._texpy
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the thermal expansion coefficient in Z ----------------------------------------------------------
#     @property
#     def TExpZ(self) -> float:
#         """Returns the thermal expansion coefficient in Z"""
#         return self._texpz
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the reference temperature -----------------------------------------------------------------------
#     @property
#     def TRef(self) -> float:
#         """Returns the reference temperature"""
#         return self._tref
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the structural element damping coefficient ------------------------------------------------------
#     @property
#     def GE(self) -> float:
#         """Returns the structural element damping coefficient"""
#         return self._ge
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the material coordinate system identification number --------------------------------------------
#     @property
#     def MCSID(self) -> float:
#         """Returns the coordinate system identification number"""
#         return self._mcsid
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the component 11 of structural damping matrix ---------------------------------------------------
#     @property
#     def GE11(self) -> float:
#         """Returns the element 11 of the structural damping matrix"""
#         return self._ge11
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the component 12 of structural damping matrix ---------------------------------------------------
#     @property
#     def GE12(self) -> float:
#         """Returns the element 12 of the structural damping matrix"""
#         return self._ge12
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the component 13 of structural damping matrix ---------------------------------------------------
#     @property
#     def GE13(self) -> float:
#         """Returns the element 13 of the structural damping matrix"""
#         return self._ge13
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the component 22 of structural damping matrix ---------------------------------------------------
#     @property
#     def GE22(self) -> float:
#         """Returns the element 22 of the structural damping matrix"""
#         return self._ge22
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the component 23 of structural damping matrix ---------------------------------------------------
#     @property
#     def GE23(self) -> float:
#         """Returns the element 23 of the structural damping matrix"""
#         return self._ge23
#     # ------------------------------------------------------------------------------------------------------------------

#     # Method to obtain the component 33 of structural damping matrix ---------------------------------------------------
#     @property
#     def GE33(self) -> float:
#         """Returns the element 33 of the structural damping matrix"""
#         return self._ge33
#     # ------------------------------------------------------------------------------------------------------------------


#     # Setters ----------------------------------------------------------------------------------------------------------
#     @G11.setter
#     def G11(self, value: float) -> None:
#         self._g11 = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @G12.setter
#     def G12(self, value: float) -> None:
#         self._g12 = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @G13.setter
#     def G13(self, value: float) -> None:
#         self._g13 = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @G22.setter
#     def G22(self, value: float) -> None:
#         self._g22 = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @G23.setter
#     def G23(self, value: float) -> None:
#         self._g23 = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @G33.setter
#     def G33(self, value: float) -> None:
#         self._g33 = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @Density.setter
#     def Density(self, value: float) -> None:
#         self._density = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @TExpX.setter
#     def TExpX(self, value: float) -> None:
#         self._texpx = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @TExpY.setter
#     def TExpY(self, value: float) -> None:
#         self._texpy = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @TExpZ.setter
#     def TExpZ(self, value: float) -> None:
#         self._texpz = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @TRef.setter
#     def TRef(self, value: float) -> None:
#         self._tref = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @GE.setter
#     def GE(self, value: float) -> None:
#         self._ge = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @MCSID.setter
#     def MCSID(self, value: float) -> None:
#         self._mcsid = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @GE11.setter
#     def GE11(self, value: float) -> None:
#         self._ge11 = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @GE12.setter
#     def GE12(self, value: float) -> None:
#         self._ge12 = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @GE13.setter
#     def GE13(self, value: float) -> None:
#         self._ge13 = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @GE22.setter
#     def GE22(self, value: float) -> None:
#         self._ge22 = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @GE23.setter
#     def GE23(self, value: float) -> None:
#         self._ge23 = value
#     # ------------------------------------------------------------------------------------------------------------------

#     @GE33.setter
#     def GE33(self, value: float) -> None:
#         self._ge33 = value
#     # ------------------------------------------------------------------------------------------------------------------
