"""Script for the definition of the class N2PSandwich."""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info.

import numpy as np
from NaxToPy.Core.N2PModelContent import N2PElement, N2PLoadCase
from NaxToPy.Core.N2PModelContent import N2PModelContent, N2PLog
from NaxToPy.Modules.common.hdf5 import HDF5_NaxTo
from NaxToPy.Modules.common.material import Orthotropic, Isotropic
from NaxToPy.Modules.common.property import IsotropicShell, Sandwich, CompositeShell
from NaxToPy.Modules.common.model_processor import elem_to_material, get_sandwich_properties
from NaxToPy.Modules.handbooks.nasa.wrinkling_nasa import wrinkling_nasa_1, wrinkling_nasa_2, wrinkling_nasa_composite
from NaxToPy.Modules.handbooks.hypersizer.wrinkling_hypersizer import wrinkling_hypersizer_isotropic, wrinkling_hypersizer_composite, wrinkling_hypersizer_honeycomb, wrinkling_hypersizer_composite_biaxial, wrinkling_hypersizer_composite_shear, wrinkling_hypersizer_composite_combined
from NaxToPy.Modules.handbooks.hypersizer.dimpling_hypersizer import dimpling_hypersizer_compression, dimpling_hypersizer_biaxial, dimpling_hypersizer_shear, dimpling_hypersizer_combined
from NaxToPy.Modules.handbooks.hypersizer.crimping_hypersizer import crimping_hypersizer_compression, crimping_hypersizer_shear, crimping_hypersizer_combined
from NaxToPy.Modules.handbooks.hsb.wrinkling_hsb import antysymmetric_hsb_wrinkling,symmetric_hsb_wrinkling
from NaxToPy.Modules.handbooks.cmh.wrinkling_cmh import wriknling_cmh_honeycomb_thick,wrinkling_cmh_honeycomb_thin, wrinkling_cmh_honeycomb_biaxial_thick, wrinkling_cmh_honeycomb_biaxial_thin
from NaxToPy.Modules.handbooks.airbus.wrinkling_airbus import wrinkling_airbus_compression_thick, wrinkling_airbus_compression_thin, wrinkling_airbus_shear, wrinkling_airbus_biaxial, wrinkling_airbus_combined
from NaxToPy.Modules.handbooks.airbus.core_shear_crimping_airbus import core_shear_crimping_airbus
from NaxToPy.Modules.handbooks.airbus.dimpling_airbus import dimpling_airbus_compression, dimpling_airbus_biaxial, dimpling_airbus_shear, dimpling_airbus_combined
from NaxToPy.Modules.handbooks.cmh.dimpling_cmh import dimpling_cmh_compression, dimpling_cmh_biaxial, dimpling_cmh_shear, dimpling_cmh_combined
from NaxToPy.Modules.handbooks.cmh.core_shear_crimping_cmh import core_shear_crimping_cmh
from NaxToPy.Modules.common.data_input_hdf5 import DataEntry

RESULT_NAME = {"Nastran": "FORCES",
               "InputFileNastran": "FORCES",
               "Abaqus": "S"}

RESULT_NAME_DISP = {"Nastran": "DISPLACEMENTS",
               "InputFileNastran": "DISPLACEMENTS",
               "Abaqus": "U"}

COMPONENT_NAME = {"Nastran": ["FX","FY","FXY","MX","MY","MXY","QX","QY"],
                  "InputFileNastran": ["FX","FY","FXY","MX","MY","MXY","QX","QY"],
                  "Abaqus": ["S1","S2","S3"]}

COMPONENT_NAME_DISP = {"Nastran": ["X","Y","Z","MAGNITUDE_D"],
                        "InputFileNastran": ["X","Y","Z","MAGNITUDE_D"],
                        "Abaqus": ["U1","U2","U3","UR"]}


def _compute_geometry(sandwich_element):
    t_sup = sandwich_element.UpperFace.Thickness
    t_inf = sandwich_element.LowerFace.Thickness
    t_core = sandwich_element.SandwichCore.Thickness
    thickness = t_sup + t_core + t_inf

    z_sup = t_sup / 2 + t_core / 2      # Mid line of the upper face
    z_inf = -t_core / 2 - t_inf / 2     # Mid line of the lower face
    I = (1 / 12) * ((t_inf ** 3) + (t_sup ** 3)) + ((t_inf * (z_inf ** 2)) + (t_sup * (z_sup ** 2))) / thickness
    return t_sup, t_inf, t_core, thickness, z_sup, z_inf, I

def _compute_loads(thickness,t_core,z_sup,z_inf,I,N_x,N_y,N_xy,M_x,M_y,M_xy):

    sigma_x_up = N_x / thickness + M_x*z_sup/I
    sigma_x_down = N_x / thickness + M_x*z_inf/I
    sigma_y_up = N_y / thickness + M_y*z_sup/I
    sigma_y_down = N_y / thickness + M_y*z_inf/I
    tau_xy = N_xy / t_core

    return sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy

def _classify_stress_state(sigma_x, sigma_y, tau_xy):
    """
    Function that classifies the stress state of a material based on normal and shear stresses.

    Input:
    - sigma_x (float): Normal stress in the x-direction.
    - sigma_y (float): Normal stress in the y-direction.
    - tau_xy (float): Shear stress in the xy-plane.

    Output:
    - load_state (str): A string describing the stress state, which can be:
        - "CompressionX": Predominantly compressive stress in the x-direction.
        - "CompressionY": Predominantly compressive stress in the y-direction.
        - "TensionX": Predominantly tensile stress in the x-direction.
        - "TensionY": Predominantly tensile stress in the y-direction.
        - "BiaxialCompression": Significant compressive stresses in both x and y directions.
        - "BiaxialTension": Significant tensile stresses in both x and y directions.
        - "PureShear": Shear stress dominates over normal stresses.
        - "Combined": A mixed or complex stress state that does not fit into the other categories.

    The classification is based on a magnitude comparison where one component is considered
    "dominant" if it is at least 100 times larger than the others.
    """

    # Take absolute values to compare variables
    abs_sigma_x = abs(sigma_x)
    abs_sigma_y = abs(sigma_y)
    abs_tau_xy = abs(tau_xy)

    # A load is considered as 'dominant' if it is 100 times greater than other
    if sigma_x < 0 and abs_sigma_x >= 100 * max(abs_sigma_y, abs_tau_xy):
        load_state = "CompressionX"
    elif sigma_y < 0 and abs_sigma_y >= 100 * max(abs_sigma_x, abs_tau_xy):
        load_state = "CompressionY"
    elif tau_xy != 0 and abs_tau_xy >= 100 * max(abs_sigma_x, abs_sigma_y):
        load_state = "PureShear"
    elif sigma_x > 0 and abs_sigma_x >= 100 * max(abs_sigma_y, abs_tau_xy):
        load_state = "TensionX"
    elif sigma_y > 0 and abs_sigma_y >= 100 * max(abs_sigma_x, abs_tau_xy):
        load_state = "TensionY"
    elif sigma_x < 0 and sigma_y < 0 and (abs_sigma_x >= 0.01 * abs_sigma_y and abs_sigma_x <= 100 * abs_sigma_y) and abs_sigma_x >= 100 * abs_tau_xy:
        load_state = "BiaxialCompression"
    elif sigma_x > 0 and sigma_y > 0 and (abs_sigma_x >= 0.01 * abs_sigma_y and abs_sigma_x <= 100 * abs_sigma_y) and abs_sigma_x >= 100 * abs_tau_xy:
        load_state = "BiaxialTension"
    else:
        load_state = "Combined"

    return load_state
def _compute_material_properties(sandwich_element: Sandwich):
    # Retrieve faces properties
    if type(sandwich_element.UpperFace) == IsotropicShell:
        Efx_up = sandwich_element.UpperFace.Young
        Efy_up = Efx_up
        nu_xy_up = sandwich_element.UpperFace.Poisson
        nu_yx_up = nu_xy_up
    else: # upper face is CompositeShell
        Efx_up, Efy_up, _, _ = sandwich_element.UpperFace.EqBenProps()
        _, _, nu_xy_up, _ = sandwich_element.UpperFace.EqMemProps()
        nu_yx_up = nu_xy_up * Efy_up / Efx_up

    if type(sandwich_element.LowerFace) == IsotropicShell:
        Efx_down = sandwich_element.LowerFace.Young
        Efy_down = Efx_down
        nu_xy_down = sandwich_element.LowerFace.Poisson
        nu_yx_down = nu_xy_down
    else: # lower face is CompositeShell
        Efx_down, Efy_down, _, _ = sandwich_element.LowerFace.EqBenProps()
        _, _, nu_xy_down, _ = sandwich_element.LowerFace.EqMemProps()
        nu_yx_down = nu_xy_down * Efy_down / Efx_down



    if type(sandwich_element.SandwichCore.Material) == Isotropic:
        Ec = sandwich_element.SandwichCore.Material.Young
        Gxz = sandwich_element.SandwichCore.Material.Shear
        Gyz = sandwich_element.SandwichCore.Material.Shear
    else: # SandwichCore.Material is Orthotropic
        # Retrieve core properties
        Ec = sandwich_element.SandwichCore.Material.YoungZ
        if Ec is None:
            msg = N2PLog.Critical.C950()
            raise Exception(msg)
        Gxz = sandwich_element.SandwichCore.Material.ShearXZ
        Gyz = sandwich_element.SandwichCore.Material.ShearYZ

    return Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz

class N2PSandwichFailure:
    """ Class to calculate sandwich structures failure modes
        Examples:
        >>> sandwich = N2PSandwichFailure()
        >>> sandwich.Model = model
        >>> sandwich.FailureMode = 'Wrinkling'
        >>> sandwich.FailureTheory = 'HyperSizer'
        >>> sandwich.LoadCases = n2ploadcases
        >>> sandwich.ElementList = n2pelems
        >>> sandwich.CoreType = 'Honeycomb'
        >>> sandwich.Parameters['K1'] = 0.8
        >>> sandwich.HDF5.FilePath = r"file output"
        >>> sandwich.calculate()
    """



    __slots__ = ('__RF','__cell_size','__core_type','__element_list','__failure_mode','__failure_theory','__hdf5',
                 '__load_cases','__materials','__model','__parameters','__sandwich_dict','__data_components',
                 '__warning_uniaxial','__warning_tension','__laminate_criteria','__ramp_radius','__bag_angle','__allowable_displacement')
    def __init__(self):

        # Initialize the class with the different attributes
        # Mandatory attributes -----------------------------------------------------------------------------------------
        self.__model: N2PModelContent = None
        self.__element_list: list[N2PElement] = None
        self.__load_cases: list[N2PLoadCase] = None
        self.__failure_mode: str = None
        self.__failure_theory: str = None
        self.__core_type: str = 'Honeycomb'
        self.__cell_size: str = None
        self.__parameters: dict = {'K1': None, 'K2': None, 'K3': None, 'C1': None, 'C2': None, 'C3':None, 'C4': None}
        self.__laminate_criteria: str = None
        self.__ramp_radius: float = None
        self.__bag_angle: float = None
        self.__allowable_displacement: float = None

        self.__RF = None
        self.__materials: dict[tuple[int, str], Orthotropic] = None

        # Initialize the HDF5
        self.__hdf5 = HDF5_NaxTo()

        # Initialize warning flags
        self.__warning_uniaxial = False # Warning raised when the load is not a uniaxial compression
        self.__warning_tension = False # Warning raised when a load in tension is given for a compression criteria (RF= 999999)

    # region Getters

    @property
    def Materials(self) -> dict[tuple[int, str], Orthotropic]:
        """
        Returns the dictionary with all the materials in the elements selected
        """
        return self.__materials

    @property
    def Model(self) -> N2PModelContent:
        """
        Property that returns the N2PModelContent object
        """
        return self.__model

    @property
    def ElementList(self) -> list[N2PElement]:
        """
        Property that returns the list of N2PElement
        """
        return self.__element_list

    @property
    def LoadCases(self) -> list[N2PLoadCase]:
        """
        Property that returns the list of N2PLoadCase
        """
        return self.__load_cases

    @property
    def FailureMode(self) -> str:
        """
        Property that returns the failure mode
        """
        return self.__failure_mode

    @property
    def FailureTheory(self) -> str:
        """
        Property that returns the failure theory
        """
        return self.__failure_theory

    @property
    def CoreType(self) -> str:
        """
        Property that returns the type of core
        """
        return self.__core_type
    @property
    def CellSize(self) -> float:
        """
        Property that returns the cell size
        """
        return self.__cell_size

    @property
    def RampRadius(self) -> float:
        """
        Property that returns the ramp radius
        """
        return self.__ramp_radius

    @property
    def BagAngle(self) -> float:
        """
        Property that returns the local angle between bag side and tool side (in degrees)
        """
        return self.__bag_angle

    @property
    def SandwichDict(self) -> dict:
        """
        Property that returns the dict mapping each element with its corresponding Sandwich class
        """
        return self.__sandwich_dict

    @property
    def HDF5(self) -> HDF5_NaxTo:
        """
        Property which returns the HDF5 attribute which contains all the necessary info to create it
        """
        return self.__hdf5

    @property
    def Parameters(self) -> float:
        """
        Property that returns parameters for each failure mode
        """

        return self.__parameters

    @property
    def LaminateCriteria(self) -> float:
        """
        Property that returns failure criteria for laminate
        """
        return self.__laminate_criteria

    @property
    def AllowableDisplacement(self) -> float:
        """
        Property that returns allowable displacement
        """
        return self.__allowable_displacement

    # endregion

    #region Setters

    @Materials.setter
    def Materials(self, value: list) -> None:
        self.__materials = value

    @Model.setter
    def Model(self, model:N2PModelContent) -> None:
        if isinstance(model,N2PModelContent):
            self.__model = model
        else:
            msg = N2PLog.Critical.C800()
            raise Exception(msg)

    @ElementList.setter
    def ElementList(self, element_list: list[N2PElement]) -> None:
        if all(isinstance(element, N2PElement) for element in element_list):
            self.__element_list = element_list
            _,_,self.__materials, _ = elem_to_material(self.__model, self.__element_list)

        else:
            msg = N2PLog.Critical.C801()
            raise Exception(msg)

    @LoadCases.setter
    def LoadCases(self, load_cases: list[N2PLoadCase]) -> None:
        if isinstance(load_cases, list):
            for lc in load_cases:
                if isinstance(lc,N2PLoadCase):
                    self.__load_cases = load_cases
                else:
                    msg = N2PLog.Critical.C802()
                    raise Exception(msg)
        else:
            msg = N2PLog.Critical.C802()
            raise Exception(msg)

    @FailureMode.setter
    def FailureMode(self, failure_mode: str) -> None:
        if failure_mode in ['Wrinkling','Crimping','Dimpling','CoreShear','CoreCrushing','Buckling','FacesheetFailure','FlatwiseTension','PanelStiffness']:
            self.__failure_mode = failure_mode
        else:
            msg = N2PLog.Critical.C951(failure_mode)
            raise Exception(msg)


    @FailureTheory.setter
    def FailureTheory(self, failure_theory: str) -> None:
        if failure_theory in ['NASA','HSB','CMH-17','Airbus','HyperSizer']:
            self.__failure_theory = failure_theory
        else:
            msg = N2PLog.Critical.C952(failure_theory)
            raise Exception(msg)

    @CoreType.setter
    def CoreType(self, core_type: str) -> None:
        if core_type in ['Continuous', 'Honeycomb']:
            self.__core_type = core_type
        else:
            msg = N2PLog.Critical.C953(core_type)
            raise Exception(msg)

    @CellSize.setter
    def CellSize(self, cell_size: float) -> None:
        if self.__core_type == 'Honeycomb':
            self.__cell_size = cell_size
        else:
            msg = N2PLog.Critical.C959()
            raise Exception(msg)

    @RampRadius.setter
    def RampRadius(self, ramp_radius: float) -> None:
        if ramp_radius <= 0:
            msg = N2PLog.Critical.C968()
            raise Exception(msg)
        self.__ramp_radius = ramp_radius

    @BagAngle.setter
    def BagAngle(self, bag_angle: float) -> None:
        if bag_angle < 0 or bag_angle > 360:
            msg = N2PLog.Critical.C969()
            raise Exception(msg)
        self.__bag_angle = bag_angle

    @Parameters.setter
    def Parameters(self, parameters: dict) -> None:
        self.__parameters = parameters

    @LaminateCriteria.setter
    def LaminateCriteria(self, laminate_criteria: dict) -> None:
        if laminate_criteria in ['TsaiHill','TsaiWu','MaxStress']:
            self.__laminate_criteria = laminate_criteria
        else:
            msg = N2PLog.Critical.C963(laminate_criteria)
            raise Exception(msg)

    @AllowableDisplacement.setter
    def AllowableDisplacement(self, allowable_displacement: float) -> None:
        if allowable_displacement < 0:
            msg = N2PLog.Critical.C973()
            raise Exception(msg)
        self.__allowable_displacement = allowable_displacement

    #endregion



    def calculate(self):

        # Once the element list is set, we need to identify the core for each element
        self.__sandwich_dict = get_sandwich_properties(self.__core_type, self.__model, self.__element_list, self.__materials)


        for sandwich_elem in self.__sandwich_dict.values():
            # Check that sandwich configuration is consistent with thin-face and weak-core approximation
            t_sup = sandwich_elem.UpperFace.Thickness
            t_inf = sandwich_elem.LowerFace.Thickness
            t_c = sandwich_elem.SandwichCore.Thickness
            height = t_sup/2 + t_c + t_inf/2

            if height/t_sup < 5.77 or height/t_inf < 5.77:
                msg = N2PLog.Critical.C961()
                raise Exception(msg)


            # Weak-core approximation check
            Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_elem)
            Ef_up = min(Efx_up,Efy_up)
            Ef_down = min(Efx_down, Efy_down)

            if 6*Ef_up*t_sup*(height**2)/(Ec*(t_c**3)) < 100 or 6*Ef_down*t_inf*(height**2)/(Ec*(t_c**3)) < 100:
                msg = N2PLog.Critical.C972()
                raise Exception(msg)


        # Extract forces results from fem solver
        results_list = [(LC.ID, LC.ActiveN2PIncrement.ID) for LC in self.__load_cases]

        # Validate load case types based on failure mode
        required_solution = 'POST_BUCKLING' if self.__failure_mode == 'Buckling' else 'STATICS'
        if required_solution == 'STATICS':
            if self.__failure_mode == 'PanelStiffness':
                expected_result = 'DISPLACEMENTS'
            else:
                expected_result = 'FORCES'
        else:
            expected_result = None

        for LC in self.__load_cases:
            if LC.TypeSolution != required_solution:
                msg = N2PLog.Critical.C967() if required_solution == 'POST_BUCKLING' else N2PLog.Critical.C965()
                raise Exception(msg)
            if expected_result and expected_result not in LC.Results:
                msg = N2PLog.Critical.C966()
                raise Exception(msg)

        # Get forces if required
        if required_solution == 'STATICS':
            forces = self.__model.get_result_by_LCs_Incr(
                results_list, RESULT_NAME[LC.Solver],
                COMPONENT_NAME[LC.Solver], coordsys=-1,
                filter_list=self.__element_list
            )

        # Retrieve force fluxes from FEM model
        self.__RF = {}
        self.__data_components = {} #Create an empty dict to map each results with its corresponding component
        for LC in self.__load_cases:
            if self.__failure_mode not in ['Buckling','PanelStiffness']:
                N_x = forces[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME[LC.Solver][0])]
                N_y = forces[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME[LC.Solver][1])]
                N_xy = forces[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME[LC.Solver][2])]
                M_x  = forces[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME[LC.Solver][3])]
                M_y = forces[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME[LC.Solver][4])]
                M_xy = forces[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME[LC.Solver][5])]
                Q_x = forces[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME[LC.Solver][6])]
                Q_y = forces[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME[LC.Solver][7])]
                self.__RF[(LC.ID,LC.ActiveN2PIncrement.ID)] = []

            if self.__failure_mode == 'Wrinkling':
                if self.__failure_theory == 'NASA':
                    # Set variables k1 and k2 for calculus (in future, it may be introduced by the user)
                    k1 = 0.63 if self.__parameters['K1'] is None else self.__parameters['K1']
                    k2 = 0.86 if self.__parameters['K2'] is None else self.__parameters['K2']

                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"),(f"RF_1 (k1 = {k1})", "f4"),(f"RF_2 (k2 = {k2})","f4"),(f"RF COMPOSITE","f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy = _compute_loads(thickness,t_core,z_sup,z_inf,I,N_x[index_elem],N_y[index_elem],N_xy[index_elem],M_x[index_elem],M_y[index_elem],M_xy[index_elem])

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)
                        Gc = Gxz
                        load_state_up = _classify_stress_state(sigma_x_up,sigma_y_up,tau_xy)
                        load_state_down = _classify_stress_state(sigma_x_down,sigma_y_down,tau_xy)

                        if load_state_up == 'CompressionX':
                            RF_1_up = wrinkling_nasa_1(sigma_x_up, Efx_up, Ec, Gc, k1)
                            RF_2_up = wrinkling_nasa_2(sigma_x_up, Efx_up, Ec, t_sup, t_core, k2)
                            RF_3_up = wrinkling_nasa_composite(sigma_x_up,Efx_up, Efy_up, t_sup, Ec, t_core, nu_xy_up,nu_yx_up)

                        elif load_state_up == 'CompressionY':
                            self.__warning_uniaxial = True
                            RF_1_up = wrinkling_nasa_1(sigma_y_up, Efy_up, Ec, Gc, k1)
                            RF_2_up = wrinkling_nasa_2(sigma_y_up, Efy_up, Ec, t_sup, t_core, k2)
                            RF_3_up = wrinkling_nasa_composite(sigma_y_up,Efx_up, Efy_up, t_sup, Ec, t_core, nu_xy_up,nu_yx_up)

                        elif load_state_up == 'BiaxialCompression':
                            self.__warning_uniaxial = True
                            RF_1_up = wrinkling_nasa_1(sigma_x_up, Efx_up, Ec, Gc, k1)
                            RF_2_up = wrinkling_nasa_2(sigma_x_up, Efx_up, Ec, t_sup, t_core, k2)
                            RF_3_up = wrinkling_nasa_composite(sigma_x_up,Efx_up, Efy_up, t_sup, Ec, t_core, nu_xy_up,nu_yx_up)

                        elif load_state_up == 'Combined':
                            self.__warning_uniaxial = True
                            if sigma_x_up < 0:
                                RF_1_up = wrinkling_nasa_1(sigma_x_up, Efx_up, Ec, Gc, k1)
                                RF_2_up = wrinkling_nasa_2(sigma_x_up, Efx_up, Ec, t_sup, t_core, k2)
                                RF_3_up = wrinkling_nasa_composite(sigma_x_up,Efx_up, Efy_up, t_sup, Ec, t_core, nu_xy_up,nu_yx_up)
                            else:
                                RF_1_up, RF_2_up, RF_3_up = 999999, 999999, 999999

                        else:
                            self.__warning_tension = True
                            RF_1_up, RF_2_up, RF_3_up = 999999, 999999, 999999

                        if load_state_down == 'CompressionX':
                            RF_1_down = wrinkling_nasa_1(sigma_x_down, Efx_down, Ec, Gc, k1)
                            RF_2_down = wrinkling_nasa_2(sigma_x_down, Efx_down, Ec, t_inf, t_core, k2)
                            RF_3_down = wrinkling_nasa_composite(sigma_x_down, Efx_down, Efy_down, t_inf, Ec, t_core,
                                                                 nu_xy_down, nu_yx_down)

                        elif load_state_down == 'CompressionY':
                            self.__warning_uniaxial = True
                            RF_1_down = wrinkling_nasa_1(sigma_y_down, Efy_down, Ec, Gc, k1)
                            RF_2_down = wrinkling_nasa_2(sigma_y_down, Efy_down, Ec, t_inf, t_core, k2)
                            RF_3_down = wrinkling_nasa_composite(sigma_y_down, Efx_down, Efy_down, t_inf, Ec, t_core,
                                                                 nu_xy_down, nu_yx_down)

                        elif load_state_down == 'BiaxialCompression':
                            self.__warning_uniaxial = True
                            RF_1_down = wrinkling_nasa_1(sigma_x_down, Efx_down, Ec, Gc, k1)
                            RF_2_down = wrinkling_nasa_2(sigma_x_down, Efx_down, Ec, t_inf, t_core, k2)
                            RF_3_down = wrinkling_nasa_composite(sigma_x_down, Efx_down, Efy_down, t_inf, Ec, t_core,
                                                                 nu_xy_down, nu_yx_down)

                        elif load_state_down == 'Combined':
                            self.__warning_uniaxial = True
                            if sigma_x_down < 0:
                                RF_1_down = wrinkling_nasa_1(sigma_x_down, Efx_down, Ec, Gc, k1)
                                RF_2_down = wrinkling_nasa_2(sigma_x_down, Efx_down, Ec, t_inf, t_core, k2)
                                RF_3_down = wrinkling_nasa_composite(sigma_x_down, Efx_down, Efy_down, t_inf, Ec,
                                                                     t_core, nu_xy_down, nu_yx_down)
                            else:
                                RF_1_down, RF_2_down, RF_3_down = 999999, 999999, 999999

                        else:
                            self.__warning_tension = True
                            RF_1_down, RF_2_down, RF_3_down = 999999, 999999, 999999

                        RF_1 = min(RF_1_up,RF_1_down)
                        RF_2 = min(RF_2_up, RF_2_down)
                        RF_3 = min(RF_3_up, RF_3_down)

                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append([RF_1,RF_2, RF_3])

                elif self.__failure_theory == 'HyperSizer':
                    k1 = 0.63 if self.__parameters['K1'] is None else self.__parameters['K1']
                    k2 = 0.86 if self.__parameters['K2'] is None else self.__parameters['K2']
                    k3 = 1 if self.__parameters['K3'] is None else self.__parameters['K3']

                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"),(f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy = _compute_loads(thickness, t_core, z_sup,
                                                                                                   z_inf, I,
                                                                                                   N_x[index_elem],
                                                                                                   N_y[index_elem],
                                                                                                   N_xy[index_elem],
                                                                                                   M_x[index_elem],
                                                                                                   M_y[index_elem],
                                                                                                   M_xy[index_elem])

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)
                        Gc = Gxz
                        load_state_up = _classify_stress_state(sigma_x_up, sigma_y_up, tau_xy)
                        load_state_down = _classify_stress_state(sigma_x_down, sigma_y_down, tau_xy)

                        if load_state_up == 'CompressionX':
                            if sandwich_element.SandwichCore.CoreType == 'Continuous':
                                RF_upper = wrinkling_hypersizer_isotropic(sigma_x_up,Efx_up,Ec,Gc,k1)
                            else: # Honeycomb core
                                if type(sandwich_element.UpperFace) == IsotropicShell:
                                    RF_upper = wrinkling_hypersizer_honeycomb(sigma_x_up,Efx_up,Ec,t_sup,t_core,k2)
                                else:
                                    RF_upper = wrinkling_hypersizer_composite(sigma_x_up,Efx_up,Efy_up,t_sup,Ec,t_core,nu_xy_up,nu_yx_up,k3)

                        elif load_state_up == 'CompressionY':
                            if sandwich_element.SandwichCore.CoreType == 'Continuous':
                                RF_upper = wrinkling_hypersizer_isotropic(sigma_y_up,Efy_up,Ec,Gc,k1)
                            else: # Honeycomb core
                                if type(sandwich_element.UpperFace) == IsotropicShell:
                                    RF_upper = 0.95*wrinkling_hypersizer_honeycomb(sigma_y_up,Efy_up,Ec,t_sup,t_core,k2)
                                else:
                                    RF_upper = 0.95*wrinkling_hypersizer_composite(sigma_y_up,Efx_up,Efy_up,t_sup,Ec,t_core,nu_xy_up,nu_yx_up,k3)

                        elif load_state_up == 'BiaxialCompression':
                            RF_upper = wrinkling_hypersizer_composite_biaxial(sigma_x_up, sigma_y_up, k2, Efx_up, Efy_up, t_sup, Ec, t_core,self.__core_type)

                        elif load_state_up == 'PureShear':
                            RF_upper = wrinkling_hypersizer_composite_shear(tau_xy,k2,Efx_up,Efy_up,t_sup,Ec,t_core)

                        elif load_state_up == 'Combined':
                            RF_upper = wrinkling_hypersizer_composite_combined(sigma_x_up,sigma_y_up,tau_xy,k2,Efx_up,Efy_up,t_sup,Ec,t_core,self.__core_type)

                        else: # Other load states will produce no compression, so RF is set to 999999
                            self.__warning_tension = True
                            RF_upper = 999999

                        if load_state_down == 'CompressionX':
                            if sandwich_element.SandwichCore.CoreType == 'Continuous':
                                RF_lower = wrinkling_hypersizer_isotropic(sigma_x_down,Efx_down,Ec,Gc,k1)
                            else: # Honeycomb core
                                if type(sandwich_element.LowerFace) == IsotropicShell:
                                    RF_lower = wrinkling_hypersizer_honeycomb(sigma_x_down,Efx_down,Ec,t_inf,t_core,k2)
                                else:
                                    RF_lower = wrinkling_hypersizer_composite(sigma_x_down,Efx_down,Efy_down,t_inf,Ec,t_core,nu_xy_down,nu_yx_down,k3)

                        elif load_state_down == 'CompressionY':
                            if sandwich_element.SandwichCore.CoreType == 'Continuous':
                                RF_lower = wrinkling_hypersizer_isotropic(sigma_y_down,Efy_down,Ec,Gc,k1)
                            else: # Honeycomb core
                                if type(sandwich_element.LowerFace) == IsotropicShell:
                                    RF_lower = 0.95*wrinkling_hypersizer_honeycomb(sigma_y_down,Efy_down,Ec,t_inf,t_core,k2)
                                else:
                                    RF_lower = 0.95*wrinkling_hypersizer_composite(sigma_y_down,Efx_down,Efy_down,t_inf,Ec,t_core,nu_xy_down,nu_yx_down,k3)

                        elif load_state_down == 'BiaxialCompression':
                            RF_lower = wrinkling_hypersizer_composite_biaxial(sigma_x_down, sigma_y_down, k2, Efx_down, Efy_down, t_inf, Ec, t_core,self.__core_type)

                        elif load_state_down == 'PureShear':
                            RF_lower = wrinkling_hypersizer_composite_shear(tau_xy,k2,Efx_down,Efy_down,t_inf,Ec,t_core)

                        elif load_state_down == 'Combined':
                            RF_lower = wrinkling_hypersizer_composite_combined(sigma_x_down,sigma_y_down,tau_xy,k2,Efx_down,Efy_down,t_inf,Ec,t_core,self.__core_type,k3)

                        else: # Other load states will produce no compression, so RF is set to 999999
                            self.__warning_tension = True
                            RF_lower = 999999

                        RF = min(RF_upper,RF_lower)
                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                elif self.__failure_theory == 'HSB':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF Antisymmetric", "f4"), (f"RF Symmetric", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy = _compute_loads(thickness, t_core,
                                                                                                   z_sup, z_inf, I,
                                                                                                   N_x[index_elem],
                                                                                                   N_y[index_elem],
                                                                                                   N_xy[index_elem],
                                                                                                   M_x[index_elem],
                                                                                                   M_y[index_elem],
                                                                                                   M_xy[index_elem])

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)

                        Gc = Gxz
                        load_state_up = _classify_stress_state(sigma_x_up, sigma_y_up, tau_xy)
                        load_state_down = _classify_stress_state(sigma_x_down, sigma_y_down, tau_xy)

                        if load_state_up == 'CompressionX':
                            RF_antisym_up = antysymmetric_hsb_wrinkling(sigma_x_up,Efx_up,t_sup,nu_xy_up,Ec,Gc)
                            RF_sym_up = symmetric_hsb_wrinkling(sigma_x_up,Efx_up,t_sup,nu_xy_up,Ec,t_core)

                        elif load_state_up == 'CompressionY':
                            self.__warning_uniaxial = True
                            RF_antisym_up = antysymmetric_hsb_wrinkling(sigma_y_up,Efy_up,t_sup,nu_xy_up,Ec,Gc)
                            RF_sym_up = symmetric_hsb_wrinkling(sigma_y_up,Efy_up,t_sup,nu_xy_up,Ec,t_core)

                        elif load_state_up == 'BiaxialCompression':
                            self.__warning_uniaxial = True
                            RF_antisym_up = antysymmetric_hsb_wrinkling(sigma_x_up,Efx_up,t_sup,nu_xy_up,Ec,Gc)
                            RF_sym_up = symmetric_hsb_wrinkling(sigma_x_up,Efx_up,t_sup,nu_xy_up,Ec,t_core)

                        elif load_state_up == 'Combined':
                            self.__warning_uniaxial = True
                            if sigma_x_up < 0:
                                RF_antisym_up = antysymmetric_hsb_wrinkling(sigma_x_up, Efx_up, t_sup, nu_xy_up, Ec, Gc)
                                RF_sym_up = symmetric_hsb_wrinkling(sigma_x_up, Efx_up, t_sup, nu_xy_up, Ec, t_core)
                            else:
                                RF_antisym_up, RF_sym_up = 999999, 999999

                        else:
                            self.__warning_tension = True
                            RF_antisym_up, RF_sym_up = 999999, 999999

                        if load_state_down == 'CompressionX':
                            RF_antisym_down = antysymmetric_hsb_wrinkling(sigma_x_down,Efx_down,t_inf,nu_xy_down,Ec,Gc)
                            RF_sym_down = symmetric_hsb_wrinkling(sigma_x_down,Efx_down,t_inf,nu_xy_down,Ec,t_core)

                        elif load_state_down == 'CompressionY':
                            self.__warning_uniaxial = True
                            RF_antisym_down = antysymmetric_hsb_wrinkling(sigma_y_down,Efy_down,t_inf,nu_xy_down,Ec,Gc)
                            RF_sym_down = symmetric_hsb_wrinkling(sigma_y_down,Efy_down,t_inf,nu_xy_down,Ec,t_core)

                        elif load_state_down == 'BiaxialCompression':
                            self.__warning_uniaxial = True
                            RF_antisym_down = antysymmetric_hsb_wrinkling(sigma_x_down,Efx_down,t_inf,nu_xy_down,Ec,Gc)
                            RF_sym_down = symmetric_hsb_wrinkling(sigma_x_down,Efx_down,t_inf,nu_xy_down,Ec,t_core)

                        elif load_state_down == 'Combined':
                            self.__warning_uniaxial = True
                            if sigma_x_down < 0:
                                RF_antisym_down = antysymmetric_hsb_wrinkling(sigma_x_down, Efx_down, t_inf, nu_xy_down, Ec, Gc)
                                RF_sym_down = symmetric_hsb_wrinkling(sigma_x_down, Efx_down, t_inf, nu_xy_down, Ec, t_core)
                            else:
                                RF_antisym_down, RF_sym_down = 999999, 999999

                        else:
                            self.__warning_tension = True
                            RF_antisym_down, RF_sym_down = 999999, 999999

                        RF_antysimm = min(RF_antisym_up, RF_antisym_down)
                        RF_symmetric = min(RF_sym_up, RF_sym_down)
                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append([RF_antysimm, RF_symmetric])

                elif self.__failure_theory == 'CMH-17':
                    # Set variables C1 to C4
                    C1 = 0.247 if self.__parameters['C1'] is None else self.__parameters['C1']
                    C2 = 0.078 if self.__parameters['C2'] is None else self.__parameters['C2']
                    C3 = 0.33 if self.__parameters['C3'] is None else self.__parameters['C3']
                    C4 = 0 if self.__parameters['C4'] is None else self.__parameters['C4']

                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy = _compute_loads(thickness, t_core,
                                                                                                   z_sup, z_inf, I,
                                                                                                   N_x[index_elem],
                                                                                                   N_y[index_elem],
                                                                                                   N_xy[index_elem],
                                                                                                   M_x[index_elem],
                                                                                                   M_y[index_elem],
                                                                                                   M_xy[index_elem])

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)

                        Gc = Gxz
                        load_state_up = _classify_stress_state(sigma_x_up, sigma_y_up, tau_xy)
                        load_state_down = _classify_stress_state(sigma_x_down, sigma_y_down, tau_xy)

                        if load_state_up == 'CompressionX':
                            if t_core >= 1.82*t_sup*((Efx_up*Ec/(Gc**2))**(1/3)):
                                RF_upper = wriknling_cmh_honeycomb_thick(sigma_x_up,C1,C2,Efx_up,t_sup,Ec,t_core,Gc)
                            else:
                                RF_upper = wrinkling_cmh_honeycomb_thin(sigma_x_up,C3,C4,Efx_up,t_sup,Ec,t_core,Gc)

                        elif load_state_up == 'CompressionY':
                            if t_core >= 1.82*t_sup*((Efy_up*Ec/(Gc**2))**(1/3)):
                                RF_upper = wriknling_cmh_honeycomb_thick(sigma_y_up,C1,C2,Efy_up,t_sup,Ec,t_core,Gc)
                            else:
                                RF_upper = wrinkling_cmh_honeycomb_thin(sigma_y_up,C3,C4,Efy_up,t_sup,Ec,t_core,Gc)

                        elif load_state_up == 'BiaxialCompression':
                            self.__warning_uniaxial = True
                            if t_core >= 1.82*t_sup*((Efx_up*Ec/(Gc**2))**(1/3)):
                                RF_upper = wrinkling_cmh_honeycomb_biaxial_thick(sigma_x_up, sigma_y_up,C1,C2, Efx_up,Efy_up,t_sup,Ec,t_core,Gc)
                            else:
                                RF_upper = wrinkling_cmh_honeycomb_biaxial_thin(sigma_x_up,sigma_y_up,C3,C4, Efx_up, Efy_up, t_sup, Ec, t_core, Gc)

                        elif load_state_up == 'Combined':
                            self.__warning_uniaxial = True
                            if sigma_x_up < 0:
                                if t_core >= 1.82*t_sup*((Efx_up*Ec/(Gc**2))**(1/3)):
                                    RF_upper = wriknling_cmh_honeycomb_thick(sigma_x_up,C1,C2,Efx_up,t_sup,Ec,t_core,Gc)
                                else:
                                    RF_upper = wrinkling_cmh_honeycomb_thin(sigma_x_up,C3,C4,Efx_up,t_sup,Ec,t_core,Gc)
                            else:
                                RF_upper = 999999

                        else:
                            self.__warning_tension = True
                            RF_upper = 999999

                        if load_state_down == 'CompressionX':
                            if t_core >= 1.82 * t_inf * ((Efx_down * Ec / (Gc ** 2)) ** (1 / 3)):
                                RF_lower = wriknling_cmh_honeycomb_thick(sigma_x_down,C1,C2,Efx_down,t_inf,Ec,t_core,Gc)
                            else:
                                RF_lower = wrinkling_cmh_honeycomb_thin(sigma_x_down,C3,C4,Efx_down,t_inf,Ec,t_core,Gc)

                        elif load_state_down == 'CompressionY':
                            if t_core >= 1.82 * t_inf * ((Efy_down * Ec / (Gc ** 2)) ** (1 / 3)):
                                RF_lower = wriknling_cmh_honeycomb_thick(sigma_y_down,C1,C2,Efy_down,t_inf,Ec,t_core,Gc)
                            else:
                                RF_lower = wrinkling_cmh_honeycomb_thin(sigma_y_down,C3,C4,Efy_down,t_inf,Ec,t_core,Gc)

                        elif load_state_down == 'BiaxialCompression':
                            self.__warning_uniaxial = True
                            if t_core >= 1.82 * t_inf * ((Efx_down * Ec / (Gc ** 2)) ** (1 / 3)):
                                RF_lower = wrinkling_cmh_honeycomb_biaxial_thick(sigma_x_down,sigma_y_down,C1,C2,Efx_down,Efy_down,t_inf,Ec,t_core,Gc)
                            else:
                                RF_lower = wrinkling_cmh_honeycomb_biaxial_thin(sigma_x_down,sigma_y_down,C3,C4,Efx_down,Efy_down,t_inf,Ec,t_core,Gc)

                        elif load_state_down == 'Combined':
                            self.__warning_uniaxial = True
                            if sigma_x_down < 0:
                                if t_core >= 1.82 * t_inf * ((Efx_down * Ec / (Gc ** 2)) ** (1 / 3)):
                                    RF_lower = wriknling_cmh_honeycomb_thick(sigma_x_down,C1,C2,Efx_down,t_inf,Ec,t_core,Gc)
                                else:
                                    RF_lower = wrinkling_cmh_honeycomb_thin(sigma_x_down,C3,C4,Efx_down,t_inf,Ec,t_core,Gc)
                            else:
                                RF_lower = 999999

                        else:
                            self.__warning_tension = True
                            RF_lower = 999999


                        RF = min(RF_upper,RF_lower)

                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                elif self.__failure_theory == 'Airbus':
                    # Set variables k1 and k2 for calculus (in future, it may be introduced by the user)
                    k1 = 0.82 if self.__parameters['K1'] is None else self.__parameters['K1']
                    k2 = 0.82 if self.__parameters['K2'] is None else self.__parameters['K2']
                    k3 = 0.44 if self.__parameters['K3'] is None else self.__parameters['K3']

                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy = _compute_loads(thickness, t_core,
                                                                                                   z_sup, z_inf, I,
                                                                                                   N_x[index_elem],
                                                                                                   N_y[index_elem],
                                                                                                   N_xy[index_elem],
                                                                                                   M_x[index_elem],
                                                                                                   M_y[index_elem],
                                                                                                   M_xy[index_elem])

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)

                        load_state_up = _classify_stress_state(sigma_x_up,sigma_y_up,tau_xy)
                        load_state_down = _classify_stress_state(sigma_x_down,sigma_y_down,tau_xy)

                        if load_state_up == 'CompressionX':
                            if (t_sup/t_core)*((Efx_up/Ec)**(1/3)) < 0.2: # Thick core
                                RF_upper = wrinkling_airbus_compression_thick(sigma_x_up,k1,Efx_up,Ec,Gxz)
                            else:
                                RF_upper = wrinkling_airbus_compression_thin(sigma_x_up,k2,Efx_up,Ec,t_sup,t_core)

                        elif load_state_up == 'CompressionY':
                            if (t_sup/t_core)*((Efy_up/Ec)**(1/3)) < 0.2:  # Thick core
                                RF_upper = wrinkling_airbus_compression_thick(sigma_y_up,k1,Efy_up,Ec,Gyz)
                            else:
                                RF_upper = wrinkling_airbus_compression_thin(sigma_y_up, k2, Efy_up, Ec, t_sup, t_core)

                        elif load_state_up == 'PureShear':

                            if type(sandwich_element.SandwichCore.Material) == Isotropic:
                                Gc = sandwich_element.SandwichCore.Material.Shear
                                E_45 = sandwich_element.SandwichCore.Material.Young
                            else:
                                Gxy = sandwich_element.SandwichCore.Material.ShearXY
                                c4 = np.cos(np.radians(45)) ** 4
                                c2 = np.cos(np.radians(45)) ** 2
                                s4 = np.sin(np.radians(45)) ** 4
                                s2 = np.sin(np.radians(45)) ** 2
                                X = -2*nu_xy_up/Efx_up + 1/Gxy
                                E_45_pos = ((1/Efx_up)*c4 +X*c2*s2 + (1/Efy_up)*s4)**(-1)

                                c4 = np.cos(np.radians(-45)) ** 4
                                c2 = np.cos(np.radians(-45)) ** 2
                                s4 = np.sin(np.radians(-45)) ** 4
                                s2 = np.sin(np.radians(-45)) ** 2
                                E_45_neg = ((1 / Efx_up) * c4 + X * c2 * s2 + (1 / Efy_up) * s4) ** (-1)

                                E_45 = min(E_45_pos,E_45_neg)
                                Gc = min(Gxz, Gyz)

                            RF_upper = wrinkling_airbus_shear(tau_xy,k3,E_45,Ec,Gc)

                        elif load_state_up == 'BiaxialCompression':
                            Gc = min(Gxz, Gyz)
                            RF_upper = wrinkling_airbus_biaxial(sigma_x_up,sigma_y_up,k1,Efx_up,Efy_up,Ec,Gc)

                        elif load_state_up == 'Combined':
                            # In combined load state, tension loads may appear. They are treated as 0
                            if sigma_x_up > 0:
                                sigma_x_up = 0
                            if sigma_y_up > 0:
                                sigma_y_up = 0


                            if type(sandwich_element.SandwichCore.Material) == Isotropic:
                                E_45 = sandwich_element.SandwichCore.Material.Young
                                Gc = sandwich_element.SandwichCore.Material.Shear
                            else:
                                c4 = np.cos(np.radians(45)) ** 4
                                c2 = np.cos(np.radians(45)) ** 2
                                s4 = np.sin(np.radians(45)) ** 4
                                s2 = np.sin(np.radians(45)) ** 2

                                Gxy = sandwich_element.SandwichCore.Material.ShearXY

                                X = -2*nu_xy_up/Efx_up + 1/Gxy
                                E_45_pos = ((1/Efx_up)*c4 +X*c2*s2 + (1/Efy_up)*s4)**(-1)

                                c4 = np.cos(np.radians(-45)) ** 4
                                c2 = np.cos(np.radians(-45)) ** 2
                                s4 = np.sin(np.radians(-45)) ** 4
                                s2 = np.sin(np.radians(-45)) ** 2
                                E_45_neg = ((1 / Efx_up) * c4 + X * c2 * s2 + (1 / Efy_up) * s4) ** (-1)

                                E_45 = min(E_45_pos,E_45_neg)
                                Gc = min(Gxz, Gyz)

                            RF_upper = wrinkling_airbus_combined(sigma_x_up,sigma_y_up,tau_xy,k1,k3,Efx_up,Efy_up,E_45,Ec,Gc)

                        else:
                            self.__warning_tension = True
                            RF_upper = 999999

                        if load_state_down == 'CompressionX':
                            if (t_inf/t_core)*((Efx_down/Ec)**(1/3)) < 0.2: # Thick core
                                RF_lower = wrinkling_airbus_compression_thick(sigma_x_down,k1,Efx_down,Ec,Gxz)
                            else:
                                RF_lower = wrinkling_airbus_compression_thin(sigma_x_down,k2,Efx_down,Ec,t_inf,t_core)

                        elif load_state_down == 'CompressionY':
                            if (t_inf/t_core)*((Efy_down/Ec)**(1/3)) < 0.2:  # Thick core
                                RF_lower = wrinkling_airbus_compression_thick(sigma_y_down,k1,Efy_down,Ec,Gyz)
                            else:
                                RF_lower = wrinkling_airbus_compression_thin(sigma_y_down, k2, Efy_down, Ec, t_inf, t_core)

                        elif load_state_down == 'PureShear':

                            if type(sandwich_element.SandwichCore.Material) == Isotropic:
                                Gc = sandwich_element.SandwichCore.Material.Shear
                                E_45 = sandwich_element.SandwichCore.Material.Young
                            else:
                                Gxy = sandwich_element.SandwichCore.Material.ShearXY
                                c4 = np.cos(np.radians(45)) ** 4
                                c2 = np.cos(np.radians(45)) ** 2
                                s4 = np.sin(np.radians(45)) ** 4
                                s2 = np.sin(np.radians(45)) ** 2
                                X = -2 * nu_xy_up / Efx_up + 1 / Gxy
                                E_45_pos = ((1 / Efx_up) * c4 + X * c2 * s2 + (1 / Efy_up) * s4) ** (-1)

                                c4 = np.cos(np.radians(-45)) ** 4
                                c2 = np.cos(np.radians(-45)) ** 2
                                s4 = np.sin(np.radians(-45)) ** 4
                                s2 = np.sin(np.radians(-45)) ** 2
                                E_45_neg = ((1 / Efx_up) * c4 + X * c2 * s2 + (1 / Efy_up) * s4) ** (-1)

                                E_45 = min(E_45_pos, E_45_neg)
                                Gc = min(Gxz, Gyz)

                            RF_lower = wrinkling_airbus_shear(tau_xy,k3,E_45,Ec,Gc)

                        elif load_state_down == 'BiaxialCompression':
                            Gc = min(Gxz, Gyz)
                            RF_lower = wrinkling_airbus_biaxial(sigma_x_down,sigma_y_down,k1,Efx_down,Efy_down,Ec,Gc)

                        elif load_state_down == 'Combined':
                            # In combined load state, tension loads may appear. They are treated as 0
                            if sigma_x_down > 0:
                                sigma_x_down = 0
                            if sigma_y_down > 0:
                                sigma_y_down = 0

                            if type(sandwich_element.SandwichCore.Material) == Isotropic:
                                E_45 = sandwich_element.SandwichCore.Material.Young
                                Gc = sandwich_element.SandwichCore.Material.Shear
                            else:
                                c4 = np.cos(np.radians(45)) ** 4
                                c2 = np.cos(np.radians(45)) ** 2
                                s4 = np.sin(np.radians(45)) ** 4
                                s2 = np.sin(np.radians(45)) ** 2

                                Gxy = sandwich_element.SandwichCore.Material.ShearXY

                                X = -2 * nu_xy_down / Efx_down + 1 / Gxy
                                E_45_pos = ((1 / Efx_down) * c4 + X * c2 * s2 + (1 / Efy_down) * s4) ** (-1)

                                c4 = np.cos(np.radians(-45)) ** 4
                                c2 = np.cos(np.radians(-45)) ** 2
                                s4 = np.sin(np.radians(-45)) ** 4
                                s2 = np.sin(np.radians(-45)) ** 2
                                E_45_neg = ((1 / Efx_down) * c4 + X * c2 * s2 + (1 / Efy_down) * s4) ** (-1)

                                E_45 = min(E_45_pos, E_45_neg)
                                Gc = min(Gxz, Gyz)

                            RF_lower = wrinkling_airbus_combined(sigma_x_down,sigma_y_down,tau_xy,k1,k3,Efx_down,Efy_down,E_45,Ec,Gc)

                        else:
                            self.__warning_tension = True
                            RF_lower = 999999

                        RF = min(RF_upper,RF_lower)


                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                else:
                    msg = N2PLog.Critical.C954(self.__failure_mode,self.__failure_theory)
                    raise Exception(msg)

            elif self.__failure_mode == 'Crimping':
                if self.__failure_theory == 'CMH-17':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy = _compute_loads(thickness,t_core,z_sup,z_inf,I,N_x[index_elem],N_y[index_elem],N_xy[index_elem],M_x[index_elem],M_y[index_elem],M_xy[index_elem])

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)

                        sigma_x = min(sigma_x_up,sigma_x_down)
                        sigma_y = min(sigma_y_up,sigma_y_down)

                        load_state = _classify_stress_state(N_x[index_elem],N_y[index_elem],N_xy[index_elem])

                        if load_state == 'CompressionX':
                            RF = core_shear_crimping_cmh(sigma_x, thickness, t_sup, t_inf, t_core,Gxz)

                        elif load_state == 'CompressionY':
                            RF = core_shear_crimping_cmh(sigma_y, thickness, t_sup, t_inf, t_core,Gyz)

                        elif load_state == 'BiaxialCompression':
                            RF_x = core_shear_crimping_cmh(sigma_x, thickness, t_sup, t_inf, t_core,Gxz)
                            RF_y = core_shear_crimping_cmh(sigma_y, thickness, t_sup, t_inf, t_core,Gyz)
                            RF = min(RF_x,RF_y)

                        elif load_state == 'PureShear':
                            RF = core_shear_crimping_cmh(tau_xy, thickness, t_sup, t_inf, t_core, np.sqrt(Gxz * Gyz))

                        elif load_state == 'Combined':
                            RF_x = core_shear_crimping_cmh(sigma_x, thickness, t_sup, t_inf, t_core,Gxz) if sigma_x != 0 else 999999
                            RF_y = core_shear_crimping_cmh(sigma_y, thickness, t_sup, t_inf, t_core,Gyz) if sigma_y != 0 else 999999
                            RF_xy = core_shear_crimping_cmh(tau_xy, thickness, t_sup, t_inf, t_core, np.sqrt(Gxz * Gyz))
                            RF = min(RF_x, RF_y, RF_xy)

                        else: # When there is no compression, no crimping occurs (RF = 999999)
                            self.__warning_tension = True
                            RF = 999999

                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                elif self.__failure_theory == 'Airbus':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy = _compute_loads(thickness,t_core,z_sup,z_inf,I,N_x[index_elem],N_y[index_elem],N_xy[index_elem],M_x[index_elem],M_y[index_elem],M_xy[index_elem])

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)

                        # Only the maximum compression load is considered
                        sigma = min(sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down,0)

                        Gc = min(Gxz, Gyz)

                        if sigma != 0:
                            RF = core_shear_crimping_airbus(sigma,t_inf,t_sup,t_core,Gc)
                        else:
                            self.__warning_tension = True
                            RF = 999999

                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                elif self.__failure_theory == 'HyperSizer':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)
                        _, _, _, _, _, _, _, _, _, Gxz, Gyz = _compute_material_properties(sandwich_element)

                        Nx = N_x[index_elem]
                        Ny = N_y[index_elem]
                        Nxy = N_xy[index_elem]
                        load_state = _classify_stress_state(Nx, Ny, Nxy)

                        if load_state == 'CompressionX':
                            RF = crimping_hypersizer_compression(Nx, Gxy,t_core)
                        elif load_state == 'CompressionY':
                            RF = crimping_hypersizer_compression(Ny,Gyz,t_core)
                        elif load_state == 'BiaxialCompression':
                            if abs(Nx) >= abs(Ny):
                                RF = crimping_hypersizer_compression(Nx,Gxz,t_core)
                            else:
                                RF = crimping_hypersizer_compression(Ny,Gyz,t_core)
                        elif load_state == 'PureShear':
                            RF = crimping_hypersizer_shear(Nxy,Gxz,Gyz,t_core)
                        elif load_state == 'Combined':
                            RF = crimping_hypersizer_combined(Nx, Ny, Nxy, Gxz, Gyz, t_core)
                        else: # No compression
                            self.__warning_tension = True
                            RF = 999999

                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                else:
                    msg = N2PLog.Critical.C954(self.__failure_mode,self.__failure_theory)
                    raise Exception(msg)

            elif self.__failure_mode == 'Dimpling':
                if self.__cell_size is None:
                    msg = N2PLog.Critical.C955()
                    raise Exception(msg)

                if self.__core_type != 'Honeycomb':
                    msg = N2PLog.Critical.C962()
                    raise Exception(msg)

                if self.__failure_theory == 'Airbus':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy = _compute_loads(thickness,t_core,z_sup,z_inf,I,N_x[index_elem],N_y[index_elem],N_xy[index_elem],M_x[index_elem],M_y[index_elem],M_xy[index_elem])

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)

                        cell_size = self.__cell_size

                        load_state_up = _classify_stress_state(sigma_x_up,sigma_y_up,tau_xy)
                        load_state_down = _classify_stress_state(sigma_x_down,sigma_y_down,tau_xy)

                        if load_state_up == 'CompressionX':
                            RF_upper = dimpling_airbus_compression(sigma_x_up,Efx_up,nu_xy_up,t_sup,cell_size)
                        elif load_state_up == 'CompressionY':
                            RF_upper = dimpling_airbus_compression(sigma_y_up, Efy_up, nu_yx_up, t_sup, cell_size)
                        elif load_state_up == 'BiaxialCompression':
                            RF_upper = dimpling_airbus_biaxial(sigma_x_up, sigma_y_up, Efx_up,Efy_up, nu_xy_up, nu_yx_up, t_sup, cell_size)
                        elif load_state_up == 'PureShear':
                            RF_upper = dimpling_airbus_shear(tau_xy,min(Efx_up,Efy_up), t_sup,cell_size)
                        elif load_state_up == 'Combined':
                            RF_upper = dimpling_airbus_combined(sigma_x_up,sigma_y_up,tau_xy,Efx_up,Efy_up,nu_xy_up,nu_yx_up,t_sup,cell_size)
                        else: # No compression
                            self.__warning_tension = True
                            RF_upper = 999999

                        if load_state_down == 'CompressionX':
                            RF_lower = dimpling_airbus_compression(sigma_x_down,Efx_down,nu_xy_down,t_inf,cell_size)
                        elif load_state_down == 'CompressionY':
                            RF_lower = dimpling_airbus_compression(sigma_y_down, Efy_down, nu_yx_down, t_inf, cell_size)
                        elif load_state_down == 'BiaxialCompression':
                            RF_lower = dimpling_airbus_biaxial(sigma_x_down, sigma_y_down, Efx_down,Efy_down, nu_xy_down, nu_yx_down, t_inf, cell_size)
                        elif load_state_down == 'PureShear':
                            RF_lower = dimpling_airbus_shear(tau_xy,min(Efx_down,Efy_down), t_inf,cell_size)
                        elif load_state_down == 'Combined':
                            RF_lower = dimpling_airbus_combined(sigma_x_down,sigma_y_down,tau_xy,Efx_down,Efy_down,nu_xy_down,nu_yx_down,t_inf,cell_size)
                        else: # No compression
                            self.__warning_tension = True
                            RF_lower = 999999

                        RF = min(RF_upper, RF_lower)

                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                elif self.__failure_theory == 'CMH-17':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy = _compute_loads(thickness,t_core,z_sup,z_inf,I,N_x[index_elem],N_y[index_elem],N_xy[index_elem],M_x[index_elem],M_y[index_elem],M_xy[index_elem])

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)

                        cell_size = self.__cell_size

                        load_state_up = _classify_stress_state(sigma_x_up,sigma_y_up,tau_xy)
                        load_state_down = _classify_stress_state(sigma_x_down,sigma_y_down,tau_xy)

                        if load_state_up == 'CompressionX':
                            RF_upper = dimpling_cmh_compression(sigma_x_up, Efx_up, nu_xy_up, t_sup, cell_size)
                        elif load_state_up == 'CompressionY':
                            RF_upper = dimpling_cmh_compression(sigma_y_up, Efy_up, nu_yx_up, t_sup, cell_size)
                        elif load_state_up == 'BiaxialCompression':
                            RF_upper = dimpling_cmh_biaxial(sigma_x_up, sigma_y_up, Efx_up, Efy_up, nu_xy_up,
                                                               nu_yx_up, t_sup, cell_size)
                        elif load_state_up == 'PureShear':
                            RF_upper = dimpling_cmh_shear(tau_xy, min(Efx_up, Efy_up), t_sup, cell_size)
                        elif load_state_up == 'Combined':
                            RF_upper = dimpling_cmh_combined(sigma_x_up, sigma_y_up, tau_xy, Efx_up, Efy_up,
                                                                nu_xy_up, nu_yx_up, t_sup, cell_size)
                        else:  # No compression
                            self.__warning_tension = True
                            RF_upper = 999999

                        if load_state_down == 'CompressionX':
                            RF_lower = dimpling_cmh_compression(sigma_x_down, Efx_down, nu_xy_down, t_inf, cell_size)
                        elif load_state_down == 'CompressionY':
                            RF_lower = dimpling_cmh_compression(sigma_y_down, Efy_down, nu_yx_down, t_inf, cell_size)
                        elif load_state_down == 'BiaxialCompression':
                            RF_lower = dimpling_cmh_biaxial(sigma_x_down, sigma_y_down, Efx_down, Efy_down,
                                                               nu_xy_down, nu_yx_down, t_inf, cell_size)
                        elif load_state_down == 'PureShear':
                            RF_lower = dimpling_cmh_shear(tau_xy, min(Efx_down, Efy_down), t_inf, cell_size)
                        elif load_state_down == 'Combined':
                            RF_lower = dimpling_cmh_combined(sigma_x_down, sigma_y_down, tau_xy, Efx_down, Efy_down,
                                                                nu_xy_down, nu_yx_down, t_inf, cell_size)
                        else:  # No compression
                            self.__warning_tension = True
                            RF_lower = 999999

                        RF = min(RF_upper,RF_lower)
                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                elif self.__failure_theory == 'HyperSizer':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy = _compute_loads(thickness,t_core,z_sup,z_inf,I,N_x[index_elem],N_y[index_elem],N_xy[index_elem],M_x[index_elem],M_y[index_elem],M_xy[index_elem])

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)

                        cell_size = self.__cell_size

                        load_state_up = _classify_stress_state(sigma_x_up,sigma_y_up,tau_xy)
                        load_state_down = _classify_stress_state(sigma_x_down,sigma_y_down,tau_xy)

                        if load_state_up == 'CompressionX':
                            RF_upper = dimpling_hypersizer_compression(sigma_x_up,Efx_up,nu_xy_up,nu_yx_up,t_sup,cell_size)
                        elif load_state_up == 'CompressionY':
                            RF_upper = dimpling_hypersizer_compression(sigma_y_up,Efy_up, nu_xy_up,nu_yx_up,t_sup,cell_size)
                        elif load_state_up == 'BiaxialCompression':
                            RF_upper = dimpling_hypersizer_biaxial(sigma_x_up, sigma_y_up,Efx_up,Efy_up,nu_xy_up,nu_yx_up,t_sup,cell_size)
                        elif load_state_up == 'PureShear':
                            RF_upper = dimpling_hypersizer_shear(sigma_x_up, sigma_y_up,tau_xy, Efx_up, Efy_up,nu_xy_up,nu_yx_up,t_sup,s)
                        elif load_state_up == 'Combined':
                            RF_upper = dimpling_hypersizer_combined(sigma_x_up, sigma_y_up, tau_xy, Efx_up, Efy_up, nu_xy_up, nu_yx_up, t_sup, cell_size)
                        else: # No compression (RF = 999999)
                            self.__warning_tension = True
                            RF_upper = 999999

                        if load_state_down == 'CompressionX':
                            RF_lower = dimpling_hypersizer_compression(sigma_x_down,Efx_down,nu_xy_down,nu_yx_down,t_inf,cell_size)
                        elif load_state_down == 'CompressionY':
                            RF_lower = dimpling_hypersizer_compression(sigma_y_down,Efy_down, nu_xy_down,nu_yx_down,t_inf,cell_size)
                        elif load_state_down == 'BiaxialCompression':
                            RF_lower = dimpling_hypersizer_biaxial(sigma_x_down, sigma_y_down,Efx_down,Efy_down,nu_xy_down,nu_yx_down,t_inf,cell_size)
                        elif load_state_down == 'PureShear':
                            RF_lower = dimpling_hypersizer_shear(sigma_x_down, sigma_y_down,tau_xy, Efx_down, Efy_down,nu_xy_down,nu_yx_down,t_inf,s)
                        elif load_state_down == 'Combined':
                            RF_lower = dimpling_hypersizer_combined(sigma_x_down, sigma_y_down, tau_xy, Efx_down, Efy_down, nu_xy_down, nu_yx_down, t_inf, cell_size)
                        else: # No compression (RF = 999999)
                            self.__warning_tension = True
                            RF_lower = 999999

                        RF = min(RF_upper,RF_lower)

                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                else:
                    msg = N2PLog.Critical.C954(self.__failure_mode,self.__failure_theory)
                    raise Exception(msg)

            elif self.__failure_mode == 'CoreShear':
                if self.__failure_theory == 'Airbus':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        if sandwich_element.SandwichCore.Material.Allowables.ShearXZ is None:
                            msg = N2PLog.Critical.C957()
                            raise Exception(msg)
                        if sandwich_element.SandwichCore.Material.Allowables.ShearYZ is None:
                            msg = N2PLog.Critical.C958()
                            raise Exception(msg)

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        tau_xz = Q_x[index_elem]/(t_core + 0.5*(t_sup+t_inf))
                        tau_yz = Q_y[index_elem]/(t_core + 0.5*(t_sup+t_inf))

                        if type(sandwich_element.SandwichCore.Material) == Isotropic:
                            shear_xz_allow = sandwich_element.SandwichCore.Material.Allowables.Yield_shear
                            shear_yz_allow = sandwich_element.SandwichCore.Material.Allowables.Yield_shear
                        else:
                            shear_xz_allow = sandwich_element.SandwichCore.Material.Allowables.ShearXZ
                            shear_yz_allow = sandwich_element.SandwichCore.Material.Allowables.ShearYZ

                        if self.__core_type == 'Honeycomb' and t_core > 12.7 and t_core < 100:
                            shear_xz_allow = shear_xz_allow*2.14*t_core**(-0.3)
                            shear_yz_allow = shear_yz_allow * 2.14 * t_core ** (-0.3)

                        RF = 1/((((tau_xz/shear_xz_allow)**2)+((tau_yz/shear_yz_allow)**2))**(1/2))
                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                elif self.__failure_theory in ['CMH-17','HyperSizer']:
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        if sandwich_element.SandwichCore.Material.Allowables.ShearXZ is None:
                            msg = N2PLog.Critical.C957()
                            raise Exception(msg)
                        if sandwich_element.SandwichCore.Material.Allowables.ShearYZ is None:
                            msg = N2PLog.Critical.C958()
                            raise Exception(msg)

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        tau_xz = Q_x[index_elem]/(t_core + 0.5*(t_sup+t_inf))
                        tau_yz = Q_y[index_elem]/(t_core + 0.5*(t_sup+t_inf))

                        if type(sandwich_element.SandwichCore.Material) == Isotropic:
                            shear_xz_allow = sandwich_element.SandwichCore.Material.Allowables.Yield_shear
                            shear_yz_allow = sandwich_element.SandwichCore.Material.Allowables.Yield_shear
                        else:
                            shear_xz_allow = sandwich_element.SandwichCore.Material.Allowables.ShearXZ
                            shear_yz_allow = sandwich_element.SandwichCore.Material.Allowables.ShearYZ

                        RF = 1/((((tau_xz/shear_xz_allow)**2)+((tau_yz/shear_yz_allow)**2))**(1/2))
                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                else:
                    msg = N2PLog.Critical.C954(self.__failure_mode,self.__failure_theory)
                    raise Exception(msg)

            elif self.__failure_mode == 'CoreCrushing':
                if self.__failure_theory == 'Airbus':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]
                        if sandwich_element.SandwichCore.Material.Allowables.ZCompressive is None:
                            msg = N2PLog.Critical.C956()
                            raise Exception(msg)

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)
                        _,_,D_up = sandwich_element.UpperFace._ABDMatrix()
                        _,_,D_down = sandwich_element.LowerFace._ABDMatrix()
                        I_x_up = D_up[0,0]/Efx_up
                        I_y_up = D_up[1,1]/Efy_up
                        I_x_down = D_down[0,0]/Efx_down
                        I_y_down = D_up[1,1]/Efy_down

                        sigma_z_up = M_x[index_elem]*z_sup/I_x_up + M_y[index_elem]*z_sup/I_y_up
                        sigma_z_down = M_x[index_elem] * z_inf / I_x_down + M_y[index_elem] * z_inf / I_y_down
                        sigma_z = min(sigma_z_up, sigma_z_down,0)

                        if type(sandwich_element.SandwichCore.Material) == Isotropic:
                            sigma_z_allow = sandwich_element.SandwichCore.Material.Allowables.Yield_compression
                        else:
                            sigma_z_allow = sandwich_element.SandwichCore.Material.Allowables.ZCompressive

                        if self.__core_type == 'Honeycomb' and t_core > 12.7 and t_core < 100:
                            sigma_z_allow = sigma_z_allow*1.29*t_core**(-0.1)

                        RF = sigma_z_allow/abs(sigma_z) if sigma_z !=0 else 999999

                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                elif self.__failure_theory == 'CMH-17':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]
                        if sandwich_element.SandwichCore.Material.Allowables.ZCompressive is None:
                            msg = N2PLog.Critical.C956()
                            raise Exception(msg)

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)
                        _,_,D_up = sandwich_element.UpperFace._ABDMatrix()
                        _,_,D_down = sandwich_element.LowerFace._ABDMatrix()
                        I_x_up = D_up[0,0]/Efx_up
                        I_y_up = D_up[1,1]/Efy_up
                        I_x_down = D_down[0,0]/Efx_down
                        I_y_down = D_up[1,1]/Efy_down

                        sigma_z_up = M_x[index_elem]*z_sup/I_x_up + M_y[index_elem]*z_sup/I_y_up
                        sigma_z_down = M_x[index_elem] * z_inf / I_x_down + M_y[index_elem] * z_inf / I_y_down
                        sigma_z = min(sigma_z_up, sigma_z_down,0)

                        if type(sandwich_element.SandwichCore.Material) == Isotropic:
                            sigma_z_allow = sandwich_element.SandwichCore.Material.Allowables.Yield_compression
                        else:
                            sigma_z_allow = sandwich_element.SandwichCore.Material.Allowables.ZCompressive

                        RF = sigma_z_allow/abs(sigma_z) if sigma_z !=0 else 999999

                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                elif self.__failure_theory == 'HyperSizer':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]
                        if sandwich_element.SandwichCore.CoreType == 'Honeycomb':
                            if sandwich_element.SandwichCore.Material.Allowables.ZCompressive is None:
                                msg = N2PLog.Critical.C956()
                                raise Exception(msg)

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)
                        _, _, D_up = sandwich_element.UpperFace._ABDMatrix()
                        _, _, D_down = sandwich_element.LowerFace._ABDMatrix()
                        d = (t_sup/2) + (t_inf/2) + t_core

                        # Compute bending loads
                        sigma1_ben_up = abs((M_x[index_elem]**2)/(d*D_up[0,0]))
                        sigma1_ben_down = abs((M_x[index_elem] ** 2) / (d * D_down[0, 0]))
                        sigma2_ben_up = abs((M_y[index_elem]**2)/(d*D_up[1,1]))
                        sigma2_ben_down = abs((M_y[index_elem] ** 2) / (d * D_down[1, 1]))

                        if type(sandwich_element.SandwichCore.Material) == Isotropic:
                            sigma_z_allow = sandwich_element.SandwichCore.Material.Allowables.Yield_Stress
                        else:
                            sigma_z_allow = sandwich_element.SandwichCore.Material.Allowables.ZCompressive

                        RF_ben = sigma_z_allow/max(sigma1_ben_up,sigma1_ben_down,sigma2_ben_up,sigma2_ben_down)
                        W_eff = 25.4 #1 inch
                        RF_joint = sigma_z_allow/max(abs(Q_x[index_elem]/W_eff),abs(Q_y[index_elem]/W_eff))

                        RF = min(RF_ben, RF_joint)
                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                else:
                    msg = N2PLog.Critical.C954(self.__failure_mode,self.__failure_theory)
                    raise Exception(msg)

            elif self.__failure_mode == 'Buckling':
                eigenvalue_buckling = LC.Increments[0].RealEigenvalue
                self.__RF[(LC.ID, LC.Increments[0].ID)] = []
                if self.__failure_theory == 'Airbus':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([(f"ID ENTITY", "i4"),(f"EigenValue", "f4")])
                    # Check for each element that cell size is big enough to avoid local stability buckling eigenmodes
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        # Compute element size
                        distances = []
                        nodes = element.Nodes  # Lista con los 4 nodos

                        for i in range(element.NumNodes):

                            coord1 = np.array(nodes[i].GlobalCoords)  # Coordenadas del nodo actual
                            coord2 = np.array(nodes[(i + 1) % 4].GlobalCoords)  # Coordenadas del siguiente nodo (cíclico)

                            distance = np.linalg.norm(coord2 - coord1)  # Distancia euclidiana
                            distances.append(distance)

                        # Take the average size
                        cell_size = sum(distances)/len(distances)

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)
                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(sandwich_element)

                        if type(sandwich_element.UpperFace) == CompositeShell:
                            # Wrinkling wavelength (upper face)
                            A_sup, B_sup, D_sup = sandwich_element.UpperFace._ABDMatrix()
                            A_eff_sup = A_sup[0,0] + (2*A_sup[0,1]*B_sup[0,1]*B_sup[1,1] - (A_sup[0,1]**2)*D_sup[1,1] - (B_sup[0,1]**2)*A_sup[1,1])/(A_sup[1,1]*D_sup[1,1] - (B_sup[1,1]**2))
                            B_eff_sup = B_sup[0,0] + (A_sup[0,1]*D_sup[0,1]*B_sup[1,1] - A_sup[0,1]*B_sup[0,1]*D_sup[1,1] -B_sup[0,1]*D_sup[0,1]*A_sup[1,1] + (B_sup[0,1]**2)*B_sup[1,1])/(A_sup[1,1]*D_sup[1,1] - (B_sup[1,1]**2))
                            D_eff_sup = D_sup[0,0] + (2*B_sup[0,1]*D_sup[0,1]*B_sup[1,1] - (B_sup[0,1]**2)*D_sup[1,1] - (D_sup[0,1]**2)*A_sup[1,1])/(A_sup[1,1]*D_sup[1,1] - (B_sup[1,1]**2))

                            D_f_sup = (D_eff_sup - B_eff_sup**2)/A_eff_sup

                        else: # sandwich_element.UpperFace == IsotropicShell
                            D_f_sup = Efx_up*(t_sup**3)/12


                        if type(sandwich_element.LowerFace) == CompositeShell:
                            A_inf, B_inf, D_inf = sandwich_element.LowerFace._ABDMatrix()
                            A_eff_inf = A_inf[0,0] + (2*A_inf[0, 1]*B_inf[0, 1]*B_inf[1, 1] - (A_inf[0, 1] ** 2) * D_inf[
                                    1, 1] - (B_inf[0, 1] ** 2) * A_inf[1, 1]) / (
                                                    A_inf[1, 1] * D_inf[1, 1] - (B_inf[1, 1] ** 2))
                            B_eff_inf = B_inf[0, 0] + (
                                        A_inf[0, 1] * D_inf[0, 1] * B_inf[1, 1] - A_inf[0, 1] * B_inf[0, 1] * D_inf[
                                    1, 1] - B_inf[0, 1] * D_inf[0, 1] * A_inf[1, 1] + (B_inf[0, 1] ** 2) * B_inf[
                                            1, 1]) / (A_inf[1, 1] * D_inf[1, 1] - (B_inf[1, 1] ** 2))
                            D_eff_inf = D_inf[0, 0] + (
                                        2 * B_inf[0, 1] * D_inf[0, 1] * B_inf[1, 1] - (B_inf[0, 1] ** 2) * D_inf[
                                    1, 1] - (D_inf[0, 1] ** 2) * A_inf[1, 1]) / (
                                                    A_inf[1, 1] * D_inf[1, 1] - (B_inf[1, 1] ** 2))

                            D_f_inf = (D_eff_inf - B_eff_inf ** 2) / A_eff_inf

                        else:
                            D_f_inf = Efx_down * (t_inf ** 3) / 12

                        lambda_wr_sup = np.pi * (D_f_sup * t_core / (2 * Ec)) ** (1 / 4)
                        lambda_wr_inf = np.pi * (D_f_inf * t_core / (2 * Ec)) ** (1 / 4)
                        lambda_wr = min(lambda_wr_inf,lambda_wr_sup)

                        C = 3
                        if cell_size < C*lambda_wr:
                            msg = N2PLog.Critical.C964()
                            raise Exception(msg)

                        self.__RF[(LC.ID, LC.Increments[0].ID)].append(eigenvalue_buckling)

                else:
                    msg = N2PLog.Critical.C954(self.__failure_mode,self.__failure_theory)
                    raise Exception(msg)

            elif self.__failure_mode == 'FacesheetFailure':
                if self.__failure_theory == 'Airbus':
                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy = _compute_loads(thickness, t_core,
                                                                                                   z_sup, z_inf, I,
                                                                                                   N_x[index_elem],
                                                                                                   N_y[index_elem],
                                                                                                   N_xy[index_elem],
                                                                                                   M_x[index_elem],
                                                                                                   M_y[index_elem],
                                                                                                   M_xy[index_elem])

                        RF_upper = 999999

                        if type(sandwich_element.UpperFace) == CompositeShell:
                            for layer_mat in sandwich_element.UpperFace.MatIDs:
                                Xc = self.__materials[layer_mat].Allowables.XCompressive
                                Xt = self.__materials[layer_mat].Allowables.XTensile
                                Yc = self.__materials[layer_mat].Allowables.YCompressive
                                Yt = self.__materials[layer_mat].Allowables.YTensile
                                S = self.__materials[layer_mat].Allowables.Shear

                                if self.__laminate_criteria == 'TsaiWu':
                                    F1 = (1/Xt - 1/Xc)
                                    F2 = (1/Yt - 1/Yc)
                                    F11 = 1/(Xt*Xc)
                                    F22 = 1/(Yt*Yc)
                                    F66 = 1/(S**2)
                                    F12 = -0.5*((F11*F22)**(0.5))

                                    A = F11*(sigma_x_up**2) + F22*(sigma_y_up**2)+F66*(tau_xy**2)+2*F12*sigma_x_up*sigma_y_up
                                    B = F1*sigma_x_up+F2*sigma_y_up

                                    lambda_cr = (-B + ((B**2 + 4*A)**(0.5)))/(2*A)

                                    if lambda_cr < RF_upper:
                                        RF_upper = lambda_cr

                                elif self.__laminate_criteria == 'TsaiHill':
                                    X1 = Xt if sigma_x_up > 0 else Xc
                                    X2 = Yt if sigma_y_up > 0 else Yc

                                    FI = ((sigma_x_up/X1)**2) - (sigma_x_up*sigma_y_up/(X1**2)) + ((sigma_y_up/X2)**2) + ((tau_xy/S)**2)
                                    RF_upper = 1/(FI**(0.5))

                                elif self.__laminate_criteria == 'MaxStress':
                                    RF_x = Xt/abs(sigma_x_up) if sigma_x_up > 0 else Xc/abs(sigma_x_up)
                                    RF_y = Yt/abs(sigma_y_up) if sigma_y_up > 0 else Yc/abs(sigma_y_up)
                                    RF_shear = S/abs(tau_xy)
                                    RF_upper = min(RF_x,RF_y, RF_shear)



                        else: # SandwichElement is IsotropicShell
                            Allo_tension = sandwich_element.UpperFace.Allowables.Yield_stress
                            Allo_compression = sandwich_element.UpperFace.Allowables.Yield_compression
                            Allo_shear = sandwich_element.UpperFace.Allowables.Yield_shear
                            RF_x = Allo_tension/abs(sigma_x_up) if sigma_x_up > 0 else Allo_compression/abs(sigma_x_up)
                            RF_y = Allo_tension/abs(sigma_y_up) if sigma_y_up > 0 else Allo_compression/abs(sigma_y_up)
                            RF_shear = Allo_shear/abs(tau_xy)
                            RF_upper = min(RF_x,RF_y,RF_shear)

                        RF_lower = 999999

                        if type(sandwich_element.LowerFace) == CompositeShell:
                            Xc = self.__materials[layer_mat].Allowables.XCompressive
                            Xt = self.__materials[layer_mat].Allowables.XTensile
                            Yc = self.__materials[layer_mat].Allowables.YCompressive
                            Yt = self.__materials[layer_mat].Allowables.YTensile
                            S = self.__materials[layer_mat].Allowables.Shear
                            for layer_mat in sandwich_element.LowerFace.MatIDs:
                                if self.__laminate_criteria == 'TsaiWu':
                                    F1 = (1/Xt - 1/Xc)
                                    F2 = (1/Yt - 1/Yc)
                                    F11 = 1/(Xt*Xc)
                                    F22 = 1/(Yt*Yc)
                                    F66 = 1/(S**2)
                                    F12 = -0.5*((F11*F22)**(0.5))

                                    A = F11*(sigma_x_down**2) + F22*(sigma_y_down**2)+F66*(tau_xy**2)+2*F12*sigma_x_down*sigma_y_down
                                    B = F1*sigma_x_down+F2*sigma_y_down

                                    lambda_cr = (-B + ((B**2 + 4*A)**(0.5)))/(2*A)

                                    if lambda_cr < RF_lower:
                                        RF_lower = lambda_cr

                                elif self.__laminate_criteria == 'TsaiHill':
                                    X1 = Xt if sigma_x_down > 0 else Xc
                                    X2 = Yt if sigma_y_down > 0 else Yc

                                    FI = ((sigma_x_down / X1) ** 2) - (sigma_x_down * sigma_y_down / (X1 ** 2)) + (
                                                (sigma_y_down / X2) ** 2) + ((tau_xy / S) ** 2)
                                    RF_lower = 1 / (FI ** (0.5))

                                elif self.__laminate_criteria == 'MaxStress':
                                    RF_x = Xt / abs(sigma_x_down) if sigma_x_down > 0 else Xc / abs(sigma_x_down)
                                    RF_y = Yt / abs(sigma_y_down) if sigma_y_down > 0 else Yc / abs(sigma_y_down)
                                    RF_shear = S / abs(tau_xy)
                                    RF_upper = min(RF_x, RF_y, RF_shear)

                        else: # SandwichElement is IsotropicShell
                            Allo_tension = sandwich_element.LowerFace.Allowables.Yield_stress
                            Allo_compression = sandwich_element.LowerFace.Allowables.Yield_compression
                            Allo_shear = sandwich_element.LowerFace.Allowables.Yield_shear
                            RF_x = Allo_tension/abs(sigma_x_down) if sigma_x_down > 0 else Allo_compression/abs(sigma_x_down)
                            RF_y = Allo_tension/abs(sigma_y_down) if sigma_y_down > 0 else Allo_compression/abs(sigma_y_down)
                            RF_shear = Allo_shear/abs(tau_xy)
                            RF_lower = min(RF_x,RF_y,RF_shear)

                        RF = min(RF_upper,RF_lower)
                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                else:
                    msg = N2PLog.Critical.C954(self.__failure_mode,self.__failure_theory)
                    raise Exception(msg)

            elif self.__failure_mode == 'FlatwiseTension':
                if self.__failure_theory == 'CMH-17':
                    if self.__ramp_radius is None:
                        msg = N2PLog.Critical.C970()
                        raise Exception(msg)

                    if self.__bag_angle is None:
                        msg = N2PLog.Critical.C971()
                        raise Exception(msg)

                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY", "i4"), (f"RF", "f4")])
                    for index_elem, element in enumerate(self.__element_list):
                        # Compute the Sandwich structure from element list and axial stress in material principal direction
                        sandwich_element = self.__sandwich_dict[element]

                        # Thickness
                        t_sup, t_inf, t_core, thickness, z_sup, z_inf, I = _compute_geometry(sandwich_element)

                        sigma_x_up, sigma_x_down, sigma_y_up, sigma_y_down, tau_xy = _compute_loads(thickness, t_core, z_sup,
                                                                                                   z_inf, I,
                                                                                                   N_x[index_elem],
                                                                                                   N_y[index_elem],
                                                                                                   N_xy[index_elem],
                                                                                                   M_x[index_elem],
                                                                                                   M_y[index_elem],
                                                                                                   M_xy[index_elem])

                        d = t_core + 0.5*(t_sup+t_inf) # Distance between facesheet midplanes
                        t_e = t_sup + t_inf

                        Efx_up, Efx_down, Efy_up, Efy_down, nu_xy_up, nu_xy_down, nu_yx_up, nu_yx_down, Ec, Gxz, Gyz = _compute_material_properties(
                            sandwich_element)
                        Gc = Gxz
                        Mx_prime = (N_x[index_elem]/2)*(t_e-d-((t_inf+t_sup)/2))
                        My_prime = (N_y[index_elem]/2)*(t_e-d-((t_inf+t_sup)/2))

                        Nx_b = ((N_x[index_elem]/2)+(Mx_prime/d))*(1/np.cos(np.radians(self.__bag_angle)))
                        Ny_b = ((N_y[index_elem]/2)+(My_prime/d))*(1/np.cos(np.radians(self.__bag_angle)))

                        fx_flat = Nx_b/self.__ramp_radius
                        fy_flat = Ny_b/self.__ramp_radius


                        RF_x_lower = abs(sigma_x_down/fx_flat)
                        RF_x_upper = abs(sigma_x_up / fx_flat)
                        RF_y_lower = abs(sigma_y_down / fy_flat)
                        RF_y_upper = abs(sigma_y_up / fy_flat)

                        RF = min(RF_x_lower,RF_x_upper,RF_y_lower,RF_y_upper)
                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)
                else:
                    msg = N2PLog.Critical.C954(self.__failure_mode,self.__failure_theory)
                    raise Exception(msg)

            elif self.__failure_mode == 'PanelStiffness':
                if self.__failure_theory == 'Airbus':
                    if self.__allowable_displacement is None:
                        msg = N2PLog.Critical.C974()
                        raise Exception(msg)


                    self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)] = np.dtype([("ID ENTITY (NODE)", "i4"), (f"RF", "f4")])
                    node_list = set()

                    # Barrer la lista de self.__element_list
                    for element in self.__element_list:
                        node_list.update(element.Nodes)

                    node_list = list(node_list)

                    displacements = self.__model.get_result_by_LCs_Incr(results_list, RESULT_NAME_DISP[self.__model.Solver],COMPONENT_NAME_DISP[self.__model.Solver],filter_list=node_list)
                    u_x = displacements[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME_DISP[LC.Solver][0])]
                    u_y = displacements[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME_DISP[LC.Solver][1])]
                    u_z = displacements[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME_DISP[LC.Solver][2])]
                    u_r = displacements[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME_DISP[LC.Solver][3])]
                    self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)] = []

                    for index_node, node in enumerate(node_list):
                        max_u = max(abs(u_x[index_node]),abs(u_y[index_node]),abs(u_z[index_node]),abs(u_r[index_node]))
                        RF = self.__allowable_displacement/abs(max_u)
                        self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)].append(RF)

                else:
                    msg = N2PLog.Critical.C954(self.__failure_mode, self.__failure_theory)
                    raise Exception(msg)


            else:
                # Execution will never enter in this part because error in setter would raise, code added for understanding
                msg = 'Failure mode not available'
                raise Exception(msg)

        if self.__warning_uniaxial:
            N2PLog.Warning.W950()

        if self.__warning_tension:
            N2PLog.Warning.W951()


        #region HDF5
        self.__hdf5.create_hdf5()
        # Once RF are computed, data must be imported to HDF5
        dataEntryList = []
        for LC in self.__load_cases:

            matrix = []
            if self.__failure_mode == 'PanelStiffness':
                for index, node in enumerate(node_list):
                    nodeID = node.ID
                    RF = self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)][index]

                    matrix_row = (nodeID, RF)
                    matrix.append(matrix_row)
            else:
                for index, elem in enumerate(self.__sandwich_dict.keys()):

                    element = elem.ID
                    if self.__failure_mode == 'Buckling':
                        RF = self.__RF[(LC.ID, LC.Increments[0].ID)][index]
                    else:
                        RF = self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)][index]

                    if isinstance(RF, list):
                        matrix_row = (element, *RF)  # Unpack all elements
                    else:
                        matrix_row = (element, RF)

                    matrix.append(matrix_row)

            # Create dtype for structured array
            components_dtype = self.__data_components[(LC.ID, LC.ActiveN2PIncrement.ID)]

            # Create structured array
            array = np.array(matrix, dtype=components_dtype)

            myDataEntry = DataEntry()
            myDataEntry.LoadCase = LC.ID
            myDataEntry.LoadCaseName = LC.Name
            if self.__failure_mode == 'Buckling':
                myDataEntry.Increment = LC.Increments[0].ID
            else:
                myDataEntry.Increment = LC.ActiveN2PIncrement.ID
            myDataEntry.Data = array
            myDataEntry.Section = 'None'
            myDataEntry.ResultsName = "SANDWICH STRUCTURE FAILURE"
            myDataEntry.Part = "(0,'0')"
            dataEntryList.append(myDataEntry)

        self.__hdf5.write_dataset(dataEntryList)

        # Record input data
        inputList = []

        inputFailureTheory = DataEntry()
        inputFailureTheory.DataInput = self.__failure_theory
        inputFailureTheory.DataInputName = "FailureTheory"

        inputFailureMode = DataEntry()
        inputFailureMode.DataInput = self.__failure_mode
        inputFailureMode.DataInputName = "FailureMode"

        inputModelPath = DataEntry()
        inputModelPath.DataInput = self.__model.FilePath
        inputModelPath.DataInputName = "Model"

        inputList.append(inputFailureTheory)
        inputList.append(inputFailureMode)
        inputList.append(inputModelPath)

        self.__hdf5._modules_input_data(inputList)
        #endregion