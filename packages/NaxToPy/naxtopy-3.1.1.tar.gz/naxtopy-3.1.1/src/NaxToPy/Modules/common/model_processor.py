"""Script for the definition of the class model_Processor and its methods"""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

import numpy as np
import sys

from NaxToPy.Core.N2PModelContent import N2PModelContent
from NaxToPy import N2PLog
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Modules.common.material import Orthotropic, Isotropic, AllowablesISO, AllowablesORTO
from NaxToPy.Modules.common.property import CompositeShell, Shell, Sandwich



def get_n2pmaterials_iso(model: N2PModelContent, element_list: list[N2PElement]) -> dict:
    """
    Function which creates a dictionary that relates the element with the n2pmaterial
    and filters out elements that trigger warnings from the original element_list.
    """
    elem_material_dict = {}
    valid_elements = []
    warning_logged = False
    property_dict = model.PropertyDict
    material_dict = model.MaterialDict
    solver = model.Solver
    
    # Predefine property type mappings to avoid repeated conditionals
    nastran_material_id_map = {
        'PSHELL': lambda prop: prop.MatMemID,
        'PSOLID': lambda prop: prop.MatID,
        'PBEAM': lambda prop: prop.MatID,
        'PROD': lambda prop: prop.MatID
    }
    
    abaqus_material_id_map = {
        'HomogeneousShellSection': lambda prop: prop.MatMemID,
        'HomogeneousSolidSection': lambda prop: prop.MatID
    }
    
    for element in element_list:
        id_prop = element.Prop
        if id_prop[0] == 0:
            if not warning_logged:
                N2PLog.Warning.W651()
                warning_logged = True
            continue
            
        prop = property_dict[id_prop]
        prop_type = prop.PropertyType
        
        # Handle Nastran solver
        if prop_type in nastran_material_id_map:
            material_id = nastran_material_id_map[prop_type](prop)
            n2pmat = material_dict[material_id]
            
            if n2pmat.MatType in ['MAT1', 'ISOTROPIC']:
                elem_material_dict[(element.ID, element.PartID)] = n2pmat
                valid_elements.append(element)
            elif not warning_logged:
                N2PLog.Warning.W651()
                warning_logged = True
                
        # Handle Abaqus solver
        elif solver == 'Abaqus' and prop_type in abaqus_material_id_map:
            material_id = abaqus_material_id_map[prop_type](prop)
            n2pmat = material_dict[material_id]
            
            if n2pmat.MatType in ['ISOTROPIC']:
                elem_material_dict[(element.ID, element.PartID)] = n2pmat
                valid_elements.append(element)
            elif not warning_logged:
                N2PLog.Warning.W651()
                warning_logged = True
                
        # Handle unsupported property types
        elif not warning_logged:
            N2PLog.Warning.W651()
            warning_logged = True
    
    # Replace the original element list with the filtered one
    element_list[:] = valid_elements

    return elem_material_dict

def get_np_array_from_result_new_report(model,result, element_map:dict, component_map: dict):
    """
    Processes the results array and returns the processed data and necessary mappings.   
    """

    # Create the aux variable which helps with the lecture of results
    aux = 0 if len(result.Body[0]) - len(component_map) == 4 else 1

    # Determine the order of indices based on component_map
    header_order = [list(result.Headers).index(header) for header in component_map.keys()]

    data = []

    # Process each row in the result.Body
    for row in result.Body:
        load_case = int(row[0])  # Load Case ID
        increment_id = int(row[1])
        element_id = int(row[3])  # Element ID
        part_id = str(row[4]) if aux == 1 else model.Parts[0]

        if (element_id, part_id) not in element_map:
            element_map[(element_id, part_id)] = len(element_map)

        # Create a row combining mapping values and component values
        row_data = [
            load_case,
            increment_id,
            element_map[(element_id, part_id)]
        ]

        # Add component values in the specified order
        for i in header_order:
            component_value = float(row[i])
            row_data.append(component_value)

        # Append the complete row to the data array
        data.append(row_data)

    # Convert the data list into a NumPy array
    data_array = np.array(data)
    return data_array


        

# Uso general para todos los módulos -----------------------------------------------------------------------------------
def get_n2pmaterials(model: N2PModelContent, element_list: list[N2PElement]) -> dict:
    """
    Function which creates a dictionary that relates the element with the n2pmaterial
    and filters out elements that trigger warnings from the original element_list.
    """
    elem_material_dict = {}
    for i in range(len(element_list)):
        id_prop = element_list[i].Prop
        if id_prop[0] == 0:
            continue

        # Como en Abaqus puede darse el caso de que una property este asociada a un elemento pero no tenga información,
        # se utiliza el metodo get() del diccionario para que estas properties tengan un None en lugar de dar error
        prop = model.PropertyDict.get(id_prop)

        if model.Solver in ['InputFileNastran', 'Nastran','H3DOptistruct']:
            if prop.PropertyType in ['PSHELL']:
                # Handle PSHELL case (single material ID)
                material_id = prop.MatMemID
                n2pmat = model.MaterialDict[material_id]
                elem_material_dict[(element_list[i].ID, element_list[i].PartID)] = n2pmat

            elif prop.PropertyType in ['PCOMP','PBAR','PBEAM','PROD','PWELD','PFAST','PSHEAR','PSOLID']:
                material_ids = prop.MatID
                n2pmats = [model.MaterialDict[material_id] for material_id in material_ids]
                elem_material_dict[(element_list[i].ID, element_list[i].PartID)] = n2pmats


        elif model.Solver in ['InputFileAbaqus','Abaqus']:
            if prop:
                if prop.PropertyType == 'HomogeneousShellSection':
                    material_id = prop.MatMemID
                    n2pmat = model.MaterialDict[material_id]
                    elem_material_dict[(element_list[i].ID, element_list[i].PartID)] = n2pmat

                elif prop.PropertyType == 'HomogeneousSolidSection':
                    material_id = prop.MatID
                    n2pmat = model.MaterialDict[material_id]
                    elem_material_dict[(element_list[i].ID, element_list[i].PartID)] = n2pmat

                elif prop.PropertyType == 'CompositeShellSection':
                    material_ids = prop.MatID
                    n2pmats = [model.MaterialDict[material_id] for material_id in material_ids]
                    elem_material_dict[(element_list[i].ID, element_list[i].PartID)] = n2pmats

        else: #Solver not known (or not implemented in the module yet)
            msg = N2PLog.Critical.C860(model.Solver)
            raise Exception(msg)

    return elem_material_dict


def create_material(material, materials, n2pmaterials):
    """ Helper function to create and store material instances """
    material_key = (material.ID, material.PartID)
    
    if material_key not in materials:
        mat_type = material.MatType
        
        if mat_type in ['MAT1', 'ISOTROPIC']:
            material_instance = Isotropic(material)
            material_instance.Allowables = getattr(material_instance, "Allowables", AllowablesISO())
        elif mat_type in ['MAT2', 'MAT8', 'LAMINA']:
            material_instance = Orthotropic(material)
            material_instance.Allowables = getattr(material_instance, "Allowables", AllowablesORTO())
        elif mat_type == 'UNDEF':
            elastic_type = material.QualitiesDict.get('Elastic type')
            if elastic_type == "ENGINEERING_CONSTANTS":
                material_instance = Orthotropic(material)
                material_instance.Allowables = getattr(material_instance, "Allowables", AllowablesORTO())
            elif elastic_type == "ORTHOTROPIC":
                raise NotImplementedError("Orthotropic Elastic Type still not implemented")
            else:
                raise NotImplementedError("Elastic type not defined")
        else:
            return None  # Unrecognized material type
        
        materials[material_key] = material_instance
        n2pmaterials[material_key] = material
    
    return materials[material_key]

def elem_to_material(model: N2PModelContent, element_list: list[N2PElement], onlyisotropic: bool = False) -> dict:
    """
    Maps elements to their corresponding material instances.
    Handles both PSHELL (single material) and PCOMP (list of materials) cases.
    """
    elem_to_mat = {}
    materials = {}
    n2pmaterials = {}

    # Retrieve the element-to-material mapping
    elem_to_n2pmat = (get_n2pmaterials_iso if onlyisotropic else get_n2pmaterials)(model, element_list)
    
    if model.Solver in ['InputFileNastran', 'Nastran', 'AbaqusInputFile', 'Abaqus','H3DOptistruct']:
        for elem_id, n2pmaterial in elem_to_n2pmat.items():
            if isinstance(n2pmaterial, list):  # Composite material case
                elem_to_mat[elem_id] = [create_material(mat, materials, n2pmaterials) for mat in n2pmaterial]
            else:  # Single material case
                elem_to_mat[elem_id] = create_material(n2pmaterial, materials, n2pmaterials)
    else:
        N2PLog.Critical.C860(model.Solver)
        sys.exit()
    return elem_to_mat, elem_to_n2pmat, materials, n2pmaterials

# ----------------------------------------------------------------------------------------------------------------------
def get_properties(model: N2PModelContent, element_list: list[N2PElement]) -> dict:
    """
    Extracts and constructs property dictionaries for elements with CompositeShell instances.

    Args:
        model (N2PModelContent): Model containing property and material data.
        element_list (list[N2PElement]): List of elements to process.

    Returns:
        tuple: A dictionary of unique properties and a dictionary mapping elements to their properties.
    """
    properties_elem = {}
    properties_unique = {}

    for element in element_list:
        n2p_property = model.PropertyDict[element.Prop]

        # Lazy instantiation of CompositeShell only if needed
        if n2p_property.PropertyType == 'PCOMP'or n2p_property.PropertyType == 'CompositeShellSection':
            prop_obj = properties_unique.get(n2p_property.ID)  # Check if already created
            if not prop_obj:
                prop_obj = CompositeShell(n2p_property, model.MaterialDict)

        elif n2p_property.PropertyType == 'PSHELL'or n2p_property.PropertyType in ['ShellSection','HomogeneousShellSection', 'HomogeneousSolidSection']:
            prop_obj = properties_unique.get(n2p_property.ID)  # Check if already created
            if not prop_obj:
                prop_obj = Shell(n2p_property, model.MaterialDict)            
        else:
            prop_obj = n2p_property

        # Store in dictionaries
        properties_elem[element] = prop_obj
        if prop_obj.ID not in properties_unique:
            properties_unique[prop_obj.ID] = prop_obj

    return properties_unique, properties_elem

def get_sandwich_properties(core_type:str, model: N2PModelContent, element_list: list[N2PElement], mat_dict: dict) -> dict:
    """
    Extracts and constructs sandwich dictionaries for elements with Sandwich instances.

    Args:
        model (N2PModelContent): Model containing property and material data.
        element_list (list[N2PElement]): List of elements to process.

    Returns:
        dict: A dictionary of unique sandwich and a dictionary mapping elements to their sandwich structure.
    """
    sandwich_elem = {}
    for element in element_list:
        n2p_property = model.PropertyDict[element.Prop]
        sandwich_obj = Sandwich(core_type,n2p_property=n2p_property,n2p_material=model.MaterialDict, mat_dict=mat_dict)
        sandwich_elem[element] = sandwich_obj


    return sandwich_elem
