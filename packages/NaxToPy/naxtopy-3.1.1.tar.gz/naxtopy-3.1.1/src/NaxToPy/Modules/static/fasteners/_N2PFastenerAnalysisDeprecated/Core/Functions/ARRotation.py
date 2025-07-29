import numpy as np
from NaxToPy import N2PLog
from NaxToPy.Core.Classes.N2PElement import N2PElement


def rotate_tensor2D(from_system: list,
                     to_system: list,
                     plane_normal: list,
                     tensor: list)-> list:
    """
    Rotates a 2D tensor from a coordinate system to another.
    A list of 2D tensors can be given as [t1xx, t1yy, t1xy, t2xx, t2yy, t2xy, t3xx, t3yy, t3xy...]

    Args:
        from_system: ndarray
        to_system: ndarray
        plane_normal: ndarray
        tensor: ndarray

    Returns:
        rotated_tensor: ndarray
    """

    tensor = np.array(tensor)

    alpha = angle_between_2_systems(from_system=from_system,
                                    to_system=to_system,
                                    plane_normal=plane_normal)

    #Rotate tensor
    c = np.cos(alpha)
    s = np.sin(alpha)

    Rt = np.array([[c ** 2, s ** 2, 2 * c * s],
                  [s ** 2, c ** 2, -2 * c * s],
                  [-c * s, c * s, c ** 2 - s ** 2]])

    original_tensor_shape = tensor.shape

    # Reshapes the list of n tensor components to a matrix of shape (3,n) with tensors as columns [txx, tyy, txy]
    tensor_reshaped = tensor.reshape((-1,3)).T

    # Rotation. Transpose is needed to be consistent.
    rotated_tensor = np.matmul(Rt, tensor_reshaped).T

    return rotated_tensor.reshape(original_tensor_shape).tolist()


def rotate_vector(vector: np.ndarray, from_system: np.ndarray, to_system: np.ndarray) -> np.ndarray:
    """Function which rotates a vector (with a number of components multiple of 3) from a coordinate system to another.
    args:
        vector: ndarray
        from_system: ndarray
        to_system: ndarray

    returns:
        transformed_vector: ndarray
    """
    # verify if the number of components of the vector is multiple of 3.
    if len(vector) % 3 != 0 or len(from_system) % 3 != 0 or len(to_system) % 3 != 0:
        N2PLog.Error.E512()

    # divide the vector in 3-component segments.
    vector_segments = [vector[i:i + 3] for i in range(0, len(vector), 3)]

    # carry out the trnasformation for each of the segments.
    transformed_segments = []
    for segment in vector_segments:
        # reshape the vectors to matrices 3xn, where n is the vector length.
        matrix_actual = np.array(from_system).reshape(3, -1)
        matrix_new = np.array(to_system).reshape(3, -1)

        # transpose the vector if needed.
        segment = np.array(segment).reshape(-1, 3)

        # calculate the rotation matrix that transforms from the "from_system" to the "to_system" reference frames.
        matrix_rotation = np.linalg.inv(matrix_actual) @ matrix_new

        # caary out the segment transformation.
        transformed_segment = (matrix_rotation @ segment.T).T
        transformed_segments.append(transformed_segment)

    # join all the segments again for the output.
    transformed_vector = np.concatenate(transformed_segments).reshape(-1)

    return transformed_vector


def project_vector(vector: list,
                   from_system: list,
                   to_system: list) -> np.ndarray:
    """
    Function which rotates a vector (with a number of components multiple of 3) from a coordinate system to another.

    Args:
        vector: ndarray
        from_system: ndarray
        to_system: ndarray

    Returns:
        transformed_vector: ndarray

    """

    from_system = np.array(from_system).reshape(3, -1)
    to_system = np.array(to_system).reshape(3, -1)
    vector = np.array(vector)


    #Normalize input
    from_system = from_system/ np.linalg.norm(from_system, axis=1, keepdims=True)
    to_system = to_system / np.linalg.norm(to_system, axis=1, keepdims=True)

    M = np.matmul(from_system, to_system.T)

    original_vector_shape = vector.shape

    vector_reshaped = vector.reshape((-1,3)).T

    projected_vector = np.matmul(M, vector_reshaped).T

    return projected_vector.reshape(original_vector_shape)

def angle_between_2_systems(
        from_system: list,
        to_system: list,
        plane_normal: list) -> float:

    """
    Given two coordinate systems and the rotation plane, returns the rotation angle in radians between the two.
    Copied from VizzerClasses N2TensorTransformation lines 411 to 461.

    Args:
        from_system: ndarray
        to_system: ndarray
        plane_normal: ndarray

    Returns:
        alpha
    """
    from_system = np.array(from_system).reshape(3, -1)
    to_system = np.array(to_system).reshape(3, -1)
    plane_normal = np.array(plane_normal)

    # Normalize input
    from_system = from_system / np.linalg.norm(from_system, axis=1, keepdims=True)
    to_system = to_system / np.linalg.norm(to_system, axis=1, keepdims=True)
    plane_normal = plane_normal / np.linalg.norm(plane_normal)

    # Project x axis of new system to element plane
    to_x = to_system[0]
    proj_to_x = to_x - np.dot(to_x, plane_normal) * plane_normal

    # Compute angles
    cos_alpha_x = np.dot(from_system[0], proj_to_x)
    if cos_alpha_x > 1:
        cos_alpha_x = 1
    elif cos_alpha_x < -1:
        cos_alpha_x = -1

    alpha = np.arccos(cos_alpha_x)

    # Check if it is necessary to reverse angle
    cos_alpha_y = np.dot(from_system[1], proj_to_x)
    if cos_alpha_y < 0:
        alpha = - alpha

    return alpha


def translate_vector(vector: list, initial_point: list, final_point: list) -> list:
    """
    Translates a 3 component vector from an initial to a final point.

    Args:
        vector: List with a 3 component vector (x, y, z).
        initial_point: List with a 3 component initial point (x, y, z).
        final_point: List with a 3 component final point (x, y, z).

    Returns:
        New translated vector.
    """

    # Realizar la traslación componente a componente

    translated_vector = [vector[i] + final_point[i] - initial_point[i] for i in range(3)]

    return translated_vector


def transformation_for_interpolation(corner_points: np.ndarray, centroid: np.ndarray, point: np.ndarray, element_system: np.ndarray, global_system = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]):
    """
    Transforms the nodes of an element and a point in it from the Global System to the Element System of the element centered in the Centroid.

    Args:
        corner_points: nodes of the element to be transformed.
        centroid: components of the centroid of the element.
        point: components of the point to be transformed.
        element_system: ndarray
        global_system: default = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    Returns:
        transformed_nodes
        transformed_point
    """

    # Definition of the nodes and point wrt the Global Refererence frame located in the centroid.
    nodes_position_vectors = [node-centroid for node in corner_points]
    point_position_vector = point-centroid

    # Transformation from the Global Reference Frame to the Element System, again wrt the centroid.
    transformed_nodes = [rotate_vector(vector, from_system = global_system, to_system = element_system) for vector in nodes_position_vectors]
    transformed_nodes = np.array([lists.tolist() for lists in transformed_nodes])

    transformed_point = rotate_vector(point_position_vector, from_system = global_system, to_system = element_system)

    return transformed_nodes, transformed_point






