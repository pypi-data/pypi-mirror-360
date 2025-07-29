"""Script for the Failure Analysis on Composite FEM Models."""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info


import NaxToPy as n2p
import numpy as np
from NaxToPy.Core.Classes.N2PProperty import N2PProperty
from NaxToPy.Core.Classes.N2PMaterial import N2PMaterial
from NaxToPy.Core.N2PModelContent import N2PModelContent
from NaxToPy.Core.Classes.N2PLoadCase import N2PLoadCase
from NaxToPy.Core.Classes.N2PComponent import N2PComponent
from NaxToPy.Core.Classes.N2PResult import N2PResult
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Modules.common.property import *
from NaxToPy.Modules.common.material import *
from NaxToPy.Modules.common.model_processor import *
from NaxToPy.Modules.common.data_input_hdf5 import *
from NaxToPy.Modules.common.hdf5 import *

import time


class N2PCompositeFailure:
    """
    Class for evaluating structural failure on composites materials.

    Example:
        >>> import NaxToPy as n2p
        >>> from NaxToPy.Modules.static.composite import N2PCompositeFailure

        >>> model = n2p.load_model(r".\model.op2")
        >>> list_elements = model.get_elements_filtered(properties=[11100004, 11100007]) # filter elements
        >>> list_elements = [e for e in model.get_elements()] # to extract all elements
        >>> list_lcs = [model.get_load_case(4001001)] # filter load cases
        >>> list_lcs = [model.get_load_case()] # to extract all load cases

        >>> my_analysis = N2PCompositeFailure()
        >>> my_analysis.Model = model
        >>> my_analysis.Elements = list_elements
        >>> my_analysis.LoadCases = list_lcs
        >>> my_analysis.FailureTheory = "TsaiWu"
        >>> my_analysis.Materials[(3,"0")].Allowables.XTensile = 10
        >>> my_analysis.Materials[(3,"0")].Allowables.XCompressive = 10
        >>> my_analysis.Materials[(3,"0")].Allowables.YTensile = 10
        >>> my_analysis.Materials[(3,"0")].Allowables.YCompressive = 10
        >>> my_analysis.Materials[(3,"0")].Allowables.Shear = 10
        >>> my_analysis.HDF5.FilePath= r".\Analysis.h5"
        >>> my_analysis.calculate()
    """

    # __slots__ = ("_model", "_element_list", "_LCs", "_failure_criterion", "_hdf5", "_materials", "_properties", "_properties_elem", "_criteria_dict","mechanical_prop_dict", "Analysis_Results",
                 
    #              )

    def __init__(self):
        """
        Initialize the class
        """
        # Mandatory attributes [User Input] ------------------------------------------------------------------------------------
        self._model: N2PModelContent = None
        self._element_list: list[N2PElement] = []
        self._LCs: list[N2PLoadCase] = None
        self._failure_criterion: str = None
        self._failure_theory: str = None
        self._m : float = None


        self._hdf5 = HDF5_NaxTo()
        self._materials: dict = None
        self._properties: dict = None
        self._properties_elem: dict = None

        self._criteria_dict = {
            "FirstPly" : " Laminate fails when first ply fails",
            "PlyByPly" : "Laminate fails when every ply fails" 
        }

        self._failureTheory_dict = {
            "TsaiWu" : "Tsai-Wu failure criterion",
            "MaxStress" : "Maximum Stress failure criterion",
            "TsaiHill": "Tsai-Hill failure criterion",
            "Hashin": "Hashin failure criterion",
            "Puck": "Puck failure criterion",
            "FMC": "Fiber Mode Concept",
        }

        self._initialize_analysis()
        

    def _initialize_analysis(self):
        """
        Method to initialize data transformation from user input to a ModelProcessor instance.

        """
        pass

    
    # Getters ------------------------------------------------------------------------------------------------------------------
    # Method to obtain the model -----------------------------------------------------------------------------------------------
    @property
    def Model(self) -> N2PModelContent:
        """ 
        N2PModelContent object to be analyzed.
        """
        return self._model
    # ----------------------------------------------------------------------------------------------------------------------

    # Method to obtain the List of elements which is going to be analyzed ------------------------------------------------------
    @property
    def Elements(self) -> list[N2PElement]:
        """
        List of N2PElements instances where analysis will be performed.
        """
        return self._element_list
    # --------------------------------------------------------------------------------------------------------------------------

    # Method to obtain the List of LoadCases which is going to be analyzed -----------------------------------------------------
    @property
    def LoadCases(self) -> list[N2PLoadCase]:
        """
        List of N2PLoadCase instances where analysis will be performed.
        """
        return self._LCs
    # --------------------------------------------------------------------------------------------------------------------------

    # Method to obtain the List of elements which is going to be analyzed ------------------------------------------------------
    @property
    def FailureCriteria(self) -> list[N2PElement]:
        """
        Property that returns the list of elements, that is, the list of elements to be analyzed.
        """
        return self._failure_criterion
    # --------------------------------------------------------------------------------------------------------------------------

        # Method to obtain the List of elements which is going to be analyzed ------------------------------------------------------
    @property
    def FailureTheory(self) -> list[N2PElement]:
        """
        Property that returns the list of elements, that is, the list of elements to be analyzed.
        """
        return self._failure_theory
    # --------------------------------------------------------------------------------------------------------------------------
    
    #Method to obtain the path where results files will be exported ------------------------------------------------------------
    @property
    def HDF5(self) -> HDF5_NaxTo:
        """
        Property that returns the path where ResultsFile will be exported.
        """

        return self._hdf5
    
    #Method to obtain material instances and their elements --------------------------------------------------------------------
    @property
    def Materials(self) -> dict:
        """
        Property that returns a dictionary with Material Instances.
        """
        return self._materials
    
    #Method to obtain property instances and their elements --------------------------------------------------------------------
    @property
    def Properties(self) -> dict:
        """
        Property that returns a dictionary with Property Instances.
        """
        return self._properties
    
    @property
    def m(self) -> float:
        """
        Property that returns the mass of the element.
        """
        return self._m

    # Setters ------------------------------------------------------------------------------------------------------------------
    @Model.setter
    def Model(self, value: N2PModelContent) -> None:
        
        if isinstance(value, N2PModelContent):
            self._model = value
        else: 
            msg = N2PLog.Error.E800()
            raise TypeError(msg)
        

    # --------------------------------------------------------------------------------------------------------------------------

    @Elements.setter
    def Elements(self, value: list[N2PElement]) -> None:

        if all(isinstance(element, N2PElement) for element in value):
            self._element_list = value

            filtered_elements = [element for element in self._element_list if self._model.PropertyDict[element.Prop].PropertyType in ('PCOMP', 'CompositeShellSection')]
            if len(self._element_list) > len(filtered_elements):
                N2PLog.Warning.W800()
            
            self._element_list = filtered_elements

            _, _, self._materials, _ = elem_to_material(self.Model, self._element_list)
            self._properties, self._properties_elem = get_properties(self.Model, self._element_list)
        else:
            msg = N2PLog.Error.E801()
            raise TypeError(msg)

    # --------------------------------------------------------------------------------------------------------------------------

    @LoadCases.setter
    def LoadCases(self, value: list[N2PLoadCase]) -> None:
        if all(isinstance(loadcase, N2PLoadCase) for loadcase in value):
            self._LCs = value
        else:
            msg = N2PLog.Error.E802()
            raise TypeError(msg)
    # --------------------------------------------------------------------------------------------------------------------------

    @FailureCriteria.setter
    def FailureCriteria(self, value: str) -> None:
        if value not in self._criteria_dict:
            msg = N2PLog.Error.E803(value, self._criteria_dict)
            raise TypeError(msg)

        self._failure_criterion = value

    # --------------------------------------------------------------------------------------------------------------------------
    
    @FailureTheory.setter
    def FailureTheory(self, value: str) -> None:
        if value not in self._failureTheory_dict:
            msg = N2PLog.Error.E803(value, self._failureTheory_dict)
            raise TypeError(msg)

        self._failure_theory = value

    # --------------------------------------------------------------------------------------------------------------------------

    @m.setter
    def m(self, value: float) -> None:
        if isinstance(value, float):
            self._m = value
        else:
            msg = N2PLog.Error.E804()
            raise TypeError(msg)
    # --------------------------------------------------------------------------------------------------------------------------

    def mechanical_prop(self):
        """
        This method relates a N2PElement instace to its mechanical properties with regard to the N2PProperty and N2PMaterial
        instances assigned to the element.

        Use of this dictionary is destined to ease the way different calculus methods access the information required to perform
        the computation.  

        Each element will have a list for its different properties, which length will be the 
        number of plies for the laminate.

        Note:
            - **1:** longitudinal direction (fiber-wise)
            - **2:** transverse direction (fiber-wise)

        Note:
            - :class:`"E1"` Young modulus in the longitudinal direction (fiber-wise)
            - :class:`"E2"` Young modulus in the transverse direcetion (fiber-wise)
            - :class:`"G"` Shear modulus
            - :class:`"Nu12"` Major Poisson ratio
            - :class:`"Nu21"` Minor Poisson ratio
            - :class:`"Xt"` Tensile Strength on longitudinal direction (fiber-wise)
            - :class:`"Xc"` Compressive Strength on longitudinal direction (fiber-wise)
            - :class:`"Yt"` Tensile Strength on trasnverse direction (fiber-wise)
            - :class:`"Yc"` Compressive Strength on transverse direction (fiber-wise)
            - :class:`"S"` Shear Strength on the 1-2 plane (fiber-wise)
            - :class:`"theta"` angle of ply orientation (fiber-wise) with regard to longitudinal direction (element-wise)

        Returns:
            dict: A dictionary is created to store all the mechanical properties of an orthotropic material assigned to an element.

        Example:
            >>> # Executing the method of a N2PCompositeFailure instance
            >>> mechanical_prop_dict = my_analysis.mechanical_prop()

            >>> # The dictionary would look like this: 
            >>> mechanical_prop_dict = {
            >>>     N2PElement(3204463, 'PartID'): {
            >>>         'E1': [220000, 220000, 220000 ], 'E2': [124300, 124300, 124300],
            >>>         'G': [75000, 75000, 75000 ],'Nu12': [0.35, 0.35, 0.35], 
            >>>         'Nu21': [0.16, 0.16, 0.16], 'Xt': [1200000, 1200000, 1200000],
            >>>         'Yt': [80000, 80000, 80000], 'Xc': [90000, 90000, 90000], 
            >>>         'Yc': [25000, 25000, 25000], 'S': [15000, 15000, 15000], 
            >>>         'theta': [0.0, 0.0, 0.0]
            >>>     },
            >>> 
            >>>     N2PElement(3204464, 'PartID'): {
            >>>         'E1': [220000, 220000, 220000], 'E2': [124300, 124300, 124300], 
            >>>         'G': [75000, 75000, 75000],'Nu12': [0.35, 0.35, 0.35], 
            >>>         'Nu21': [0.16, 0.16, 0.16], 'Xt': [1200000, 1200000, 1200000],
            >>>         'Yt': [80000, 80000, 80000], 'Xc': [90000, 90000, 90000 ], 
            >>>         'Yc': [25000, 25000, 25000], 'S': [15000, 15000, 15000], 
            >>>         'theta': [0.0, 0.0, 0.0]
            >>>     },
            >>> 
            >>>     N2PElement(..., 'PartID'): {
            >>>         ...
            >>>     },
            >>>     
            >>>     ...
            >>> }

        """
        
        # Construction of mechanical_prop: dict using ModelProcessor instances------------------------------------------------
        
        self.mechanical_prop_dict = {}
        for element, property in self._properties_elem.items():
            E1 = []
            E2 = []
            G = []
            Nu12 = []
            Nu21 = []
            theta = []
            # thickness = [] - it will be used in the future for the ply-by-ply evaluation criterion

            self.mechanical_prop_dict[element] = {"E1":E1, "E2":E2, "G":G, "Nu12": Nu12, "Nu21":Nu21,"theta":theta }
            
            for lamina in property.laminae:                
                E1.append(lamina.Ex)
                E2.append(lamina.Ey)
                G.append(1)
                Nu12.append(lamina.Nuxy)
                Nu21.append((lamina.Ey/lamina.Ex)*lamina.Nuxy)
                theta.append(lamina.theta)

        return self.mechanical_prop_dict
    
    # @profile
    def calculate(self):
        """
        Select and performs the failure criterion calculation based on the user-specified type.
        """

        for material_id, material in self.Materials.items():
            if not all([
                hasattr(material.Allowables, "XTensile") and material.Allowables.XTensile is not None,
                hasattr(material.Allowables, "XCompressive") and material.Allowables.XCompressive is not None,
                hasattr(material.Allowables, "YTensile") and material.Allowables.YTensile is not None,
                hasattr(material.Allowables, "YCompressive") and material.Allowables.YCompressive is not None

            ]):
                if self._failure_criterion == 'Puck':
                    if not all([hasattr(material.Allowables, "InterlaminarShear") and material.Allowables.InterlaminarShear is not None]):
                        msg = N2PLog.Error.E804()
                        raise TypeError(msg)
                msg = N2PLog.Error.E804()
                raise TypeError(msg)
            
        # Allowables Initialization ------------------------------------------------------------------------------------


        self.allowables_prop = {property.ID: {} for property in self._properties.values()}

        for prop_ID, property in self._properties.items():
            self.allowables_prop[prop_ID] = {
                "Xt": [self.Materials[l.mat_ID].Allowables.XTensile for l in property.Laminate],
                "Xc": [self.Materials[l.mat_ID].Allowables.XCompressive for l in property.Laminate],
                "Yt": [self.Materials[l.mat_ID].Allowables.YTensile for l in property.Laminate],
                "Yc": [self.Materials[l.mat_ID].Allowables.YCompressive for l in property.Laminate],
                "S":  [self.Materials[l.mat_ID].Allowables.Shear for l in property.Laminate]

            }

        self.allowables_elem = {n2p_element: {} for n2p_element in self._element_list}

        for element, property in self._properties_elem.items():
            self.allowables_elem[element] = self.allowables_prop[property.ID]

        self._initialize_analysis()

        self.Analysis_Results = {lc:{"Initial_Results":{}, "Failure_Results":{}, "Order_Results": {}} for lc in self.LoadCases}

        # First Ply Failure computation -----------------------------------------------------------------------------------------

        start_time = time.time()

        for LC in self.LoadCases:
            # print(LC.ID)
            i = 0
            if self._failure_criterion == 'FirstPly':

                if self._failure_theory == 'TsaiWu':
                    
                    self.coefficients_TsaiWu_prop = {prop_ID: {} for prop_ID in self.allowables_prop}

                    for prop_ID, allowables in self.allowables_prop.items():
                        Xt, Xc = np.array(allowables["Xt"]), np.array(allowables["Xc"])
                        Yt, Yc = np.array(allowables["Yt"]), np.array(allowables["Yc"])
                        S = np.array(allowables["S"])

                        # Compute Tsai-Wu coefficients using NumPy
                        F1 = 1 / Xt - 1 / Xc
                        F2 = 1 / Yt - 1 / Yc
                        F11 = 1 / (Xt * Xc)
                        F22 = 1 / (Yt * Yc)
                        F66 = 1 / (S ** 2)
                        F12 = -0.5 * np.sqrt(F11 * F22)

                        # Store computed coefficients in the dictionary
                        self.coefficients_TsaiWu_prop[prop_ID] = {
                            "F1": F1, "F2": F2,
                            "F11": F11, "F22": F22, "F66": F66,
                            "F12": F12
                        }


                    self.coefficients_TsaiWu_elem = {n2p_element: {} for n2p_element in self._element_list}

                    for element, property in self._properties_elem.items():
                        self.coefficients_TsaiWu_elem[element] = self.coefficients_TsaiWu_prop[property.ID]

                    self.Analysis_Results[LC]["Initial_Results"], self.Analysis_Results[LC]["Failure_Results"], self.Analysis_Results[LC]["Order_Results"]  = self._calculate_TsaiWu(LC, i)
                elif self._failure_theory == 'MaxStress':
                    self.Analysis_Results[LC]["Initial_Results"], self.Analysis_Results[LC]["Failure_Results"], self.Analysis_Results[LC]["Order_Results"] = self._calculate_Max_Stress(LC, i)
                elif self._failure_theory == 'TsaiHill':
                    self.Analysis_Results[LC]["Initial_Results"], self.Analysis_Results[LC]["Failure_Results"], self.Analysis_Results[LC]["Order_Results"] = self._calculate_Tsai_Hill(LC, i)
                elif self._failure_theory == 'Hashin':
                    self.Analysis_Results[LC]["Initial_Results"], self.Analysis_Results[LC]["Failure_Results"], self.Analysis_Results[LC]["Order_Results"] = self._calculate_Hashin(LC, i)
                elif self._failure_theory == 'Puck':
                    self.Analysis_Results[LC]["Initial_Results"], self.Analysis_Results[LC]["Failure_Results"], self.Analysis_Results[LC]["Order_Results"] = self._calculate_Puck(LC, i)
                elif self._failure_theory == 'FMC':
                    self.Analysis_Results[LC]["Initial_Results"], self.Analysis_Results[LC]["Failure_Results"], self.Analysis_Results[LC]["Order_Results"] = self._calculate_FMC(LC, i)

                elif self._failure_theory == 'All':
                    return self._calculate_Max_Stress(), self._calculate_TsaiWu(), self._calculate_Tsai_Hill(), self._calculate_Hashin(), self._calculate_Puck()
                else: 
                    raise ValueError(f"Unsupported failure theory: {self._failure_theory}")
            
        # Ply by ply Failure computation -----------------------------------------------------------------------------------------
            elif self._failure_criterion == 'PlyByPly':

                if self._failure_theory == 'TsaiWu':

                    self.coefficients_TsaiWu_prop = {prop_ID: {} for prop_ID in self.allowables_prop}

                    for prop_ID, allowables in self.allowables_prop.items():
                        Xt, Xc = np.array(allowables["Xt"]), np.array(allowables["Xc"])
                        Yt, Yc = np.array(allowables["Yt"]), np.array(allowables["Yc"])
                        S = np.array(allowables["S"])

                        # Compute Tsai-Wu coefficients using NumPy
                        F1 = 1 / Xt - 1 / Xc
                        F2 = 1 / Yt - 1 / Yc
                        F11 = 1 / (Xt * Xc)
                        F22 = 1 / (Yt * Yc)
                        F66 = 1 / (S ** 2)
                        F12 = -0.5 * np.sqrt(F11 * F22)

                        # Store computed coefficients in the dictionary
                        self.coefficients_TsaiWu_prop[prop_ID] = {
                            "F1": F1, "F2": F2,
                            "F11": F11, "F22": F22, "F66": F66,
                            "F12": F12
                        }


                    self.coefficients_TsaiWu_elem = {n2p_element: {} for n2p_element in self._element_list}

                    for element, property in self._properties_elem.items():
                        self.coefficients_TsaiWu_elem[element] = self.coefficients_TsaiWu_prop[property.ID]


                    self.Analysis_Results[LC]['Initial_Results'],_,_ = self._calculate_TsaiWu(LC, i)

                    start_time = time.time()
                    _, self.Analysis_Results[LC]['Initial_Results'], self.Analysis_Results[LC]['Failure_Results'], self.Analysis_Results[LC]['Order_Results'] = self.ply_by_ply_failure(LC)
                    end_time = time.time()

                    # print(f"Execution time: {end_time - start_time:.6f} seconds")

                elif self._failure_theory == 'MaxStress':
                    self.Analysis_Results[LC]['Initial_Results'],_,_ = self._calculate_Max_Stress(LC, i)
                    _, self.Analysis_Results[LC]['Initial_Results'], self.Analysis_Results[LC]['Failure_Results'], self.Analysis_Results[LC]['Order_Results'] = self.ply_by_ply_failure(LC)
                elif self._failure_theory == 'TsaiHill':
                    self.Analysis_Results[LC]['Initial_Results'],_,_ = self._calculate_Tsai_Hill(LC, i)
                    _, self.Analysis_Results[LC]['Initial_Results'], self.Analysis_Results[LC]['Failure_Results'], self.Analysis_Results[LC]['Order_Results'] = self.ply_by_ply_failure(LC)
                elif self._failure_theory == 'FMC':
                    self.Analysis_Results[LC]['Initial_Results'],_,_ = self._calculate_FMC(LC, i)
                    _, self.Analysis_Results[LC]['Initial_Results'], self.Analysis_Results[LC]['Failure_Results'], self.Analysis_Results[LC]['Order_Results'] = self.ply_by_ply_failure(LC)
                
                elif self._failure_theory == 'Hashin' or self._failure_theory == 'Puck':

                    raise ValueError(f"Unsupported failure theory for Ply By Ply method: {self._failure_theory}")
                
                    # self.Analysis_Results[LC]['Initial_Results'] = self._calculate_Hashin(LC, i)
                    # _, self.Analysis_Results[LC]['Initial_Results'], self.Analysis_Results[LC]['Failure_Results'], self.Analysis_Results[LC]['Order_Results'] = self.ply_by_ply_failure(LC)

                # elif self._failure_theory == 'Puck':
                #     self.Analysis_Results = self._calculate_Puck()

                elif self._failure_theory == 'All':
                    return self._calculate_Max_Stress(), self._calculate_TsaiWu(), self._calculate_Tsai_Hill(), self._calculate_Hashin(), self._calculate_Puck()
                else: 
                    raise ValueError(f"Unsupported failure theory: {self._failure_theory}")
            
            else:
                raise ValueError(f"Unsupported failure criterion: {self._failure_criterion}")
        return self._transform_results(self.LoadCases)
            
# -------------------------------------------- CRITERION DEFINITION -----------------------------------------------------------
   
# TSAI-WU----------------------------------------------------------------------------------------------------------------------     
    # @profile     
    def _calculate_TsaiWu(self, LC, i):
        """
        Method to Implement the Tsai-Wu Failure Criterion.

        This method evaluates failure modes (fiber failure) for 
        composite laminates under combined loading conditions.
        
        Returns:
            dict: Dictionary with N2PElement instances as keys and FI - i.e Failure Index: lists as values. 

        If FI > 1 then consider material failure in the corresponding element.

        """

        # Stresses & Forces Import --------------------------------------------------------------------------------
        if i == 0:
            self.Forces_element = self._extract_forces(LC)

            # Initialize storage arrays
            self._elements_IDs = list(self.Forces_element.keys())  # Extract element IDs
            self._n_elements = len(self._element_list)

            # Extract properties
            self.original_list_composite_shells = [self._properties_elem[element] for element in self._elements_IDs]
            self._array_thicknesses = np.array([shell._thicknesses for shell in self.original_list_composite_shells], dtype=object)  # Variable length
            self._array_num_plies = np.array([shell._num_plies for shell in self.original_list_composite_shells])

            # Convert Forces_element dict to NumPy array
            self._NM = np.array([np.nan_to_num(self.Forces_element[element], nan=0) for element in self._elements_IDs])

            # Compute z_positions for all elements
            self._Z_positions = [
                -sum(t) / 2 + np.cumsum(t) - (np.array(t) / 2) for t in self._array_thicknesses
            ]  # List of arrays
        else:
            pass

        self._list_composite_shells = list(self._properties_elem.values())    
    
        self.sigma1_element, self.sigma2_element, self.sigma12_element = self._transform_forces_to_stresses()

        # Initialize Result Storage -------------------------------------------------------------------------------------
        self.TsaiWuResults = {n2p_element: [] for n2p_element in self._element_list}
        Failure_Results = {n2p_element: () for n2p_element in self._element_list}
        Order_Results = {n2p_element: [] for n2p_element in self._element_list}

        # Computation ---------------------------------------------------------------------------------------------------
        for n2p_element, coeffs in self.coefficients_TsaiWu_elem.items():

            # Initialize RF storage
            RF_values = np.full(len(coeffs["F1"]), np.nan)

            # Get stresses
            sigma1 = np.array(self.sigma1_element[n2p_element], dtype=np.float64)
            sigma2 = np.array(self.sigma2_element[n2p_element], dtype=np.float64)
            sigma12 = np.array(self.sigma12_element[n2p_element], dtype=np.float64)


            # Identify valid (non-zero, non-NaN) stress cases
            valid = ~(np.isnan(sigma1) | np.isnan(sigma2) | np.isnan(sigma12)) & \
                    ~((sigma1 == 0) & (sigma2 == 0) & (sigma12 == 0))

            # Compute RF values for valid indices
            if np.any(valid):
                Q = coeffs["F11"] * sigma1**2 + 2 *coeffs["F12"] * sigma1 * sigma2 + coeffs["F22"] * sigma2**2 + coeffs["F66"] * sigma12**2
                L = coeffs["F1"] * sigma1 + coeffs["F2"] * sigma2

                RF_values[valid] = np.sqrt((L[valid]**2 + 4 * Q[valid]) - L[valid]) / (2 * Q[valid])

            # Store RF per element
            self.TsaiWuResults[n2p_element] = RF_values.tolist()

            # Determine minimum RF and its corresponding ply
            min_id = np.nanargmin(RF_values)
            min_value = RF_values[min_id]
            Failure_Results[n2p_element] = (min_value, min_id + 1)


            # # Compute failure order Assign final output tuple for each ply
            sorted_values = sorted([(v, i) for i, v in enumerate(RF_values) if v < 1], key = lambda x:x[0], reverse=False)

            index_dict = {val: order + 1 for order, (val, _) in enumerate(sorted_values)}

            result = [(v, index_dict.get(v, 0)) for v in RF_values]

            Order_Results[n2p_element] = result

        # Return results
        return self.TsaiWuResults, Failure_Results, Order_Results
        # -------------------------------------------------------------------------------------------------------------------------
    
# -----------------------------------------------------------------------------------------------------------------------------    

# MAXIMUM STRESS --------------------------------------------------------------------------------------------------------------
    # @profile 
    def _calculate_Max_Stress(self, LC, i):
        """
        Method to implement the Maximum Stress failure criterion.

        This method evaluates failure modes (fiber failure) for 
        composite laminates under combined loading conditions.
        
        Returns:
            dict: Dictionary with N2PElement instances as keys and RF: lists as values.
        """

        # Stresses importation ------------------------------------------------------------------------------------------------

        if i == 0:
            self.Forces_element = self._extract_forces(LC)

            # Initialize storage arrays
            self._elements_IDs = list(self.Forces_element.keys())  # Extract element IDs
            self._n_elements = len(self._element_list)

            # Extract properties
            self.original_list_composite_shells = [self._properties_elem[element] for element in self._elements_IDs]
            self._array_thicknesses = np.array([shell._thicknesses for shell in self.original_list_composite_shells], dtype=object)  # Variable length
            self._array_num_plies = np.array([shell._num_plies for shell in self.original_list_composite_shells])

            # Convert Forces_element dict to NumPy array
            self._NM = np.array([np.nan_to_num(self.Forces_element[element], nan=0) for element in self._elements_IDs])

            # Compute z_positions for all elements
            self._Z_positions = [
                -sum(t) / 2 + np.cumsum(t) - (np.array(t) / 2) for t in self._array_thicknesses
            ]  # List of arrays
        else:
            pass

        self._list_composite_shells = list(self._properties_elem.values())

        self.sigma1_element, self.sigma2_element, self.sigma12_element = self._transform_forces_to_stresses()

        # Results dict initialisation -----------------------------------------------------------------------------------------
        self.MaxStressResults = { n2p_element: [] for n2p_element in self._element_list}

        Failure_Results = {n2p_element: () for n2p_element in self._element_list }

        Order_Results = { n2p_element: [] for n2p_element in self._element_list}

        # Computation ---------------------------------------------------------------------------------------------------------

        for n2p_element, allowables in self.allowables_elem.items():

            Xt, Xc, Yt, Yc, S = (allowables[key] for key in ("Xt", "Xc", "Yt", "Yc", "S"))

            RF_Values = []

            for lamina in range(len(Xt)):
                sigma1 = self.sigma1_element[n2p_element][lamina]
                sigma2 = self.sigma2_element[n2p_element][lamina]
                sigma12 = self.sigma12_element[n2p_element][lamina]

                if np.isnan(sigma1) and np.isnan(sigma2) and np.isnan(sigma12):
                    RF = np.nan

                elif sigma1 == 0 and sigma2 == 0 and sigma12 == 0:
                    RF = np.nan
                else:
                    C = S[lamina]/abs(sigma12)

                    if sigma1 < 0:
                        A = Xc[lamina]/abs(sigma1)
                    else:
                        A = Xt[lamina]/sigma1
                    
                    if sigma2 < 0:
                        B = Yc[lamina]/abs(sigma2)
                    else:
                        B = Yt[lamina]/sigma2
                    
                    RF = min(A, B, C)

                RF_Values.append(RF)

            # Store RF per element --------------------------------------------------------------------------------------------

            self.MaxStressResults[n2p_element] = RF_Values

            position, min_value = min(enumerate(RF_Values), key=lambda x: x[1])
            Failure_Results[n2p_element] = (min_value, position + 1)

            sorted_values = sorted([(v, i) for i, v in enumerate(RF_Values) if v < 1], key = lambda x:x[0], reverse=False)
            index_dict = {val: order + 1 for order, (val, _) in enumerate(sorted_values)}
            result = [(v, index_dict.get(v, 0)) for v in RF_Values]
            Order_Results[n2p_element] = result

        
        return self.MaxStressResults, Failure_Results, Order_Results

# -----------------------------------------------------------------------------------------------------------------------------   

# TSAI-HILL -------------------------------------------------------------------------------------------------------------------
    # @profile
    def _calculate_Tsai_Hill(self, LC, i):
        """
        Method to implement the Tsai-Hill failure criterion.

        This method evaluates failure modes (fiber failure) for 
        composite laminates under combined loading conditions.
        
        Returns:
            dict: Dictionary with N2PElement instances as keys and RF: lists as values.
        """

        # Stresses Importation

        if i == 0:
            self.Forces_element = self._extract_forces(LC)

            # Initialize storage arrays
            self._elements_IDs = list(self.Forces_element.keys())  # Extract element IDs
            self._n_elements = len(self._element_list)

            # Extract properties
            self.original_list_composite_shells = [self._properties_elem[element] for element in self._elements_IDs]
            self._array_thicknesses = np.array([shell._thicknesses for shell in self.original_list_composite_shells], dtype=object)  # Variable length
            self._array_num_plies = np.array([shell._num_plies for shell in self.original_list_composite_shells])

            # Convert Forces_element dict to NumPy array
            self._NM = np.array([np.nan_to_num(self.Forces_element[element], nan=0) for element in self._elements_IDs])

            # Compute z_positions for all elements
            self._Z_positions = [
                -sum(t) / 2 + np.cumsum(t) - (np.array(t) / 2) for t in self._array_thicknesses
            ]  # List of arrays
        else:
            pass

        self._list_composite_shells = list(self._properties_elem.values())  

        self.sigma1_element, self.sigma2_element, self.sigma12_element = self._transform_forces_to_stresses()

        # Results dict intitialization ----------------------------------------------------------------------------------------
        self.TsaiHillResults = { n2p_element: [] for n2p_element in self._element_list}

        Failure_Results = {n2p_element: () for n2p_element in self._element_list }

        Order_Results = { n2p_element: [] for n2p_element in self._element_list}

        # Computation ---------------------------------------------------------------------------------------------------------
        for n2p_element, allowables in self.allowables_elem.items():

            Xt, Xc, Yt, Yc, S = (allowables[key] for key in ("Xt", "Xc", "Yt", "Yc", "S"))

            # Criterion evaluation per ply ------------------------------------------------------------------------------------

            RF_Values = []

            for lamina in range(len(Xt)):
                sigma1 = self.sigma1_element[n2p_element][lamina]
                sigma2 = self.sigma2_element[n2p_element][lamina]
                sigma12 = self.sigma12_element[n2p_element][lamina]

                # Tsai-Hill formula -------------------------------------------------------------------------------------------

                if np.isnan(sigma1) and np.isnan(sigma2) and np.isnan(sigma12):
                    RF = np.nan

                elif sigma1 == 0 and sigma2 == 0 and sigma12 == 0:
                    RF = np.nan
                else:
                    if sigma1 > 0:
                        term_1 = (sigma1 / Xt[lamina]) ** 2
                    else:
                        term_1 = (sigma1 / Xc[lamina]) ** 2

                    if sigma2 > 0:
                        term_2 = (sigma2 / Yt[lamina]) ** 2
                    else:
                        term_2 = (sigma2 / Yc[lamina]) ** 2

                    term_3 = (sigma12 / S[lamina]) ** 2
                    term_4 = (sigma1 * sigma2) / (Xt[lamina] * Yt[lamina])

                    a = term_1 + term_2 + term_3 - term_4
                    RF = 1/(a**0.5)

                RF_Values.append(RF)

            # Store RF per element --------------------------------------------------------------------------------------------
            self.TsaiHillResults[n2p_element] = RF_Values

            position, min_value = min(enumerate(RF_Values), key=lambda x: x[1])
            Failure_Results[n2p_element] = (min_value, position + 1)

            sorted_values = sorted([(v, i) for i, v in enumerate(RF_Values) if v < 1], key = lambda x:x[0], reverse=False)
            index_dict = {val: order + 1 for order, (val, _) in enumerate(sorted_values)}
            result = [(v, index_dict.get(v, 0)) for v in RF_Values]
            Order_Results[n2p_element] = result

        # ---------------------------------------------------------------------------------------------------------------------
        return self.TsaiHillResults, Failure_Results, Order_Results

# -----------------------------------------------------------------------------------------------------------------------------

# HASHIN ----------------------------------------------------------------------------------------------------------------------
    # @profile
    def _calculate_Hashin(self, LC, i):
        """
        Method to Implement the Hashin Failure Criterion.

        This method evaluates failure modes (fiber failure and matrix failure) for 
        composite laminates under combined loading conditions.
        
        Returns:
            dict: Dictionary with N2PElement instances as keys and RF:tuple (RF_fiber, RF_matrix) lists as values.
        """

        # Stresses importation ------------------------------------------------------------------------------------------------
        if i == 0:
            self.Forces_element = self._extract_forces(LC)

            # Initialize storage arrays
            self._elements_IDs = list(self.Forces_element.keys())  # Extract element IDs
            self._n_elements = len(self._element_list)

            # Extract properties
            self.original_list_composite_shells = [self._properties_elem[element] for element in self._elements_IDs]
            self._array_thicknesses = np.array([shell._thicknesses for shell in self.original_list_composite_shells], dtype=object)  # Variable length
            self._array_num_plies = np.array([shell._num_plies for shell in self.original_list_composite_shells])

            # Convert Forces_element dict to NumPy array
            self._NM = np.array([np.nan_to_num(self.Forces_element[element], nan=0) for element in self._elements_IDs])

            # Compute z_positions for all elements
            self._Z_positions = [
                -sum(t) / 2 + np.cumsum(t) - (np.array(t) / 2) for t in self._array_thicknesses
            ]  # List of arrays
        else:
            pass

        
        self._list_composite_shells = list(self._properties_elem.values())  

        self.sigma1_element, self.sigma2_element, self.sigma12_element = self._transform_forces_to_stresses()

        # Results dict initialization -----------------------------------------------------------------------------------------
        self.HashinResults = {n2p_element: [] for n2p_element in self._element_list}

        Failure_Results = {n2p_element: () for n2p_element in self._element_list }

        Order_Results = { n2p_element: [] for n2p_element in self._element_list}

        # Computation ---------------------------------------------------------------------------------------------------------
        for n2p_element, allowables in self.allowables_elem.items():

            Xt, Xc, Yt, Yc, S = (allowables[key] for key in ("Xt", "Xc", "Yt", "Yc", "S"))

            # Criterion Evaluation per ply ------------------------------------------------------------------------------------
            RF_values = []
            for lamina in range(len(Xt)):
                sigma1 = self.sigma1_element[n2p_element][lamina]
                sigma2 = self.sigma2_element[n2p_element][lamina]
                sigma12 = self.sigma12_element[n2p_element][lamina]

                mode = None

                # Hashin Fiber Failure ----------------------------------------------------------------------------------------
                if sigma1 == 0 and sigma2 == 0 and sigma12 == 0:
                    RF_fiber = np.nan
                    RF_matrix = np.nan
                    RF = (RF_fiber, RF_matrix)
                elif np.isnan(sigma1) and np.isnan(sigma2) and np.isnan(sigma12):
                    RF_fiber = np.nan
                    RF_matrix = np.nan
                    RF = (RF_fiber, RF_matrix)


                else:
                    if sigma1 >= 0:  # Tensile fiber failure

                        RF_fiber = (1/((sigma1 / Xt[lamina]) ** 2 + (sigma12 / S[lamina]) ** 2))**0.5
                    else:  # Compressive fiber failure
                        
                        RF_fiber = (1/((sigma1 / Xc[lamina]) ** 2))**0.5

                    # Hashin Matrix Failure ---------------------------------------------------------------------------------------
                    if sigma2 >= 0:  # Tensile matrix failure
                        
                        RF_matrix = ( 1 /
                            ((sigma2 / Yt[lamina]) ** 2
                            + (sigma12 / S[lamina]) ** 2)
                            ) ** 0.5

                    else:  # Compressive matrix failure

                        L = (0.25*(Yc[lamina]/S[lamina]**2)-(1/Yc[lamina]))*sigma2
                        Q = (0.25*(sigma2**2)/(S[lamina]**2)) + ((sigma12**2)/(S[lamina]**2))

                        RF_matrix = (-L + math.sqrt(L**2 + 4*Q))/(2*Q)
                  

                    # Combine both criteria ---------------------------------------------------------------------------------------
                    RF = (RF_fiber, RF_matrix)
                RF_values.append(RF)

            # Store RF per element --------------------------------------------------------------------------------------------
            self.HashinResults[n2p_element] = RF_values
            
            # Failure_Results -------------------------------------
            # Extract RF values from fiber and matrix independently
            RF_values_fiber, RF_values_matrix = np.array(RF_values).T

            # Acquire min RF from fiber and its position in the array
            min_value_fiber = np.min(RF_values_fiber)
            position_fiber = np.argmin(RF_values_fiber)

            # Acquire min RF from matrix and its position in the array
            min_value_matrix = np.min(RF_values_matrix)
            position_matrix = np.argmin(RF_values_matrix)
            
            Failure_Results[n2p_element] = (min_value_fiber, position_fiber + 1, min_value_matrix, position_matrix + 1)

            # Order_Results ------------------------------------
            # Sort fiber values and create index dictionary
            sorted_indices_fiber = np.argsort(RF_values_fiber)  # Get sorted indices
            sorted_values_fiber = RF_values_fiber[sorted_indices_fiber]  # Get sorted values
            valid_fiber_mask = sorted_values_fiber < 1  # Mask for values < 1

            index_dict_fiber = {sorted_values_fiber[i]: i + 1 for i in range(len(sorted_values_fiber)) if valid_fiber_mask[i]}

            # Sort matrix values and create index dictionary
            sorted_indices_matrix = np.argsort(RF_values_matrix)
            sorted_values_matrix = RF_values_matrix[sorted_indices_matrix]
            valid_matrix_mask = sorted_values_matrix < 1

            index_dict_matrix = {sorted_values_matrix[i]: i + 1 for i in range(len(sorted_values_matrix)) if valid_matrix_mask[i]}

            # Generate results
            result = [(vf, index_dict_fiber.get(vf, 0), vm, index_dict_matrix.get(vm, 0))
                    for vf, vm in zip(RF_values_fiber, RF_values_matrix)]

            Order_Results[n2p_element] = result


        # ---------------------------------------------------------------------------------------------------------------------
        return self.HashinResults, Failure_Results, Order_Results
# -----------------------------------------------------------------------------------------------------------------------------

# PUCK ------------------------------------------------------------------------------------------------------------------------

    def _calculate_Puck(self, LC, i):
        """
        Method to implement the Puck Failure Criterion.

        This method evaluates failure modes (fiber failure and matrix failure) for 
        composite laminates under combined loading conditions.
        
        Returns:
            dict: Dictionary with N2PElement instances as keys and RF:tuple (RF_fiber, RF_matrix) lists as values.

        ** In Puck’s theory, the failure plane is not necessarily aligned with the material axes. Instead, it is inclined by an angle 𝜃(typically from −90∘ to +90∘), and failure is evaluated on this plane.

        Puck defines 𝑓𝐼(𝜃)=tan(𝜃)

        So the more inclined the fracture plane is, the larger the shear contribution to matrix failure.

        But that’s only part of the full Puck approach. The inclination angle also affects normal and shear stresses on the fracture plane, which are used to build the full failure criterion. **
        """

        # According to Puck and Schürmann. A default engineering value can be used when fracture plane is unknown.

        fi = 1.12
        
        # Stresses importation ------------------------------------------------------------------------------------------------
        if i == 0:
            self.Forces_element = self._extract_forces(LC)

            # Initialize storage arrays
            self._elements_IDs = list(self.Forces_element.keys())  # Extract element IDs
            self._n_elements = len(self._element_list)

            # Extract properties
            self.original_list_composite_shells = [self._properties_elem[element] for element in self._elements_IDs]
            self._array_thicknesses = np.array([shell._thicknesses for shell in self.original_list_composite_shells], dtype=object)  # Variable length
            self._array_num_plies = np.array([shell._num_plies for shell in self.original_list_composite_shells])

            # Convert Forces_element dict to NumPy array
            self._NM = np.array([np.nan_to_num(self.Forces_element[element], nan=0) for element in self._elements_IDs])

            # Compute z_positions for all elements
            self._Z_positions = [
                -sum(t) / 2 + np.cumsum(t) - (np.array(t) / 2) for t in self._array_thicknesses
            ]  # List of arrays
        else:
            pass

        
        self._list_composite_shells = list(self._properties_elem.values())  

        self.sigma1_element, self.sigma2_element, self.sigma12_element = self._transform_forces_to_stresses()

        # Results dict initialization -----------------------------------------------------------------------------------------
        self.PuckResults = {n2p_element: [] for n2p_element in self._element_list}

        Failure_Results = {n2p_element: () for n2p_element in self._element_list }

        Order_Results = { n2p_element: [] for n2p_element in self._element_list}

        # Allowables importation ------------------------------------------------------------------------------------------
        for n2p_element, allowables in self.allowables_elem.items():

            Xt, Xc, Yt, Yc, S = (allowables[key] for key in ("Xt", "Xc", "Yt", "Yc", "S"))

            # Criterion Evaluation per ply ------------------------------------------------------------------------------------
            RF_values = []
            for lamina in range(len(Xt)):
                sigma1 = self.sigma1_element[n2p_element][lamina]
                sigma2 = self.sigma2_element[n2p_element][lamina]
                sigma12 = self.sigma12_element[n2p_element][lamina]

                mode = None

                # Hashin Fiber Failure ----------------------------------------------------------------------------------------
                if sigma1 == 0 and sigma2 == 0 and sigma12 == 0:
                    RF_fiber = np.nan
                    RF_matrix = np.nan
                    RF = (RF_fiber, RF_matrix)
                elif np.isnan(sigma1) and np.isnan(sigma2) and np.isnan(sigma12):
                    RF_fiber = np.nan
                    RF_matrix = np.nan
                    RF = (RF_fiber, RF_matrix)


                else:       
                    # Fiber Failure Mode (FF)--------------------------------------------------------------------------------------
                    if sigma1 >= 0:  # Tensile Fiber Failure
                        RF_fiber = Xt[lamina] / sigma1
                    else:  # Compressive Fiber Failure
                        RF_fiber = Xc[lamina] / abs(sigma1)

                    # Inter-Fiber Failure Mode (IFF) --------------------------------------------------------------------------------

                    if sigma2 >= 0:  # Matrix tensile failure (IFF-A)
                        RF_matrix = 1 / math.sqrt((sigma2/Yt[lamina])**2 + (sigma12/S[lamina])**2)
                    else:  # Matrix compressive failure (IFF-C)
                        Q = (sigma12/S[lamina])**2
                        L = ((sigma2/Yc[lamina]) + fi * abs(sigma12)/S[lamina])**2
                        RF_matrix = 1 / math.sqrt(Q + L)

                    # Store results -------------------------------------------------------------------------------------------
                    
                    RF = (RF_fiber, RF_matrix)
                RF_values.append(RF)

            # Store RF per element --------------------------------------------------------------------------------------------
            self.PuckResults[n2p_element] = RF_values

            # Failure_Results -------------------------------------
            # Extract RF values from fiber and matrix independently
            RF_values_fiber, RF_values_matrix = np.array(RF_values).T

            # Acquire min RF from fiber and its position in the array
            min_value_fiber = np.min(RF_values_fiber)
            position_fiber = np.argmin(RF_values_fiber)

            # Acquire min RF from matrix and its position in the array
            min_value_matrix = np.min(RF_values_matrix)
            position_matrix = np.argmin(RF_values_matrix)
            
            Failure_Results[n2p_element] = (min_value_fiber, position_fiber + 1, min_value_matrix, position_matrix + 1)

            # Order_Results ------------------------------------
            # Sort fiber values and create index dictionary
            sorted_indices_fiber = np.argsort(RF_values_fiber)  # Get sorted indices
            sorted_values_fiber = RF_values_fiber[sorted_indices_fiber]  # Get sorted values
            valid_fiber_mask = sorted_values_fiber < 1  # Mask for values < 1

            index_dict_fiber = {sorted_values_fiber[i]: i + 1 for i in range(len(sorted_values_fiber)) if valid_fiber_mask[i]}

            # Sort matrix values and create index dictionary
            sorted_indices_matrix = np.argsort(RF_values_matrix)
            sorted_values_matrix = RF_values_matrix[sorted_indices_matrix]
            valid_matrix_mask = sorted_values_matrix < 1

            index_dict_matrix = {sorted_values_matrix[i]: i + 1 for i in range(len(sorted_values_matrix)) if valid_matrix_mask[i]}

            # Generate results
            result = [(vf, index_dict_fiber.get(vf, 0), vm, index_dict_matrix.get(vm, 0))
                    for vf, vm in zip(RF_values_fiber, RF_values_matrix)]

            Order_Results[n2p_element] = result
        
        # Return results --------------------------------------------------------------------------------------------------
            
        return self.PuckResults, Failure_Results, Order_Results

# --------------------------------------------------------------------------------

# FMC ------------------------------------------------------------------------------------------------------------------------

    def _calculate_FMC(self, LC, i):
        """
        Method to Implement the Fiber Mode Concept (FMC) Failure Criterion.

        This method evaluates FF (fiber failure) and IFF (intra fiber failure) failure modes for composite laminates under combined loading conditions.
        
        Returns:
            dict: Dictionary with N2PElement instances as keys and FI - i.e Failure Index: lists as values. 

        If FI > 1 then consider material failure in the corresponding element.

        """

        # Stresses & Forces Import --------------------------------------------------------------------------------
        if i == 0:
            self.Forces_element = self._extract_forces(LC)

            # Initialize storage arrays
            self._elements_IDs = list(self.Forces_element.keys())  # Extract element IDs
            self._n_elements = len(self._element_list)

            # Extract properties
            self.original_list_composite_shells = [self._properties_elem[element] for element in self._elements_IDs]
            self._array_thicknesses = np.array([shell._thicknesses for shell in self.original_list_composite_shells], dtype=object)  # Variable length
            self._array_num_plies = np.array([shell._num_plies for shell in self.original_list_composite_shells])

            # Convert Forces_element dict to NumPy array
            self._NM = np.array([np.nan_to_num(self.Forces_element[element], nan=0) for element in self._elements_IDs])

            # Compute z_positions for all elements
            self._Z_positions = [
                -sum(t) / 2 + np.cumsum(t) - (np.array(t) / 2) for t in self._array_thicknesses
            ]  # List of arrays
        else:
            pass

        self._list_composite_shells = list(self._properties_elem.values())    
    
        self.sigma1_element, self.sigma2_element, self.sigma12_element = self._transform_forces_to_stresses()

        # Initialize Result Storage -------------------------------------------------------------------------------------
        self.FMCResults = {n2p_element: [] for n2p_element in self._element_list}
        Failure_Results = {n2p_element: () for n2p_element in self._element_list}
        Order_Results = {n2p_element: [] for n2p_element in self._element_list}

        # Computation ---------------------------------------------------------------------------------------------------

        for element, allowable in self.allowables_elem.items():
            sigma1 = np.array(self.sigma1_element[element], dtype=np.float64)
            sigma2 = np.array(self.sigma2_element[element], dtype=np.float64)
            sigma12 = np.array(self.sigma12_element[element], dtype=np.float64)
            
            Xt = np.array(allowable['Xt'])
            Xc = np.array(allowable['Xc'])
            Yt = np.array(allowable['Yt'])
            Yc = np.array(allowable['Yc'])
            S = np.array(allowable['S'])

            mu21 = np.array([self.Materials[lamina.mat_ID].mu21 for lamina in self._properties_elem[element].Laminate])

            b2 = np.array([self.Materials[lamina.mat_ID].b2 for lamina in self._properties_elem[element].Laminate])

            # Inter Fiber Failure - Shear direction fiberwise.            # Fiber Failure - Longitudinal direction fiberwise.
            FF_1 = np.where(
                np.isnan(sigma1),       # Condition: If sigma1 is NaN
                np.nan,                 # Result if sigma1 is NaN
                np.where(
                    sigma1 == 0,        # Condition: If sigma1 is 0
                    np.nan,                  # Result if sigma1 is 0
                    np.where(
                        sigma1 > 0,         # Condition: sigma1 > 0
                        (sigma1 / Xt)**self.m,        # Formula if condition is True
                        (np.abs(sigma1) / Xc)**self.m # Formula if condition is False
                    )
                )
            )
            
            # Inter Fiber Failure - Transversal direction fiberwise.
            IFF_1 = np.where(
                np.isnan(sigma2),  # Condition: If sigma2 is NaN
                np.nan,            # Result if sigma2 is NaN
                np.where(
                    sigma2 == 0,   # Condition: If sigma2 is 0
                    np.nan,             # Result if sigma2 is 0
                    np.where(
                        sigma2 > 0,          # Condition: sigma2 > 0
                        (sigma2 / Yt)**self.m,  # Formula if condition is True
                        (np.abs(sigma2) / Yc)**self.m            # Formula if condition is False
                    )
                )
            )
            
            # Inter Fiber Failure - Shear direction fiberwise.
            IFF_2 = np.where(
                np.isnan(sigma12),  # Condition: If sigma12 is NaN
                np.nan,             # Result if sigma12 is NaN
                np.where(
                    sigma12 == 0,   # Condition: If sigma12 is 0
                    np.nan,              # Result if sigma12 is 0
                    np.where(
                        np.abs((sigma12) + mu21*sigma2) > 0,
                        (np.abs((sigma12) + mu21*sigma2)/S)**self.m,# Formula if condition is True
                        0) #Formula if codition is false 
                )
            )
            
            # Sum the results across all plies
            RF = (FF_1 + IFF_1 + IFF_2)**(-1/self.m)

            # Store RF per element --------------------------------------------------------------------------------------------
            self.FMCResults[element] = RF.tolist()

            # Failure_Results -------------------------------------
            # Acquire min RF from fiber and its position in the array
            min_value = np.min(RF)
            position = np.argmin(RF)
            Failure_Results[element] = (min_value, position + 1)

            # Order_Results ------------------------------------
            # Sort values and create index dictionary
            sorted_indices = np.argsort(RF)  # Get sorted indices
            sorted_values = RF[sorted_indices]  # Get sorted values
            valid_mask = sorted_values < 1  # Mask for values < 1
            index_dict = {sorted_values[i]: i + 1 for i in range(len(sorted_values)) if valid_mask[i]}
            # Generate results
            result = [(v, index_dict.get(v, 0)) for v in RF]
            Order_Results[element] = result
            
        # Return results --------------------------------------------------------------------------------------------------
        return self.FMCResults, Failure_Results, Order_Results

                

                

        


# ---------------------------------------------
      
    def _extract_stresses(self):

        """
        Method to extract Stress results from N2PModelContent. Differentiates between the different solvers
        supported by NaxToPy.

        Returns a series of a dictionaries that store the planar stresses (fiber-wise orientation) for each
        section (ply) of the element

        """
        # Dictionary initialisation -------------------------------------------------------------------------------------------
        self.sections_sigma1 = {}
        self.sections_sigma2 = {}
        self.sections_sigma12 = {}

        # Extraction of stress results on all the elements --------------------------------------------------------------------
        if self._model.Solver == 'Nastran' or self._model.Solver == 'Optistruct':
            results = 'STRESSES'
            component1 = 'NORMAL-1'
            component2 = 'NORMAL-2'
            component12 = 'NORMAL-12'
        
        elif self._model.Solver == 'Abaqus':
            results = 'S'
            component1 = 'S11'
            component2 = 'S22'
            component12 = 'S12'
        
        elif self._model.Solver == 'Ansys':
            results = 'STRESSES'
            component1 = 'XX'
            component2 = 'YY'
            component12 = 'XY'

        for lc in self._LCs:
            self.sections_results_sigma1 = lc.get_result(results).get_component(component1).Sections
            self.sections_results_sigma2 = lc.get_result(results).get_component(component2).Sections
            self.sections_results_sigma12 = lc.get_result(results).get_component(component12).Sections
            for section1, section2, section12 in zip(self.sections_results_sigma1, self.sections_results_sigma2, self.sections_results_sigma12):
                self.sections_sigma1[section1] = lc.get_result(results).get_component(component1).get_result_array([section1.Name])[0]
                self.sections_sigma2[section2] = lc.get_result(results).get_component(component2).get_result_array([section2.Name])[0]
                self.sections_sigma12[section12] = lc.get_result(results).get_component(component12).get_result_array([section12.Name])[0]


        # Apply filter to acquire results at just the elements selected by user ------------------------------------------------

        index = [elem.InternalID for elem in self._element_list]

        for section1, section2, section12 in zip(self.sections_sigma1, self.sections_sigma2, self.sections_sigma12):
            self.sections_sigma1[section1] = [self.sections_sigma1[section1][i] for i in index]
            self.sections_sigma2[section2] = [self.sections_sigma2[section2][i] for i in index]
            self.sections_sigma12[section12] = [self.sections_sigma12[section12][i] for i in index]

        # Create Dictionary to relate stresses in different laminaes to its respective N2PElement instance ---------------------
        
        # Dictionary initialization --------------------------------------------------------------------------------------------
        self.sigma1_element = {n2p_element: [] for n2p_element in self._element_list}
        self.sigma2_element = {n2p_element: [] for n2p_element in self._element_list}    
        self.sigma12_element = {n2p_element: [] for n2p_element in self._element_list}        

        # Read the list of elements obtained from user input ------------------------------------------------------------------- 
        for i in range(len(self._element_list)):
            # Acquiring N2PElement instance                                         
            n2p_element = self._element_list[i] 
            # List to temporaly store stresses on each element                                   
            sigma1_values = []
            sigma2_values = []
            sigma12_values = []

            #Go through the sections and obtain the corresponding stresses for this element                                                      
            for section in self.sections_sigma1.keys():     #, self.sections_sigma2.keys(), self.sections_sigma12.keys(): 
                sigma1_values.append(self.sections_sigma1[section][i])
            for section in self.sections_sigma2.keys():
                sigma2_values.append(self.sections_sigma2[section][i])
            for section in self.sections_sigma12.keys():
                sigma12_values.append(self.sections_sigma12[section][i])

            # Assign the stresses list to the N2PElement in the stress_element dictionary
            self.sigma1_element[n2p_element] = sigma1_values
            self.sigma2_element[n2p_element] = sigma2_values
            self.sigma12_element[n2p_element] = sigma12_values
    
        
        return self.sigma1_element, self.sigma2_element, self.sigma12_element 
    
    # @profile
    def _extract_forces(self, LC):

        """
        Method to extract Forces results from N2PModelContent. Differentiates between the different solvers
        supported by NaxToPy.

        Returns a dictionary that store the planar forces and moments (global axis orientation) for each
        section (ply) of the element.

            Forces_element = {N2PElement : [Fx, Fy, Fz, Mx, My, Mz]}



        """
        # Dictionary initialisation -------------------------------------------------------------------------------------------

        
        self.sections_Fx = {}
        self.sections_Fy = {}
        self.sections_Fxy = {}
        self.sections_Mx = {}
        self.sections_My = {}
        self.sections_Mxy = {}


        # Extraction of stress results on all the elements --------------------------------------------------------------------
        if self._model.Solver == 'Nastran' or self._model.Solver == 'Optistruct' or self._model.Solver == 'InputFileNastran':
            results = 'FORCES'
            componentFx = 'FX'
            componentFy = 'FY'
            componentFxy = 'FXY'
            componentMx = 'MX'
            componentMy = 'MY'
            componentMxy = 'MXY'
        
        # elif self._model.Solver == 'Abaqus':
        #     componentFx = 'FX'
        #     componentFy = 'FY'
        #     componentFz = 'FZ'
        #     componentMx = 'MX'
        #     componentMy = 'MY'
        #     componentMz = 'MZ'
        
        # elif self._model.Solver == 'Ansys':
        #     componentFx = 'FX'
        #     componentFy = 'FY'
        #     componentFz = 'FZ'
        #     componentMx = 'MX'
        #     componentMy = 'MY'
        #     componentMz = 'MZ'


        self.sections_results_Fx = LC.get_result(results).get_component(componentFx).Sections
        self.sections_results_Fy = LC.get_result(results).get_component(componentFy).Sections
        self.sections_results_Fxy = LC.get_result(results).get_component(componentFxy).Sections
        self.sections_results_Mx = LC.get_result(results).get_component(componentMx).Sections
        self.sections_results_My = LC.get_result(results).get_component(componentMy).Sections
        self.sections_results_Mxy = LC.get_result(results).get_component(componentMxy).Sections
        for sectionFx, sectionFy, sectionFxy, sectionMx, sectionMy, sectionMxy in zip(self.sections_results_Fx, self.sections_results_Fy, self.sections_results_Fxy,self.sections_results_Mx, self.sections_results_My, self.sections_results_Mxy):
            self.sections_Fx[sectionFx] = LC.get_result(results).get_component(componentFx).get_result_array([sectionFx.Name])[0]
            self.sections_Fy[sectionFy] = LC.get_result(results).get_component(componentFy).get_result_array([sectionFy.Name])[0]
            self.sections_Fxy[sectionFxy] = LC.get_result(results).get_component(componentFxy).get_result_array([sectionFxy.Name])[0]
            self.sections_Mx[sectionMx] = LC.get_result(results).get_component(componentMx).get_result_array([sectionMx.Name])[0]
            self.sections_My[sectionMy] = LC.get_result(results).get_component(componentMy).get_result_array([sectionMy.Name])[0]
            self.sections_Mxy[sectionMxy] = LC.get_result(results).get_component(componentMxy).get_result_array([sectionMxy.Name])[0]


        # Apply filter to acquire results at just the elements selected by user ------------------------------------------------

        index = [elem.InternalID for elem in self._element_list]

        for sectionFx, sectionFy, sectionFxy, sectionMx, sectionMy, sectionMxy in zip(self.sections_results_Fx, self.sections_results_Fy, self.sections_results_Fxy,self.sections_results_Mx, self.sections_results_My, self.sections_results_Mxy):
            self.sections_Fx[sectionFx] = [self.sections_Fx[sectionFx][i] for i in index]
            self.sections_Fy[sectionFy] = [self.sections_Fy[sectionFy][i] for i in index]
            self.sections_Fxy[sectionFxy] = [self.sections_Fxy[sectionFxy][i] for i in index]
            self.sections_Mx[sectionMx] = [self.sections_Mx[sectionMx][i] for i in index]
            self.sections_My[sectionMy] = [self.sections_My[sectionMy][i] for i in index]
            self.sections_Mxy[sectionMxy] = [self.sections_Mxy[sectionMxy][i] for i in index]

        # Create Dictionary to relate forces in different laminaes to its respective N2PElement instance ------------------------
        
        # Dictionary initialization ---------------------------------------------------------------------------------------------
        self.Fx_element = {n2p_element: [] for n2p_element in self._element_list}
        self.Fy_element = {n2p_element: [] for n2p_element in self._element_list}    
        self.Fxy_element = {n2p_element: [] for n2p_element in self._element_list}        
        self.Mx_element = {n2p_element: [] for n2p_element in self._element_list}
        self.My_element = {n2p_element: [] for n2p_element in self._element_list}    
        self.Mxy_element = {n2p_element: [] for n2p_element in self._element_list} 

        self.Forces_element = {n2p_element: [] for n2p_element in self._element_list}   

        # Read the list of elements obtained from user input -------------------------------------------------------------------- 
        for i in range(len(self._element_list)):
            # Acquiring N2PElement instance -------------------------------------------------------------------------------------                                         
            n2p_element = self._element_list[i] 
            # List to temporaly store forces on each element --------------------------------------------------------------------                                   
            Fx_values = []
            Fy_values = []
            Fxy_values = []
            Mx_values = []
            My_values = []
            Mxy_values = []
            Forces = []

            #Go through the sections and obtain the corresponding forces for this element ---------------------------------------                                                       
            for section in self.sections_Fx.keys():     
                Fx_values.append(self.sections_Fx[section][i])
                Forces.append(self.sections_Fx[section][i])
            for section in self.sections_Fy.keys():
                Fy_values.append(self.sections_Fy[section][i])
                Forces.append(self.sections_Fy[section][i])
            for section in self.sections_Fxy.keys():
                Fxy_values.append(self.sections_Fxy[section][i])
                Forces.append(self.sections_Fxy[section][i])
            for section in self.sections_Mx.keys():     
                Mx_values.append(self.sections_Mx[section][i])
                Forces.append(self.sections_Mx[section][i])
            for section in self.sections_My.keys():
                My_values.append(self.sections_My[section][i])
                Forces.append(self.sections_My[section][i])
            for section in self.sections_Mxy.keys():
                Mxy_values.append(self.sections_Mxy[section][i])
                Forces.append(self.sections_Mxy[section][i])

            # Assign the stresses list to the N2PElement in the stress_element dictionary --------------------------------------
            self.Fx_element[n2p_element] = Fx_values
            self.Fy_element[n2p_element] = Fy_values
            self.Fxy_element[n2p_element] = Fxy_values
            self.Mx_element[n2p_element] = Mx_values
            self.My_element[n2p_element] = My_values
            self.Mxy_element[n2p_element] = Mxy_values

            self.Forces_element[n2p_element] = Forces
    
        
        return self.Forces_element 
    
    # @profile
    def _transform_forces_to_stresses(self):
        """
        Computes sigma1, sigma2, and sigma12 for each element based on applied forces.

        Returns:
            sigma1_element (dict): {N2PElement(ID, '0') : [σ1_layer1, ..., σ1_layer_i]}.
            sigma2_element (dict): {N2PElement(ID, '0') : [σ2_layer1, ..., σ2_layer_i]}.
            sigma12_element (dict): {N2PElement(ID, '0') : [τ12_layer1, ..., τ12_layer_i]}.

        This method is applicable to both FirstPly and PlyByPly failure criterions. 

        For the last one. ABD Matrix has to be recomputed. ABD Matrix might be ZERO when full laminate fails.
        
        This method automatically assigns a NaN value to each lamina of the element where failure has occurred. 

        Stresses are originally computed in material axis, as this is the reference system which Forces are referred to.

        Transformation to local axis is performed when calling the method _transform_stress_to_local(self, stress_global_ theta)

        """

        # Output dicts
        sigma1_element = {}
        sigma2_element = {}
        sigma12_element = {}

        # Extract ABD Matrices.
        ABD_matrices = np.array([shell._ABDMATRIX for shell in self._list_composite_shells])  # Shape (n_elements, 3, 3)

        # Reshape ABD_matrices to match the required (6,6) shape.
        ABD_expanded = np.zeros((self._n_elements, 6, 6))
        ABD_expanded[:, :3, :3] = ABD_matrices[:, 0]  # A-matrix
        ABD_expanded[:, :3, 3:] = ABD_matrices[:, 1]  # B-matrix
        ABD_expanded[:, 3:, :3] = ABD_matrices[:, 1]  # B-matrix
        ABD_expanded[:, 3:, 3:] = ABD_matrices[:, 2]  # D-matrix

        # Compute strain_curvature.
        strain_curvature = np.array([np.linalg.solve(ABD_expanded[i], self._NM[i]) for i in range(self._n_elements)])  # Shape (n_elements, 6)

        epsilon_0 = strain_curvature[:, :3]  # Membrane strains
        kappa = strain_curvature[:, 3:]  # Curvatures

        # Initialize output arrays
        sigma1_layers, sigma2_layers, sigma12_layers = [], [], []

        # Initialise Rotation matrix.

        R = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 2]
        ])

        R_inv = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 0.5]
        ])

        for idx, (shell, z_pos, n_plies) in enumerate(zip(self._list_composite_shells, self._Z_positions, self._array_num_plies)):
            # Compute strain at each ply using broadcasting
            strain_k = epsilon_0[idx][:, None] + kappa[idx][:, None] * z_pos  # Shape (3, num_plies)


            # Extract Q_matrices and Q_bar for all plies
            Q_matrices = np.array([ply._Qmatrix for ply in shell._laminate])  # (num_plies, 3, 3)

            thetas = np.array([ply._theta for ply in shell._laminate])  # (num_plies,)

            stress_material = np.array([
                self._transform_stress_to_local(Q_matrices[i], strain_k[:, i], thetas[i], R, R_inv)
                for i in range(n_plies)
            ])  # Shape (num_plies, 3)

            sigma1_layers.append(stress_material[:, 0])
            sigma2_layers.append(stress_material[:, 1])
            sigma12_layers.append(stress_material[:, 2])

        # Convert lists to dictionary format
        sigma1_element = dict(zip(self._elements_IDs, sigma1_layers))
        sigma2_element = dict(zip(self._elements_IDs, sigma2_layers))
        sigma12_element = dict(zip(self._elements_IDs, sigma12_layers))

        return sigma1_element, sigma2_element, sigma12_element
        
    # @profile
    def _transform_stress_to_local(self, Q_matrix, strain_k, theta, R, R_inv):
        """
        Transforms the stress from global (laminate) coordinates to local (material) coordinates.

        Parameters:
            stress_global (numpy array): Stress vector [σx, σy, τxy] in the global system.
            theta (float): Ply orientation angle in degrees.

        Returns:
            stress_material (numpy array): Stress vector [σ1, σ2, τ12] in the material system.
        """

        theta_rad = np.radians(theta)
        m = np.cos(theta_rad)
        n = np.sin(theta_rad)

        m_squared = m**2
        n_squared = n**2
        mn = m*n
        mn2 = 2*mn

        T_sigma = np.array([
            ([m_squared, n_squared, mn2]),
            ([n_squared, m_squared, -mn2]),
            ([-mn, mn, m_squared - n_squared])
        ])

        qr = np.matmul(Q_matrix, R)
        qrt = np.matmul(qr, T_sigma)
        qrtrinv = np.matmul(qrt, R_inv)
        qrtrinvs = np.matmul(qrtrinv, strain_k)

        return qrtrinvs


    def _extract_strains(self):

        # """
        # Method to extract Strain results from N2PModelContent. Differentiates between the different solvers
        # supported by NaxToPy.

        # Returns a series of a dictionaries that store the planar stresses (fiber-wise orientation) for each
        # section (ply) of the element

        # """
        # # Dictionary initialisation -------------------------------------------------------------------------------------------
        # self.sections_sigma1 = {}
        # self.sections_sigma2 = {}
        # self.sections_sigma12 = {}

        # # Extraction of stress results on all the elements --------------------------------------------------------------------
        # if self._model.Solver == 'Nastran' or self._model.Solver == 'Optistruct':
        #     results = 'STRESSES'
        #     component1 = 'NORMAL-1'
        #     component2 = 'NORMAL-2'
        #     component12 = 'NORMAL-12'
        
        # elif self._model.Solver == 'Abaqus':
        #     results = 'S'
        #     component1 = 'S11'
        #     component2 = 'S22'
        #     component12 = 'S12'
        
        # elif self._model.Solver == 'Ansys':
        #     results = 'STRESSES'
        #     component1 = 'XX'
        #     component2 = 'YY'
        #     component12 = 'XY'

        # for lc in self._LCs:
        #     self.sections_results_sigma1 = lc.get_result(results).get_component(component1).Sections
        #     self.sections_results_sigma2 = lc.get_result(results).get_component(component2).Sections
        #     self.sections_results_sigma12 = lc.get_result(results).get_component(component12).Sections
        #     for section1, section2, section12 in zip(self.sections_results_sigma1, self.sections_results_sigma2, self.sections_results_sigma12):
        #         self.sections_sigma1[section1] = lc.get_result(results).get_component(component1).get_result_array([section1.Name])[0]
        #         self.sections_sigma2[section2] = lc.get_result(results).get_component(component2).get_result_array([section2.Name])[0]
        #         self.sections_sigma12[section12] = lc.get_result(results).get_component(component12).get_result_array([section12.Name])[0]


        # # Apply filter to acquire results at just the elements selected by user ------------------------------------------------

        # index = [elem.InternalID for elem in self._element_list]

        # for section1, section2, section12 in zip(self.sections_sigma1, self.sections_sigma2, self.sections_sigma12):
        #     self.sections_sigma1[section1] = [self.sections_sigma1[section1][i] for i in index]
        #     self.sections_sigma2[section2] = [self.sections_sigma2[section2][i] for i in index]
        #     self.sections_sigma12[section12] = [self.sections_sigma12[section12][i] for i in index]

        # # Create Dictionary to relate stresses in different laminaes to its respective N2PElement instance ---------------------
        
        # # Dictionary initialization --------------------------------------------------------------------------------------------
        # self.sigma1_element = {n2p_element: [] for n2p_element in self._element_list}
        # self.sigma2_element = {n2p_element: [] for n2p_element in self._element_list}    
        # self.sigma12_element = {n2p_element: [] for n2p_element in self._element_list}        

        # # Read the list of elements obtained from user input ------------------------------------------------------------------- 
        # for i in range(len(self._element_list)):
        #     # Acquiring N2PElement instance                                         
        #     n2p_element = self._element_list[i] 
        #     # List to temporaly store stresses on each element                                   
        #     sigma1_values = []
        #     sigma2_values = []
        #     sigma12_values = []

        #     #Go through the sections and obtain the corresponding stresses for this element                                                      
        #     for section in self.sections_sigma1.keys():     #, self.sections_sigma2.keys(), self.sections_sigma12.keys(): 
        #         sigma1_values.append(self.sections_sigma1[section][i])
        #     for section in self.sections_sigma2.keys():
        #         sigma2_values.append(self.sections_sigma2[section][i])
        #     for section in self.sections_sigma12.keys():
        #         sigma12_values.append(self.sections_sigma12[section][i])

        #     # Assign the stresses list to the N2PElement in the stress_element dictionary
        #     self.sigma1_element[n2p_element] = sigma1_values
        #     self.sigma2_element[n2p_element] = sigma2_values
        #     self.sigma12_element[n2p_element] = sigma12_values
    
        
        return self.sigma1_element, self.sigma2_element, self.sigma12_element 
    
    
    def _transform_results(self, List_LCs):
        """
        Method to transform a results dictionary into multiple Numpy array.

        This method also takes responsibility for results file creation into h5 type format.
        HDF5_NaxTo and DataEntry classes, and their methods, are imported and used for file creation.  
        
        Args:
            Analysis_Results (dict): Dictionary with N2PElement instances as keys, and RF:list as values.

        Returns: 
            datasets (list[np.array]): A list of Numpy arrays [ElementID, RF], one per section (layer). 
        """

        n_elements = len(self.Elements)
        results_names = ['Initial_Results', 'Failure_Results', 'Order_Results']
        self.dataEntryList = []
        self._hdf5.create_hdf5()

        # Predefine data types
        dtype_map = {
            'default': [("ID ENTITY", "i4"), ("RF", "f4")],
            'Hashin_Puck': [("ID ENTITY", "i4"), ("RF_fiber", "f4"), ("RF_matrix", "f4")],
            'Failure_Hashin_Puck': [("ID ENTITY", "i4"), ("FI_fiber", "f4"), ("ID_fiber", "f4"),
                                    ("FI_matrix", "f4"), ("ID_matrix", "f4")],
            'Failure_Default': [("ID ENTITY", "i4"), ("RF", "f4"), ("Lamina", "f4")],
            'Order_Hashin_Puck': [("ID ENTITY", "i4"), ("RF_fiber", "f4"), ("order_fiber", "f4"),
                                ("RF_matrix", "f4"), ("order_matrix", "f4")],
            'Order_Default': [("ID ENTITY", "i4"), ("RF", "f4"), ("Order", "f4")]
        }

        for LC in List_LCs:
            results_dict = self.Analysis_Results[LC]
            failure_theory = self._failure_theory in ('Hashin', 'Puck')

            # Get max number of sections across all elements (vectorized version)
            max_sections = {
                key: max(map(len, results_dict[key].values())) for key in results_names
            }

            # Select the correct dtype
            dtype_initial = np.dtype(dtype_map['Hashin_Puck'] if failure_theory else dtype_map['default'])
            dtype_failure = np.dtype(dtype_map['Failure_Hashin_Puck'] if failure_theory else dtype_map['Failure_Default'])
            dtype_order = np.dtype(dtype_map['Order_Hashin_Puck'] if failure_theory else dtype_map['Order_Default'])

            # Create empty arrays
            arrays_initial = np.full((max_sections['Initial_Results'], n_elements), np.nan, dtype=dtype_initial)
            array_failure = np.full(n_elements, np.nan, dtype=dtype_failure)
            arrays_order = np.full((max_sections['Order_Results'], n_elements), np.nan, dtype=dtype_order)

            # Convert dictionary to NumPy array (Vectorized Method)
            element_ids = np.array([e.ID for e in self.Elements], dtype=np.int32)

            # Process `Initial_Results`           
            structured_data = []
            if failure_theory:
                for element, values in results_dict['Initial_Results'].items():
                    for rf_fiber, rf_matrix in values:
                        structured_data.append((element, rf_fiber, rf_matrix))

                for col_idx, (element, values) in enumerate(results_dict['Initial_Results'].items()):
                    for row_idx, (rf_fiber, rf_matrix) in enumerate(values):
                        arrays_initial[row_idx, col_idx] = (element.ID, rf_fiber, rf_matrix)
            else:
                for element, values in results_dict['Initial_Results'].items():
                    for rf in values:
                        structured_data.append((element, rf))

                for col_idx, (element, values) in enumerate(results_dict['Initial_Results'].items()):
                    for row_idx, rf in enumerate(values):
                        arrays_initial[row_idx, col_idx] = (element.ID, rf)




            # Process `Failure_Results`
            failure_data = np.array([
                (element.ID, *failure) if isinstance(failure, tuple) and len(failure) == (4 if failure_theory else 2)
                else ((element.ID, np.nan, -1, np.nan, -1) if failure_theory else (element.ID, np.nan, -1))
                for element, failure in results_dict['Failure_Results'].items()
            ], dtype=dtype_failure)
            
            array_failure[:] = failure_data

            # Process `Order_Results`
            structured_data = []
            if failure_theory:
                for element, values in results_dict['Order_Results'].items():
                    for rf_fiber, order_fiber, rf_matrix, order_matrix in values:
                        structured_data.append((element, rf_fiber, order_fiber, rf_matrix, order_matrix))

                for col_idx, (element, values) in enumerate(results_dict['Order_Results'].items()):
                    for row_idx, (rf_fiber, order_fiber, rf_matrix, order_matrix) in enumerate(values):
                        arrays_order[row_idx, col_idx] = (element.ID, rf_fiber, order_fiber, rf_matrix, order_matrix)
            else:
                for element, values in results_dict['Order_Results'].items():
                    for rf, order in values:
                        structured_data.append((element, rf, order))

                for col_idx, (element, values) in enumerate(results_dict['Order_Results'].items()):
                    for row_idx, (rf, order) in enumerate(values):
                        arrays_order[row_idx, col_idx] = (element.ID, rf, order)

            # Store results
            datasets = [arrays_initial, array_failure, arrays_order]

            for i, dataset in enumerate(datasets):
                result_name = results_names[i]

                if i == 1:  # Failure_Results (single array)
                    data_entry = DataEntry()
                    data_entry.LoadCase = LC.ID
                    data_entry.LoadCaseName = 'Load Case'
                    data_entry.Increment = LC.ActiveN2PIncrement.ID
                    data_entry.Data = dataset
                    data_entry.Section = 'all'
                    data_entry.ResultsName = result_name
                    data_entry.Part = "(0,'0')"
                    self.dataEntryList.append(data_entry)
                else:  # Initial_Results and Order_Results (multiple sections)
                    for j in range(max_sections[result_name]):
                        data_entry = DataEntry()
                        data_entry.LoadCase = LC.ID
                        data_entry.LoadCaseName = 'Load Case'
                        data_entry.Increment = LC.ActiveN2PIncrement.ID
                        data_entry.Data = dataset[j]
                        data_entry.Section = str(j)
                        data_entry.ResultsName = result_name
                        data_entry.Part = "(0,'0')"
                        self.dataEntryList.append(data_entry)

        # Save to HDF5
        self._hdf5.write_dataset(self.dataEntryList)
        return None
    

    # @profile
    def ply_by_ply_failure(self, LC):

        """
        Method to evaluate progressive degradation in the laminate caused by the consecutive failures in individual plies under 
        a specific load distribution.

        This method will consider RF_values evaluated at each criterion as a starting point. If failure occurs at any single lamina
        it will be deactivated.

        Laminates will be recomputed in terms of ABD Matrix and load distribution with the remaining active plies.

        Failure criteria will be evaluated until every single ply fails. Stating Laminate failure.

        Laminates may resist loads even isolated plies fail.

        Returns:

         - A dict with the FIs for the initial loads and laminate configuration: Initial_Results = {N2PElement: [FI1, FI2, FI3, ..., FIn]}
         - A dict with the summary of the Failure Analysis:
            
            * If the laminate fails: Failure_Results = {N2PElement:(FI, lamina_ID)} - where FI will be the highest FI from Initial_Results.
              The FI for the lamina that initiates laminate failure.
            * If the laminate does not fail: Failure_Results = {N2PElement: (FI, lamina_ID)} - where FI will be the highest value from final
              iteration from healthy laminas.

         - A dict with the FI for every ply of the laminate, and its corresponding failure order: Failure_Order = {N2PElement : [(FI, 2), (FI, 0), (FI, 1) ]}
            * If the Lamina does not fail, a zero value will be assigned to its corresponding FI.
        
        """

        # Initialise Results Dict from First Iteration Results. ------------------------------------------------------------------
        self._Initial_Results = self.Analysis_Results[LC]['Initial_Results']
        self.Ply_By_Ply_Results = self._Initial_Results
        self._Failure_Results = {}
        self._Order_Results = {}

        # self.init_res = np.array(list(self._Initial_Results.values()))

        max_length = max(len(res) for res in self._Initial_Results.values())
        padded_initial_results = {element: res + [np.nan]*(max_length - len(res)) for element, res in self._Initial_Results.items()}
        
        self.init_res = np.array(list(padded_initial_results.values()), dtype=object)
        self.temp_array = np.zeros_like(self.init_res)
        self.temp_array2 = np.ones_like(self.init_res)

        # Narrow down the number of total iterations to the number of plies of the studied laminates - Iterations. ---------------
        # must not exceed the total number of plies, which is the upper limit in case plies fail one by one. ---------------------
        
        MaxPLies = [property.NumPlies for property in self.Properties.values()]
        iter_limit = max(MaxPLies)

        if self.FailureTheory == 'Hashin':

            # Isolating results. -----------------------------------------------------------------------------------------------------

            RFs_List_of_List = self.Ply_By_Ply_Results.values() # List of RFs Tuple lists per element. -------------------------------------
            RFs_fiber = [RF[0] for List in RFs_List_of_List for RF in List] # Listof FIs per element. -----------------------------------------


            # Defining failure condition - failure will occur if RF < 1 every time it is not NaN. ------------------------------------

            failure = any(RF < 1 if not np.isnan(RF) else False for RF in RFs_fiber)


            i = 0
            MaxPLies = [property.NumPlies for property in self.Properties.values()]
            iter_limit = max(MaxPLies)


            # auxiliary dict created to store the order where failure index are added to Order_Results dict. -------------------------
            
            from collections import defaultdict
            fiber_addition_counter = defaultdict(int)
            matrix_addition_counter = defaultdict(int)

            # Failure condition. Iterative Loop and Solution Convergence criterion. -------------------------------------------------

            while failure and i < iter_limit: 
                
                for element, original_property in self._properties_elem.items():

                    
                    # addition = 1

                    property = CompositeShell()
                    property.NumPlies = original_property.NumPlies
                    property.thicknesses = original_property.thicknesses
                    property.theta = original_property.theta
                    property.simmetry = original_property.simmetry

                    property.Laminate = []
                    for ply, RF_tuple in zip(original_property.Laminate, self.Ply_By_Ply_Results[element]):
                        RF_fiber, RF_matrix = RF_tuple
                        Lamina = Laminae()
                        Lamina.Ex = ply.Ex
                        Lamina.Ey = ply.Ey
                        Lamina.Nuxy = ply.Nuxy
                        Lamina.Nuyx = ply.Nuyx
                        Lamina.ShearXY = ply.ShearXY
                        Lamina.Qmatrix = ply.Qmatrix
                        Lamina.QBar = ply.QBar
                        Lamina.thickness = ply.thickness
                        Lamina.theta = ply.theta
                        Lamina.material = ply.material
                        Lamina.mat_ID = ply.mat_ID

                        Lamina.isActive = False if not np.isnan(RF_tuple[0]) and RF_tuple[0] < 1 else ply.isActive

                        property.Laminate.append(Lamina)

                    property._ABDMATRIX = property._ABDMatrix()
                    self._properties_elem[element] = property

                    # Definition of Order_Results dict.
                    if element not in self._Order_Results:
                        self._Order_Results[element] = [0] * len(self.Ply_By_Ply_Results[element]) # (RF_fiber, Failure_order_fiber, RF_matrix, Failure_order_matrix)
                    
                    output = self._Order_Results[element]

                    # Extract plies where RF_fiber < 1 with their index and RF_matrix

                    RFs_fiber_below_1 = [(RF[0], j, RF[1]) for j, RF in enumerate(self.Ply_By_Ply_Results[element]) if RF[0] < 1]

                    RFs_matrix_below_1 = [(RF[1], j, RF[0]) for j, RF in enumerate(self.Ply_By_Ply_Results[element]) if RF[1] < 1]



                    if not RFs_fiber_below_1 and not RFs_matrix_below_1:
                        # No failure - keep failure order as 0
                        output = [(RF[0], 0, RF[1], 0) for RF in self.Ply_By_Ply_Results[element]]
                        self._Order_Results[element]= output
                        
                    else:
                        # Sort fiber failures by RF_fiber in ascending order
                        RFs_fiber_below_1.sort(reverse=False, key=lambda x:x[0]) # sort by minimum RF_fiber (ascending)

                        for RF_fiber, j, RF_matrix in RFs_fiber_below_1:
                            if isinstance(output[j], tuple): # avoid overwritting existing tuples
                                continue
                            
                            output[j] = (RF_fiber, fiber_addition_counter[element] + 1, output[j], output[j]) # update fiber order 
                            fiber_addition_counter[element] += 1

                        # Sort matrix failures by RF_matrix in ascending order
                        RFs_matrix_below_1.sort(key=lambda x:x[0])
                        for RF_matrix, j, RF_fiber in RFs_matrix_below_1:
                            if isinstance(output[j], tuple):
                                continue
                            output[j] = (output[j], output[j],RF_matrix, matrix_addition_counter[element]+1) # update matrix order
                            matrix_addition_counter[element] += 1
                        
                        # for (FI, j) in enumerate(FIs_above_1, start=1):
                            
                        #     if isinstance
                        #     output[j] = (FI, addition_counter[element] + 1)
                        #     addition_counter[element] += 1

                        self._Order_Results[element] = output

                # Recalculate results for the nex iteration

                self.Ply_By_Ply_Results = self._calculate_Hashin(LC)

                # Update results and check failure condition again (ONLY BASED ON RF_fiber)
                self.iter_res = np.array([list(map(lambda x: x[0], List)) for List in self.Ply_By_Ply_Results.values()])
                self.init_res = self.init_res[:,:,0]
                self.init_res = np.fmin(self.init_res, self.iter_res)

                for key, row in zip(self.Ply_By_Ply_Results.keys(), self.init_res):
                    # self.Ply_By_Ply_Results[key] = [(RF_fiber, RF_matrix) for RF_fiber, RF_matrix in zip(row.tolist(), self.Ply_By_Ply_Results[key])]

                    RFs_matrix = [RF[1] for RF in self.Ply_By_Ply_Results[key]]
                    self.Ply_By_Ply_Results[key] = [(RF_fiber, RF_matrix) for RF_fiber, RF_matrix in zip(row.tolist(), RFs_matrix)]

                # Update failure condition - only based on fiber
                failure = np.any(np.less(self.iter_res, 1.0))
                self.init_res = np.array(list(self.Ply_By_Ply_Results.values()))

                i += 1
                # print(i)


        else:

            # Isolating results. -----------------------------------------------------------------------------------------------------

            RFs_List_of_List = self.Ply_By_Ply_Results.values() # List of RFs lists per element. -------------------------------------
            RFs = [RF for List in RFs_List_of_List for RF in List] # Listof FIs per element. -----------------------------------------


            # Defining failure condition - failure will occur if RF < 1 every time it is not NaN. ------------------------------------

            failure = any(RF < 1 if not np.isnan(RF) else False for RF in RFs)


            i = 1
            # print(i)

            MaxPLies = [property.NumPlies for property in self.Properties.values()]
            iter_limit = max(MaxPLies)

            j:float = 1.0

            # Order_Results dict initilialisation with Initial_Results dict. If failure, we take the minimum value < 1. If not, we take all of the values and assing them a 0 index - meaning no failure has occured at the corresponding ply. -------------------------------

            for element, RFs in self.Ply_By_Ply_Results.items():
                fail_elem = any(RF < 1 if not np.isnan(RF) else False for RF in self.Ply_By_Ply_Results[element])

                if fail_elem:
                    RFs = np.array(RFs)
                    min_RF = np.min(RFs)
                    pos_min = np.argmin(RFs)
                    output = [(0, 0) for _ in range(len(RFs))]
                    output[pos_min] = (min_RF, j )
                    self._Order_Results[element] = output
                else:
                    self._Order_Results[element] = [(RF,0) for RF in RFs]
                    


            # auxiliary dict created to store the order where failure index are added to Order_Results dict. -------------------------
            from collections import defaultdict
            addition_counter = defaultdict(int)

            # Failure condition. Iterative Loop and Solution Convergence criterion. -------------------------------------------------

            RF_min = {element: [np.min(values)] if np.min(values) < 1 else [np.nan] for element, values in self.Ply_By_Ply_Results.items()}

            while failure and i < iter_limit: 

                j += 1
               
                for element, original_property in self._properties_elem.items():

                    fail_elem = any(RF < 1 if not np.isnan(RF) else False for RF in self.Ply_By_Ply_Results[element])
                    len_laminate = len(self._properties_elem[element].Laminate)

                    if fail_elem and j <= len_laminate:

                    
                        # addition = 1

                        property = CompositeShell()
                        property.NumPlies = original_property.NumPlies
                        property.thicknesses = original_property.thicknesses
                        property.theta = original_property.theta
                        property.simmetry = original_property.simmetry
                        property._id = original_property.ID
                        property._mat_IDs = original_property.MatIDs

                        property.Laminate = []

                        for ply, RF in zip(original_property.Laminate, self.Ply_By_Ply_Results[element]):
                            Lamina = Laminae()
                            Lamina.Ex = ply.Ex
                            Lamina.Ey = ply.Ey
                            Lamina.Nuxy = ply.Nuxy
                            Lamina.Nuyx = ply.Nuyx
                            Lamina.ShearXY = ply.ShearXY
                            Lamina.Qmatrix = ply.Qmatrix
                            Lamina.QBar = ply.QBar
                            Lamina.thickness = ply.thickness
                            Lamina.theta = ply.theta
                            Lamina.material = ply.material
                            Lamina.mat_ID = ply.mat_ID

                            Lamina.isActive = False if not np.isnan(RF) and RF < 1 and RF in RF_min[element] else ply.isActive

                            property.Laminate.append(Lamina)

                        property.ABDMatrix = property._ABDMatrix()
                        self._properties_elem[element] = property
                    
                    else:
                        continue


                if self.FailureTheory == 'TsaiWu':
                    self.Ply_By_Ply_Results,_,_ = self._calculate_TsaiWu(LC, i)
                if self.FailureTheory == 'TsaiHill':
                    self.Ply_By_Ply_Results,_,_ = self._calculate_Tsai_Hill(LC,i)
                if self.FailureTheory == 'MaxStress':
                    self.Ply_By_Ply_Results,_,_ = self._calculate_Max_Stress(LC, i)
                if self.FailureTheory == 'FMC':
                    self.Ply_By_Ply_Results,_,_ = self._calculate_FMC(LC, i)

                for element, values in self.Ply_By_Ply_Results.items():
                    
                    values = np.array(values) # transforming a list into a NumPy array
                    
                    valid_values = values[(values < 1) & ~np.isnan(values)] # NumPy allows yout to apply conditions to entire arrays without looping. You can write conditions directly on NumPy arrays.

                    new_min = np.min(valid_values) if valid_values.size > 0 else np.nan

                    # We complete adding Failed plies to Order_Results dict.
                    fail_elem = any(RF < 1 if not np.isnan(RF) else False for RF in values)

                    if fail_elem:

                        valid_indices = np.where((values < 1) & ~np.isnan(values))[0]  # Get valid indices

                        pos_min = valid_indices[np.argmin(values[valid_indices])] if valid_indices.size > 0 else None

                        output = self._Order_Results[element]
                        output[pos_min] = (new_min, j)
                        self._Order_Results[element] = output

                    else:
                        valid_indices = np.where((values>=1))[0]

                        output = self._Order_Results[element]
                        for index in valid_indices:
                            output[index] = (values[index], 0)
                        self._Order_Results[element]=output


                    if element in RF_min:
                        RF_min[element].append(new_min if new_min < 1 else np.nan)
                    

                # Update results, preserving the atlready stored results. New results are filtered using np.nan values. Once they are clearly differentiated, we can use np.where to replace the values in the original array with the new ones. --------------------------------------------------------------------------------------------------------------------------------

                padded_iter_results = [res + [np.nan]*(max_length - len(res)) for res in self.Ply_By_Ply_Results.values()]
        
                self.iter_res = np.array(padded_iter_results)

                # self.iter_res = np.array(list(self.Ply_By_Ply_Results.values()))

                self.init_res = np.where(np.isnan(self.iter_res), self.init_res, self.iter_res)

                for key, row in zip(self.Ply_By_Ply_Results.keys(), self.init_res):
                    self.Ply_By_Ply_Results[key] = row.tolist()

                # Update failure condition. --------------------------------------------------------------------------------------------------------------------------------

                condition = np.less(self.iter_res, 1.0)
                failure = np.any(condition)

                i += 1
                # print(i)


        # Definition of Failure_Results dict.
        if self.FailureTheory == 'Hashin':
            for element, RFs in self.Ply_By_Ply_Results.items():
                RFs_fiber, RFs_matrix = np.array(RFs).T

                condition = RFs_fiber < 1.0
                
                failure = np.all(condition)
                if failure: 
                    RFs_fiber_Init, RFs_matrix_Init = np.array(self._Initial_Results[element]).T
                    min_id_fiber = RFs_fiber_Init.argmin()
                    RF_fiber = RFs_fiber_Init[min_id_fiber]

                    
                    min_id_matrix = RFs_matrix_Init.argmin()
                    RF_matrix = RFs_matrix_Init[min_id_matrix]

                    Lamina_ID_fiber = min_id_fiber + 1
                    Lamina_ID_matrix = min_id_matrix + 1

                    self._Failure_Results[element]=(RF_fiber, Lamina_ID_fiber, RF_matrix, Lamina_ID_matrix)
                else:
                    failing_indices_fiber = np.where(RFs_fiber>=1)[0]
                    if failing_indices_fiber.size > 0:
                        min_id_fiber = failing_indices_fiber[np.argmin(RFs_fiber[failing_indices_fiber])]
                        RF_fiber = RFs_fiber[min_id_fiber]

                        min_id_matrix = RFs_matrix.argmin()
                        RF_matrix = RFs_matrix[min_id_matrix]

                        Lamina_ID_fiber = min_id_fiber + 1
                        Lamina_ID_matrix = min_id_matrix + 1

                        self._Failure_Results[element]=(RF_fiber, Lamina_ID_fiber, RF_matrix, Lamina_ID_matrix)
                            
        else:    
            for element, RFs in self.Ply_By_Ply_Results.items():
                RFs = np.array(RFs)

                #filter out NaN values
                valid_RFs = RFs[~np.isnan(RFs)] 
                # Check failure condition *only on valid values* (ignoring NaNs)
                failure = np.all(valid_RFs < 1.0) if valid_RFs.size > 0 else False

                if failure:
                    RFs_Init = np.array(self._Initial_Results[element])
                    min_id = np.nanargmin(RFs_Init)
                    RF = RFs_Init[min_id]
                    Lamina_ID = float(min_id + 1)
                    self._Failure_Results[element] = (RF, Lamina_ID)
                else:
                    failing_indices = np.where((RFs>=1) & ~np.isnan(RFs))[0]
                    if failing_indices.size > 0:
                        min_id = failing_indices[np.nanargmin(RFs[failing_indices])]
                        RF = RFs[min_id]
                        Lamina_ID = float(min_id + 1)
                        self._Failure_Results[element] = (RF, Lamina_ID)

        for element, original_property in self._properties_elem.items():
            [setattr(Lamina, "isActive", True) for Lamina in original_property.Laminate]  
            original_property.ABDMatrix = original_property._ABDMatrix()


        # completing Initial_Results and Order_Results dict with NaN values in empty layers.

        padded_order_results = {element: res + [(np.nan, -1)]*(max_length - len(res)) for element, res in self._Order_Results.items()}

        for element in self.Ply_By_Ply_Results:
            self._Initial_Results[element] = padded_initial_results[element]
            self._Order_Results[element] = padded_order_results[element]

        


        



        return self.Ply_By_Ply_Results, self._Initial_Results, self._Failure_Results, self._Order_Results
    