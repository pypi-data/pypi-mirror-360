"""Script for the definition of the class N2PNeuber."""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info.

from collections import defaultdict
import numpy as np
import subprocess
import importlib.util
import os
from typing import Union

from NaxToPy.Core.N2PModelContent import N2PModelContent
from NaxToPy.Core.N2PModelContent import load_model
from NaxToPy.Modules.common.model_processor import elem_to_material
from NaxToPy.Core.Classes.N2PMaterial import N2PMaterial
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core.Classes.N2PLoadCase import N2PLoadCase
from NaxToPy.Modules.common.material import Material
from NaxToPy import N2PLog
from NaxToPy.Modules.common.data_input_hdf5 import DataEntry
from NaxToPy.Modules.common.hdf5 import HDF5_NaxTo
from NaxToPy.Core.Classes.N2PComponent import _get_memory_usage


class N2PNeuber:
    """ Class used to obtain stresses using the Neuber method.

    Examples:
    
        >>> import NaxToPy as n2p
        >>> from NaxToPy.Modules.static.metallic import N2PNeuber
        >>> model = n2p.load_model(r"file path")
        >>> element_list = [(24581218, '0')]
        >>> n2pelem = model.get_elements(element_list)
        >>> n2plc = model._load_case(68195)
        >>> neuber = N2PNeuber() 
        >>> neuber.Model = model # compulsory input
        >>> neuber.Element_list = n2pelem # compulsory input
        >>> neuber.LoadCases = n2plc # compulsory input
        >>> neuber.calculate() # neuber stress are calculated
    """

    __slots__ = (
        '_model',
        '_element_list',
        '_load_cases_list',
        '_elem_to_n2pmat',
        '_n2pmaterials',
        '_materials',
        '_elem_to_mat',
        '_results',
        '_neuber_results',
        '_neuber_results_strain',
        '_transformed_data',
        '_component_map',
        '_element_map',
        '_section_map',
        '_hdf5',
        '_input_record_list',
        '_boolean',
        '_material_properties_array',
        '_strains_index',
        '_strains_map'
    )

    def __init__(self) -> None:
        # Mandatory attributes -----------------------------------------------------------------------------------------
        self._model: N2PModelContent = None
        self._element_list: list[N2PElement] = []
        self._load_cases_list: list[N2PLoadCase] = None

        # Materials attributes -----------------------------------------------------------------------------------------
        self._elem_to_n2pmat: dict[tuple[int, str], Material] = None
        self._n2pmaterials: dict[tuple[int, str], N2PMaterial] = None
        self._materials: dict[tuple[int, str], Material] = None
        self._elem_to_mat: dict[tuple[int, str], Material] = None

        # Results attributes -------------------------------------------------------------------------------------------
        self._results: np.ndarray = None
        self._neuber_results: np.ndarray = None
        self._neuber_results_strain: np.ndarray = None
        self._transformed_data: list[DataEntry] = []
        self._strains_index: int = 0
        self._strains_map: dict = {'STRESSES':0, 'STRAINS':1, 'BOTH':2}

        # Mapping attributes -------------------------------------------------------------------------------------------
        self._component_map: dict = {}
        self._element_map:dict = {}
        self._section_map: dict = {}

        # Memory control -----------------------------------------------------------------------------------------------
        self._boolean: bool = False

        # HDF5 ---------------------------------------------------------------------------------------------------------
        self._hdf5 = HDF5_NaxTo()
        self._input_record_list: list[DataEntry] = []
        self._transformed_data: list[DataEntry] = []
    # ------------------------------------------------------------------------------------------------------------------

    # region Getters
    # Method to obtain the model ---------------------------------------------------------------------------------------
    @property 
    def Model(self) -> N2PModelContent: 
        """
        Property that returns the model attribute, that is, the N2PModelContent to be analyzed. 
        """
        
        return self._model 
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the List of elements which is going to be analyzed ----------------------------------------------
    @property
    def ElementList(self) -> list[N2PElement]:
        """
        Property that returns the list of elements, that is, the list of elements to be analyzed.
        """
        
        return self._element_list
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the load cases ---------------------------------------------------------------------------------
    @property
    def LoadCaseList(self) -> list[N2PLoadCase]:
        """
        Property that returns the load_cases list, that is, the list of the IDs of the load cases to be analyzed. 
        """

        return self._load_cases_list
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain de dictionary of elements to N2PMaterial --------------------------------------------------------
    @property
    def Elem_to_N2PMaterial(self) -> dict[tuple[int, str], Material]:
        """
        Property that returns a dictionary that relates the elements to the N2PMaterial.
        """

        return self._elem_to_n2pmat
    # ------------------------------------------------------------------------------------------------------------------

    #Method to obtain the materials asigned to the elements ------------------------------------------------------------
    @property
    def Materials(self) -> dict[tuple[int, str], Material]:
        """
        Property that returns a list of the materials created.
        """

        return self._materials
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain de dictionary of elements to Material -----------------------------------------------------------
    @property
    def Elem_to_Material(self) -> dict[tuple[int, str], Material]:
        """
        Property that returns a dictionary that relates the elements to the Material.
        """
        return self._elem_to_mat
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain the list od N2PMaterials ------------------------------------------------------------------------
    @property
    def N2PMaterials(self) -> dict[tuple[int, str], N2PMaterial]:
        """
        Property that returns the list of N2PMaterials.
        """

        return self._n2pmaterials
    # ------------------------------------------------------------------------------------------------------------------

    # Method to obtain HDF5 attribute which contains all the necessary info to create it -------------------------------
    @property
    def HDF5(self) -> HDF5_NaxTo:
        """
        Property which returns the HDF5 attribute which contains all the necessary info to create it
        """

        return self._hdf5
    # -----------------------------------------------------------------------------------------------------------------

    # Method to obtain the boolean for Stress or Strains calculation --------------------------------------------------
    @property
    def ResultType(self) -> str:
        """
        Type of result that has been chosen.
        """
        return self._strains_map[self._strains_index]
    # -----------------------------------------------------------------------------------------------------------------

    # endregion

    # region Setters

    # Setters ----------------------------------------------------------------------------------------------------------
    @Model.setter 
    def Model(self, value: N2PModelContent) -> None: 
        self._model = value 
    # ------------------------------------------------------------------------------------------------------------------

    @ElementList.setter
    def ElementList(self, value: list[N2PElement]) -> None:
        if all(isinstance(element, N2PElement) for element in value):
            self._element_list = value
            self._reset_attributes()
            self._elem_to_mat, self._elem_to_n2pmat, self._materials, self._n2pmaterials = elem_to_material(self._model,self._element_list,True)
            if len(self._element_list) > 20000:
                dictionary_gen = transform_dict(self._elem_to_mat)
                self._model = load_model(self._model.FilePath, dict_gen = dictionary_gen, filter = "ELEMENTS")
                self._element_list = self._model.get_elements()
                self._boolean = True
        else:
            msg = N2PLog.Critical.C663()
            raise RuntimeError(msg)
    # ------------------------------------------------------------------------------------------------------------------

    @LoadCaseList.setter
    def LoadCaseList(self, value: list[N2PLoadCase]) -> None:
        if isinstance(value, list):
            if all(isinstance(lc, N2PLoadCase) for lc in value):
                self._load_cases_list = value
            else:
                msg = N2PLog.Critical.C664()
                raise RuntimeError(msg)     
        else:
            msg = N2PLog.Critical.C664()
            raise RuntimeError(msg)
    # ------------------------------------------------------------------------------------------------------------------

    @ResultType.setter
    def ResultType(self, value: str) -> None:
        if value == 'STRESSES':
            self._strains_index = 0
        elif value == 'STRAINS':
            self._strains_index = 1
        elif value == 'BOTH':
            self._strains_index = 2
        else:
            print('Invalid Input')

    # endregion

    # region Private Functions
    def _reset_attributes(self) -> None:
        """Reset the attributes to their initial values"""
        # Materials attributes -----------------------------------------------------------------------------------------
        self._elem_to_n2pmat: dict[tuple[int, str], Material] = None
        self._n2pmaterials: dict[tuple[int, str], N2PMaterial] = None
        self._materials: dict[tuple[int, str], Material] = None
        self._elem_to_mat: dict[tuple[int, str], Material] = None

        # Results attributes -------------------------------------------------------------------------------------------
        self._results = None
        self._neuber_results = None
        self._transformed_data = []
        self._neuber_results_strain = None
        
        # Mapping attributes -------------------------------------------------------------------------------------------
        self._component_map: dict = {}
        self._element_map:dict = {}
        self._section_map: dict = {}
    # ------------------------------------------------------------------------------------------------------------------

    def _reset_attributes_per_iteration(self) -> None:
        """Reset the attributes to their initial values"""
         # Results attributes -------------------------------------------------------------------------------------------
        self._results = None
        self._neuber_results = None
        self._transformed_data = []
        self._neuber_results_strain = None
        
        # Mapping attributes -------------------------------------------------------------------------------------------
        self._component_map: dict = {}
        self._element_map:dict = {}
        self._section_map: dict = {}

    def _get_stress_by_elem2(self) -> None:
        """
        Retrieves the stress results associated with the elements and stores them in a NumPy array.
        Optimized for performance.
        """

        # Precompute and store the loadcase/increment ID tuple
        lc_incr_list = [(lc.ID, lc.ActiveN2PIncrement.ID) for lc in self._load_cases_list]
        
        # Use list of predefined strings and search for first match
        input_string_result = next((r for r in ['STRESSES', 'S'] if r in self._load_cases_list[0].Results), None)
        
        # Use an assembly for faster search of unnecessary components
        unnecessary_component = {
            'LAYER', 'ANGLE_PRINCIPAL', 'PRINCIPAL_MAJOR', 'PRINCIPAL_MINOR', 'MARGIN_SAFETY',
            'MARGIN_OF_SAFETY_IN_TENSION', 'MARGIN_OF_SAFETY_IN_COMPRESSION', 'FIRST_PPAL_STRESS',
            'FIRST_PPAL_X-COS', 'SECOND_PPAL_X-COS', 'THIRD_PPAL_X-COS', 'OUT_OF_PLANE_PPAL', 'MEAN_PRESS',
            'OCTAHEDRAL_SHEAR_STRESS', 'SECOND_PPAL_STRESS', 'FIRST_PPAL_Y-COS', 'SECOND_PPAL_Y-COS',
            'THIRD_PPAL_Y-COS', 'THIRD_PPAL_STRESS', 'MIN_IN_PLANE_PPAL', 'FIRST_PPAL_Z-COS', 'SECOND_PPAL_Z-COS',
            'THIRD_PPAL_Z-COS', 'VON_MISES', 'VONMISES', 'FIRST_INVARIANT', 'SECOND_INVARIANT', 'THIRD_INVARIANT',
            'FIBER_DISTANCE', 'MAXIMUM_PRINCIPAL', 'MAX_IN_PLANE_PPAL', 'MINIMUM_PRINCIPAL', 'TRESCA_2D',
            'AXIAL_SAFETY_MARGIN', 'TORSIONAL_SAFETY_MARGIN', 'MAX_SHEAR', 'MAX_PPAL', 'MID_PPAL', 'MIN_PPAL', 'TRESCA', 'PRESS',
            'Von Mises', 'Max principal', 'Med principal', 'Min principal', 'ZZ', 'YZ', 'XZ'
        }

        # Get results and components in one step
        result_obj = self._load_cases_list[0].get_result(input_string_result)
        
        # Optimise grouping of components by section
        section_to_components = defaultdict(list)
        for component in result_obj.Components:
            if component not in unnecessary_component:
                for section in result_obj.get_component(component).Sections:
                    section_to_components[section.Name].append(component)

        # Create maps for faster search
        self._component_map = [{component: idx for idx, component in enumerate(components)}
                            for components in section_to_components.values()]
        self._section_map = {section: idx for idx, section in enumerate(section_to_components.keys())}
        self._element_map = {(ele.ID, ele.PartID): idx for idx, ele in enumerate(self._element_list)}
        
        # Pre-allocate array for results - store IDs as integers for efficiency
        num_sections = len(section_to_components)
        num_elements = len(self._element_list)
        num_load_cases = len(self._load_cases_list)
        num_rows = num_load_cases * num_elements * num_sections
        max_components = max(len(components) for components in section_to_components.values())
        num_columns = 4 + max_components
        
        # Preallocar with exact size
        all_results = np.full((num_rows, num_columns), np.nan, dtype=np.float32)
        
        row_idx = 0
        for section_name, components in section_to_components.items():
            # Get all results for this section in one go
            if not self._boolean:
                result = self.Model.get_result_by_LCs_Incr(
                    lc_incr_list, input_string_result, components, [section_name], filter_list=self._element_list
                )
            else:
                result = self.Model.get_result_by_LCs_Incr(
                    lc_incr_list, input_string_result, components, [section_name]
                )
            
            section_idx = self._section_map[section_name]
            num_components = len(components)
            
            # Vectorise assignment for each load case
            for lc_idx, lc in enumerate(self._load_cases_list):
                lc_id, incr_id = lc.ID, lc.ActiveN2PIncrement.ID
                
                # Process all elements at once for this load/increment/section combination
                for elem_idx, elem_id in enumerate(self._element_map.values()):
                    # Extract values for all components of this element
                    values = [result[(lc_id, incr_id, comp)][elem_id] for comp in components]
                    
                    # Fill the whole row with values and index information
                    all_results[row_idx, 0] = lc_id
                    all_results[row_idx, 1] = incr_id
                    all_results[row_idx, 2] = elem_id
                    all_results[row_idx, 3:3+num_components] = values
                    all_results[row_idx, -1] = section_idx
                    
                    row_idx += 1
        
        self._results = all_results
    # ------------------------------------------------------------------------------------------------------------------

    def _neuber_method_hsb(self, elastic_stress: float, modulus_e: float, yield_stress: float, exponent_n: float, element: Union[tuple,int]):
        """
        Solves the Neuber method equation using initial guesses and fsolve.
            
        Returns:
            float: Calculated stress value, or None if no solution is found.
        """
        # Define the Ramberg-Osgood equation to solve ------------------------------------------------------------------
        def equation(x):
            return (elastic_stress**2 / modulus_e) - x * ((x / modulus_e) + 0.002 * (x / yield_stress) ** exponent_n)

        # Attempt to solve with different initial guesses --------------------------------------------------------------
        initial_guesses = [0.1, 1, 10, 100, 1000]
        for x0 in initial_guesses:
            try:
                stress_val, = _f_solve(equation, x0)
                if abs(equation(stress_val)) < 1e-5:  # Ensure solution is close to zero
                    return stress_val
            except ValueError:
                continue
        N2PLog.Error.E674(element)
        N2PLog.set_console_level("CRITICAL")
        return None
    # ------------------------------------------------------------------------------------------------------------------

    def _neuber_method_fast(self):
        """
        Solves the Neuber method equation using initial guesses and root from scipy. This method uses a parallelization 
        process to optimize the calculation.
        """
        # start_time = time.time()
        
        module_e = self._material_properties_array[:, 0]
        yield_stress_arr = self._material_properties_array[:, 1]
        ro_exp = self._material_properties_array[:, 2]

        n_rows = self._results.shape[0]
        n_cols = self._results.shape[1] - 4  

        all_fsolve_result = np.full((n_rows, n_cols), np.nan)
        
        # Define the equation for the calculations
        def equation_single(sigma, sigma_e, E, sigma_y, n):
            """Neuber's Equation"""
            return (sigma_e**2 / E) - sigma * ((sigma / E) + 0.002 * (sigma / sigma_y) ** n)
        
        # Method which process each column
        def process_column(col_idx):
            result_col = col_idx + 3
            stress_comp = self._results[:, result_col]
            valid_mask = (~np.isnan(stress_comp)) & (abs(stress_comp) > yield_stress_arr)
            
            # Keep original values
            fsolve_result = np.copy(stress_comp)
            
            if np.any(valid_mask):
                indices = np.where(valid_mask)[0]
                
                # Get values only for valid indices
                stresses = stress_comp[indices]
                E_values = module_e[indices]
                sigma_y_values = yield_stress_arr[indices]
                n_values = ro_exp[indices]
                
                # Solving parallel batches of points
                def solve_point(i):
                    try:
                        # Use a positive initial value explicitly
                        x0 = abs(stresses[i]) * 0.95
                        
                        # ensure that we search in the positive interval
                        sol = root(
                            equation_single, 
                            x0,  # Valor inicial positivo
                            args=(abs(stresses[i]), E_values[i], sigma_y_values[i], n_values[i]),
                            method='hybr',
                            options={'xtol': 1e-6, 'maxfev': 100}
                        )
                        
                        if sol.success:
                            # Maintaining the original sign of the effort
                            result = abs(sol.x[0])
                            if stresses[i] < 0:
                                result = -result
                            return result
                        else:
                            N2PLog.Error.E675()
                            N2PLog.set_console_level("CRITICAL")
                            return stresses[i]  # Keep original value if it does not converge
                    except:
                        N2PLog.Error.E675()
                        N2PLog.set_console_level("CRITICAL")
                        return stresses[i]  # Keep original value if error
                
                # Parallel solving using multiple cores
                n_jobs = min(8, os.cpu_count() or 1)  # Use up to 8 cores
                
                # print(f"Procesando columna {col_idx+1} de {n_cols} con {len(indices)} puntos")
                batch_results = Parallel(n_jobs=n_jobs)(
                    delayed(solve_point)(i) for i in range(len(indices))
                )
                
                # Assign results
                fsolve_result[indices] = batch_results
                
            return fsolve_result
        
        # Process all columns
        for col_idx in range(n_cols):
            all_fsolve_result[:, col_idx] = process_column(col_idx)
            # elapsed = time.time() - start_time
            # print(f"Columna {col_idx+1}/{n_cols} completada en {elapsed:.2f} segundos")
        
        return all_fsolve_result
    # ------------------------------------------------------------------------------------------------------------------
    
    def _process_results_as_flat_array_fast(self):
        """
        Processes an array of results and computes corrected values for each stress component.

        Returns a flat NumPy array where each row contains:
            - Load Case
            - Element ID mapped
            - Corrected stress value (All components)
            - Section mapped

        Returns:
            None: Updates the self._neuber_results attribute.
        """

        inverted_element_map = {v: k for k, v in self._element_map.items()}

        # Make sure self._neuber_results has the same form as self._results
        self._neuber_results = np.copy(self._results)

        # Copy the first three columns and the last column of _results to _neuber_results
        self._neuber_results[:, :3] = self._results[:, :3]  # Copy the first three columns
        self._neuber_results[:, -1] = self._results[:, -1]  # Copy the last column


        # The array of materials needed for the neuber calculations is created.
        self._material_properties_array = np.empty((self._results.shape[0],3))
        for i, row in enumerate(self._results):
            self._material_properties_array[i,0] = self._elem_to_mat[inverted_element_map[row[2]]].Young
            self._material_properties_array[i,1] = self._elem_to_mat[inverted_element_map[row[2]]].Allowables.Yield_stress
            self._material_properties_array[i,2] = self._elem_to_mat[inverted_element_map[row[2]]].Allowables.RO_exponent

        self._neuber_results[:, 3:-1] = self._neuber_method_fast()
        N2PLog.set_console_level("WARNING")
        
        
        
        return None
    # ------------------------------------------------------------------------------------------------------------------

    def _process_results_as_flat_array(self):
        """
        Processes an array of results and computes corrected values for each stress component.

        Returns a flat NumPy array where each row contains:
            - Load Case
            - Element ID mapped
            - Corrected stress value (All components)
            - Section mapped

        Returns:
            None: Updates the self._neuber_results attribute.
        """

        inverted_element_map = {v: k for k, v in self._element_map.items()}
        material_properties = {
            key: (value.Young, value.Allowables.Yield_stress, value.Allowables.RO_exponent)
            for key, value in self._elem_to_mat.items()
        }
        count = 0
        num_rows_num_column = self._results.shape
        self._neuber_results = np.zeros((num_rows_num_column))

        # Iterate through each row in the results array
        for row in self._results:
            # Extract LoadCase, Element_ID, Increment_ID, and Section
            load_case = row[0]
            increment_id = row[1]
            element_id = row[2]
            section = row[-1]  # Last column
            

            element = inverted_element_map[element_id]
            modulus_e, yield_stress, exponent_n = material_properties[element]

            # Initialize the processed data row
            processed_data = [load_case, increment_id, element_id]

            # Process each stress component
            for i in range(3, len(row) - 1):  # Components are after the first 3 indices and before the section
                
                component_value = row[i]

                if not np.isnan(component_value) and abs(component_value) > yield_stress:  # Skip NaN values
                    corrected_value = self._neuber_method_hsb(
                        abs(component_value), modulus_e, yield_stress, exponent_n, element
                    )
                    if component_value < 0:
                        component_value = -component_value
                else:
                    corrected_value = component_value  # Keep NaN if present

                # Add the corrected value to the row
                processed_data.append(corrected_value)
            
            # Add the section ID to the row
            processed_data.append(section)

            self._neuber_results[count] = processed_data
            count = count + 1
        N2PLog.set_console_level("WARNING")

        return None
    # ------------------------------------------------------------------------------------------------------------------
    
    def _transform_data(self) -> None:
        """
        Transforms the data in self._neuber_results and self._neuber_results_strain
        into DataEntry instances, grouped by section and split by parts.

        Optimised version to improve performance with large datasets.
        """
        attributes_to_process = [
            ('_neuber_results', 'STRESS_NEUBER')
            # ('_neuber_results_strain', 'STRAIN_NEUBER')
        ]

        # Invert mapping dictionaries
        inverted_element_map = {v: k for k, v in self._element_map.items()}
        loadcase_name_map = {lc.ID: lc.Name for lc in self._load_cases_list}
        inverted_section_map = {value: key for key, value in self._section_map.items()}
        
        # Parts mapping
        part_id_map = self._model._N2PModelContent__StrPartToID
        
        transformed_data = []
        
        for results_attribute, results_name in attributes_to_process:
            results_data = getattr(self, results_attribute, None)
            if results_data is None:
                raise ValueError(f"Attribute '{results_attribute}' does not exist or is None.")
            
            # Convert results_data to numpy array for faster processing
            results_array = np.array(results_data, dtype=object)
            
            # Extract relevant columns for grouping
            loadcase_ids = results_array[:, 0]
            increment_ids = results_array[:, 1]
            element_ids = results_array[:, 2]
            sections = results_array[:, -1]
            
            # Using a dictionary approach for more efficient clustering
            grouped_indices = {}
            for idx, (lc, inc, sec) in enumerate(zip(loadcase_ids, increment_ids, sections)):
                key = (lc, inc, sec)
                if key not in grouped_indices:
                    grouped_indices[key] = []
                grouped_indices[key].append(idx)
            
            # Process each set of data
            for (loadcase_id, increment_id, section), indices in grouped_indices.items():
                # Obtain components for this section
                components_list = list(self._component_map[int(section)].keys())

                # Extracting relevant rows at once using fancy indexing
                rows = results_array[indices]
                
                # Extraer element_ids para estas filas
                group_element_ids = rows[:, 2]
                
                # Extract element_ids for these rows
                part_indices = {}
                for idx, element_id in enumerate(group_element_ids):
                    element_key = inverted_element_map.get(element_id)
                    if element_key:
                        part = element_key[1]
                        if part not in part_indices:
                            part_indices[part] = []
                        part_indices[part].append(idx)
                
                # Process each part
                for part, part_idx in part_indices.items():
                    part_rows = rows[part_idx]
                    
                    # Extract only the columns we need (element_id and components)
                    element_ids = part_rows[:, 2].astype(np.int32)
                    components_data = part_rows[:, 3:-1].astype(np.float64)
                    
                    # Check for valid data (not all NaN in components)
                    valid_mask = ~np.all(np.isnan(components_data), axis=1)
                    if not np.any(valid_mask):
                        continue
                    
                    # Filter only valid rows
                    filtered_element_ids = element_ids[valid_mask]
                    filtered_components = components_data[valid_mask]
                    
                    # Replace element IDs with their original values
                    original_element_ids = np.array([inverted_element_map[eid][0] for eid in filtered_element_ids])
                    
                    # Determine non-NaN columns
                    nan_cols = np.all(np.isnan(filtered_components), axis=0)
                    valid_components = [components_list[i] for i in range(len(components_list)) if i < len(nan_cols) and not nan_cols[i]]
                    
                    # Create filtered dtype
                    filtered_dtype = [('ID_ENTITY', 'i4')] + [(name, 'f8') for name in valid_components]
                    
                    # Create structured array directly
                    result_count = len(original_element_ids)
                    result_data = np.zeros(result_count, dtype=filtered_dtype)
                    result_data['ID_ENTITY'] = original_element_ids
                    
                    # Copy only valid components
                    for i, comp_name in enumerate(valid_components):
                        col_idx = components_list.index(comp_name)
                        if col_idx < filtered_components.shape[1]:
                            result_data[comp_name] = filtered_components[:, col_idx]
                    
                    # Only create the entry if we have valid data
                    if len(result_data) > 0 and len(result_data.dtype) > 2:
                        entry = DataEntry()
                        entry.LoadCase = int(loadcase_id)
                        entry.LoadCaseName = loadcase_name_map.get(loadcase_id, "")
                        entry.Increment = int(increment_id)
                        entry.Section = inverted_section_map.get(section, None)
                        entry.Data = result_data
                        entry.ResultsName = results_name
                        entry.Part = repr((part_id_map[part], part))
                        
                        transformed_data.append(entry)
        
        self._transformed_data = transformed_data
        return transformed_data
    # ------------------------------------------------------------------------------------------------------------------

    def _prepare_input_data(self) -> None:
        dtype_in = [
            ("Material ID", "S30" if self.Model.Solver == 'Abaqus' else "i4"),
            ("RO_exponent", "i4"), 
            ("Yield Stress", "i4")]
        input_list = []
        for mat in list(self._materials.values()):
            input_each_mat = [mat.ID, mat.Allowables.RO_exponent, mat.Allowables.Yield_stress]
            input_list.append(input_each_mat)

        input_list = np.array([tuple(row) for row in input_list], dtype=dtype_in)
        
        input_instance = DataEntry()
        input_instance.DataInput = input_list
        input_instance.DataInputName = 'Materials Input'
        self._input_record_list.append(input_instance)

        input_list = self.Model.FilePath
        input_instance = DataEntry()
        input_instance.DataInput = input_list
        input_instance.DataInputName = 'Model Path'
        self._input_record_list.append(input_instance)
        
        return None
    # ------------------------------------------------------------------------------------------------------------------

    # endregion

    # region Public Functions 
    def Ramberg_Osgood_curve(self, elements: list[N2PElement]):
        """
        Plots the Ramberg-Osgood curves for a given list of elements.

        This method generates stress-strain curves for the materials associated with 
        the provided elements.

        Args:
            elements (list[N2PElement]): A list of elements for which the Ramberg-Osgood curves 
                are to be plotted. Each element is mapped to a material with the required properties 
                (Young's modulus, yield stress, and Ramberg-Osgood exponent).

        Returns:
            Plot:
                - X-axis: Strain
                - Y-axis: Stress
                - A curve for each unique material with a legend displaying:
                    - E: Young's modulus
                    - YS: Yield stress
                    - n: Ramberg-Osgood exponent
                - Gridlines, axis labels, and a title for better readability.
        """
            
        try:
            if importlib.util.find_spec("matplotlib") is None:
                subprocess.call(['pip', 'install', "matplotlib"])
    
            import matplotlib.pyplot as plt
        except RuntimeError:
            msg = N2PLog.Critical.C106()
            raise RuntimeError(msg)
        
        plt.figure(figsize=(10, 6))  # Set the figure size

        plotted_materials = set()  # To avoid redundant plotting for materials

        for element in elements:
            material = self._elem_to_mat[element]

            # Extract material properties
            modulus_e = material.Young
            yield_stress = material.Allowables.Yield_stress
            exponent_n = material.Allowables.RO_exponent

            # Check if the material is already plotted
            material_id = (modulus_e, yield_stress, exponent_n)
            if material_id in plotted_materials:
                continue

            plotted_materials.add(material_id)

            # Generate stress values
            stress = np.linspace(1e-6, yield_stress * 1.5, 500)  # Avoid division by zero

            # Calculate the Ramberg-Osgood strain
            strain_ro = (stress / modulus_e) + 0.002 * (stress / yield_stress) ** exponent_n
            strain_elastic = stress / modulus_e

            # Neuber hyperbola calculation
            neuber_constant = yield_stress * (yield_stress / modulus_e)  # C = sigma_yield * epsilon_yield
            neuber_strain = neuber_constant / stress  # Direct calculation of the hyperbola

            # Find intersection points for filtering Neuber hyperbola
            intersection_indices = np.where((neuber_strain >= strain_elastic) & (neuber_strain <= strain_ro))[0]
            if len(intersection_indices) > 0:
                start_idx = max(0, intersection_indices[0] - 100)  # Add extra points for visibility
                end_idx = min(len(stress), intersection_indices[-1] + 100)  # Add extra points for visibility

                stress_filtered = stress[start_idx:end_idx]
                neuber_strain_filtered = neuber_strain[start_idx:end_idx]

                # Plot the Neuber hyperbola (filtered)
                plt.plot(neuber_strain_filtered, stress_filtered, linestyle='-.', color='red', label='Neuber-Hyperbola')

            # Plot the Ramberg-Osgood curve
            plt.plot(strain_ro, stress, label='Ramber-osgood curve')

            # Plot the elastic curve
            plt.plot(strain_elastic, stress, linestyle='--', label='Elastic curve')

        # Finalize the plot
        plt.title("Ramberg-Osgood curves")
        plt.xlabel("Strain")
        plt.ylabel("Stress")
        plt.axhline(0, color='black', linewidth=0.8)
        plt.axvline(0, color='black', linewidth=0.8)
        plt.grid(color='gray', linestyle='--', linewidth=0.5)
        plt.xlim(0, max(strain_ro) / 32)
        plt.legend()
        plt.show()
    # ------------------------------------------------------------------------------------------------------------------


    def calculate(self) -> None:
        """
        Executes all necessary calculations as the final step in the workflow.

        Returns:
            None
        """
        # Check if all the inputs are given by the user ----------------------------------------------------------------
        for pos, material in enumerate(self._materials.values()):
            if material.Allowables.Yield_stress is None:
                msg = N2PLog.Critical.C661()
                raise RuntimeError(msg)
            if material.Allowables.RO_exponent is None:
                msg = N2PLog.Critical.C662()
                raise RuntimeError(msg)

        # Calculate the final result -----------------------------------------------------------------------------------
        original_load_cases = self._load_cases_list[:]

        self._hdf5.create_hdf5()
        self._prepare_input_data()
        self._hdf5._modules_input_data(self._input_record_list)

        _, _, initial_memory = _get_memory_usage()

        # First iteration with 5 load cases ----------------------------------------------------------------------------
        num_total_load_cases = len(original_load_cases)
        num_lc_per_it = min(5, num_total_load_cases)
        self._load_cases_list = original_load_cases[:num_lc_per_it]

        self._get_stress_by_elem2()

        if importlib.util.find_spec("joblib") and importlib.util.find_spec("scipy"):
            from joblib import Parallel, delayed
            from scipy.optimize import root
            self._process_results_as_flat_array_fast()
        else:
            self._process_results_as_flat_array()


        self._transform_data()

        _, available_memory, final_memory = _get_memory_usage()
        used_memory = final_memory - initial_memory
        used_memory = max(used_memory, 100)  # Asegurar mínimo de 100
        num_lc_per_it = int(available_memory * 0.8 / (used_memory / num_lc_per_it))

        if not self.HDF5.MemoryFile:
            self.HDF5.write_dataset(self._transformed_data)
            self._reset_attributes_per_iteration()

        #---------------------------------------------------------------------------------------------------------------

        # Iterate on the remaining cases -------------------------------------------------------------------------------
        if num_total_load_cases > 5:
            for i in range(5, num_total_load_cases, num_lc_per_it):
                self._load_cases_list = original_load_cases[i:min(i + num_lc_per_it, num_total_load_cases)]
                
                self._get_stress_by_elem2()

                if importlib.util.find_spec("joblib") is not None and importlib.util.find_spec("scipy") is not None:
                    self._process_results_as_flat_array_fast()
                else:
                    self._process_results_as_flat_array()

                self._transform_data()

                if not self.HDF5.MemoryFile:
                    self.HDF5.write_dataset(self._transformed_data)
                    self._reset_attributes_per_iteration()

        if not self.HDF5.MemoryFile:
            self.HDF5.write_dataset(self._transformed_data)
        
        # --------------------------------------------------------------------------------------------------------------

        self._load_cases_list = original_load_cases

    # ------------------------------------------------------------------------------------------------------------------

    # endregion

# region Replicated Functions

def _jacobian(f, x, h=1e-5):
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

def _newton_raphson(f, x0, tol=1e-8, max_iter=100):
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
        J = _jacobian(f, x)
        try:
            dx = np.linalg.solve(J, -fx)
        except np.linalg.LinAlgError:
            raise ValueError("Jacobian is singular, try a different initial guess")
        x += dx
    raise ValueError("No convergence: reached max_iter")

def _f_solve(func, x0):
    """
    Finds the roots of a nonlinear equation or system of equations.

    Parameters:
    func (callable): Function representing the equation or system. It must return an array.
    x0 (array-like): Initial guess for the root.

    Returns:
    numpy.ndarray: Computed root of the equation/system.
    """
    x0 = np.atleast_1d(x0)  # Ensure input is an array
    return _newton_raphson(func, x0)


# endregion

# region Useful Functions
def transform_dict(original_dict):
    grouped_dict = defaultdict(list)
    for element_id, part_id in original_dict.keys():
        grouped_dict[str(part_id)].append(element_id)  # O(1) inserción
    return dict(grouped_dict)
# endregion

# region Desactivated Methods

# def reserve_factor_calculation_stress_strain_law(elastic_stress,e_modulus, neuber_allowable_strain, proof_stress, index):
#     """Calculates the reserve factor usign elastic-perfectly plastic stress-strain law

#     Args:
#         elastic_stress (float): Elastic stress value.
#         e_ modulus (float): Modulus of elasticity.
#         neuber_allowable_strain (float): Neuber allowable strain value.
#         proof_stress (float): Proof stress value.

#     Returns:
#         float: Calculated reserve factor.
#     """

#     reserve_factor = ((neuber_allowable_strain*proof_stress*e_modulus+proof_stress**2)**0.5)/(elastic_stress)

#     print(f"Calculated Neuber Reserve Factor for the problem {index + 1} usig elastic-perfectly plastic stress-strain law is: {round(reserve_factor, 2)}")
#     if reserve_factor < 1:
#         print("Warning: The Neuber Reserve Factor is less than 1")
    
#     return reserve_factor

# def get_neuber_result(self, lc: int, component: str, section: str, element_id: int, part_id: str = '0') -> float:
#     """
#     Retrieves the Neuber method result for a specific load case, stress component, element-part, 
#     and section.

#     Args:
#         lc (int): Identifier of the load case.
#         component (str): The stress component to retrieve.
#         element_id (int): Identifier of the element.
#         part_id (str, optional): Identifier of the part containing the element. Defaults to '0'.
#         section (str): Section identifier for filtering results.

#     Returns:
#         float: The Neuber stress result for the specified parameters.
#     """
#     # Obtain indices from the maps
#     section_index = self._section_map[section]
#     component_index = self._component_map[section_index][component]
#     element_index = self._element_map[(element_id, part_id)]


#     # Filter results in the combined array -------------------------------------------------------------------------
#     filtered = self._neuber_results[
#         (self._neuber_results[:, 0] == lc) &  # Filter by Load Case
#         (self._neuber_results[:, 2] == element_index) &    # Filter by element
#         (self._neuber_results[:, -1] == section_index)     # Filter by section (added column)
#     ]
#     return filtered[0, 3 + component_index]
# endregion
