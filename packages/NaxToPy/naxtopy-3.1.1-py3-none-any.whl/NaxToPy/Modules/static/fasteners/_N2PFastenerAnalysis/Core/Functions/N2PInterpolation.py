"""
Script with several functions used to perform interpolations when calculating the bypass loads. 
"""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info

import numpy as np 

from NaxToPy import N2PLog

# Method used to transform a point to isoparametric coordinates --------------------------------------------------------
def transform_isoparametric(point, quad, tol: float = 0.01, maxIter: int = 25, errorCounter = 0, maxErrorCounter = 10): 

    """
    Transforms a 3D point to isoparametric coordinates within a quadrilateral. Even though it is a 2D transformation, 
    the points can be introduced either in 3D or 2D format.

    Args:
        point -> 3D point (x, y, z).
        quad -> list of four 3D points defining the quadrilateral.
        tol: float = 0.01 -> tolerance used to avoid bad approximations.
        maxIter: int = 25 -> maximum number of iterations. 

    Returns:
        u, v: float -> isoparametric coordinates of the point within the quadrilateral.

    Calling example: 
        >>> u, v = transform_isoparametric(point, vertices)
    """

    xi_eta = np.zeros(2) 
    for iteration in range(maxIter):
        xi, eta = xi_eta
        N = 0.25 * np.array([(1 - xi) * (1 - eta),(1 + xi) * (1 - eta),(1 + xi) * (1 + eta),(1 - xi) * (1 + eta)])
        
        dN_dxi = 0.25 * np.array([-(1 - eta),(1 - eta),(1 + eta),-(1 + eta)])
        dN_deta = 0.25 * np.array([-(1 - xi),-(1 + xi),(1 + xi),(1 - xi)])
        
        X = N @ quad
        R = X - point
        
        J = np.zeros((2, 2))
        J[0, 0] = dN_dxi @ quad[:, 0] 
        J[0, 1] = dN_deta @ quad[:, 0]  
        J[1, 0] = dN_dxi @ quad[:, 1] 
        J[1, 1] = dN_deta @ quad[:, 1] 
        
        delta = np.linalg.solve(J, -R[:2]) 
        xi_eta += delta
        
        if np.linalg.norm(delta) < tol:
            break
        if iteration == maxIter - 1: 
            errorCounter = errorCounter + 1
            if errorCounter == maxErrorCounter: 
                N2PLog.Warning.W546(543)
                N2PLog.set_console_level("ERROR")
            N2PLog.Warning.W543(point, quad)
            xi_eta = np.array([np.nan, np.nan])
    
    return *xi_eta, errorCounter
# ----------------------------------------------------------------------------------------------------------------------

# Method used to transform a point to barycentric coordinates ----------------------------------------------------------
def transform_barycentric(point, nodes): 

    """
    Transforms a 3D point to barycentric coordinates within a triangle.

    Args:
        point -> 1D ndarray of shape (3,) representing the 3D point in the triangle.
        nodes -> 2D ndarray of shape (3, 3) representing the coordinates of the triangle's three corners.

    Returns:
        alpha, beta, gamma: float -> barycentric coordinates of the point within the triangle.

    Calling example: 
        >>> alpha, beta, gamma = transform_barycentric(point, vertices)
    """

    det = (nodes[1][1] - nodes[2][1])*(nodes[0][0] - nodes[2][0]) + \
          (nodes[2][0] - nodes[1][0])*(nodes[0][1] - nodes[2][1])
    alpha = ((nodes[1][1] - nodes[2][1])*(point[0] - nodes[2][0]) + \
             (nodes[2][0] - nodes[1][0])*(point[1] - nodes[2][1]))/det
    beta = ((nodes[2][1] - nodes[0][1])*(point[0] - nodes[2][0]) + \
            (nodes[0][0] - nodes[2][0])*(point[1] - nodes[2][1]))/det
    gamma = 1 - alpha - beta

    return alpha, beta, gamma
# ----------------------------------------------------------------------------------------------------------------------

# Method used to interpolate -------------------------------------------------------------------------------------------
def interpolation(point, vertices, values, tol: float = 0.01, errorCounter = 0, maxErrorCounter = 10): 
    
    """
    Performs 3D interpolation within a triangle or quadrilateral.

    Args:
        point -> 1D ndarray of shape (3,) representing the 3D point in the shape.
        vertices -> 2D ndarray of shape (n, 3) representing the coordinates of the shape's corners (n = 3 for a 
        triangle, n = 4 for a quadrilateral).
        values -> 2D ndarray of shape (n, 6) representing the values at the shape's corners.
        tol: float = 0.01 -> tolerance used to avoid bad approximations.

    Returns:
        interpolatedValue: float -> interpolated value at the given point as a 1D ndarray of shape (6,).

    Calling example: 
        >>> interpolatedForces = interpolation(pointCoordElem, cornerCoordElem, values)
    """
    
    n = vertices.shape[0]
    # CTRIA3
    if n == 3:
        alpha, beta, gamma = transform_barycentric(point, vertices)
        interpolatedValue = alpha * values[:,0] + beta * values[:,1] + gamma * values[:,2]
    # CQUAD4
    elif n == 4:
        xi, eta, errorCounter = transform_isoparametric(point, vertices, tol, errorCounter, maxErrorCounter)
        N = 0.25 * np.array([(1 - xi) * (1 - eta), (1 + xi) * (1 - eta), (1 + xi) * (1 + eta), (1 - xi) * (1 + eta)])
        interpolatedValue = [] 
        for i in values: 
            interpolatedValue.append(N@i) 
        interpolatedValue = np.array(interpolatedValue)
    else: 
        errorCounter = errorCounter + 1 
        if errorCounter == maxErrorCounter: 
            N2PLog.Warning.W546(542)
            N2PLog.set_console_level("ERROR")
        N2PLog.Warning.W542(vertices = vertices)
        interpolatedValue = values 
    return interpolatedValue, errorCounter
# ----------------------------------------------------------------------------------------------------------------------