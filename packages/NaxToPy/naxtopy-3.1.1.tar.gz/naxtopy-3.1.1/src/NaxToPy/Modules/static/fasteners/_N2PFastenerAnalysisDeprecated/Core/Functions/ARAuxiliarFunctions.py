import numpy as np

############################### HELPER FUNCTIONS ################################
def point_in_quad_original(point: list, vertices_quad: list) -> bool:
    """Check if a point is inside a quadrilateral.

    Args:
        point: list
        vertices_quad: list

    Returns:
        bool: True if the point is inside the quadrilateral, False otherwise.
    """
    count = 0
    # Iterate over the vertices
    for i in range(len(vertices_quad)):
        v1 = vertices_quad[i]
        v2 = vertices_quad[(i + 1) % len(vertices_quad)]
        # Calculate the vector that represents the line from v1 to v2
        side_quad_vector = v2 - v1
        # Calculate the vector that represents the line from the point to v1
        point_v1_vector = v1 - point
        # Calculate the cross product of the two vectors
        cross_product = np.cross(side_quad_vector, point_v1_vector)
        # If the z component of the cross product is negative, the point is inside the quadrilateral
        if cross_product[2] < 0:
            return False
    # If the point is not inside the quadrilateral, it is outside
    return True


def point_in_quad(point: list, vertices_quad: list, tolerancedistance=0.01) -> bool:
    """
    A function to check if a point is inside a quadrilateral defined by its vertices.

    Args:
        point: tuple
        vertices_quad: list[list]
        tolerancedistance: float (default=0.01).

    Returns:
        bool: True if the point is inside the quadrilateral, False otherwise.
    """
    # Iterate over the sides of the square
    for i in range(len(vertices_quad)):
        # Get the adjacent vertices
        v1 = vertices_quad[i]
        v2 = vertices_quad[(i + 1) % len(vertices_quad)]
        # Calculate the distance between the point and the line
        distance = distance_point_segment(point, v1, v2)
        # If the distance is less than the tolerance, the point is inside the square
        if distance < tolerancedistance:
            return True
    # If the point is not inside the square, it is outside
    return point_in_quad_original(point, vertices_quad)


def distance_point_segment(p: list, v1: list, v2: list) -> float:
    """
    Calculate the distance between a point p and a line segment defined by two points v1 and v2.

    Args:
        p: numpy array
        v1: numpy array
        v2: numpy array

    Returns:
        distance: float
    """

    # Vector representing the segment
    delta_v2_v1 = v2 - v1
    # Projection of p onto delta_v2_v1
    t = np.dot(p - v1, delta_v2_v1) / np.dot(delta_v2_v1, delta_v2_v1)
    t = np.clip(t, 0, 1)
    # Projected point
    projected = v1 + t * delta_v2_v1
    # Distance between p and proyectado
    distance = np.linalg.norm(p - projected)
    return distance


def point_in_triangle(point: list, vertices_triangular: list, tolerance=0.01) -> bool:
    """
    A function to determine if a point is inside a triangular region defined by three vertices.

    Parameters:
        point: list
        vertices_triangular: list[list]
        tolerance: float

    Returns:
        bool
    """
    # Coordinates of triangle vertices
    v0, v1, v2 = vertices_triangular

    # Point coordinates
    x = point[0]
    y = point[1]

    # Barycentric coordinates
    denom = (v1[1] - v2[1]) * (v0[0] - v2[0]) + (v2[0] - v1[0]) * (v0[1] - v2[1])
    b1 = ((v1[1] - v2[1]) * (x - v2[0]) + (v2[0] - v1[0]) * (y - v2[1])) / denom
    b2 = ((v2[1] - v0[1]) * (x - v2[0]) + (v0[0] - v2[0]) * (y - v2[1])) / denom
    b3 = 1 - b1 - b2

    # Check if point is inside triangle
    if (-tolerance <= b1 <= 1 + tolerance
        and -tolerance <= b2 <= 1 + tolerance
        and -tolerance <= b3 <= 1 + tolerance
    ) or (distance_point_segment(point, v0, v1) <= tolerance
          or distance_point_segment(point, v1, v2) <= tolerance
          or distance_point_segment(point, v0, v2) <= tolerance):
        return True
    return False


def point_in_element(point: list, vertices_element: list, tolerancedistance=0.01) -> bool:
    """
    Check if the given point is inside the element defined by the vertices.

    Args:
        point: tuple
        vertices_element: list[list]
        tolerancedistance: float (default=0.01)

    Returns:
        None if the element is neither a quad nor a triangle

        True if the point is inside the element
        False if the point is outside the element
    """
    # Check if quad or triangle
    if len(vertices_element) == 4:
        return point_in_quad(point, vertices_element, tolerancedistance)
    elif len(vertices_element) == 3:
        return point_in_triangle(point, vertices_element, tolerancedistance)
    else:
        return None

def equal_points(point1: list, point2: list, max_deviation=0.1) -> bool:
    """
    A function that checks if two points are equal with a maximum deviation of 0.01.

    Args:
        point1: list
        point2: list
        max_deviation: float (default is 0.01)

    Returns:
        bool: True if the points are considered equal within the specified tolerance, False otherwise
    """

    if (point1[0] >= 0) != (point2[0] >= 0) or \
            (point1[1] >= 0) != (point2[1] >= 0) or \
            (point1[2] >= 0) != (point2[2] >= 0):
        return False

    for coord1, coord2 in zip(point1, point2):
        if abs(coord1 - coord2) > max_deviation:
            return False
    return True


def same_direction(vector1: list, vector2: list, tolerance_degrees=35) -> bool:
    """
    A function that checks if two vectors are in the same direction.

    Args:
        vector1: numpy array or list
        vector2: numpy array or list
        tolerance_degrees: float (default is 10)

    Returns:
        bool: True if the vectors are in the same direction within the specified tolerance, False otherwise
    """
    # Convert the input vectors to numpy arrays
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)

    # Normalize the vectors
    vector1_normalized = vector1 / np.linalg.norm(vector1)
    vector2_normalized = vector2 / np.linalg.norm(vector2)

    # Dot product between the normalized vectors
    dot_product = np.dot(vector1_normalized, vector2_normalized)

    # Angle between the normalized vectors in degrees
    angle_degrees = np.degrees(np.arccos(dot_product))

    # Verify if the angle is within the specified tolerance or its complementary
    return np.abs(angle_degrees) < tolerance_degrees or np.abs(180 - angle_degrees) < tolerance_degrees
