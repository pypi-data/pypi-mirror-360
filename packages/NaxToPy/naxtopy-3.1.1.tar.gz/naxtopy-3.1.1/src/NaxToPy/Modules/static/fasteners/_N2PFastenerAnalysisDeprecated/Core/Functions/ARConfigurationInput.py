import os
from io import open
import NaxToPy as N2P
import json


def get_config_data(path_file: str) -> dict:
    """ Function which reads a txt file with Json Format and obtains the corresponding Configuration Data that will be
        used in the study itself, which will be stored in a dictionary.
           
        Args: 
            path_file: str

        Returns:
            configuration_data : dict

        Calling example:

                data = get_config_data(path_file = jsontxt_path)
      
    """
    if os.path.exists(path_file) and os.path.isfile(path_file):
        with open(path_file, 'r') as file:
            data_json = json.load(file) # Reading of the file in json format.

        configuration_data = {} # Definition of the dictionary where all the data will be stored.

        ##################################### MISC DATA ##################################

        analysis_name = data_json["Analysis Name"]
        analysis_type = data_json["Joints Analysis Type"]

        ##################################### INPUT FILES ################################

        model_fem = data_json["Input Files"].get("Model FEM")
        model_results = data_json["Input Files"].get("Model Results")
        model_fasteners_csv = data_json["Input Files"].get("Model Fasteners csv")
        serialize = data_json["Input Files"].get("Serialized location")
        deserialize = data_json["Input Files"].get("File to Deserialize")

        ##################################### BYPASS LOADS ################################

        area_factor = data_json["Bypass Loads"].get("Area Factor", 2.5) # Area factor used in "get_bypass_loads" function. Default value = 2.5
        material_factor = data_json["Bypass Loads"].get("Material Factor", 4.5) # Material Factor used in "get_bypass_loads" function. Default value = 4.5
        box_tol = data_json["Bypass Loads"].get("Box Tolerance", 1e-3) # Box Tolerance used in "get_bypass_loads" function. Default value = 1e-3
        max_iter = data_json["Bypass Loads"].get("Max Iterations", 200) # Max Iterations used in "get_bypass_loads" function. Default value = 200

        ##################################### OUTPUT FILES ################################

        Output_path = data_json["Output Path"]

        ##################################### EXTRA INPUT DATA ################################

        corner_data = eval(data_json["Corner Data"])
        derived_cases = data_json["Derived Cases Names"]
        derived_cases_factors = data_json["Derived Cases Factors"]
        derived_type = data_json["Derived Type"]
        ##################################### ALLOWABLES ################################

        allowables_connection = data_json["Allowables Connection File"]

        ##################################### DICTIONARY ##################################

        # Updating of the dictionary with the new acquired data.
        configuration_data.update({"Analysis Name": analysis_name, "Joints Analysis Type": analysis_type, "Model FEM": model_fem, "Model Results": model_results, "Model Fasteners csv": model_fasteners_csv,
            "Serialized location": serialize,"File to Deserialize": deserialize, "Area Factor": area_factor, "Material Factor": material_factor, "Box Tolerance": box_tol, "Max Iterations": max_iter,
            "Output Path": Output_path, "Corner Data": corner_data, "Derived Cases Names": derived_cases, "Derived Cases Factors": derived_cases_factors,
            "Derived Type": derived_type, "Allowables Connection": allowables_connection})

        return configuration_data
    
    # If the file path is not found or the file is not valid for the study, the function will not be used and it will be intended that another file path is introduced.
    else:
        N2P.N2PLog.Error.user("[get_config_data] Try and introduce another path direction. The one you selected cannot be found or it is insecure.") 
        return None

