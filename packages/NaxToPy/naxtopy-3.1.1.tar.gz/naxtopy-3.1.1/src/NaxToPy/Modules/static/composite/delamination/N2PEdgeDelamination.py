"""Script for the definition of the class N2PDelamination."""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info.

import numpy as np

from NaxToPy.Core.N2PModelContent import N2PElement, N2PLoadCase
from NaxToPy.Core.N2PModelContent import N2PModelContent, N2PNode, N2PLog
from NaxToPy.Modules.common.data_input_hdf5 import DataEntry
from NaxToPy.Modules.common.hdf5 import HDF5_NaxTo
from NaxToPy.Modules.common.material import Orthotropic
from NaxToPy.Modules.common.model_processor import elem_to_material, get_properties
from NaxToPy.Modules.common.property import CompositeShell

MAXITERS = 1000
MAXLAYERS = 100
TOL = 1e-10

RESULT_NAME = {"Nastran": "DISPLACEMENTS",
               "Abaqus": "U"}

COMPONENT_NAME = {"Nastran": ["X","Y","Z"],
                  "Abaqus": ["U1","U2","U3"]}

def jacobian(f, x, h=1e-5):
    """
    Approximates the Jacobian matrix of a given function using finite differences.

    Parameters:
    f (callable): Function for which the Jacobian is computed. It must return an array.
    x (array-like): Point at which the Jacobian is evaluated.
    h (float, optional): Step size for finite differences. Default is 1e-5.

    Returns:
    numpy.ndarray: Approximated Jacobian matrix.
    """
    n = len(x)
    J = np.zeros((n, n))
    fx = f(x)
    for i in range(n):
        x_i = x.copy()
        x_i[i] += h
        J[:, i] = (f(x_i) - fx) / h
    return J

def newton_raphson(f, x0, tol=1e-8, max_iter=100):
    """
    Solves a system of nonlinear equations using the Newton-Raphson method.

    Parameters:
    f (callable): Function representing the system of equations. It must return an array.
    x0 (array-like): Initial guess for the solution.
    tol (float, optional): Tolerance for convergence. Default is 1e-8.
    max_iter (int, optional): Maximum number of iterations. Default is 100.

    Returns:
    numpy.ndarray: Approximate solution to the system.

    Raises:
    ValueError: If the Jacobian is singular or if the method does not converge within max_iter iterations.
    """
    x = np.array(x0, dtype=float)
    for _ in range(max_iter):
        fx = f(x)
        if np.linalg.norm(fx, ord=2) < tol:
            return x
        J = jacobian(f, x)
        try:
            dx = np.linalg.solve(J, -fx)
        except np.linalg.LinAlgError:
            raise ValueError("Jacobian is singular, try a different initial guess")
        x += dx
    raise ValueError("No convergence: reached max_iter")

def f_solve(func, x0):
    """
    Finds the roots of a nonlinear equation or system of equations.

    Parameters:
    func (callable): Function representing the equation or system. It must return an array.
    x0 (array-like): Initial guess for the root.

    Returns:
    numpy.ndarray: Computed root of the equation/system.
    """
    x0 = np.atleast_1d(x0)  # Ensure input is an array
    return newton_raphson(func, x0)


class N2PEdgeDelamination:
    """ Class used to obtain interlaminar stresses and RF from Edge Delamination

    Examples:

        >>> import NaxToPy as n2p
        >>> from NaxToPy.Modules.static.delamination import N2PDelamination
        >>> model = n2p.load_model(r"file path")
        >>> element_list = [3026292,3026293,3026294] # List of element
        >>> n2pelem = model.get_elements(element_list)
        >>> load_case_id = [68195, 68196] # List of ID of Load Cases
        >>> n2plc = model.get_load_case(load_case_id)
        >>> delam = N2PDelamination()
        >>> delam.Model = model  # Assign the model
        >>> delam.ElementList = n2pelem  # Assign elements
        >>> delam.LoadCases = n2plc  # Assign load cases
        >>> mat_ID = 4  #ID of the material
        >>> part_mat = '0' # Part ID of the material
        >>> delam.Materials[(mat_ID,part_mat)].YoungZ = 12000  #Assign the Z elastic modulus
        >>> delam.Materials[(mat_ID,part_mat)].PoissonXZ = 0.3  # Assign the XZ Poisson ratio
        >>> delam.Materials[(mat_ID,part_mat)].PoissonYZ = 0.3  # Assign the YZ Poisson ratio
        >>> delam.Materials[(mat_ID,part_mat)].Allowables.ShearXZ = 105  #Assign the shear XZ allowable
        >>> delam.Materials[(mat_ID,part_mat)].Allowables.ShearYZ = 105  #Assign the shear YZ allowable
        >>> delam.Materials[(mat_ID,part_mat)].Allowables.ZCompressive = 108  #Assign the compressive Z allowable
        >>> delam.Materials[(mat_ID,part_mat)].Allowables.ZTensile = 53.9  #Assign the tensile Z allowable
        >>> delam.FailureCriteria = 'CI'
        >>> for LC in delam.LoadCases:
        >>>    LC.RefTemp = -30
        >>> int_distance = {}
        >>> for element in n2pelem:
        >>>    int_distance[element] = 5
        >>> delam.IntegrationDistance = int_distance
        >>> delam.HDF5.FilePath = r"file output"
        >>> delam.calculate()
    """

    __slots__ = ('__Bconstants','__BconstantsThermal','__RF','__edge_mech_Nx','__edge_mech_strains','__edge_props',
        '__edge_thermal_Nx','__edge_thermal_strains','__edges','__element_list','__failure_criteria','__hdf5',
        '__int_distance','__load_cases','__materials','__mechanical_layer_stresses','__model','__processor_object',
        '__relative_orientation','__strains','__thermal_layer_stresses')
    
    def __init__(self):

        # Initialize the class with the different attributes
        # Mandatory attributes -----------------------------------------------------------------------------------------
        self.__model: N2PModelContent = None
        self.__element_list: list[N2PElement] = None
        self.__load_cases: list[N2PLoadCase] = None
        self.__int_distance: float = None
        self.__failure_criteria: str = 'CI'

        self.__edges: list[tuple[N2PElement, N2PNode, N2PNode]] = []
        self.__processor_object = None
        self.__RF = None
        self.__materials: dict[tuple[int, str], Orthotropic] = None

        # Initialize the HDF5
        self.__hdf5 = HDF5_NaxTo()

    # region Getters

    @property
    def Materials(self) -> dict[tuple[int, str], Orthotropic]:
        """
        Read-Only. Dictionary with all the materials in the elements selected
        """
        return self.__materials


    @property
    def Edges(self) -> list[tuple[N2PElement, N2PNode, N2PNode]]:
        """
        Returns a list of tuples with the different edges of the element selection
        """
        return self.__edges

    @property
    def Model(self) -> N2PModelContent:
        """
        Read/Write, Mandatory. N2PModelContent object
        """
        return self.__model

    @property
    def ElementList(self) -> list[N2PElement]:
        """
        Read/Write, Mandatory. List of N2PElement
        """
        return self.__element_list

    @property
    def LoadCases(self) -> list[N2PLoadCase]:
        """
        Read/Write, Mandatory. List of N2PLoadCase
        """
        return self.__load_cases


    @property
    def IntegrationDistance(self) -> float:
        """
        Read/Write, Optional.
        """
        return self.__int_distance

    @property
    def FailureCriteria(self) -> str:
        """
        Read/Write, Optional.
        """
        return self.__failure_criteria

    @property
    def HDF5(self) -> HDF5_NaxTo:
        """
        Read/Write, Optional. HDF5 attribute which contains all the necessary info to create it
        """
        return self.__hdf5

    # endregion

    # region Setters

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

            # Get free edges from the element list provided
            self.__edges = self.__model.get_free_edges(self.__element_list)


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

    @IntegrationDistance.setter
    def IntegrationDistance(self, int_distance: dict) -> None:
        if not isinstance(int_distance, dict):
            msg = N2PLog.Critical.C850()
            raise Exception(msg)
        for key, value in int_distance.items():
            if not isinstance(key, N2PElement):
                msg = N2PLog.Critical.C851(key)
                raise Exception(msg)
            if not isinstance(value, (int,float)):
                msg = N2PLog.Critical.C852(value, key)
                raise Exception(msg)
        self.__int_distance = int_distance

    @FailureCriteria.setter
    def FailureCriteria(self, failure_criteria: str) -> None:
        if failure_criteria in ['MI','TI','CI']:
            self.__failure_criteria = failure_criteria
        else:
            msg = N2PLog.Critical.C853()
            raise Exception(msg)

    # endregion

    def __calculate_equivalent_mechanical_load(self) -> None:
        """
        Calculate the equivalent mechanical loads and strains derived from the epsilon_x applied
        :return: None
        """
        self.__edge_mech_Nx = {}
        self.__edge_mech_strains = {}

        for LC in self.__load_cases:
            self.__edge_mech_Nx[(LC.ID,LC.ActiveN2PIncrement.ID)] = []
            self.__edge_mech_strains[(LC.ID,LC.ActiveN2PIncrement.ID)] = []
            # Compute mechanical load for each element to be analyzed
            for index, edge in enumerate(self.__edges):
                edge_elem = edge[0]
                prop_edge = self.__edge_props[edge_elem]

                # Retrieve A matrix
                A = prop_edge._ABDMATRIX[0]
                strain_x = self.__strains[(LC.ID,LC.ActiveN2PIncrement.ID)][index]
                # Submatrix for the 2x2 system
                submatrix_A = np.array([[A[1, 1], A[1, 2]],
                                        [A[1, 2], A[2, 2]]])
                # Right-hand side vector
                rhs = np.array([-A[0, 1] * strain_x, -A[0, 2] * strain_x])

                # Solve for strain_y and gamma_xy
                strain_y, gamma_xy = np.linalg.solve(submatrix_A, rhs)

                # Calculate axial load in the x-direction
                Nx_mech_eq = A[0, 0] * strain_x + A[0, 1] * strain_y + A[0, 2] * gamma_xy

                self.__edge_mech_Nx[(LC.ID,LC.ActiveN2PIncrement.ID)].append(Nx_mech_eq)
                self.__edge_mech_strains[(LC.ID,LC.ActiveN2PIncrement.ID)].append((strain_x, strain_y, gamma_xy))

    def __calculate_equivalent_thermal_loads(self) -> None:
        """
        Calculate the equivalent thermal loads derived from the deltaT applied.
        :return: None
        """
        self.__edge_thermal_Nx = {}
        self.__edge_thermal_strains = {}
        for LC in self.__load_cases:
            self.__edge_thermal_Nx[(LC.ID,LC.ActiveN2PIncrement.ID)] = []
            self.__edge_thermal_strains[(LC.ID,LC.ActiveN2PIncrement.ID)] = []
            # Iterate on the property associated to each element
            for index_i,edge in enumerate(self.__edges):
                edge_elem = edge[0]
                prop_elem = self.__edge_props[edge_elem]
                # Initialize thermal stresses
                thermal_stress = np.array([0, 0, 0])
                # Iterate on each layer of the laminate
                for index_j,(material,thickness,theta) in enumerate(zip(prop_elem._mat_IDs,prop_elem._thicknesses,prop_elem._theta)):
                    # Retrieve coefficients of thermal expansion in both directions
                    mu_a = self.Materials[material].TExpX
                    mu_b = self.Materials[material].TExpY

                    # Calculate the thermal expansions in the a and b directions
                    Etha = mu_a * LC.RefTemp
                    Ethb = mu_b * LC.RefTemp
                    beta = self.__relative_orientation[(LC.ID),(LC.ActiveN2PIncrement.ID)][index_i]
                    psi = np.radians(theta) + beta  # Convert orientation from degrees to radians

                    t_k = thickness  # Thickness of the layer

                    # Method to obtain the Q' matrix
                    Qprime = prop_elem.QMatrix(index_j)  # Q' matrix of the layer

                    # Calculate the thermal strains in the material
                    Eth1 = (np.cos(psi) ** 2) * Etha + (np.sin(psi) ** 2) * Ethb
                    Eth2 = (np.sin(psi) ** 2) * Etha + (np.cos(psi) ** 2) * Ethb
                    Eth12 = 2 * np.cos(psi) * np.sin(psi) * (Etha - Ethb)

                    # Create the thermal strains vector for this layer
                    Eth_vector = np.array([Eth1, Eth2, Eth12])

                    # Transform strains into stresses and add to the previous
                    thermal_stress = thermal_stress + (Qprime @ Eth_vector) * t_k

                # Retrieve A matrix and invert it
                A = prop_elem._ABDMATRIX[0]
                A_inv = np.linalg.inv(A)

                # Compute the strain vector by solving the system of equations
                strain_vector = A_inv @ thermal_stress

                # Extract individual strain components
                strain_1, strain_2, gamma_12 = strain_vector

                # Return the calculated thermal load and strains
                Nx_thermal_eq = thermal_stress[0]

                self.__edge_thermal_Nx[(LC.ID),(LC.ActiveN2PIncrement.ID)].append(Nx_thermal_eq)
                self.__edge_thermal_strains[(LC.ID),(LC.ActiveN2PIncrement.ID)].append((strain_1, strain_2, gamma_12))

    def __calculate_layer_mechanical_stresses(self) -> None:
        """
        Calculate mechanical stresses for each interface of the laminate
        :return: None
        """
        # Initialize arrays for store the stresses and the associated constants
        self.__mechanical_layer_stresses = {}
        self.__Bconstants = {}
        for LC in self.__load_cases:
            self.__mechanical_layer_stresses[(LC.ID,LC.ActiveN2PIncrement.ID)] = []
            self.__Bconstants[(LC.ID,LC.ActiveN2PIncrement.ID)] = []
            for global_index, (edge, strains) in enumerate(zip(self.__edges, self.__edge_mech_strains[(LC.ID,LC.ActiveN2PIncrement.ID)])):
                edge_elem = edge[0]
                prop_edge = self.__edge_props[edge_elem]
                # Initialize cumulative sums for B2k, B4k, and B5k constants
                sumB2k = 0
                sumB4k = 0
                sumB5k = 0

                # Create the mechanical strain vector for efficient matrix operations
                strain_x = strains[0]
                strain_y = strains[1]
                gamma_xy = strains[2]
                strain_vector_mech = np.array([strain_x, strain_y, gamma_xy])

                # Initialize the C and X coefficients to zero
                C = [0] * 12
                X = [0] * 11

                # Compute the thickness of the whole laminate
                thickness = sum(prop_edge._thicknesses)

                # Initialize up and down Z coordinates for each layer
                ZD1 = thickness/2 # Z down coordinate of each layer

                # Iterate over each layer in the sequence
                self.__Bconstants[(LC.ID,LC.ActiveN2PIncrement.ID)].append([])
                self.__mechanical_layer_stresses[(LC.ID,LC.ActiveN2PIncrement.ID)].append([])

                for index, (mat_ply,thick_ply, theta_ply) in enumerate(zip(prop_edge._mat_IDs,prop_edge._thicknesses,prop_edge._theta)):
                    material = self.Materials[mat_ply]

                    if type(material) != Orthotropic:
                        msg = N2PLog.Critical.C854(material.ID)
                        raise Exception(msg)
                    # Update up and down Z coordinates
                    ZD = ZD1
                    ZD1 -= thick_ply

                    # Retreieve material properties
                    Ea = material.YoungX
                    Eb = material.YoungY
                    Ez = material.YoungZ
                    G_ab = material.ShearXY
                    G_az = material.ShearXZ
                    G_bz = material.ShearYZ
                    nu_ab = material.PoissonXY
                    nu_az = material.PoissonXZ
                    nu_bz = material.PoissonYZ
                    mu_a = material.TExpX
                    mu_b = material.TExpY

                    # Check that material has out of plane young modulus and poisson ratio
                    if Ez is None or nu_az is None or nu_bz is None:
                        msg = N2PLog.Critical.C855()
                        raise Exception(msg)
                    # Calculate Q' and thickness
                    Q_prime = prop_edge.QMatrix(index)
                    t_k = thick_ply

                    # Compute trigonometric values for orientation angle (Psi)
                    beta = self.__relative_orientation[(LC.ID),(LC.ActiveN2PIncrement.ID)][global_index]
                    psi = np.radians(theta_ply) + beta
                    sn = np.sin(psi)
                    cm = np.cos(psi)
                    c2 = cm ** 2
                    s2 = sn ** 2
                    cs = sn * cm
                    c2s2 = c2 - s2

                    # Compute compliance matrix components (D terms)
                    D11 = 1 / Ea
                    D22 = 1 / Eb
                    D33 = 1 / Ez
                    D12 = -nu_ab / Ea
                    D13 = -nu_az / Ea
                    D23 = -nu_bz / Eb
                    D44 = 1 / G_bz
                    D55 = 1 / G_az
                    D66 = 1 / G_ab

                    # Intermediate variables to reduce redundant calculations
                    v1 = s2 * D11 + c2 * D12
                    v2 = s2 * D12 + c2 * D22
                    v3 = cs ** 2 * D66
                    v4 = 2 * cs * (D11 - D12)
                    v5 = 2 * cs * (D12 - D22)

                    # Compute the full compliance matrix components (S terms)
                    S11 = c2 * (c2 * D11 + s2 * D12) + s2 * (c2 * D12 + s2 * D22) + v3
                    S12 = c2 * v1 + s2 * v2 - v3
                    S13 = c2 * D13 + s2 * D23
                    S33 = D33
                    S22 = s2 * v1 + c2 * v2 + v3
                    S23 = s2 * D13 + c2 * D23

                    # Compute remaining compliance components
                    v3 = c2s2 * D66
                    S16 = c2 * v4 + s2 * v5 - cs * v3
                    S26 = s2 * v4 + s2 * v5 + cs * v3
                    S36 = 2 * cs * (D13 - D23)
                    S66 = 2 * cs * v4 - 2 * cs * v5 + c2s2 ** 2 * D66
                    S44 = c2 * D44 + s2 * D55
                    S45 = cs * (D55 - D44)
                    S55 = s2 * D44 + c2 * D55

                    # Calculate S_bar values (for transformed compliance matrix)
                    S22_bar = S22 - (S12 ** 2) / S11
                    S23_bar = S23 - S12 * S13 / S11
                    S26_bar = S26 - (S12 * S16) / S11
                    S33_bar = S33 - (S13 ** 2) / S11
                    S36_bar = S36 - (S13 * S16) / S11
                    S66_bar = S66 - (S16 ** 2) / S11

                    # Calculate the stress vector: [σ_xk, σ_yk, τ_xyk] = Q' @ [ε_x, ε_y, γ_xy]
                    stress_vector_M = Q_prime @ strain_vector_mech
                    sigma_xk, sigma_yk, tau_xyk = stress_vector_M

                    # Compute the constants B2k, B4k, B5k based on the current layer's properties
                    # Please note that the definition of these variables does not seem to be in accordance with those
                    # described in the documentation. However, it has been decided to multiply the variables in the
                    # documentation by their corresponding stresses to avoid numerical errors when these are very small.
                    # To be consistent with the expressions described in the documentation, we must drag these stresses and
                    # apply them to the rest of the variables that depend on B2, B4 and B5 (F1k, F2k, coefficients C and X, etc.)

                    B2 = -tau_xyk * ZD - sumB2k
                    B4 = -sigma_yk * ZD - sumB4k
                    B5 = sigma_yk * ZD ** 2 / 2 + sumB5k

                    # Update cumulative sums for the constants B2, B4, and B5
                    sumB2k += tau_xyk * t_k
                    sumB4k += sigma_yk * t_k
                    sumB5k += sigma_yk * t_k * (ZD + ZD1) / 2

                    # Precompute powers of ZD and ZD1 to avoid redundant calculations
                    ZK2 = ZD ** 2
                    ZK3 = ZD ** 3
                    ZK4 = ZD ** 4
                    ZK5 = ZD ** 5

                    ZK6 = ZD1 ** 2
                    ZK7 = ZD1 ** 3
                    ZK8 = ZD1 ** 4
                    ZK9 = ZD1 ** 5

                    # Intermediate terms that will be reused in multiple F functions
                    V1 = B4 * (ZK2 - ZK6)  # Common term for F1k, F2k, F3k, F4k
                    V2 = ZK3 - ZK7  # Another common term

                    # Compute the F functions based on the given formulae
                    F1k = (3 * (ZK5 - ZK9) * (sigma_yk ** 2) +
                           15 * B4 * sigma_yk * (ZK4 - ZK8) +
                           20 * (B5 * sigma_yk + B4 ** 2) * V2 +
                           60 * B5 * V1 + 60 * B5 ** 2 * t_k)

                    F2k = (V2 / 6 * sigma_yk + V1 / 2 + B5 * t_k)

                    F3k = (V2 / 3 * (sigma_yk ** 2) + V1 * sigma_yk + B4 ** 2 * t_k)

                    F4k = (V2 / 3 * sigma_yk * tau_xyk +
                           (ZK2 - ZK6) * (B4 * tau_xyk + B2 * sigma_yk) / 2 +
                           B2 * B4 * t_k)

                    F5k = (V2 / 3 * (tau_xyk ** 2) +
                           B2 * tau_xyk * (ZK2 - ZK6) +
                           B2 ** 2 * t_k)

                    # Compute common intermediate variables
                    ZK9 = S33_bar * F1k
                    ZK1 = (sigma_yk ** 2) * S22_bar * t_k
                    ZK2 = (sigma_yk * tau_xyk) * S26_bar * t_k
                    ZK3 = 2 * strain_x * t_k / S11
                    ZK4 = sigma_yk * S23_bar * F2k
                    ZK5 = S45 * F4k
                    ZK6 = tau_xyk * S36_bar * F2k
                    ZK7 = S55 * F5k
                    ZK8 = (tau_xyk ** 2) * S66_bar * t_k
                    ZK0 = S44 * F3k

                    # Update C constants using the computed intermediate variables
                    C[0] += ZK9
                    C[2] += ZK1 + ZK2 + ZK3 * S12 * sigma_yk
                    C[3] += -ZK4 + ZK0 / 2 - ZK6 + ZK5
                    C[4] += 3 * ZK1 + 4 * ZK2 + 2 * ZK3 * S12 * sigma_yk
                    C[7] += -2 * ZK4 - 2 * ZK6 + ZK0 + 2 * ZK5 + ZK7
                    C[8] += ZK7
                    C[9] += 3 * ZK1 + 3 * ZK8 + 6 * ZK2 + 2 * ZK3 * (S12 * sigma_yk + S16 * tau_xyk)
                    C[10] += 5 * ZK1 + 3 * ZK8 + 8 * ZK2 + 2 * ZK3 * (2 * S12 * sigma_yk + S16 * tau_xyk)

                    # Update X constants
                    X[0] += sigma_yk * t_k * S12 / S11
                    X[1] += t_k * tau_xyk * S16 / S11
                    X[2] += (sigma_yk ** 2) * S22_bar * t_k
                    X[3] += S33_bar * F1k
                    X[4] += (tau_xyk ** 2) * S66_bar * t_k
                    X[5] += -sigma_yk * S23_bar * F2k
                    X[6] += 2 * (sigma_yk * tau_xyk) * S26_bar * t_k
                    X[7] += -tau_xyk * S36_bar * F2k
                    X[8] += S44 * F3k
                    X[9] += S45 * F4k
                    X[10] += S55 * F5k

                    self.__Bconstants[(LC.ID,LC.ActiveN2PIncrement.ID)][global_index].append((B2, B4, B5))

                # Finalize C coefficients
                C[0] /= 120
                C[1] = 2 * C[0]
                C[5] = C[4] / 2
                C[6] = 6 * C[0]
                C[11] = C[4]

                # Initial guess for phi0 and the scaling factor b based on thickness
                phi0 = 2
                b = 20 * thickness

                for iter in range(MAXITERS):
                    # Step 1: Compute the lambda polynomial using the current phi0, and find its real roots
                    lambda_poly = [(phi0**4) * C[0],
                                   (phi0**4) * C[1],
                                   C[2] + (phi0**2) * C[3],
                                   C[4],C[5]]

                    lmbda_roots = np.roots(lambda_poly)
                    real_lmbda = lmbda_roots[np.isreal(lmbda_roots)].real  # Filter out non-real roots

                    # Step 2: For each real lambda, compute the corresponding phi values (roots of phi polynomial)
                    lmbd_phi_pairs = []
                    for lmbda in real_lmbda:
                        phi_poly = [(lmbda**3) * C[6],
                                    0,
                                    (lmbda**2) * C[7] + lmbda * C[8],
                                    0,
                                    (lmbda**2) * C[9] + lmbda * C[10] + C[11]]

                        phi_roots = np.roots(phi_poly)
                        real_phi = phi_roots[np.isreal(phi_roots)].real  # Filter out non-real roots
                        for phi in real_phi:
                            lmbd_phi_pairs.append((lmbda, phi))  # Collect valid (lambda, phi) pairs

                    # Step 3: Minimize PC by evaluating the PC function for each (lambda, phi) pair
                    strain_PC = strain_x

                    phi_opt, lambda_opt, PC_min = 0, 0, float('inf')  # Initialize optimal values
                    for L, P in lmbd_phi_pairs:

                        PC = 2 * strain_PC * (X[0] * (b - ((1 + L) / (L * P))) + X[1] *
                                             (b - (1 / P))) + X[2] * (b - (3 * (L**2) + 5 * L + 3) /
                                                                      (2 * L * P * (1 + L))) + \
                             X[3] * ((P**3) * (L**2) / (120 * (1 + L))) + X[4] * (b - 1.5 / P) -\
                             X[5] * ((P * L) / (1 + L)) + X[6] * (b - (3 * (L**2) + 4 * L + 2) / (2 * L * P * (1 + L)))\
                             + ((P * L) / (1 + L)) * (X[8] / 2 - X[7] + X[9]) + X[10] * P / 2  # Calculate PC for the current pair


                        if abs(PC) < abs(PC_min):  # Update optimal (lambda, phi) if a smaller PC is found
                            PC_min, phi_opt, lambda_opt = PC, P, L

                    # Step 4: Check for convergence (if change in phi is smaller than tolerance)
                    if abs(phi_opt - phi0) < TOL:
                        break  # Converged, return the optimal values

                    # Update phi0 for the next iteration
                    phi0 = phi_opt
                if iter == MAXITERS:
                    raise ValueError("Optimization did not converge within the maximum number of iterations.")

                # Once solution is obtained, use the constants to integrate and obtain average values of stresses
                phi = phi_opt
                lmbda = lambda_opt
                distance = self.__int_distance[edge_elem]
                D1 = np.exp(-phi*distance)
                D2 = np.exp(-phi*lmbda*distance)

                ZD1 = thickness/2

                for index, (mat_ply, thick_ply, theta_ply) in enumerate(zip(prop_edge._mat_IDs, prop_edge._thicknesses, prop_edge._theta)):
                    ZD1 -= thick_ply
                    B2 = self.__Bconstants[(LC.ID,LC.ActiveN2PIncrement.ID)][global_index][index][0]
                    B4 = self.__Bconstants[(LC.ID,LC.ActiveN2PIncrement.ID)][global_index][index][1]
                    B5 = self.__Bconstants[(LC.ID,LC.ActiveN2PIncrement.ID)][global_index][index][2]
                    Q_prime = prop_edge.QMatrix(index)
                    sigma_xk, sigma_yk, tau_xyk = Q_prime @ strain_vector_mech
                    D3 = sigma_yk * ZD1 ** 2 / 2.0 + B4 * ZD1 + B5
                    D4 = sigma_yk * ZD1 + B4
                    D5 = tau_xyk * ZD1 + B2

                    # Average stresses calculation by integrating the layer stresses
                    tau_xzA = (1 - D1) * D5 / distance
                    tau_yzA = (lmbda * (1 - D1) - (1 - D2)) * D4 / (distance * (lmbda - 1))
                    sigma_zA = lmbda * phi * D3 * (D1 - D2) / (distance * (lmbda - 1))
                    self.__mechanical_layer_stresses[(LC.ID,LC.ActiveN2PIncrement.ID)][global_index].append((sigma_zA, tau_xzA, tau_yzA))

    def __calculate_layer_thermal_stresses(self) -> None:
        """
        Calculate thermal stresses for each interface of the laminate.
        :return: None
        """
        self.__thermal_layer_stresses = {}
        self.__BconstantsThermal = {}

        for LC in self.__load_cases:
            self.__thermal_layer_stresses[(LC.ID,LC.ActiveN2PIncrement.ID)] = []
            self.__BconstantsThermal[(LC.ID,LC.ActiveN2PIncrement.ID)] = []
            for global_index, (edge, strains) in enumerate(zip(self.__edges, self.__edge_thermal_strains[(LC.ID,LC.ActiveN2PIncrement.ID)])):
                # Initialize cumulative sums for B2k, B4k, and B5k constants
                edge_elem = edge[0]
                prop_edge = self.__edge_props[edge_elem]
                sumB2k = 0
                sumB4k = 0
                sumB5k = 0

                # Create the mechanical strain vector for efficient matrix operations
                strain_x = strains[0]
                strain_y = strains[1]
                gamma_xy = strains[2]
                strain_vector_mech = np.array([strain_x, strain_y, gamma_xy])

                # Initialize the C and X coefficients to zero
                C = [0] * 12
                X = [0] * 11

                # Compute the thickness of the whole laminate
                thickness = sum(prop_edge._thicknesses)

                # Initialize up and down Z coordinates for each layer
                ZD = thickness / 2 + prop_edge._thicknesses[0]  # Z up coordinate of each layer
                ZD1 = thickness / 2  # Z down coordinate of each layer

                # Iterate over each layer in the sequence
                self.__thermal_layer_stresses[(LC.ID,LC.ActiveN2PIncrement.ID)].append([])
                self.__BconstantsThermal[(LC.ID,LC.ActiveN2PIncrement.ID)].append([])

                for index, (mat_ply, thick_ply, theta_ply) in enumerate(zip(prop_edge._mat_IDs, prop_edge._thicknesses, prop_edge._theta)):
                    material = self.Materials[mat_ply]
                    if type(material) != Orthotropic:
                        msg = N2PLog.Critical.C854()
                        raise Exception(msg)
                    # Update up and down Z coordinates
                    ZD = ZD1
                    ZD1 -= thick_ply

                    # Retreieve material properties
                    Ea = material.YoungX
                    Eb = material.YoungY
                    Ez = material.YoungZ
                    G_ab = material.ShearXY
                    G_az = material.ShearXZ
                    G_bz = material.ShearYZ
                    nu_ab = material.PoissonXY
                    nu_az = material.PoissonXY
                    nu_bz = material.PoissonXY
                    mu_a = material.TExpX
                    mu_b = material.TExpY

                    # Calculate Q' and thickness
                    Q_prime = prop_edge.QMatrix(index)
                    t_k = thick_ply

                    # Compute trigonometric values for orientation angle (Psi)
                    beta = self.__relative_orientation[(LC.ID),(LC.ActiveN2PIncrement.ID)][global_index]
                    psi = np.radians(theta_ply) + beta  # Convert angle from degrees to radians
                    sn = np.sin(psi)
                    cm = np.cos(psi)
                    c2 = cm ** 2
                    s2 = sn ** 2
                    cs = sn * cm
                    c2s2 = c2 - s2

                    # Compute compliance matrix components (D terms)
                    D11 = 1 / Ea
                    D22 = 1 / Eb
                    D33 = 1 / Ez
                    D12 = -nu_ab / Ea  # Symmetry of the compliance matrix
                    D13 = -nu_az / Ea
                    D23 = -nu_bz / Eb
                    D44 = 1 / G_bz
                    D55 = 1 / G_az
                    D66 = 1 / G_ab

                    # Intermediate variables to reduce redundant calculations
                    v1 = s2 * D11 + c2 * D12
                    v2 = s2 * D12 + c2 * D22
                    v3 = cs ** 2 * D66
                    v4 = 2 * cs * (D11 - D12)
                    v5 = 2 * cs * (D12 - D22)

                    # Compute the full compliance matrix components (S terms)
                    S11 = c2 * (c2 * D11 + s2 * D12) + s2 * (c2 * D12 + s2 * D22) + v3
                    S12 = c2 * v1 + s2 * v2 - v3
                    S13 = c2 * D13 + s2 * D23
                    S33 = D33
                    S22 = s2 * v1 + c2 * v2 + v3
                    S23 = s2 * D13 + c2 * D23

                    # Compute remaining compliance components
                    v3 = c2s2 * D66
                    S16 = c2 * v4 + s2 * v5 - cs * v3
                    S26 = s2 * v4 + s2 * v5 + cs * v3
                    S36 = 2 * cs * (D13 - D23)
                    S66 = 2 * cs * v4 - 2 * cs * v5 + c2s2 ** 2 * D66
                    S44 = c2 * D44 + s2 * D55
                    S45 = cs * (D55 - D44)
                    S55 = s2 * D44 + c2 * D55

                    # Calculate S_bar values (for transformed compliance matrix)
                    S22_bar = S22 - (S12 ** 2) / S11
                    S23_bar = S23 - S12 * S13 / S11
                    S26_bar = S26 - (S12 * S16) / S11
                    S33_bar = S33 - (S13 ** 2) / S11
                    S36_bar = S36 - (S13 * S16) / S11
                    S66_bar = S66 - (S16 ** 2) / S11

                    # Calculate the thermal expansions in the a, b, and z directions
                    Etha = mu_a * LC.RefTemp
                    Ethb = mu_b * LC.RefTemp

                    # Retrieve thermal strains from edge elements
                    strain_1 = self.__edge_thermal_strains[(LC.ID),(LC.ActiveN2PIncrement.ID)][global_index][0]
                    strain_2 = self.__edge_thermal_strains[(LC.ID),(LC.ActiveN2PIncrement.ID)][global_index][1]
                    gamma_12 = self.__edge_thermal_strains[(LC.ID),(LC.ActiveN2PIncrement.ID)][global_index][2]

                    # Calculate the thermal strains in the material
                    Eth1 = (np.cos(psi) ** 2) * Etha + (np.sin(psi) ** 2) * Ethb
                    Eth2 = (np.sin(psi) ** 2) * Etha + (np.cos(psi) ** 2) * Ethb
                    Eth12 = 2 * (np.cos(psi) * np.sin(psi)) * (Etha - Ethb)

                    Ebd1 = strain_1 - Eth1
                    Ebd2 = strain_2 - Eth2
                    Gbd12 = gamma_12 - Eth12

                    strain_vector_thermal = np.array([Ebd1, Ebd2, Gbd12])

                    # Calculate the stress vector: [σ_xk, σ_yk, τ_xyk] = Q' @ [ε_x, ε_y, γ_xy]
                    stress_vector_thermal = Q_prime @ strain_vector_thermal
                    sigma_xkT, sigma_ykT, tau_xykT = stress_vector_thermal

                    # Compute the constants B2k, B4k, B5k using the current layer's properties
                    B2T = -tau_xykT * ZD - sumB2k
                    B4T = -sigma_ykT * ZD - sumB4k
                    B5T = sigma_ykT * ZD * ZD / 2 + sumB5k

                    # Update cumulative sums for B2, B4, and B5 constants
                    sumB2k += (tau_xykT * t_k)
                    sumB4k += (sigma_ykT * t_k)
                    sumB5k += (sigma_ykT * t_k * (ZD + ZD1) / 2)

                    # Precompute powers of ZD and ZD1 to avoid redundant calculations
                    ZK2 = ZD ** 2
                    ZK3 = ZD ** 3
                    ZK4 = ZD ** 4
                    ZK5 = ZD ** 5

                    ZK6 = ZD1 ** 2
                    ZK7 = ZD1 ** 3
                    ZK8 = ZD1 ** 4
                    ZK9 = ZD1 ** 5

                    # Intermediate terms that will be reused in multiple F functions
                    V1 = B4T * (ZK2 - ZK6)
                    V2 = ZK3 - ZK7

                    # Compute F functions
                    F1kT = 3 * (ZK5 - ZK9) * (sigma_ykT ** 2) + 15 * B4T * sigma_ykT * (ZK4 - ZK8) \
                           + 20 * (B5T * sigma_ykT + B4T ** 2) * V2 + 60 * B5T * V1 + 60 * B5T ** 2 * t_k
                    F2kT = V2 / 6 * sigma_ykT + V1 / 2 + B5T * t_k
                    F3kT = V2 / 3 * (sigma_ykT ** 2) + V1 * sigma_ykT + B4T ** 2 * t_k
                    F4kT = V2 / 3 * sigma_ykT * tau_xykT + (ZK2 - ZK6) * (B4T * tau_xykT + B2T * sigma_ykT) / 2 \
                           + B2T * B4T * t_k
                    F5kT = V2 / 3 * (tau_xykT ** 2) + B2T * tau_xykT * (ZK2 - ZK6) + B2T ** 2 * t_k

                    ZK1 = (sigma_ykT ** 2) * S22_bar * t_k
                    ZK2 = sigma_ykT * tau_xykT * S26_bar * t_k
                    ZK3 = 4 * (Eth2 - Eth1 * S12 / S11) * sigma_ykT * t_k
                    ZK4 = sigma_ykT * S23_bar * F2kT
                    ZK5 = S45 * F4kT
                    ZK6 = tau_xykT * S36_bar * F2kT
                    ZK7 = S55 * F5kT
                    ZK8 = (tau_xykT ** 2) * S66_bar * t_k
                    ZK9 = S33_bar * F1kT
                    ZK10 = 4 * (Eth12 - Eth1 * S16 / S11) * tau_xykT * t_k
                    ZK0 = S44 * F3kT

                    # Update C coefficients
                    C[0] += ZK9  # C1
                    C[2] += ZK1 + ZK2 + 0.5 * ZK3  # C3
                    C[3] += -ZK4 + 0.5 * ZK0 - ZK6 + ZK5  # C4
                    C[4] += 3 * ZK1 + 4 * ZK2 + ZK3  # C5
                    C[7] += -2 * ZK4 - 2 * ZK6 + ZK0 + 2 * ZK5 + ZK7  # C8
                    C[8] += ZK7  # C9
                    C[9] += 3 * ZK1 + 3 * ZK8 + 6 * ZK2 + ZK3 + ZK10  # C10
                    C[10] += 5 * ZK1 + 3 * ZK8 + 8 * ZK2 + 2 * ZK3 + ZK10  # C11

                    # Update X coefficients
                    X[0] += 2 * t_k * sigma_ykT * (Eth2 - Eth1 * S12 / S11)  # X1
                    X[1] += 2 * t_k * tau_xykT * (Eth12 - Eth1 * S16 / S11)  # X2
                    X[2] += ZK1  # X3
                    X[3] += ZK9  # X4
                    X[4] += ZK8  # X5
                    X[5] += -ZK4  # X6
                    X[6] += 2 * ZK2  # X7
                    X[7] += -ZK6  # X8
                    X[8] += ZK0  # X9
                    X[9] += ZK5  # X10
                    X[10] += ZK7  # X11
                    self.__BconstantsThermal[(LC.ID),(LC.ActiveN2PIncrement.ID)][global_index].append((B2T, B4T, B5T))

                # Finalize C coefficients
                C[0] /= 120
                C[1] = 2 * C[0]
                C[5] = C[4] / 2
                C[6] = 6 * C[0]
                C[11] = C[4]

                # Initial guess for phi0 and the scaling factor b based on thickness
                phi0 = 2
                b = 20 * thickness

                for iter in range(MAXITERS):
                    # Step 1: Compute the lambda polynomial using the current phi0, and find its real roots
                    lambda_poly = [(phi0 ** 4) * C[0],
                                   (phi0 ** 4) * C[1],
                                   C[2] + (phi0 ** 2) * C[3],
                                   C[4], C[5]]

                    lmbda_roots = np.roots(lambda_poly)
                    real_lmbda = lmbda_roots[np.isreal(lmbda_roots)].real  # Filter out non-real roots

                    # Step 2: For each real lambda, compute the corresponding phi values (roots of phi polynomial)
                    lmbd_phi_pairs = []
                    for lmbda in real_lmbda:
                        phi_poly = [(lmbda ** 3) * C[6],
                                    0,
                                    (lmbda ** 2) * C[7] + lmbda * C[8],
                                    0,
                                    (lmbda ** 2) * C[9] + lmbda * C[10] + C[11]]

                        phi_roots = np.roots(phi_poly)
                        real_phi = phi_roots[np.isreal(phi_roots)].real  # Filter out non-real roots
                        for phi in real_phi:
                            lmbd_phi_pairs.append((lmbda, phi))  # Collect valid (lambda, phi) pairs

                    # Step 3: Minimize PC by evaluating the PC function for each (lambda, phi) pair
                    strain_PC = 0.5

                    phi_opt, lambda_opt, PC_min = 0, 0, float('inf')  # Initialize optimal values
                    for L, P in lmbd_phi_pairs:

                        PC = 2 * strain_PC * (X[0] * (b - ((1 + L) / (L * P))) + X[1] *
                                              (b - (1 / P))) + X[2] * (b - (3 * (L ** 2) + 5 * L + 3) /
                                                                       (2 * L * P * (1 + L))) + \
                             X[3] * ((P ** 3) * (L ** 2) / (120 * (1 + L))) + X[4] * (b - 1.5 / P) - \
                             X[5] * ((P * L) / (1 + L)) + X[6] * (b - (3 * (L ** 2) + 4 * L + 2) / (2 * L * P * (1 + L))) \
                             + ((P * L) / (1 + L)) * (X[8] / 2 - X[7] + X[9]) + X[
                                 10] * P / 2  # Calculate PC for the current pair

                        if abs(PC) < abs(PC_min):  # Update optimal (lambda, phi) if a smaller PC is found
                            PC_min, phi_opt, lambda_opt = PC, P, L

                    # Step 4: Check for convergence (if change in phi is smaller than tolerance)
                    if abs(phi_opt - phi0) < TOL:
                        break  # Converged, return the optimal values

                    # Update phi0 for the next iteration
                    phi0 = phi_opt
                    if iter == MAXITERS:
                        N2PLog.Critical.C856()


                phi = phi_opt
                lmbda = lambda_opt
                distance = self.__int_distance[edge_elem]
                D1 = np.exp(-phi * distance)
                D2 = np.exp(-phi * lmbda * distance)

                ZD1 = thickness / 2

                for index, (mat_ply, thick_ply, theta_ply) in enumerate(zip(prop_edge._mat_IDs,prop_edge._thicknesses, prop_edge._theta)):
                    ZD1 -= thick_ply
                    B2 = self.__BconstantsThermal[(LC.ID),(LC.ActiveN2PIncrement.ID)][global_index][index][0]
                    B4 = self.__BconstantsThermal[(LC.ID),(LC.ActiveN2PIncrement.ID)][global_index][index][1]
                    B5 = self.__BconstantsThermal[(LC.ID),(LC.ActiveN2PIncrement.ID)][global_index][index][2]

                    mu_a = self.Materials[mat_ply].TExpX
                    mu_b = self.Materials[mat_ply].TExpY

                    beta = self.__relative_orientation[(LC.ID),(LC.ActiveN2PIncrement.ID)][global_index]
                    psi = np.radians(theta_ply) + beta
                    Etha = mu_a * LC.RefTemp
                    Ethb = mu_b * LC.RefTemp

                    # Calculate the thermal strains in the material
                    Eth1 = (np.cos(psi) ** 2) * Etha + (np.sin(psi) ** 2) * Ethb
                    Eth2 = (np.sin(psi) ** 2) * Etha + (np.cos(psi) ** 2) * Ethb
                    Eth12 = 2 * (np.cos(psi) * np.sin(psi)) * (Etha - Ethb)  # Coupling term

                    Ebd1 = strain_1 - Eth1
                    Ebd2 = strain_2 - Eth2
                    Gbd12 = gamma_12 - Eth12

                    Q_prime = prop_edge.QMatrix(index)
                    strain_vector_thermal = np.array([Ebd1, Ebd2, Gbd12])

                    # Calculate the stress vector: [σ_xk, σ_yk, τ_xyk] = Q' @ [ε_x, ε_y, γ_xy]
                    stress_vector_thermal = Q_prime @ strain_vector_thermal
                    sigma_xkT, sigma_ykT, tau_xykT = stress_vector_thermal
                    D3 = sigma_ykT * ZD1 ** 2 / 2.0 + B4 * ZD1 + B5
                    D4 = sigma_ykT * ZD1 + B4
                    D5 = tau_xykT * ZD1 + B2

                    # Thermal stresses calculation
                    tau_xzTA = (1 - D1) * D5 / distance
                    tau_yzTA = (lmbda * (1 - D1) - (1 - D2)) * D4 / (distance * (lmbda - 1))
                    sigma_zTA = lmbda * phi * D3 * (D1 - D2) / (distance * (lmbda - 1))
                    self.__thermal_layer_stresses[(LC.ID),(LC.ActiveN2PIncrement.ID)][global_index].append((sigma_zTA, tau_xzTA, tau_yzTA))

    def calculate(self) -> None:
        """
        Executes all necessary calculations as the final step in the workflow.

        Returns:
            None
        """

        # Check load cases list and element list

        # Load case list is a mandatory input
        if self.__load_cases is None:
            msg = N2PLog.Critical.C858()
            raise Exception(msg)
        else:
            # Check if lc_list is a list of N2PLoadCases (otherwise raise error)
            if not all(isinstance(lc, N2PLoadCase) for lc in self.__load_cases):
                msg = N2PLog.Critical.C802()
                raise Exception(msg)

        # Element List is a mandatory input
        if self.__element_list is None:
            msg = N2PLog.Critical.C859()
            raise Exception(msg)
        else:
            # Check if lc_list is a list of N2PElements (otherwise raise error)
            if not all(isinstance(elem, N2PElement) for elem in self.__element_list):
                msg = N2PLog.Critical.C801()
                raise Exception(msg)

        #If materials allowables are not defined, raise an error
        for material in self.__materials.values():
            if material.Allowables.ShearXZ is None or material.Allowables.ShearYZ is None or material.Allowables.ZTensile is None or material.Allowables.ZCompressive is None:
                msg = N2PLog.Critical.C857(material.ID)
                raise Exception(msg)


        # If temperature of the load case is not set, set by default to 0
        for LC in self.__load_cases:
            if LC.RefTemp is None:
                N2PLog.Warning.W850(LC)
                LC.RefTemp = 0


        _, self.__edge_props = get_properties(self.__model,self.__element_list)

        # If integration distance is not defined, set by default to the element thickness
        if self.__int_distance is None:
            N2PLog.Warning.W851()
            self.__int_distance = {}
            for element in self.__element_list:
                self.__int_distance[element] = self.__edge_props[element].Thickness


        # Check that all properties are CompositeShell
        for prop_check in self.__edge_props.values():
            if type(prop_check) is not CompositeShell:
                msg = N2PLog.Critical.C861()
                raise Exception(msg)

        strains_dict = {}
        relative_orientation = {}

        results_list = [(LC.ID,LC.ActiveN2PIncrement.ID) for LC in self.__load_cases]

        displacements = self.__model.get_result_by_LCs_Incr(results_list, RESULT_NAME[LC.Solver],COMPONENT_NAME[LC.Solver], coordsys=0)


        for LC in self.__load_cases:
            # Get the displacements of each node from results in the 3 directions
            displacements_X = displacements[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME[LC.Solver][0])]
            displacements_Y = displacements[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME[LC.Solver][1])]
            displacements_Z = displacements[(LC.ID, LC.ActiveN2PIncrement.ID, COMPONENT_NAME[LC.Solver][2])]

            strains_dict[(LC.ID,LC.ActiveN2PIncrement.ID)] = []

            relative_orientation[(LC.ID,LC.ActiveN2PIncrement.ID)] = []

            # Compute the initial and the final position of the nodes considering the displacements
            for index,edge in enumerate(self.__edges):
                # Initial position of the nodes
                nodeA_X0 = edge[1].X
                nodeA_Y0 = edge[1].Y
                nodeA_Z0 = edge[1].Z
                nodeB_X0 = edge[2].X
                nodeB_Y0 = edge[2].Y
                nodeB_Z0 = edge[2].Z
                # Compute the original length of each edge
                vectorAB = [nodeB_X0-nodeA_X0, nodeB_Y0-nodeA_Y0, nodeB_Z0-nodeA_Z0]
                L0 = np.linalg.norm(vectorAB)

                # Compute the displacements for both nodes of the edge
                displacement_AX = displacements_X[edge[1].InternalID]
                displacement_BX = displacements_X[edge[2].InternalID]
                displacement_AY = displacements_Y[edge[1].InternalID]
                displacement_BY = displacements_Y[edge[2].InternalID]
                displacement_AZ = displacements_Z[edge[1].InternalID]
                displacement_BZ = displacements_Z[edge[2].InternalID]

                # Compute the final position of each node by adding displacements
                nodeA_XF = nodeA_X0 + displacement_AX
                nodeA_YF = nodeA_Y0 + displacement_AY
                nodeA_ZF = nodeA_Z0 + displacement_AZ
                nodeB_XF = nodeB_X0 + displacement_BX
                nodeB_YF = nodeB_Y0 + displacement_BY
                nodeB_ZF = nodeB_Z0 + displacement_BZ
                # Compute the final length of the edge
                LF = np.linalg.norm([nodeB_XF-nodeA_XF, nodeB_YF-nodeA_YF, nodeB_ZF-nodeA_ZF])
                # Compute the strain from initial and final length
                strain = (LF-L0)/L0

                strains_dict[(LC.ID,LC.ActiveN2PIncrement.ID)].append(strain)

                # Retrieve material system
                material_sys_vectorX = edge[0].MaterialSystemArray[0:3]

                # Cosine of angle between both vectors
                cos_angle_beta = np.dot(vectorAB, material_sys_vectorX) / (
                            np.linalg.norm(vectorAB) * np.linalg.norm(material_sys_vectorX))

                # Calculate angle in radians
                angle_beta = np.arccos(np.clip(cos_angle_beta, -1.0, 1.0))
                relative_orientation[(LC.ID,LC.ActiveN2PIncrement.ID)].append(angle_beta)

        self.__relative_orientation = relative_orientation
        self.__strains = strains_dict

        # Calculate previous steps
        self.__calculate_equivalent_mechanical_load()

        self.__calculate_equivalent_thermal_loads()

        self.__calculate_layer_mechanical_stresses()

        self.__calculate_layer_thermal_stresses()

        self.__hdf5.create_hdf5()



        # Initialize RF array
        self.__RF = {}
        for LC in self.__load_cases:
            self.__RF[(LC.ID,LC.ActiveN2PIncrement.ID)] = []
            for global_index, (elem_mech, elem_thermal, edge) in enumerate(zip(self.__mechanical_layer_stresses[(LC.ID,LC.ActiveN2PIncrement.ID)],
                                                                                    self.__thermal_layer_stresses[(LC.ID,LC.ActiveN2PIncrement.ID)],
                                                                                    self.__edges)):
                # Since calculations are performed at interfaces between layers, the array size must be one unit smaller
                # than the number of layers, so the last element is removed.
                elem_mech.pop()
                elem_thermal.pop()

                edge_elem = edge[0]
                elem_prop = self.__edge_props[edge_elem]
                # Iterate on each interface
                self.__RF[(LC.ID,LC.ActiveN2PIncrement.ID)].append([])
                for index, (mech_stress, thermal_stress, mat_ply, thick_ply, theta_ply) in enumerate(zip(elem_mech, elem_thermal, elem_prop._mat_IDs, elem_prop._thicknesses, elem_prop._theta)):
                    tau_xzF = self.Materials[mat_ply].Allowables.ShearXZ
                    tau_yzF = self.Materials[mat_ply].Allowables.ShearYZ
                    sigma_zFt = self.Materials[mat_ply].Allowables.ZTensile
                    sigma_zFc = self.Materials[mat_ply].Allowables.ZCompressive
                    sigma_zA = mech_stress[0]
                    sigma_zTA = thermal_stress[0]
                    tau_xzA = mech_stress[1]
                    tau_xzTA = thermal_stress[1]
                    tau_yzA = mech_stress[2]
                    tau_yzTA = thermal_stress[2]

                    # Mechanical case
                    if self.__failure_criteria == 'MI':
                        def equation1(RF):
                            return (((RF * tau_xzA + tau_xzTA) / tau_xzF) ** 2) + (
                                        ((RF * tau_yzA + tau_yzTA) / tau_yzF) ** 2) + (
                                    ((RF * sigma_zA + sigma_zTA) / sigma_zFt) ** 2) - 1

                        def equation2(RF):
                            return (((RF * tau_xzA + tau_xzTA) / tau_xzF) ** 2) + (
                                        ((RF * tau_yzA + tau_yzTA) / tau_yzF) ** 2) + (
                                    ((RF * sigma_zA + sigma_zTA) / sigma_zFc) ** 2) - 1

                        RF1 = float(f_solve(equation1, -50))
                        RF2 = float(f_solve(equation1, 50))
                        RF3 = float(f_solve(equation2, -50))
                        RF4 = float(f_solve(equation2, 50))
                        RF_array = []

                        if RF1 * (sigma_zA + sigma_zTA) >= 0:
                            RF_array.append(RF1)

                        if RF2 * (sigma_zA + sigma_zTA) >= 0:
                            if abs(RF1 - RF2) > 1e-6:
                                RF_array.append(RF2)

                        if RF3 * (sigma_zA + sigma_zTA) <= 0:
                            RF_array.append(RF3)

                        if RF4 * (sigma_zA + sigma_zTA) <= 0:
                            if abs(RF3 - RF4) > 1e-6:
                                RF_array.append(RF4)

                        if len(RF_array) < 2:
                            RF_array.append(-RF_array[0])



                    # Thermal case
                    elif self.__failure_criteria == 'TI':
                        def equation1(RF):
                            return (((tau_xzA + RF * tau_xzTA) / tau_xzF) ** 2) + (
                                        ((tau_yzA + RF * tau_yzTA) / tau_yzF) ** 2) + (
                                    ((sigma_zA + RF * sigma_zTA) / sigma_zFt) ** 2) - 1

                        def equation2(RF):
                            return (((tau_xzA + RF * tau_xzTA) / tau_xzF) ** 2) + (
                                        ((tau_yzA + RF * tau_yzTA) / tau_yzF) ** 2) + (
                                    ((sigma_zA + RF * sigma_zTA) / sigma_zFc) ** 2) - 1

                        RF1 = float(f_solve(equation1, -50))
                        RF2 = float(f_solve(equation1, 50))
                        RF3 = float(f_solve(equation2, -50))
                        RF4 = float(f_solve(equation2, 50))
                        RF_array = []
                        if (sigma_zA + RF1 * sigma_zTA) >= 0:
                            RF_array.append(RF1)

                        if (sigma_zA + RF2 * sigma_zTA) >= 0:
                            if abs(RF1 - RF2) > 1e-6:
                                RF_array.append(RF2)

                        if (sigma_zA + RF3 * sigma_zTA) <= 0:
                            RF_array.append(RF3)

                        if (sigma_zA + RF4 * sigma_zTA) <= 0:
                            if abs(RF3 - RF4) > 1e-6:
                                RF_array.append(RF4)

                        if len(RF_array) < 2:
                            RF_array.append(-RF_array[0])



                    # Combined case
                    elif self.__failure_criteria == 'CI':
                        def equation1(RF):
                            return ((RF * (tau_xzA + tau_xzTA) / tau_xzF) ** 2) + (
                                        (RF * (tau_yzA + tau_yzTA) / tau_yzF) ** 2) + (
                                    (RF * (sigma_zA + sigma_zTA) / sigma_zFt) ** 2) - 1

                        def equation2(RF):
                            return ((RF * (tau_xzA + tau_xzTA) / tau_xzF) ** 2) + (
                                        (RF * (tau_yzA + tau_yzTA) / tau_yzF) ** 2) + (
                                    (RF * (sigma_zA + sigma_zTA) / sigma_zFc) ** 2) - 1

                        RF1 = float(f_solve(equation1, -50))
                        RF2 = float(f_solve(equation1, 50))
                        RF3 = float(f_solve(equation2, -50))
                        RF4 = float(f_solve(equation2, 50))
                        RF_array = []
                        if RF1 * (sigma_zA + sigma_zTA) >= 0:
                            RF_array.append(RF1)

                        if RF2 * (sigma_zA + sigma_zTA) >= 0:
                            if abs(RF1 - RF2) > 1e-6:
                                RF_array.append(RF2)

                        if RF3 * (sigma_zA + sigma_zTA) <= 0:
                            RF_array.append(RF3)

                        if RF4 * (sigma_zA + sigma_zTA) <= 0:
                            if abs(RF3 - RF4) > 1e-6:
                                RF_array.append(RF4)

                        if len(RF_array) < 2:
                            RF_array.append(-RF_array[0])


                    RF_array = tuple([min(abs(rf),50) for rf in RF_array])
                    self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)][global_index].append(RF_array)




        dataEntryList = []
        for LC in self.__load_cases:
            for index_layer in range(MAXLAYERS):
                matrix = []
                for index, edge in enumerate(self.__edges):
                    # When all layers with results are appended to the export matrix, don't write more datasets
                    if index_layer < len(self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)][index]):
                        element = edge[0]
                        RF_c = self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)][index][index_layer][0]
                        RF_t = self.__RF[(LC.ID, LC.ActiveN2PIncrement.ID)][index][index_layer][1]
                        sigma_zM = self.__mechanical_layer_stresses[(LC.ID, LC.ActiveN2PIncrement.ID)][index][index_layer][0]
                        tau_xzM = self.__mechanical_layer_stresses[(LC.ID, LC.ActiveN2PIncrement.ID)][index][index_layer][1]
                        tau_yzM = self.__mechanical_layer_stresses[(LC.ID, LC.ActiveN2PIncrement.ID)][index][index_layer][2]
                        sigma_zT = self.__thermal_layer_stresses[(LC.ID, LC.ActiveN2PIncrement.ID)][index][index_layer][0]
                        tau_xzT = self.__thermal_layer_stresses[(LC.ID, LC.ActiveN2PIncrement.ID)][index][index_layer][1]
                        tau_yzT = self.__thermal_layer_stresses[(LC.ID, LC.ActiveN2PIncrement.ID)][index][index_layer][2]
                        matrix_row = [element.ID, RF_c, RF_t, sigma_zM, tau_xzM, tau_yzM, sigma_zT, tau_xzT, tau_yzT]
                        matrix.append(matrix_row)

                unique_rows = {}

                for row in matrix:
                    id_ = row[0]
                    value = min(abs(row[1]), abs(row[2]))  # El menor valor absoluto entre las columnas 2 y 3

                    # Si el ID no está en el diccionario o el valor actual es más cercano a 0, actualiza
                    if id_ not in unique_rows or value < unique_rows[id_][1]:
                        unique_rows[id_] = (row, value)

                # Extraer las filas únicas del diccionario
                filtered_matrix = [entry[0] for entry in unique_rows.values()]

                # Crear el dtype para el array estructurado
                components_dtype = np.dtype([
                    ("ID ENTITY", "i4"),
                    ("RF_c", "f4"),
                    ("RF_t", "f4"),
                    ("sigma_zM", "f4"),
                    ("tau_xzM", "f4"),
                    ("tau_yzM", "f4"),
                    ("sigma_zT", "f4"),
                    ("tau_xzT", "f4"),
                    ("tau_yzT", "f4")
                ])

                # Convertir cada fila en una tupla para asegurar compatibilidad
                filtered_matrix_tuples = [tuple(row) for row in filtered_matrix]

                # Crear el array estructurado
                array = np.array(filtered_matrix_tuples, dtype=components_dtype)

                if len(array) > 0:
                    myDataEntry = DataEntry()
                    myDataEntry.LoadCase = LC.ID
                    myDataEntry.LoadCaseName = LC.Name
                    myDataEntry.Increment = LC.ActiveN2PIncrement.ID
                    myDataEntry.Data = array
                    myDataEntry.Section = f'Interlayer {index_layer+1}-{index_layer+2}'
                    myDataEntry.ResultsName = "EDGE DELAMINATION FAILURE"
                    myDataEntry.Part = "(0,'0')"
                    dataEntryList.append(myDataEntry)

        self.__hdf5.write_dataset(dataEntryList)

        # Record input data
        inputList = []

        data_int_distance = np.array([(element.ID, value) for element, value in self.__int_distance.items()],dtype=[("Element ID", "i4"), ("IntDistance", "f8")])
        inputDistance = DataEntry()
        inputDistance.DataInput = data_int_distance
        inputDistance.DataInputName = "IntDistance"

        data_ref_temp = np.array([(LC.ID, LC.RefTemp) for LC in self.__load_cases], dtype=[("Load Case ID", "i4"), ("RefTemperature", "f8")])
        inputTemperature = DataEntry()
        inputTemperature.DataInput = data_int_distance
        inputTemperature.DataInputName = "RefTemperature"

        inputFailureCriteria = DataEntry()
        inputFailureCriteria.DataInput = self.__failure_criteria
        inputFailureCriteria.DataInputName = "FailureCriteria"

        inputModelPath = DataEntry()
        inputModelPath.DataInput = self.__model.FilePath
        inputModelPath.DataInputName = "Model"

        data_material = np.array([(str(material.ID), material.YoungX, material.YoungY, material.YoungZ,
                                   material.ShearXY, material.ShearXZ, material.ShearYZ, material.PoissonXY,
                                   material.PoissonXZ, material.PoissonYZ, material.TExpX, material.TExpY,
                                   material.Allowables.Shear,material.Allowables.ShearXZ,
                                   material.Allowables.ShearYZ, material.Allowables.XCompressive,
                                   material.Allowables.XTensile, material.Allowables.YCompressive,
                                   material.Allowables.YTensile, material.Allowables.ZCompressive,
                                   material.Allowables.ZTensile) for material in self.__materials.values()],
                                 dtype=[("MaterialID","|S5"),("YoungX","f4"),("YoungY","f4"),("YoungZ","f4"),
                                        ("ShearXY","f4"),("ShearXZ","f4"),("ShearYZ","f4"),("PoissonXY","f4"),
                                        ("PoissonXZ","f4"),("PoissonYZ","f4"),("TExpX","f4"),("TExpY","f4"),
                                        ("ShearXY(allow)","f4"),("ShearXZ(allow)","f4"),("ShearYZ(allow)","f4"),
                                        ("Xc","f4"),("Xt","f4"),("Yc","f4"),("Yt","f4"),("Zc","f4"),("Zt","f4")])

        inputMaterial = DataEntry()
        inputMaterial.DataInput = data_material
        inputMaterial.DataInputName = "Material"


        inputList.append(inputDistance)
        inputList.append(inputTemperature)
        inputList.append(inputFailureCriteria)
        inputList.append(inputModelPath)
        inputList.append(inputMaterial)

        self.__hdf5._modules_input_data(inputList)



