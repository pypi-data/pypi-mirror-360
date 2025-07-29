"""
Script used to extract the results from the results files. 
"""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

import numpy as np

from NaxToPy import N2PLog
from NaxToPy.Core.N2PModelContent import N2PModelContent 
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core.Classes.N2PLoadCase import N2PLoadCase

# Method used to obtain the results dictionary -------------------------------------------------------------------------
def get_results(model: N2PModelContent, loadCaseList: list[N2PLoadCase], cornerData: bool = False): 

    """
    Method used to obtain two numpy arrays with all important results that have to be saved in memory. The results 
    arrays are 3D numpy arrays in which the first dimension corresponds to each load case, the second dimension 
    corresponds to the type of result, and the third dimension corresponds to the value in each element. Therefore, the 
    arrays' dimensions will be a*b*c, where a is the number of load cases, b is the ammount of results that are asked 
    for (9 for the regular results array and 6 for the corner data results array), and c is the number of elements in 
    which results are asked (for the regular results array, c will be the number of elements in the model and, for the 
    corner results array, c will be the number of elements * the number of nodes in each element). The innermost 
    array is ordered by the elements' internal IDs, just like the results directly extracted. The results that are 
    obtained are the following: 
        - FX 1D 
        - FY 1D 
        - FZ 1D 
        - FX 
        - FY 
        - FXY 
        - MX 
        - MY 
        - MXY 
        - FX CORNER
        - FY CORNER 
        - FXY CORNER 
        - MX CORNER 
        - MY CORNER 
        - MXY CORNER
    If cornerData is set to False, the corner results array will simply be np.array([]) 

    Args: 
        model: N2PModelContent -> compulsory input.
        loadcase: list[N2PLoadCase] -> load cases to be studied. 
        cornerData: bool = False -> boolean which shows whether the corner data is to be used or not.
        jointType: str = "CFAST" -> string which shows what is the joint's type. 

    Returns: 
        resultsList: np.ndarray  
        resultsListCorner: np.ndarray 
        brokenLC: list[N2PLoadCase] -> list of broken load cases. 

    If results have been obtained in the corner, it is recommended to use them, as this data will be more accurate and 
    the computed bypass loads will be more precise, but the process is slower. Therefore, when cornerData is set to 
    False, a warning will appear. 

    It is important to note that, if cornerData is set to False and there are actually results in the corner, the 
    program should function correctly (just not taking into account this data). Similarly, if cornerData is set to True 
    but there is no corner data in the results, the arrays corresponding to the corner forces will be filled with 
    nan. This is not problematic (it just takes longer), but it could be bad if this data is used for the bypass 
    calculations for obvious reasons. 

    Currently, the following solvers are supported: 
        - Nastran and InputFileNastran 
        - Abaqus and InputFileAbaqus 

    Calling example: 
        >>> myResults, myResultsCorner, brokenLoadCases = get_results(model1, model1.LoadCases[0:10], False)
    """

    lclist = [(i, i.ActiveN2PIncrement) for i in loadCaseList]
    solver = model.Solver 
    # The results and components template will be diferent depending on whether the solver is Nastran or Optistruct 
    # Note: depending on whether the joint is a CFAST, CWELD or CBUSH, the template will also be different. For 
    # Nastran 'CFAST' and 'CBUSH' everything works fine. For Nastran 'CWELD' everything works (perhaps not fine, 
    # but it works) and for Optistruct everything, it hasn't been tried yet. 
    if solver == "InputFileNastran" or solver == "Nastran" or solver == "Optistruct": 
        if "FX" in loadCaseList[0].get_result("FORCES").Components.keys(): 
            results = ["FORCES", "FORCES",  "FORCES"]
            components = ["FX", "FY", "FZ", "FX", "FY", "FXY", "MX", "MY", "MXY"] 
        else: 
            results = ["FORCES (1D)", "FORCES", "MOMENTS"]
            components = ["X", "Y", "Z", "XX", "YY", "XY", "XX", "YY", "XY"]
    elif solver == "InputFileAbaqus":
        results = ["FORCES (1D)", "FORCES", "MOMENTS"]
        components = ["X", "Y", "Z", "XX", "YY", "XY", "XX", "YY", "XY"]
    elif solver == "Abaqus": 
        results = ["SF", "SF",  "SM"]
        components = ["SF1", "SF2", "SF3", "SF4", "SF5", "SF6", "SM1", "SM2", "SM3"] 
    else:
        N2PLog.Error.E518(solver)
        return None 

    if results[0] == results[1]: 
        if results[0] == results[2]: 
            extractedForces = model.get_result_by_LCs_Incr(lclist, results[0], list(set(components)))
        else: 
            extractedForces = model.get_result_by_LCs_Incr(lclist, results[0], components[0:6]) | \
                              model.get_result_by_LCs_Incr(lclist, results[2], components[6:9])
    elif results[0] == results[2]: 
        extractedForces = model.get_result_by_LCs_Incr(lclist, results[0], components[0:3] + components[6:9]) | \
                          model.get_result_by_LCs_Incr(lclist, results[1], components[3:6])
    elif results[1] == results[2]: 
        extractedForces = model.get_result_by_LCs_Incr(lclist, results[0], components[0:3]) | \
                          model.get_result_by_LCs_Incr(lclist, results[1], components[3:9])
    else: 
        extractedForces = model.get_result_by_LCs_Incr(lclist, results[0], components[0:3]) | \
                          model.get_result_by_LCs_Incr(lclist, results[1], components[3:6]) | \
                          model.get_result_by_LCs_Incr(lclist, results[2], components[6:9])
    
    brokenLC = [] 
    resultsList = np.array([[extractedForces[i[0].ID, i[1].ID, j] if extractedForces[i[0].ID, i[1].ID, j] is not None 
                             else brokenLC.append(i) for j in components] for i in lclist])
    resultsListCorner = np.array([])
    if cornerData: 
        # If cornerData = True, results are also obtained using this corner data 
        if results[1] == results[2]: 
            extractedForcesCorner = model.get_result_by_LCs_Incr(lclist, results[1], components[3:9], aveNodes = 0, 
                                                                 cornerData = True)
        else: 
            extractedForcesCorner = model.get_result_by_LCs_Incr(lclist, results[1], components[3:6], aveNodes = 0, 
                                                                 cornerData = True) | \
                                    model.get_result_by_LCs_Incr(lclist, results[2], components[6:9], aveNodes = 0, 
                                                                 cornerData = True)

        # Correction for CTRIA elements: 
        # When obtaining results from trias, only results in the centroid are supported. Therefore, when the option 
        # of Corner Data is selected, the results of the tria obtained in the centroid are translated to the 3 
        # nodes which form it.
        elementNodal = model.elementnodal() 
        unsewElementsID = [elementNodal.get(i)[2] for i in elementNodal.keys()]
        unsewElementsPartID = [elementNodal.get(i)[0] for i in elementNodal.keys()]
        unsewElements = [model.get_elements((unsewElementsID[i], unsewElementsPartID[i])) 
                         for i in range(len(unsewElementsID))]

        for i, j in enumerate(unsewElements): 
            if isinstance(j, N2PElement) and j.TypeElement == "CTRIA3":
                for k in lclist: 
                    for l in components[3:]: 
                        extractedForcesCorner[k[0].ID, k[1].ID, l][i] = extractedForces[k[0].ID, 
                                                                                        k[1].ID, l][j.InternalID]
        resultsListCorner = np.array([[extractedForcesCorner[i[0].ID, i[1].ID, j] 
                                       if extractedForcesCorner[i[0].ID, i[1].ID, j] is not None 
                                       else brokenLC.append(i) for j in components[3:]] for i in lclist])
        
    model.clear_results_memory()  
    return resultsList, resultsListCorner, brokenLC 
# ----------------------------------------------------------------------------------------------------------------------