import numpy as np
import NaxToPy as N2P
from NaxToPy import N2PLog

def transform_isoparametric(point, quad):
    """
    Transform a 3D point to isoparametric coordinates within a quadrilateral. Even though it is a 2D transformation, the
    points can be introduced either in 3D or 2D format.

    Args:
    - point: A 3D point (x, y, z).  
    - quad: A list of four 3D points defining the quadrilateral.

    Returns:
    - u, v: Isoparametric coordinates of the point within the quadrilateral.
    """
    # Definition of coefficients a and b.
    a0 = 0.25*((quad[0][0] + quad[1][0]) + (quad[2][0] + quad[3][0]))
    a1 = 0.25*((quad[1][0] - quad[0][0]) + (quad[2][0] - quad[3][0]))
    a2 = 0.25*((quad[2][0] + quad[3][0]) - (quad[0][0] + quad[1][0]))
    a3 = 0.25*((quad[0][0] - quad[1][0]) + (quad[2][0] - quad[3][0]))

    b0 = 0.25*((quad[0][1] + quad[1][1]) + (quad[2][1] + quad[3][1]))
    b1 = 0.25*((quad[1][1] - quad[0][1]) + (quad[2][1] - quad[3][1]))
    b2 = 0.25*((quad[2][1] + quad[3][1]) - (quad[0][1] + quad[1][1]))
    b3 = 0.25*((quad[0][1] - quad[1][1]) + (quad[2][1] - quad[3][1]))

    # Definition of x0 and y0.
    x0 = point[0] - a0
    y0 = point[1] - b0

    # Definition of A, B and C
    A = a3*b2 - a2*b3
    B = (x0*b3 + a1*b2) - (y0*a3 + a2*b1)
    C = x0*b1 - y0*a1

    tol = 1e-4 # Tolerance in order to avoid bad approximations.
    tol2 = -tol
    # Obtention of v using Av^2 + Bv + C = 0
    if A < tol and A > tol2: # A=0
        if B < tol and B > tol2: # B=0
            N2PLog.Error.E510()
            return [None, None], [None, None]
        v_results = [-C/B, -C/B]
    elif B < tol and B > tol2: # Only B=0
        v_results = [(-C/A)**0.5, -((-C/A)**0.5)]
    else:
        discriminant = B**2 - 4*A*C
        if discriminant < 0:
            N2PLog.Error.E510()
            return [None, None], [None, None]
        v_results = [(-B + discriminant**0.5)/(2*A), (-B - discriminant**0.5)/(2*A)]

    # Obtention of u.
    u_results = [None, None]
    for i, v in enumerate(v_results):
        denom = a1 + a3*v
        if denom < tol and denom > tol2 and a1!=0 and a3!=0:
            u = (y0*a3 + a1*b2)/(a3*b1 - a1*b3)
            v = -a1/a3
            v_results[i] = v
            u_results[i] = u
        elif denom < tol and denom > tol2 and a3==0:
            u = (y0*a2 - b2*x0)/(b3*x0 - a2*b1)
            v = x0/a2
            v_results[i] = v
            u_results[i] = u
        else:
            u = (x0 - a2*v)/(denom)
            u_results[i] = u
    results1 = [u_results[0], v_results[0]]
    results2 = [u_results[1], v_results[1]]
    all_results = [results1, results2]

    def value_detection(pair):
        return all(-1-tol <= value <= 1+tol for value in pair)

    # Encontrar el primer par en ambos conjuntos donde ambos valores estén dentro del rango [-1, 1]
    result = None
    for pair in all_results:
        if value_detection(pair):
            result = result or pair  # Guarda el primer par que cumple la condición
            break
    return result[0], result[1]

def transform_barycentric(point, triangle_nodes):
    """
    Transform a 3D point to barycentric coordinates within a triangle.

    Args:
    - point: A 1D ndarray of shape (3,) representing the 3D point in the triangle.
    - triangle_nodes: A 2D ndarray of shape (3, 3) representing the coordinates of the triangle's three corners.

    Returns:
    - Barycentric coordinates (alpha, beta, gamma) of the point within the triangle.
    """

    det_T = (triangle_nodes[1][1]-triangle_nodes[2][1])*(triangle_nodes[0][0]-triangle_nodes[2][0])+(triangle_nodes[2][0]-triangle_nodes[1][0])*(triangle_nodes[0][1]-triangle_nodes[2][1])

    alpha = ((triangle_nodes[1][1]-triangle_nodes[2][1])*(point[0]-triangle_nodes[2][0])+(triangle_nodes[2][0]-triangle_nodes[1][0])*(point[1]-triangle_nodes[2][1]))/det_T

    betha = ((triangle_nodes[2][1]-triangle_nodes[0][1])*(point[0]-triangle_nodes[2][0])+(triangle_nodes[0][0]-triangle_nodes[2][0])*(point[1]-triangle_nodes[2][1]))/det_T

    gamma = 1 - alpha - betha

    return alpha, betha, gamma

def interpolation(point, vertices, values):
    """
    Perform 3D interpolation within a triangle or quadrilateral.

    Args:
    - point: A 1D ndarray of shape (3,) representing the 3D point in the shape.
    - vertices: A 2D ndarray of shape (n, 3) representing the coordinates of the shape's corners (n=3 for a triangle, n=4 for a quadrilateral).
    - values: A 2D ndarray of shape (n, 6) representing the values at the shape's corners.

    Returns:
    - Interpolated value at the given point as a 1D ndarray of shape (6,).
    """
    n = vertices.shape[0]

    # CTRIA3
    if n == 3:
        alpha, beta, gamma = transform_barycentric(point, vertices)
        interpolated_value = (
            alpha * values[0] +
            beta * values[1] +
            gamma * values[2]
        )

    # CQUAD4
    elif n == 4:  # Quadrilateral
        #u, v = __transform_to_isoparametric(point, vertices)
        u, v = transform_isoparametric(point, vertices)
        f00 = values[0] * 0.25 * (1-u) * (1-v)
        f01 = values[1] * 0.25 * (1+u) * (1-v)
        f10 = values[2] * 0.25 * (1+u) * (1+v)
        f11 = values[3] * 0.25 * (1-u) * (1+v)


        interpolated_value = f00 + f01 + f10 + f11
    else:
        N2P.N2PLog.Error.E511()
        return 0

    return interpolated_value


