"""
Script with several functions used to perform rotations from one reference frame to another. 
"""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

import numpy as np 

from NaxToPy import N2PLog
from NaxToPy.Core.Classes.N2PElement import N2PElement 

# Method used to rotate a 2D tensor ------------------------------------------------------------------------------------
def rotate_tensor2D(fromSystem: list, toSystem: list, planeNormal: list, tensor: list) -> list: 

    """
    Method used to a 2D tensor from one coordinate system to another. 
    
    Args: 
        fromSystem: list -> original system.
        toSystem: list -> destination system. 
        planeNormal: list -> rotation plane. 
        tensor: list -> tensor to rotate. 

    Returns: 
        rotatedTensor: list 

    Calling example: 
        >>> forcesRot = rotate_tensor2D(elementSystem, materialSystem, elementSystem[6:9], forces)
    """

    tensor = np.array(tensor) 
    alpha = angle_between_2_systems(fromSystem, toSystem, planeNormal) 
    # Definition of the rotation matrix 
    c = np.cos(alpha) 
    s = np.sin(alpha) 
    R = np.array([[c**2, s**2, 2*s*c], 
                  [s**2, c**2, -2*s*c], 
                  [-s*c, s*c, c**2 - s**2]])
    shape = tensor.shape 
    tensorReshaped = tensor.reshape((-1, 3)).T 
    rotatedTensor = np.matmul(R, tensorReshaped).T 
    return rotatedTensor.reshape(shape).tolist() 
# ----------------------------------------------------------------------------------------------------------------------

# Method used to rotate a vector (1D tensor) ---------------------------------------------------------------------------
def rotate_vector(vector: list, fromSystem: list, toSystem: list) -> np.ndarray: 

    """
    Method used to rotate a vector from a coordinate system to another.

    Args:
        vector: list -> vector to be rotated. 
        fromSystem: list -> original system. 
        toSystem: list -> destination system. 

    Returns:
        rotatedVector: ndarray 

    Calling example: 
        >>> transformedNode = rotate_vector(nodeVector, globalSystem, elementSystem)
    """

    # Verify if every input has a length which is a multiple of three 
    if len(vector) %3 != 0 or len(fromSystem) %3 != 0 or len(toSystem) %3 != 0: 
        N2PLog.Warning.W541()
        return vector 
    vectorSegments = [vector[i: i + 3] for i in range(0, len(vector), 3)]
    transformedSegments = [] 
    # Vectors are reshaped into matrices 
    matrixCurrent = np.array(fromSystem).reshape(3, -1) 
    matrixNew = np.array(toSystem).reshape(3, -1) 
    for i in vectorSegments: 
        i = np.array(i).reshape(-1, 3) 
        matrixRotation = np.linalg.inv(matrixCurrent) @ matrixNew 
        transformedSegments.append((matrixRotation @ i.T).T)
    rotatedVector = np.concatenate(transformedSegments).reshape(-1) 
    return rotatedVector 
# ----------------------------------------------------------------------------------------------------------------------

# Method used to obtain the angle between two systems ------------------------------------------------------------------
def angle_between_2_systems(fromSystem: list, toSystem: list, planeNormal: list) -> float:

    """
    Method used to return the rotation angle, in radians, between two coordinate systems, given also the rotation plane.
    Args:
        fromSystem: list -> first system. 
        toSystem: list -> second system. 
        planeNormal: list -> rotation plane. 

    Returns:
        alpha: float -> angle, in radians, that the two systems form.

    Calling example: 
        >>> alpha = angle_between_2_systems(system1D, materialSystem, materialSystem[6:9])
    """

    fromSystem = np.array(fromSystem).reshape(3, -1)
    toSystem = np.array(toSystem).reshape(3, -1)
    planeNormal = np.array(planeNormal)

    fromSystem = fromSystem / np.linalg.norm(fromSystem, axis = 1, keepdims = True)
    toSystem = toSystem / np.linalg.norm(toSystem, axis = 1, keepdims = True)
    planeNormal = planeNormal / np.linalg.norm(planeNormal)

    toX = toSystem[0]
    projToX = toX - np.dot(toX, planeNormal) * planeNormal

    cosX = np.dot(fromSystem[0], projToX)
    if cosX > 1:
        cosX = 1
    elif cosX < -1:
        cosX = -1

    alpha = np.arccos(cosX)

    cosY = np.dot(fromSystem[1], projToX)
    if cosY < 0:
        alpha = - alpha

    return alpha
# ----------------------------------------------------------------------------------------------------------------------

# Method used to transforme a reference frame as a list into a matrix --------------------------------------------------
def system_to_matrix(system: list) -> np.ndarray: 

    """
    Method used to transform a reference frame as a list of nine floats into a 3x3 matrix. 

    Args: 
        system: list 
    
    Returns: 
        matrix: np.ndarray 

    Calling example: 
        >>> system_to_matrix(point.ElemSystemArray)
    """
    
    matrix = np.array([system[0:3], system[3:6], system[6:9]])
    return matrix 
# ----------------------------------------------------------------------------------------------------------------------

# Method used to determine if a point is inside an element or not ------------------------------------------------------
def point_in_element(points: np.ndarray, element: N2PElement, tol: float = 0.01, project: bool = True, 
                     errorCounter = 0, maxErrorCounter = 10) -> tuple[np.ndarray, np.ndarray]: 
    
    """
    Method used to determine if certain points lie within an element or not, or if that point's projection lies within 
    that same element. This is done dividing the quad in two triangles (in case the element is a quad; if it is a tria, 
    the program deals directly with that element) and obtaining the barycentric coordinates inside that triangle. If 
    the barycentric coordinates are all positive and their sum is less than 1, the point is inside the triangle. 

    Args: 
        points: np.ndarray -> array of points to be checked 
        element: N2PElement -> element to be checked 
        tol: float -> numerical tolerance 

    Returns: 
        found: np.ndarray -> array of booleans that shows if the point checked is inside the element or not 
        newPoints: np.ndarray -> array of projected points 
    """

    N = points.shape[0]
    found = np.full(N, False)
    newPoints = points.copy()
    nodes = element.Nodes
    coords = np.array([node.GlobalCoords for node in nodes])
    centroid = np.array(element.Centroid)
    if element.TypeElement == "CQUAD4":
        charDistance2 = max(np.sum((coords - centroid)**2, axis = 1))
        distance2 = np.sum((points - centroid)**2, axis = 1)
        mask1 = distance2 < charDistance2
        if np.any(mask1): 
            tri1 = (coords[0], coords[1], coords[2])
            tri2 = (coords[0], coords[2], coords[3])
            bcoords1 = barycentric_coords(points[mask1], *tri1)
            inside1 = __is_inside_barycentric(bcoords1, tol)
            found[mask1] |= inside1 
            mask2 = mask1.copy() 
            mask2[mask1] = ~inside1 
            if np.any(mask2):
                bcoords2 = barycentric_coords(points[mask2], *tri2)
                inside2 = __is_inside_barycentric(bcoords2, tol)
                found[mask2] |= inside2 
            unfoundMask = ~found
            if np.any(unfoundMask) and project:
                projectedPoints = project_point(points[unfoundMask], element)
                newPoints[unfoundMask] = projectedPoints
                bcoords1 = barycentric_coords(projectedPoints, *tri1)
                inside1 = __is_inside_barycentric(bcoords1, tol)
                found[unfoundMask] |= inside1
                remainingMask = ~found
                if np.any(remainingMask):
                    projectedPointsRemaining = newPoints[remainingMask]
                    bcoords2 = barycentric_coords(projectedPointsRemaining, *tri2)
                    inside2 = __is_inside_barycentric(bcoords2, tol)
                    found[remainingMask] |= inside2
    elif element.TypeElement == "CTRIA3":
        charDistance2 = max(np.sum((coords - centroid)**2, axis = 1))
        distance2 = np.sum((points - centroid)**2, axis = 1) 
        mask1 = distance2 < charDistance2 
        if np.any(mask1): 
            tri = (coords[0], coords[1], coords[2])
            bcoords = barycentric_coords(points[mask1], *tri)
            inside = __is_inside_barycentric(bcoords, tol)
            found[mask1] |= inside
            unfoundMask = ~found
            if np.any(unfoundMask):
                projectedPoints = project_point(points[unfoundMask], element)
                newPoints[unfoundMask] = projectedPoints
                bcoords = barycentric_coords(projectedPoints, *tri)
                inside = __is_inside_barycentric(bcoords, tol)
                found[unfoundMask] |= inside
    else:
        errorCounter = errorCounter + 1
        if errorCounter == maxErrorCounter: 
            N2PLog.Warning.W546(542)
            N2PLog.set_console_level("ERROR")
        N2PLog.Warning.W542(element = element)
        return np.zeros(len(points), dtype = bool), points, errorCounter

    return found, newPoints, errorCounter
# ----------------------------------------------------------------------------------------------------------------------
    
# Method used to obtain the barycentric coordinates --------------------------------------------------------------------
def barycentric_coords(points: np.ndarray, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray: 
    
    """
    Method used to determine the barycentric coordinates of a certain points with respect to a triangle with vertices 
    (a, b, c). The barycentric coordinates are defined as 
        u = Area of the BCP triangle / Area of the ABC triangle 
        v = Area of the ACP triangle / Area of the ABC triangle 
        w = Area of the ABP triangle / Area of the ABC triangle 
    
    Args: 
        points: np.ndarray -> array of points to be checked 
        a, b, c: np.ndarray -> coordinates of the triangle's vertices 

    Returns: 
        u, v, w: barycentric coordinates
    """
    
    ab = b - a 
    ac = c - a 
    A_0 = np.linalg.norm(np.cross(ab, ac)) 
    pa = a - points  
    pb = b - points
    pc = c - points
    A_pbc = np.linalg.norm(np.cross(pb, pc), axis = 1)  
    A_pca = np.linalg.norm(np.cross(pc, pa), axis = 1)
    A_pab = np.linalg.norm(np.cross(pa, pb), axis = 1)
    return np.column_stack((A_pbc, A_pca, A_pab)) / A_0
# ----------------------------------------------------------------------------------------------------------------------

# Method used to project a point into the plane of an element ----------------------------------------------------------
def project_point(points: np.ndarray, element: N2PElement, charDistance: float = 0.5) -> np.ndarray: 

    """
    Method used to project a point into an element. This is done simply by projecting the point into the plane defined 
    by the three first nodes in the element, so a point cannot be projected into an element with less than three nodes.

    Args: 
        points: np.ndarray -> array of points to be projected
        element: N2PElement
        charDistance: float -> a point will only be projected if the distance from the original point and the 
        projection is less than the characteristic distance of the element (by default, 50% of the element length). 

    Returns: 
        projection: np.ndarray -> array of projected points 
    """

    nodes = element.Nodes
    p1 = np.array(nodes[0].GlobalCoords) 
    p2 = np.array(nodes[1].GlobalCoords)
    p3 = np.array(nodes[2].GlobalCoords)

    maxDistance = charDistance*np.linalg.norm(p1 - p3)
    
    normal = np.cross(p2 - p1, p3 - p1)
    normal /= np.linalg.norm(normal) 
    
    distances = np.dot(points - p1, normal)  
    mask = np.linalg.norm(distances[:, np.newaxis] * normal, axis = 1) > maxDistance 
    distances[mask] = np.zeros(len(distances))[mask]
    return points - distances[:, np.newaxis] * normal  
# ----------------------------------------------------------------------------------------------------------------------

# Method used to do the necessary transformations to later interpolate adequately -------------------------------------- 
def transformation_for_interpolation(cornerPoints: np.ndarray, centroid: np.ndarray, point: np.ndarray, 
                                     elementSystem = np.ndarray, 
                                     globalSystem = np.eye(3)) -> tuple[np.ndarray, np.ndarray]:
    
    """
    Method used to transform the nodes of an element and a point in it from the global system to the element system of 
    the element centered in the centroid.

    Args:
        cornerPoints: ndarray -> nodes of the element to be transformed.
        centroid: ndarray -> centroid of the element.
        point: ndarray -> point to be transformed.
        elementSystem: ndarray -> element coordinate system 
        globalSystem: ndarray -> global coordinate system 

    Returns:
        transformedNodes, transformedPoint

    Calling example: 
        >>> nodes, point = transformation_for_interpolation(cornerCoordsGlobal, centroid, boxPoints[0], 
                                                            system_to_matrix(boxPoints[0].MaterialSystemArray))
    """

    # Definition of the nodes and point with regards to the Global Refererence frame located in the centroid
    nodesVector = cornerPoints - centroid
    pointVector = point - centroid

    # Transformation from the Global Reference Frame to the Element System with regards to the centroid.
    R = elementSystem @ globalSystem.T

    transformedNodes = nodesVector @ R.T
    transformedPoint = pointVector @ R.T

    return transformedNodes, transformedPoint
# ----------------------------------------------------------------------------------------------------------------------

def __is_inside_barycentric(bcoords, tol: float = 0.01):
    positive = np.all(bcoords >= -tol, axis = 1)
    sumOne = np.abs(np.sum(bcoords, axis = 1) - 1) <= tol
    return positive & sumOne
# ----------------------------------------------------------------------------------------------------------------------