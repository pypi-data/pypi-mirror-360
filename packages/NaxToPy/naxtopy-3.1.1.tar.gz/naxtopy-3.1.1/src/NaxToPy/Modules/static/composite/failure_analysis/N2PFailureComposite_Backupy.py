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


class N2PLaminateFailure:
    """
    Abstract base class for evaluating structural failure on composites materials
    """

    # __slots__ = ("_model", "_element_list", "_LCs", "_failure_criterion", "_hdf5", "_materials", "_properties", "_properties_elem", "_criteria_dict","mechanical_prop_dict", "Analysis_Results",
                 
    #              )

    def __init__(self):
        """
        Initialize the class

        Args: 
            model: raw data extracted from a N2PModelContent instance user-provided
            elements : list of N2PElements instances where analysis will be performed.
            loadcase : list of N2PLoadCase instances where analysis will be performed.
        """
        # Mandatory attributes [User Input] ------------------------------------------------------------------------------------
        self._model: N2PModelContent = None
        self._element_list: list[N2PElement] = []
        self._LCs: list[N2PLoadCase] = None
        self._failure_criterion: str = None
        self._failure_theory: str = None


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
            "Puck": "Puck failure criterion"
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
        Property that returns the model attribute, that is, the N2PModelContent object to be analyzed.
        """
        return self._model
    # ----------------------------------------------------------------------------------------------------------------------

    # Method to obtain the List of elements which is going to be analyzed ------------------------------------------------------
    @property
    def Elements(self) -> list[N2PElement]:
        """
        Property that returns the list of elements, that is, the list of elements to be analyzed.
        """
        return self._element_list
    # --------------------------------------------------------------------------------------------------------------------------

    # Method to obtain the List of LoadCases which is going to be analyzed -----------------------------------------------------
    @property
    def LoadCases(self) -> list[N2PLoadCase]:
        """
        Property that returns the list of elements, that is, the list of elements to be analyzed.
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
    def mechanical_prop(self):
        """
        This method relates a N2PElement instace to its mechanical properties with regard to the N2PProperty and N2PMaterial instances
        assigned to the element.

        Use of this dictionary is destined to ease the way different calculus methods access the information required to perform the 
        computation.  

        Returns: 

        A dictionary is created to store all the mechanical properties of an orthotropic material assigned to an element.

        Each element will have a list for its different properties, which length will be the 
        number of plies for the laminate.

        For clarifying reasons:
        1: longitudinal direction (fiber-wise)
        2: transverse direction (fiber-wise)

        E1: Young modulus in the longitudinal direction (fiber-wise)
        E2: Young modulus in the transverse direcetion (fiber-wise)
        G: Shear modulus
        Nu12: Major Poisson ratio
        Nu21: Minor Poisson ratio
        Xt: Tensile Strength on longitudinal direction (fiber-wise)
        Xc: Compressive Strength on longitudinal direction (fiber-wise)
        Yt: Tensile Strength on trasnverse direction (fiber-wise)
        Yc: Compressive Strength on transverse direction (fiber-wise)
        S: Shear Strength on the 1-2 plane (fiber-wise)
        theta: angle of ply orientation (fiber-wise) with regard to longitudinal direction (element-wise)

        EXAMPLE

            mechanical_prop = {
                                N2PElement(3204463, 'PartID'): {'E1': [220000, 220000, 220000 ], 'E2': [124300, 124300, 124300],
                                                                'G': [75000, 75000, 75000 ],'Nu12': [0.35, 0.35, 0.35], 
                                                                'Nu21': [0.16, 0.16, 0.16], 'Xt': [1200000, 1200000, 1200000],
                                                                'Yt': [80000, 80000, 80000], 'Xc': [90000, 90000, 90000], 
                                                                'Yc': [25000, 25000, 25000], 'S': [15000, 15000, 15000], 
                                                                'theta': [0.0, 0.0, 0.0]
                                                                },

                                N2PElement(3204464, 'PartID'): {'E1': [220000, 220000, 220000], 'E2': [124300, 124300, 124300], 
                                                                'G': [75000, 75000, 75000],'Nu12': [0.35, 0.35, 0.35], 
                                                                'Nu21': [0.16, 0.16, 0.16], 'Xt': [1200000, 1200000, 1200000],
                                                                'Yt': [80000, 80000, 80000], 'Xc': [90000, 90000, 90000 ], 
                                                                'Yc': [25000, 25000, 25000], 'S': [15000, 15000, 15000], 
                                                                'theta': [0.0, 0.0, 0.0]
                                                                },

                                N2PElement(......, 'PartID'): {
                                                                },

                                .....
            }

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
            print(LC.ID)
            i = 0
            if self._failure_criterion == 'FirstPly':

                if self._failure_theory == 'TsaiWu':
                    self.Analysis_Results[LC]["Initial_Results"], self.Analysis_Results[LC]["Failure_Results"], self.Analysis_Results[LC]["Order_Results"]  = self._calculate_TsaiWu(LC, i)
                elif self._failure_theory == 'MaxStress':
                    self.Analysis_Results[LC]["Initial_Results"], self.Analysis_Results[LC]["Failure_Results"], self.Analysis_Results[LC]["Order_Results"] = self._calculate_Max_Stress(LC)
                elif self._failure_theory == 'TsaiHill':
                    self.Analysis_Results[LC]["Initial_Results"], self.Analysis_Results[LC]["Failure_Results"], self.Analysis_Results[LC]["Order_Results"] = self._calculate_Tsai_Hill(LC)
                elif self._failure_theory == 'Hashin':
                    self.Analysis_Results[LC]["Initial_Results"], self.Analysis_Results[LC]["Failure_Results"], self.Analysis_Results[LC]["Order_Results"] = self._calculate_Hashin(LC)
                elif self._failure_theory == 'Puck':
                    self.Analysis_Results = self._calculate_Puck()
                elif self._failure_theory == 'All':
                    return self._calculate_Max_Stress(), self._calculate_TsaiWu(), self._calculate_Tsai_Hill(), self._calculate_Hashin(), self._calculate_Puck()
                else: 
                    raise ValueError(f"Unsupported failure theory: {self._failure_theory}")
            
        # Ply by ply Failure computation -----------------------------------------------------------------------------------------
            elif self._failure_criterion == 'PlyByPly':

                if self._failure_theory == 'TsaiWu':
                    self.Analysis_Results[LC]['Initial_Results'],_,_ = self._calculate_TsaiWu(LC, i)

                    start_time = time.time()
                    _, self.Analysis_Results[LC]['Initial_Results'], self.Analysis_Results[LC]['Failure_Results'], self.Analysis_Results[LC]['Order_Results'] = self.ply_by_ply_failure(LC)
                    end_time = time.time()

                    print(f"Execution time: {end_time - start_time:.6f} seconds")

                elif self._failure_theory == 'MaxStress':
                    self.Analysis_Results[LC]['Initial_Results'],_,_ = self._calculate_Max_Stress(LC)
                    _, self.Analysis_Results[LC]['Initial_Results'], self.Analysis_Results[LC]['Failure_Results'], self.Analysis_Results[LC]['Order_Results'] = self.ply_by_ply_failure(LC)
                elif self._failure_theory == 'TsaiHill':
                    self.Analysis_Results[LC]['Initial_Results'],_,_ = self._calculate_Tsai_Hill(LC)
                    _, self.Analysis_Results[LC]['Initial_Results'], self.Analysis_Results[LC]['Failure_Results'], self.Analysis_Results[LC]['Order_Results'] = self.ply_by_ply_failure(LC)
                elif self._failure_theory == 'Hashin':
                    self.Analysis_Results[LC]['Initial_Results'] = self._calculate_Hashin(LC)
                    _, self.Analysis_Results[LC]['Initial_Results'], self.Analysis_Results[LC]['Failure_Results'], self.Analysis_Results[LC]['Order_Results'] = self.ply_by_ply_failure(LC)

                elif self._failure_theory == 'Puck':
                    self.Analysis_Results = self._calculate_Puck()
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
            self._list_composite_shells = [self._properties_elem[element] for element in self._elements_IDs]
            self._array_thicknesses = np.array([shell._thicknesses for shell in self._list_composite_shells], dtype=object)  # Variable length
            self._array_num_plies = np.array([shell._num_plies for shell in self._list_composite_shells])

            # Convert Forces_element dict to NumPy array
            self._NM = np.array([np.nan_to_num(self.Forces_element[element], nan=0) for element in self._elements_IDs])

            # Compute z_positions for all elements
            self._Z_positions = [
                -sum(t) / 2 + np.cumsum(t) - (np.array(t) / 2) for t in self._array_thicknesses
            ]  # List of arrays
        else:
            pass

    
        self.sigma1_element, self.sigma2_element, self.sigma12_element = self._transform_forces_to_stresses()

        # Allowables Initialization ------------------------------------------------------------------------------------
        # self.allowables = {n2p_element: {} for n2p_element in self._element_list}

        # for element, property in self._properties_elem.items():
        #     self.allowables[element] = {
        #         "Xt": [self.Materials[l.mat_ID].Allowables.XTensile for l in property.Laminate],
        #         "Xc": [self.Materials[l.mat_ID].Allowables.XCompressive for l in property.Laminate],
        #         "Yt": [self.Materials[l.mat_ID].Allowables.YTensile for l in property.Laminate],
        #         "Yc": [self.Materials[l.mat_ID].Allowables.YCompressive for l in property.Laminate],
        #         "S":  [self.Materials[l.mat_ID].Allowables.Shear for l in property.Laminate]
        #     }

        # Initialize Result Storage -------------------------------------------------------------------------------------
        self.TsaiWuResults = {n2p_element: [] for n2p_element in self._element_list}
        Failure_Results = {n2p_element: () for n2p_element in self._element_list}
        Order_Results = {n2p_element: [] for n2p_element in self._element_list}

        # Computation ---------------------------------------------------------------------------------------------------
        for n2p_element, allowables in self.allowables_elem.items():
            
            # Extract allowables for this element
            Xt, Xc = np.array(allowables["Xt"]), np.array(allowables["Xc"])
            Yt, Yc = np.array(allowables["Yt"]), np.array(allowables["Yc"])
            S = np.array(allowables["S"])

            # Compute Tsai-Wu coefficients
            F1, F2 = (1 / Xt - 1 / Xc), (1 / Yt - 1 / Yc)
            F11, F22, F66 = 1 / (Xt * Xc), 1 / (Yt * Yc), 1 / (S ** 2)
            F12 = -0.5 * np.sqrt(F11 * F22)

            # Initialize RF storage
            RF_values = np.full(len(Xt), np.nan)

            # Get stresses
            sigma1 = np.array(self.sigma1_element[n2p_element])
            sigma2 = np.array(self.sigma2_element[n2p_element])
            sigma12 = np.array(self.sigma12_element[n2p_element])

            sigma1 = np.array(sigma1, dtype=np.float64)
            sigma2 = np.array(sigma2, dtype=np.float64)
            sigma12 = np.array(sigma12, dtype=np.float64)


            # Identify valid (non-zero, non-NaN) stress cases
            valid = ~(np.isnan(sigma1) | np.isnan(sigma2) | np.isnan(sigma12)) & \
                    ~((sigma1 == 0) & (sigma2 == 0) & (sigma12 == 0))

            # Compute RF values for valid indices
            if np.any(valid):
                Q = F11 * sigma1**2 + 2 * F12 * sigma1 * sigma2 + F22 * sigma2**2 + F66 * sigma12**2
                L = F1 * sigma1 + F2 * sigma2

                RF_values[valid] = np.sqrt((L[valid]**2 + 4 * Q[valid]) - L[valid]) / (2 * Q[valid])

            # Store RF per element
            self.TsaiWuResults[n2p_element] = RF_values.tolist()

            # Determine minimum RF and its corresponding ply
            min_id = np.nanargmin(RF_values)
            min_value = RF_values[min_id]
            Failure_Results[n2p_element] = (min_value, min_id + 1)

            # Compute failure order
            sorted_indices = np.argsort(RF_values[RF_values < 1])
            failure_order = {RF_values[i]: rank + 1 for rank, i in enumerate(sorted_indices)}
            
            # Assign final output tuple for each ply
            Order_Results[n2p_element] = [(RF, failure_order.get(RF, 0)) for RF in RF_values]

        # Return results
        return self.TsaiWuResults, Failure_Results, Order_Results
        # -------------------------------------------------------------------------------------------------------------------------
    
# -----------------------------------------------------------------------------------------------------------------------------    

# MAXIMUM STRESS --------------------------------------------------------------------------------------------------------------

    def _calculate_Max_Stress(self, LC):
        """
        Method to implement the Maximum Stress failure criterion.

        This method evaluates failure modes (fiber failure) for 
        composite laminates under combined loading conditions.
        
        Returns:
            dict: Dictionary with N2PElement instances as keys and RF: lists as values.
        """

        # Stresses importation ------------------------------------------------------------------------------------------------
        self.Forces_element = self._extract_forces(LC)
        self.sigma1_element, self.sigma2_element, self.sigma12_element = self._transform_forces_to_stresses()

        # Allowables importation ----------------------------------------------------------------------------------------------
        self.allowables: dict = {n2p_element: [] for n2p_element in self._element_list}        
        for element, property in self._properties_elem.items():
            Xt = []
            Xc = []
            Yt = []
            Yc = []
            S = []

            self.allowables[element] = {"Xt":Xt, "Xc":Xc, "Yt": Yt, "Yc":Yc, "S": S}

            for lamina in property.Laminate:                
                Xt.append(self.Materials[lamina.mat_ID].Allowables.XTensile)
                Xc.append(self.Materials[lamina.mat_ID].Allowables.XCompressive)
                Yt.append(self.Materials[lamina.mat_ID].Allowables.YTensile)
                Yc.append(self.Materials[lamina.mat_ID].Allowables.YCompressive)
                S.append(self.Materials[lamina.mat_ID].Allowables.Shear)

        # Results dict initialisation -----------------------------------------------------------------------------------------
        self.MaxStressResults = { n2p_element: [] for n2p_element in self._element_list}

        Failure_Results = {n2p_element: () for n2p_element in self._element_list }

        Order_Results = { n2p_element: [] for n2p_element in self._element_list}

        # Computation ---------------------------------------------------------------------------------------------------------

        for n2p_element, property in self.allowables.items():
            Xt, Xc, Yt, Yc, S = (property[key] for key in ("Xt", "Xc", "Yt", "Yc", "S"))

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

    def _calculate_Tsai_Hill(self, LC):
        """
        Method to implement the Tsai-Hill failure criterion.

        This method evaluates failure modes (fiber failure) for 
        composite laminates under combined loading conditions.
        
        Returns:
            dict: Dictionary with N2PElement instances as keys and RF: lists as values.
        """

        # Stresses Importation
        self.Forces_element = self._extract_forces(LC)
        self.sigma1_element, self.sigma2_element, self.sigma12_element = self._transform_forces_to_stresses()

        # Allowables importation ----------------------------------------------------------------------------------------------
        self.allowables: dict = {n2p_element:[] for n2p_element in self._element_list}
        for element, property in self._properties_elem.items():
            Xt = []
            Xc = []
            Yt = []
            Yc = []
            S = []

            self.allowables[element] = {"Xt":Xt, "Xc":Xc, "Yt":Yc, "Yc":Yc, "S":S}

            for lamina in property.Laminate:
                Xt.append(self.Materials[lamina.mat_ID].Allowables.XTensile)
                Xc.append(self.Materials[lamina.mat_ID].Allowables.XCompressive)
                Yt.append(self.Materials[lamina.mat_ID].Allowables.YTensile)
                Yc.append(self.Materials[lamina.mat_ID].Allowables.YCompressive)
                S.append(self.Materials[lamina.mat_ID].Allowables.Shear)
        # Results dict intitialization ----------------------------------------------------------------------------------------
        self.TsaiHillResults = { n2p_element: [] for n2p_element in self._element_list}

        Failure_Results = {n2p_element: () for n2p_element in self._element_list }

        Order_Results = { n2p_element: [] for n2p_element in self._element_list}

        # Computation ---------------------------------------------------------------------------------------------------------
        for n2p_element, property in self.allowables.items():

            # Data acquisition on useful properties, from mechanical_prop:dict ------------------------------------------------
            
            Xt = property["Xt"]
            Xc = property["Xc"]
            Yt = property["Yt"]
            Yc = property["Yc"]
            S = property["S"]

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

    def _calculate_Hashin(self, LC):
        """
        Method to Implement the Hashin Failure Criterion.

        This method evaluates failure modes (fiber failure and matrix failure) for 
        composite laminates under combined loading conditions.
        
        Returns:
            dict: Dictionary with N2PElement instances as keys and RF:tuple (RF_fiber, RF_matrix) lists as values.
        """

        # Stresses importation ------------------------------------------------------------------------------------------------
        self.Forces_element = self._extract_forces(LC)
        self.sigma1_element, self.sigma2_element, self.sigma12_element = self._transform_forces_to_stresses()

        # Allowables importation ----------------------------------------------------------------------------------------------
        self.allowables: dict = {n2p_element: [] for n2p_element in self._element_list}
        for element, property in self._properties_elem.items():
            Xt = []
            Xc = []
            Yt = []
            Yc = []
            S = []

            self.allowables[element] = {"Xt": Xt, "Xc": Xc, "Yt": Yt, "Yc": Yc, "S": S}

            for lamina in property.Laminate:
                Xt.append(self.Materials[lamina.mat_ID].Allowables.XTensile)
                Xc.append(self.Materials[lamina.mat_ID].Allowables.XCompressive)
                Yt.append(self.Materials[lamina.mat_ID].Allowables.YTensile)
                Yc.append(self.Materials[lamina.mat_ID].Allowables.YCompressive)
                S.append(self.Materials[lamina.mat_ID].Allowables.Shear)

        # Results dict initialization -----------------------------------------------------------------------------------------
        self.HashinResults = {n2p_element: [] for n2p_element in self._element_list}

        Failure_Results = {n2p_element: () for n2p_element in self._element_list }

        Order_Results = { n2p_element: [] for n2p_element in self._element_list}

        # Computation ---------------------------------------------------------------------------------------------------------
        for n2p_element, property in self.allowables.items():
            # Data acquisition on useful properties, from mechanical_prop:dict ------------------------------------------------
            Xt = property["Xt"]
            Xc = property["Xc"]
            Yt = property["Yt"]
            Yc = property["Yc"]
            S = property["S"]

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

            # position_fiber, min_value_fiber = min(enumerate(RF_values_fiber), key=lambda x: x[1])

            # position_matrix, min_value_matrix = min(enumerate(RF_values_matrix), key=lambda x: x[1])
            
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

    def _calculate_Puck(self):
        """
        Method to implement the Puck Failure Criterion.

        This method evaluates failure modes (fiber failure and matrix failure) for 
        composite laminates under combined loading conditions.
        
        Returns:
            dict: Dictionary with N2PElement instances as keys and RF:tuple (RF_fiber, RF_matrix) lists as values.
        """

        # Stresses importation --------------------------------------------------------------------------------------------
        self.sigma1_element, self.sigma2_element, self.sigma12_element = self._extract_stresses()

        # Allowables importation ------------------------------------------------------------------------------------------
        self.allowables: dict = {n2p_element: [] for n2p_element in self._element_list}        
        for element, property in self._properties_elem.items():
            Xt = []
            Xc = []
            Yt = []
            Yc = []
            S = []
            tau12 = []  # Interlaminar shear strength (optional for some cases)

            self.allowables[element] = {"Xt":Xt, "Xc":Xc, "Yt":Yt, "Yc":Yc, "S":S, "tau12": tau12}

            for lamina in property.Laminate:                
                Xt.append(self.Materials[lamina.mat_id].Allowables.XTensile)
                Xc.append(self.Materials[lamina.mat_id].Allowables.XCompressive)
                Yt.append(self.Materials[lamina.mat_id].Allowables.YTensile)
                Yc.append(self.Materials[lamina.mat_id].Allowables.YCompressive)
                S.append(self.Materials[lamina.mat_id].Allowables.Shear)
                tau12.append(self.Materials[lamina.mat_id].Allowables.InterlaminarShear)

        # Results dictionary initialization -------------------------------------------------------------------------------
        self.PuckResults = { n2p_element: [] for n2p_element in self._element_list}

        # Computation -----------------------------------------------------------------------------------------------------
        for n2p_element, property in self.allowables.items():
            
            # Data acquisition for useful properties ----------------------------------------------------------------------
            Xt = property["Xt"]
            Xc = property["Xc"]
            Yt = property["Yt"]
            Yc = property["Yc"]
            S = property["S"]
            tau12 = property["tau12"]

            # Puck coefficients computation for each ply ------------------------------------------------------------------
            RF_fiber_values = []  
            RF_matrix_values = []  

            for lamina in range(len(Xt)):
                sigma1 = self.sigma1_element[n2p_element][lamina]
                sigma2 = self.sigma2_element[n2p_element][lamina]
                sigma12 = self.sigma12_element[n2p_element][lamina]

                # Fiber Failure Mode --------------------------------------------------------------------------------------
                if sigma1 >= 0:  # Tensile Fiber Failure
                    RF_fiber = (sigma1/Xt[lamina])**2 + (sigma12/S[lamina])**2
                else:  # Compressive Fiber Failure
                    RF_fiber = (sigma1/Xc[lamina])**2

                # Inter-Fiber Failure Mode --------------------------------------------------------------------------------

                if sigma2 >= 0:  # Matrix tensile failure
                    RF_matrix = (sigma2/Yt[lamina])**2 + (sigma12/S[lamina])**2
                else:  # Matrix compressive failure
                    RF_matrix = (sigma2/Yc[lamina])**2 + (sigma12/S[lamina])**2

                # Store results -------------------------------------------------------------------------------------------
                RF_fiber_values.append(RF_fiber)
                RF_matrix_values.append(RF_matrix)

            # Combine results per element ----------------------------------------------------------------------------------
            RF_values = [(rf_f, rf_m) for rf_f, rf_m in zip(RF_fiber_values, RF_matrix_values)]
            self.PuckResults[n2p_element] = RF_values

        # Return results --------------------------------------------------------------------------------------------------
        return self.PuckResults

# -----------------------------------------------------------------------------------------------------------------------------
      
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

        # T_sigma = np.array([
        #     [m**2, n**2,  2*m*n],
        #     [n**2, m**2, -2*m*n],
        #     [-m*n,  m*n, m**2 - n**2]
        # ])

        T_sigma = np.array([
            ([m_squared, n_squared, mn2]),
            ([n_squared, m_squared, -mn2]),
            ([-mn, mn, m_squared - n_squared])
        ])

        qr = np.matmul(Q_matrix, R)
        qrt = np.matmul(qr, T_sigma)
        qrtrinv = np.matmul(qrt, R_inv)
        qrtrinvs = np.matmul(qrtrinv, strain_k)
        
        # return Q_matrix @ R @ T_sigma @ R_inv @ strain_k  
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
            'Failure_Default': [("ID ENTITY", "i4"), ("RF", "f4"), ("Lamina", "i4")],
            'Order_Hashin_Puck': [("ID ENTITY", "i4"), ("RF_fiber", "f4"), ("order_fiber", "i4"),
                                ("RF_matrix", "f4"), ("order_matrix", "i4")],
            'Order_Default': [("ID ENTITY", "i4"), ("RF", "f4"), ("Order", "i4")]
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
            if failure_theory:
                initial_data = np.array([
                    (element.ID, *(FI_values[j] if j < len(FI_values) else (np.nan, np.nan)))
                    for element, FI_values in results_dict['Initial_Results'].items()
                    for j in range(max_sections['Initial_Results'])
                ], dtype=dtype_initial)
            else:
                initial_data = np.array([
                    (element.ID, FI_values[j] if j < len(FI_values) else np.nan)
                    for element, FI_values in results_dict['Initial_Results'].items()
                    for j in range(max_sections['Initial_Results'])
                ], dtype=dtype_initial)

            arrays_initial[:len(initial_data)] = initial_data.reshape(max_sections['Initial_Results'], n_elements)

            # Process `Failure_Results`
            failure_data = np.array([
                (element.ID, *failure) if isinstance(failure, tuple) and len(failure) == (4 if failure_theory else 2)
                else ((element.ID, np.nan, -1, np.nan, -1) if failure_theory else (element.ID, np.nan, -1))
                for element, failure in results_dict['Failure_Results'].items()
            ], dtype=dtype_failure)
            
            array_failure[:] = failure_data

            # Process `Order_Results`
            if failure_theory:
                order_data = np.array([
                    (element.ID, *(order[j] if j < len(order) else (np.nan, -1, np.nan, -1)))
                    for element, order in results_dict['Order_Results'].items()
                    for j in range(max_sections['Order_Results'])
                ], dtype=dtype_order)
            else:
                order_data = np.array([
                    (element.ID, *(order[j] if j < len(order) else (np.nan, -1)))
                    for element, order in results_dict['Order_Results'].items()
                    for j in range(max_sections['Order_Results'])
                ], dtype=dtype_order)

            arrays_order[:len(order_data)] = order_data.reshape(max_sections['Order_Results'], n_elements)

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

        self.init_res = np.array(list(self._Initial_Results.values()))
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
                print(i)


        else:

            # Isolating results. -----------------------------------------------------------------------------------------------------

            RFs_List_of_List = self.Ply_By_Ply_Results.values() # List of RFs lists per element. -------------------------------------
            RFs = [RF for List in RFs_List_of_List for RF in List] # Listof FIs per element. -----------------------------------------


            # Defining failure condition - failure will occur if RF < 1 every time it is not NaN. ------------------------------------

            failure = any(RF < 1 if not np.isnan(RF) else False for RF in RFs)


            i = 1
            print(i)

            MaxPLies = [property.NumPlies for property in self.Properties.values()]
            iter_limit = max(MaxPLies)

            j = 1

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

                # for element, original_property in self._properties_elem.items():
                #     RF_values = np.array(self.Ply_By_Ply_Results[element])

                #     # Check if any ply in the element fails
                #     if np.any((RF_values < 1) & ~np.isnan(RF_values)):
                        
                #         # Copy properties in place instead of creating a new instance
                #         property = CompositeShell()
                #         property.NumPlies = original_property.NumPlies
                #         property.thicknesses = original_property.thicknesses
                #         property.theta = original_property.theta
                #         property.simmetry = original_property.simmetry

                #         # Vectorized update of `isActive` for failed plies
                #         RF_min_values = np.array(RF_min[element])
                #         is_active_array = np.where((RF_values < 1) & ~np.isnan(RF_values) & np.isin(RF_values, RF_min_values), False, True)

                #         # Efficiently create updated `Lamina` objects
                #         property.Laminate = []
                #         for ply, is_active in zip(original_property.Laminate, is_active_array):
                #             lamina = Laminae()
                #             lamina.Ex = ply.Ex
                #             lamina.Ey = ply.Ey
                #             lamina.Nuxy = ply.Nuxy
                #             lamina.Nuyx = ply.Nuyx
                #             lamina.ShearXY = ply.ShearXY
                #             lamina.Qmatrix = ply.Qmatrix
                #             lamina.QBar = ply.QBar
                #             lamina.isActive = is_active

                #             property.Laminate.append(lamina)

                #         # Recalculate ABD matrix
                #         property.ABDMatrix = property._ABDMatrix()

                #         # Update element properties
                #         self._properties_elem[element] = property


                
                for element, original_property in self._properties_elem.items():

                    fail_elem = any(RF < 1 if not np.isnan(RF) else False for RF in self.Ply_By_Ply_Results[element])

                    if fail_elem:

                    
                        # addition = 1

                        property = CompositeShell()
                        property.NumPlies = original_property.NumPlies
                        property.thicknesses = original_property.thicknesses
                        property.theta = original_property.theta
                        property.simmetry = original_property.simmetry

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

                    # # Definition of Order_Results dict.
                    # if element not in self._Order_Results:
                    #     self._Order_Results[element] = [0] * len(self.Ply_By_Ply_Results[element])
                    
                    # output = self._Order_Results[element]
                    # RFs_below_1 = [(RF, j) for j, RF in enumerate(self.Ply_By_Ply_Results[element]) if RF < 1]

                    # if not RFs_below_1:
                    #     output = [(RF, 0) for RF in self.Ply_By_Ply_Results[element]]
                    #     self._Order_Results[element]= output
                    #     # continue
                    # else:
                    #     RFs_below_1.sort(reverse=False, key=lambda x:x[0])

                    #     for RF, j in RFs_below_1:
                    #         if isinstance(output[j], tuple):
                    #             continue
                    #         output[j] = (RF, addition_counter[element]+1)
                    #         addition_counter[element] += 1
                        
                    #     # for (FI, j) in enumerate(FIs_above_1, start=1):
                            
                    #     #     if isinstance
                    #     #     output[j] = (FI, addition_counter[element] + 1)
                    #     #     addition_counter[element] += 1

                    #     self._Order_Results[element] = output


                if self.FailureTheory == 'TsaiWu':
                    self.Ply_By_Ply_Results,_,_ = self._calculate_TsaiWu(LC, i)
                if self.FailureTheory == 'TsaiHill':
                    self.Ply_By_Ply_Results,_,_ = self._calculate_Tsai_Hill(LC)
                if self.FailureTheory == 'MaxStress':
                    self.Ply_By_Ply_Results,_,_ = self._calculate_Max_Stress(LC)

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
                    





                self.iter_res = np.array(list(self.Ply_By_Ply_Results.values()))
                self.init_res = np.where(np.isnan(self.iter_res), self.init_res, self.iter_res)

                for key, row in zip(self.Ply_By_Ply_Results.keys(), self.init_res):
                    self.Ply_By_Ply_Results[key] = row.tolist()



                condition = np.less(self.iter_res, 1.0)
                failure = np.any(condition)

                i += 1
                print(i)


        # En la última iteración se añaden los valores restantes, con índice 0.

        # if self.FailureTheory == 'Hashin':
        #     for element, values in self.Ply_By_Ply_Results.items():
        #         for k, (RF_fiber, RF_matrix) in enumerate(values):
        #             if isinstance(self._Order_Results[element][k], tuple): # is already assigned, don't modify
        #                 continue

        #             # Assign default failure orders(0) since thse plies never failed
        #             self._Order_Results[element][k] = (RF_fiber, 0, RF_matrix, 0)


        # else:

        #     self._Order_Results = {
        #         element: [
        #             (RF, 0) if not isinstance(self._Order_Results[element][k], tuple) else self._Order_Results[element][k]  
        #             for k, RF in enumerate(values)
        #         ]
        #         for element, values in self.Ply_By_Ply_Results.items()
        #     } 

            # for element, values in self.Ply_By_Ply_Results.items():
            #     for k, RF in enumerate(values):
            #         if isinstance(self._Order_Results[element][k], tuple):  # Si ya tiene un valor, no modificar
            #                     continue
            #         self._Order_Results[element][k] = (RF, 0)

                    # if FI < 1:
                    #     self.Order_Results[element][k] = (FI, 0)
                    # else:
                    #     continue



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
                condition = RFs < 1.0
                failure = np.all(condition)
                if failure:
                    RFs_Init = np.array(self._Initial_Results[element])
                    min_id = RFs_Init.argmin()
                    RF = RFs_Init[min_id]
                    Lamina_ID = min_id + 1
                    self._Failure_Results[element] = (RF, Lamina_ID)
                else:

                    failing_indices = np.where(RFs>=1)[0]
                    if failing_indices.size > 0:
                        min_id = failing_indices[RFs[failing_indices].argmin()]
                        RF = RFs[min_id]
                        Lamina_ID = min_id + 1
                        self._Failure_Results[element] = (RF, Lamina_ID)

        for element, original_property in self._properties_elem.items():
            [setattr(Lamina, "isActive", True) for Lamina in original_property.Laminate]  
            original_property.ABDMatrix = original_property._ABDMatrix()


        return self.Ply_By_Ply_Results, self._Initial_Results, self._Failure_Results, self._Order_Results