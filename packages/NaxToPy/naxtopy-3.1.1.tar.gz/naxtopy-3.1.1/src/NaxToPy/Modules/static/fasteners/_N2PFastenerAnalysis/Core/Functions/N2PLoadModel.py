"""
Script with several functions used to identify which elements of a model are close to joints and load a new, reduced 
model with those elements. 
"""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

import os 

import NaxToPy as NP 
from NaxToPy.Core import N2PModelContent
from NaxToPy.Modules.static.fasteners.joints.N2PJoint import N2PJoint

# Method used to load only a part of the model -------------------------------------------------------------------------
def load_reduced_model(model: N2PModelContent, joints: list[N2PJoint], adjacencyLevel: int) -> N2PModelContent: 

    """
    Method used to load a model with only the elements that make up the element's joints, as well as all elements up to 
    certain level of adjacency. For example, if adjacencyLevel is set to 2, the model will include all elements that 
    make up the joints, as well as the elements adjacent to them, and the elements adjacent to the elements adjacent to 
    them. 

    Args: 
        model: N2PModelContent 
        joints: list[N2PJoint] 
        adjacencyLevel: int 

    Returns: 
        newModel: N2PModelContent -> model with only the new elements loaded in

    Calling example: 
        >>> newModel = load_reduced_model(oldModel, jointsList, 4)
    """

    # All elements that make up the joints are selected 
    plateElements = list(set(j for k in joints for i in k.PlateElementList for j in i))
    boltElements = list(set(j for i in joints for j in i.BoltElementList))
    totalElements = list(set(plateElements + boltElements))
    totalElementsID = [(i.ID, i.PartID) for i in totalElements]
    totalElements = model.get_elements(totalElementsID)
    # The get_elements_adjacent() function fires as many times as the adjacencyLevel says, thus obtaining several 
    # layers of adjacent elements. 
    for i in range(adjacencyLevel): 
        totalElements = model.get_elements_adjacent(totalElements)
    elementDictionary = {} 
    for i in totalElements: 
        if i.PartID not in elementDictionary.keys(): 
            elementDictionary[i.PartID] = [i.ID] 
        else: 
            elementDictionary[i.PartID].append(i.ID)
    # Other, generally unimportant ModelContent attributes are obtained 
    path = model.FilePath
    parallel = model._N2PModelContent__vzmodel.LoadModelInParallel
    solver = model.Solver
    # A new reduced model is created and returned 
    newModel = NP.load_model(path, parallel, solver, elementDictionary, 'ELEMENTS')
    return newModel
# ----------------------------------------------------------------------------------------------------------------------

# Method used to extract all files in a folder -------------------------------------------------------------------------
def import_results(path: str) -> list[str]: 

    """
    Method used to extract all files in a folder. 

    Args: 
        path: str -> folder path.

    Returns: 
        files: list[str]
    """
    
    files = [] 
    for i, j, k in os.walk(path): 
        for l in k: 
            files.append(os.path.join(i, l))
    if type(files) != list: 
        files = [files]
    return files
# ----------------------------------------------------------------------------------------------------------------------