from NaxToPy.Core import N2PModelContent
from NaxToPy import N2PLog

def get_derived_loadcases(model: N2PModelContent, loadcases_names: list, derived_type: str, derived_factors: list) -> list:
        """
        Stores in a list the resultant derived loadcases IDs. The user must define the load cases that are set to be
        combined with the rest of the loadcases of the model.

        If this input list of IDs is empty: either the function will either not have an output or it will calculate the
        proportional cases to the ones in the model.

        The output will be the ids of the selected load cases to study in the following steps depending on the parameter
        called "derived_type".

                “Raw”: Only Raw load cases are returned.
                “Derived”: Only derived load cases are returned.
                “All”: All load cases are returned: Derived + Raw


        Args:
            model: N2PModelContent
            loadcases_names: list
            derived_type: str
            derived_factors: list

        Returns:
            derived_locases_ids: list

        Calling example:

                derived_loadcases = get_derived_loadcases(model = model1, loadcases_names=loadcases_names,
                                                          derived_type = derived_type, derived_factors = derived_factors)


        Additional information:

        •	If “loadcases_names” list is empty, there are two possible ways to continue depending on the factors list.
            If the second factor in the list is not equal to 1.0, an update of the existent load cases is set to happen,
            multiplying this factor times each of the load cases, having linearly proportional new load cases. In the case
            that this second factor is 1.0, there is no reason to apply this function, and the first model is the output itself.

        •   If both “loadcases_names”  and “derived_factors” are empty lists, there will not be any procedure and an
            output of 0 will be defined for “total_list_ids” (take into account that this is the default value for the next
            function). In addition, an error message will be displayed: “There are not possible derived load cases for the
            data introduced.”

        •	When “loadcases_names”  and “derived_factors” lists are not empty, a combination between load cases is
            carried out. First, the same procedure explained previously is done: obtaining linear

        """
        loadcases_ids = []

        # From the input list obtain only the IDs of the load cases.
        for chain in loadcases_names:
                words = chain.split()
                last = words[-1]
                id = ''.join(c for c in last if c.isdigit())
                loadcases_ids.append(int(id))

        loadcasename_id = 0 # ID of the new derived loadcase.
        initialLoadCases = model.LoadCases
        list_derived_loadcases = [] # Output list with the combined loadcases.
        lenModelLcs = len(model.LoadCases) - len(loadcases_ids)
        initialLoadCasesIDs = [loadcase.ID for loadcase in model.LoadCases]

        derived_lc_dict = {lc.ID: lc for lc in initialLoadCases}

        # No combination of different load cases, only linear proportionality of each load case.

        if loadcases_ids == [] and derived_factors[1] != 1.0:
                for i, loadcase in enumerate(initialLoadCases):
                        if i < lenModelLcs:
                                # If the ID of the loadcases is the same in both lists, the combination is not done.
                                loadcasename_id -= 1                                
                                loadcasesderived = model.new_derived_loadcase(
                                        "{}_{}".format(loadcase.Name, "ROOM"),
                                        "{}*<LC{}:FR{}>".format(derived_factors[1], loadcase.ID, loadcase.Increments[-1].ID))
                                derived_lc_dict[loadcasesderived.ID] = loadcasesderived
                                list_derived_loadcases.append(loadcasesderived)
                derived_type = "Derived"

        # Combination of different load cases.

        elif loadcases_ids != [] :

                # First obtain the same proportionallity as in the case where no combination is done.
                for i, loadcase in enumerate(initialLoadCases):               
                        if (i < lenModelLcs) and (loadcase.ID not in loadcases_ids):
                                loadcasename_id -= 1                                
                                loadcasesderived = model.new_derived_loadcase(
                                        "{}_{}".format(loadcase.Name, "ROOM"),
                                        "{}*<LC{}:FR{}>".format(derived_factors[1], loadcase.ID, loadcase.Increments[-1].ID))
                                derived_lc_dict[loadcasesderived.ID] = loadcasesderived
                                list_derived_loadcases.append(loadcasesderived) 
                
                # Loop for both the model loadcases list and the input loadcases list is carried out in order to combinate them.
                for combinedlc_ID in loadcases_ids:
                        # If the loadcase in the "to combine" list is not in the model, an Error message is displayed.

                        if combinedlc_ID not in initialLoadCasesIDs:
                                N2PLog.Error.user("[get_derived_loadcases] The selected Loadcase to be combined is not in the model loadcases data.")
                                continue                                                                                          
                        for i, loadcase in enumerate(initialLoadCases):
                                # If the ID of the loadcases is the same in both lists, the combination is not done.
                                if (combinedlc_ID != loadcase.ID) and (loadcase.ID not in loadcases_ids) and (i < lenModelLcs):
                                        loadcasename_id -= 1
                                        combined_loadcase = derived_lc_dict[combinedlc_ID]
                                        name_combinedlc = combined_loadcase.Name
                                        # derived load case name
                                        if "+" in name_combinedlc or "HT" in loadcase.Name:
                                                newName = "HOT"
                                        if "-" in name_combinedlc or "CT" in loadcase.Name:
                                                newName = "COLD"                               
                                        loadcasesderived = model.new_derived_loadcase(
                                                "{}_{}".format(loadcase.Name, newName),
                                                "{}*<LC{}:FR{}>+{}*<LC{}:FR{}>".format(
                                                        derived_factors[0], combined_loadcase.ID, combined_loadcase.Increments[-1].ID,
                                                        derived_factors[1], loadcase.ID, loadcase.Increments[-1].ID))

                                        derived_lc_dict[loadcasesderived.ID] = loadcasesderived
                                        list_derived_loadcases.append(loadcasesderived)
                derived_type = "Derived"

        if list_derived_loadcases == [] and loadcases_ids != []: # When no derived loadcases are obtained, an Error message is displayed and no output is obtained.
                N2PLog.Error.user("[get_derived_loadcases] There are not possible derived load cases for the data introduced.")
                return 0, model

        # The list of Derived Loadcases IDs is obtained and displayed.
        derived_locases_ids = [lc.ID for lc in list_derived_loadcases]

        ################################## DIFFERENT OUTPUTS #################################

        # All loadcases are returned: Derived + Raw
        if derived_type == "All":
                total_list_ids = [lc.ID for lc in model.get_load_case()] + derived_locases_ids
        # Only Raw loadcases are returned.
        elif derived_type == "Raw":
                total_list_ids = [lc.ID for lc in model.get_load_case()]
        # Only derived loadcases are returned.
        elif derived_type == "Derived":
                total_list_ids = derived_locases_ids

        return total_list_ids