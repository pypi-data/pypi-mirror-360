import time
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core import N2PModelContent
from NaxToPy import N2PLog
from time import time

def get_results(model: N2PModelContent,
                loadcase=0,
                corner_data = True):
    """
    Stores the needed results from a N2PModelContent in memory. Returns a dictionary of dictionaries where the first key
    is the loadcase ID and the second is the wanted result. It also returns a variable specifying the number of load
    cases that will be studied. This will vary with the input the user gives: a load case ID, a list of load cases IDs
    or if nothing is introduced, all the load cases will be analysed.

    Args:
        model: N2PModelContent
        loadcase: integer|list|tuple (Default value is 0 -> All load cases are analysed)
        corner_data: bool

    Returns: 
        ResultsDict: dict
        analysis_type: str

    Calling example:

            results, analysis_type = get_results(model = model1, corner_data = corner)

    Additional information:

    •	It is important to remark that if the results have been obtained in corner, it is highly recommended to use this
        data as it will be more accurate in order to compute bypass loads. It is also interesting that, as when obtaining
        results in corner also the data in centroid is stored, if “Corner Data”: “False”, the program should always function
        correctly. However, if “Corner Data” is set “True” and there are no results obtained in corner, an error will occur.
        It is also remarkable the fact that even though the resutls in corner data are more precise, the process is much
        slower.

    •	This function was created in order to retrieve results only once for each load case, as the running time of the
        program would be really large if results were obtained in every loop.

    •	As mentioned before, it is highly recommended to use corner data as the bypass loads calculation will be more
        accurate. If corner data is not selected, a warning message will be displayed: “Calculation using the results in
        the center may not be as precise as when Corner Data used."

    •	For optimization reasons, if corner data is not selected, the corresponding elements in the results dictionary
        will be filled with None and the results will only be obtained in the centroid.

    •	The procedure explained in the previous point cannot be used in the corner case, as the centroid results are
        needed in both cases because the TRIA elements have no results in corner.

    •	When a great amount of result files has been loaded (a folder full of op2 files), the result retrieving may take
        some time. Therefore, it is recommended to get the results once and serialize the obtained dictionary when the
        same model will be used for different analysis. This can be done in a similar way as it will be done in point 9
        (but much simpler).
            -	In order to serialize the dictionary into a file, package pickle can be used, using the following code
                lines. Where “serialized_file_location” is the path where the file will be saved (must be a pkl file as:
                "C:\\results.pkl") and “results” is the results dictionary obtained using the function “get_results”.

                                    with open(serialized_file_location, 'wb') as f):
                                        pickle.dump(results, f)

            -	In order to deserialize the file once it was created in a previous analysis, a similar procedure is
                followed. Now, in a new study, there will not be a reason for using the function “get_results”, as it is
                possible to directly obtain the same dictionary from the .pkl file using the following code lines. As
                previously mentioned, “serialized_file_location” will be the path where the dictionary was serialized before
                (a .pkl file), and “results” is the dictionary that will be used in the following functions.

                                    with open(serialized_file_location, 'rb') as f:
                                        results = pickle.load(f)

            -	This is just an example using this method; however, this same procedure can be done using some other
                packages, like JSON.

    """

    # Warning if Corner data is not selected.
    if not corner_data:
        N2PLog.Warning.W511()


    # Specicify for which loadcases to get results
    model_locases_ids = tuple([lc.ID for lc in model.get_load_case()])

    if loadcase == 0:
        loadcase_ids = model_locases_ids
        analysis_type = "All Load Cases"
    elif isinstance(loadcase, int) and loadcase in model_locases_ids:
        loadcase_ids = tuple([loadcase])
        analysis_type = "1 Load Case"
    elif (isinstance(loadcase, list) or isinstance(loadcase, tuple)) and all(lc in model_locases_ids for lc in loadcase):
        loadcase_ids = tuple(loadcase)
        analysis_type = "Envelope"
    else:
        N2PLog.Error.E504()
        return 0

    ResultsDict = {key: None for key in loadcase_ids}

    for lc_id in loadcase_ids:
        # Extract loadcase
        lc = model.get_load_case(lc_id)

        ### Define loadcase solver to know results and components names. Needed to be done for each lodcase in
        # case different results are imported from different solvers
        solver = lc.Solver

        # Specify solver: Nastran or Opti
        if solver == "Nastran":
            result = ["FORCES", "FORCES",  "FORCES"]
            component = ["FX", "FY", "FZ", "FX", "FY", "FXY", "MX", "MY", "MXY"]
        elif solver == "Optistruct":
            result = ["FORCES (1D)", "FORCES", "MOMENTS"]
            component = ["X", "Y", "Z", "XX", "YY", "XY", "XX", "YY", "XY"]
        else:
            N2PLog.Critical.C500()
            return 0

        # Ask for results.

        ave_nodes_corner_data = 0 # This means that the actual value is taken, not the average nor the max or min in the node.

        t1 = time()


        # Results query
        fx1D = lc.Results.get(result[0]).Components.get(component[0]).get_result_ndarray()[0] # Force in X direction.
        fy1D = lc.Results.get(result[0]).Components.get(component[1]).get_result_ndarray()[0]  # Force in Y direction.
        fz1D = lc.Results.get(result[0]).Components.get(component[2]).get_result_ndarray()[0]  # Force in Z direction.

        model.clear_results_memory()

        # 2D forces are asked in element system and with no corner data.

        fx = lc.Results.get(result[1]).get_component(component[3]).get_result_ndarray()[0]
        fy = lc.Results.get(result[1]).get_component(component[4]).get_result_ndarray()[0]
        fxy = lc.Results.get(result[1]).get_component(component[5]).get_result_ndarray()[0]
        mx = lc.Results.get(result[2]).get_component(component[6]).get_result_ndarray()[0]
        my = lc.Results.get(result[2]).get_component(component[7]).get_result_ndarray()[0]
        mxy = lc.Results.get(result[2]).get_component(component[8]).get_result_ndarray()[0]

        model.clear_results_memory()

        fx_corner = None
        fy_corner = None
        fxy_corner = None
        mx_corner = None
        my_corner = None
        mxy_corner = None

        if corner_data:

            # 2D forces are asked in element system and with corner data.
            fx_corner = lc.Results.get(result[1]).get_component(component[3]).get_result_ndarray(cornerData=corner_data, aveNodes=ave_nodes_corner_data)[0]
            fy_corner = lc.Results.get(result[1]).get_component(component[4]).get_result_ndarray(cornerData=corner_data, aveNodes=ave_nodes_corner_data)[0]
            fxy_corner = lc.Results.get(result[1]).get_component(component[5]).get_result_ndarray(cornerData=corner_data, aveNodes=ave_nodes_corner_data)[0]
            mx_corner = lc.Results.get(result[2]).get_component(component[6]).get_result_ndarray(cornerData=corner_data, aveNodes=ave_nodes_corner_data)[0]
            my_corner = lc.Results.get(result[2]).get_component(component[7]).get_result_ndarray(cornerData=corner_data, aveNodes=ave_nodes_corner_data)[0]
            mxy_corner = lc.Results.get(result[2]).get_component(component[8]).get_result_ndarray(cornerData=corner_data, aveNodes=ave_nodes_corner_data)[0]


            # TRIAS CASES:

            # When obtaining results from trias, only results in the centroid are supported. Therefore, when the option of
            # Corner Data is selected, the results of the tria obtained in the centroid are translated to the 3 nodes which form it.


            element_nodal = model.elementnodal()
            unsew_element_ids = [element_nodal.get(us_node)[2] for us_node in element_nodal.keys()]
            unsew_element = [model.get_elements((elem, 0)) for elem in unsew_element_ids]

            for index, element in enumerate(unsew_element):
                if isinstance(element, N2PElement) and element.TypeElement == "CTRIA3":
                    fx_corner[index] = fx[element.InternalID]
                    fy_corner[index] = fy[element.InternalID]
                    fxy_corner[index] = fxy[element.InternalID]
                    mx_corner[index] = mx[element.InternalID]
                    my_corner[index] = my[element.InternalID]
                    mxy_corner[index] = mxy[element.InternalID]

        t2 = time()
        # print("time to obtain results {}".format(t2-t1))

        ResultsDict[lc_id] = {
            "FX1D": fx1D,
            "FY1D": fy1D,
            "FZ1D": fz1D,

            "FX": fx,
            "FY": fy,
            "FXY": fxy,
            "MX": mx,
            "MY": my,
            "MXY": mxy,

            "FX CORNER": fx_corner,
            "FY CORNER": fy_corner,
            "FXY CORNER": fxy_corner,
            "MX CORNER": mx_corner,
            "MY CORNER": my_corner,
            "MXY CORNER": mxy_corner,

            "corner_data": corner_data,
            "Name": lc.Name
        }

    return ResultsDict