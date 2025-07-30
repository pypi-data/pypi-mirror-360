import autograd.numpy as np


def compute_specular_points_coordinates(
    start_coordinates, end_coordinates, TX_COORD, rx_coordinates
):
    """
    Compute the coordinates of the specular reflection points between the transmitter, receiver(s),
    and the ellipsoidal reflection surface.

    Parameters
    ----------
    start_coordinates : array_like
        Start point of the trajectory line (typically a GNSS satellite position).
    end_coordinates : array_like
        End point of the trajectory line.
    TX_COORD : array_like
        Coordinates of the transmitter.
    rx_coordinates : array_like
        Coordinates of one or more receivers (shape (3,) or (N, 3)).

    Returns
    -------
    ndarray
        Coordinates of the specular reflection point(s), shape (3,) or (N, 3) depending on input.
    """

    single_rx = rx_coordinates.ndim == 1

    if single_rx:
        rx_coordinates = np.array([rx_coordinates])

    specular_points_coordinates = np.array(
        [
            solve_line_ellipsoid_intersection(
                start_coordinates, end_coordinates, TX_COORD, receiver_coordinates
            )
            for receiver_coordinates in rx_coordinates
        ]
    )

    if single_rx:
        specular_points_coordinates = specular_points_coordinates[0]

    return specular_points_coordinates


def solve_line_ellipsoid_intersection(
    start_coordinates, end_coordinates, TX_COORD, receiver_coordinates
):
    """
    Compute the intersection point of a trajectory line and the ellipsoidal reflection surface.

    Parameters
    ----------
    start_coordinates : array_like
        Start point of the trajectory line.
    end_coordinates : array_like
        End point of the trajectory line.
    TX_COORD : array_like
        Coordinates of the transmitter.
    receiver_coordinates : array_like
        Coordinates of the receiver.

    Returns
    -------
    ndarray
        Specular point coordinates in the global coordinate system.
    """

    P13, P23, PT3, PR3, alpha, beta = move_to_ellipsoid_reference_frame(
        start_coordinates, end_coordinates, TX_COORD, receiver_coordinates
    )  # Move to a cartesian coordinate system in which the origin is the center of the ellipsoid and the coordinate axes are the ellipsoid axes
    p3 = find_specular_point_ellipsoid_frame(P13, P23, PR3, PT3)

    # Solve equation
    p3 = np.array([p3[0], p3[1], p3[2]])  # Tangent point in third coordinate system

    # From third coordinate system (ellipsoid) to Dourbocentric one
    Rx = np.array(
        [[1, 0, 0], [0, np.cos(beta), np.sin(beta)], [0, -np.sin(beta), np.cos(beta)]]
    )
    Rz = np.array(
        [
            [np.cos(alpha), np.sin(alpha), 0],
            [-np.sin(alpha), np.cos(alpha), 0],
            [0, 0, 1],
        ]
    )
    p2 = Rx @ p3  # Rotation around 1x (-alpha)
    p1 = Rz @ p2  # Rotation around 1z (-beta)

    return p1 + receiver_coordinates / 2  # Translation


def compute_fresnel_geometry(
    start_coordinates, end_coordinates, TX_COORD, rx_coordinates
):
    specular_points_coordinates = compute_specular_points_coordinates(
        start_coordinates, end_coordinates, TX_COORD, rx_coordinates
    )
    """
    Compute the Fresnel zone geometry factor K for given transmitter and receiver positions.

    Parameters
    ----------
    start_coordinates : array_like
        Start of the trajectory line.
    end_coordinates : array_like
        End of the trajectory line.
    TX_COORD : array_like
        Transmitter coordinates.
    rx_coordinates : array_like
        Receiver coordinates (shape (3,) or (N, 3)).

    Returns
    -------
    float or ndarray
        Fresnel geometry factor K, scalar if single receiver, array if multiple.
    """

    single_specular_point = specular_points_coordinates.ndim == 1

    if single_specular_point:
        specular_points_coordinates = np.array([specular_points_coordinates])

    range_tx_specular_point = np.linalg.norm(
        specular_points_coordinates - TX_COORD, axis=1
    )
    range_rx_specular_point = np.linalg.norm(
        specular_points_coordinates - rx_coordinates, axis=1
    )

    normal_propagation_plane = np.cross(
        TX_COORD - specular_points_coordinates,
        rx_coordinates - specular_points_coordinates,
        axis=1,
    )
    normal_propagation_plane = normal_propagation_plane / np.linalg.norm(
        normal_propagation_plane, axis=1
    ).reshape(-1, 1)

    direction = (end_coordinates - start_coordinates) / np.linalg.norm(
        end_coordinates - start_coordinates
    )

    phi = (
        1
        / 2
        * np.arccos(
            loop_dot(
                TX_COORD - specular_points_coordinates,
                rx_coordinates - specular_points_coordinates,
            )
            / (
                np.linalg.norm(TX_COORD - specular_points_coordinates, axis=1)
                * np.linalg.norm(rx_coordinates - specular_points_coordinates, axis=1)
            )
        )
    )

    beta = np.arcsin(np.abs(np.dot(normal_propagation_plane, direction)))

    K = np.zeros(rx_coordinates.shape[0])
    K = np.sqrt(
        (range_tx_specular_point * range_rx_specular_point)
        / (
            (range_tx_specular_point + range_rx_specular_point)
            * (1 - ((np.sin(phi) ** 2) * (np.cos(beta) ** 2)))
        )
    )

    if single_specular_point:
        K = K[0]

    return K


def compute_geometry_parameters(
    start_coordinates, end_coordinates, TX_COORD, rx_coordinates
):
    """
    Compute range and angular geometry parameters between transmitter, receiver(s), and specular point(s).

    Parameters
    ----------
    start_coordinates : array_like
        Start of the trajectory line.
    end_coordinates : array_like
        End of the trajectory line.
    TX_COORD : array_like
        Transmitter coordinates.
    rx_coordinates : array_like
        Receiver coordinates (shape (3,) or (N, 3)).

    Returns
    -------
    tuple of ndarray
        Contains:
        - range_tx_specular_point (ndarray): Distance TX to specular point(s)
        - range_rx_specular_point (ndarray): Distance RX to specular point(s)
        - phi (ndarray): Half of the angle between TX and RX vectors
        - beta (ndarray): Angle between propagation plane normal and trajectory direction
    """

    specular_points_coordinates = compute_specular_points_coordinates(
        start_coordinates, end_coordinates, TX_COORD, rx_coordinates
    )

    single_specular_point = specular_points_coordinates.ndim == 1

    if single_specular_point:
        specular_points_coordinates = np.array([specular_points_coordinates])

    range_tx_specular_point = np.linalg.norm(
        specular_points_coordinates - TX_COORD, axis=1
    )
    range_rx_specular_point = np.linalg.norm(
        specular_points_coordinates - rx_coordinates, axis=1
    )

    normal_propagation_plane = np.cross(
        TX_COORD - specular_points_coordinates,
        rx_coordinates - specular_points_coordinates,
        axis=1,
    )
    normal_propagation_plane = normal_propagation_plane / np.linalg.norm(
        normal_propagation_plane, axis=1
    ).reshape(-1, 1)

    direction = (end_coordinates - start_coordinates) / np.linalg.norm(
        end_coordinates - start_coordinates
    )

    phi = (
        1
        / 2
        * np.arccos(
            loop_dot(
                TX_COORD - specular_points_coordinates,
                rx_coordinates - specular_points_coordinates,
            )
            / (
                np.linalg.norm(TX_COORD - specular_points_coordinates, axis=1)
                * np.linalg.norm(rx_coordinates - specular_points_coordinates, axis=1)
            )
        )
    )

    beta = np.arcsin(np.abs(np.dot(normal_propagation_plane, direction)))

    return range_tx_specular_point, range_rx_specular_point, phi, beta


def move_to_ellipsoid_reference_frame(P1, P2, PT, PR):
    """
    Transform coordinates into the ellipsoid-aligned reference frame.

    Parameters
    ----------
    P1, P2 : array_like
        Endpoints of the line segment.
    PT : array_like
        Transmitter coordinates.
    PR : array_like
        Receiver coordinates.

    Returns
    -------
    tuple
        Transformed coordinates (P13, P23, PT3, PR3) and rotation angles (alpha, beta).
    """

    P11 = P1 - PR / 2
    P21 = P2 - PR / 2
    PR1 = PT - PR / 2
    PT1 = PR - PR / 2

    # Rotation around z axis
    alpha = np.arctan2(PR1[0], PR1[1])  # Angle between first and second system
    Rz = np.array(
        [
            [np.cos(alpha), -np.sin(alpha), 0],
            [np.sin(alpha), np.cos(alpha), 0],
            [0, 0, 1],
        ]
    )  # Rotation matrix
    P12 = Rz.dot(P11)
    P22 = Rz.dot(P21)
    PT2 = Rz.dot(PT1)
    PR2 = Rz.dot(PR1)

    # Rotation around x axis
    beta = -np.arctan2(PR2[2], PR2[1])  # Angle between second and third axis
    Rx = np.array(
        [[1, 0, 0], [0, np.cos(beta), -np.sin(beta)], [0, np.sin(beta), np.cos(beta)]]
    )  # Rotation matrix
    P13 = Rx.dot(P12)
    P23 = Rx.dot(P22)
    PT3 = Rx.dot(PT2)
    PR3 = Rx.dot(PR2)

    return P13, P23, PT3, PR3, alpha, beta


def find_specular_point_ellipsoid_frame(p1, p2, PR, PT):
    """
    Solve the geometric condition for specular reflection on an ellipsoid in its reference frame.

    Parameters
    ----------
    p1, p2 : array_like
        Transformed trajectory segment endpoints in ellipsoid frame.
    PR, PT : array_like
        Receiver and transmitter positions in ellipsoid frame.

    Returns
    -------
    ndarray
        Coordinates of the specular reflection point in the ellipsoid reference frame.
    """

    f = compute_distance_points(PT, PR) / 2  # Half the interfocal distance
    f_2 = f**2

    c2 = (p1[1] - p2[1]) ** 2 * (
        (p1[1] - p2[1]) ** 2 + ((p1[0] - p2[0]) ** 2 + (p1[2] - p2[2]) ** 2)
    )  # b^4 coef
    c1 = (p1[1] - p2[1]) ** 2 * (
        -2 * (p1[1] - p2[1]) ** 2 * f_2
        - ((p1[0] - p2[0]) ** 2 + (p1[2] - p2[2]) ** 2) * f_2
        - (p2[1] ** 2) * (p1[0] ** 2 + p1[2] ** 2)
        + 2 * p1[1] * p2[1] * (p1[0] * p2[0] + p1[2] * p2[2])
        - p1[1] ** 2 * (p2[0] ** 2 + p2[2] ** 2)
        - (p2[0] * p1[2] - p1[0] * p2[2]) ** 2
    )  # b^2 coefficient
    c0 = (
        (p1[1] - p2[1]) ** 2
        * f_2
        * (
            (p1[1] - p2[1]) ** 2 * f_2
            + p2[1] ** 2 * (p1[0] ** 2 + p1[2] ** 2)
            - 2 * p1[1] * p2[1] * (p1[0] * p2[0] + p1[2] * p2[2])
            + p1[1] ** 2 * (p2[0] ** 2 + p2[2] ** 2)
        )
    )

    delta = c1**2 - 4 * c2 * c0
    sol_1 = (-c1 + np.sqrt(delta)) / (2 * c2)
    sol_2 = (-c1 - np.sqrt(delta)) / (2 * c2)

    sol = np.array([sol_1, sol_2])

    a, b = check_specular_point_solution(sol, f)  # Get the single values for a and b

    A = (
        ((p2[0] - p1[0]) ** 2 + (p2[2] - p1[2]) ** 2) * b**2
        + a**2 * (p2[1] - p1[1]) ** 2
    ) / ((p2[1] - p1[1]) ** 2)
    B = (
        2
        * b**2
        * (
            (p2[0] - p1[0]) * (p2[1] - p1[1]) * p2[0]
            + (p2[2] - p1[2]) * (p2[1] - p1[1]) * p2[2]
            - p2[1] * ((p2[0] - p1[0]) ** 2 + (p2[2] - p1[2]) ** 2)
        )
        / ((p2[1] - p1[1]) ** 2)
    )

    if A != 0:  # Constraint on A
        p_1 = -B / (
            2 * A
        )  # Y coordinate of the reflection point (just a single solution)

    p_0 = p2[0] + (p2[0] - p1[0]) / (p2[1] - p1[1]) * (
        p_1 - p2[1]
    )  # X coordinate of the reflection point
    p_2 = p2[2] + (p2[2] - p1[2]) / (p2[1] - p1[1]) * (
        p_1 - p2[1]
    )  # Z coordinate of the reflection point

    p = np.array([p_0, p_1, p_2])

    return p


def compute_distance_points(P1, P2):
    res = np.sqrt((P1[0] - P2[0]) ** 2 + (P1[1] - P2[1]) ** 2 + (P1[2] - P2[2]) ** 2)
    return res


def check_specular_point_solution(sol, f):
    for i in range(sol.shape[0]):
        if sol[i] - f**2 > 0:
            b2 = sol[i]
            b = np.sqrt(b2)
            a = np.sqrt(b2 - f**2)
            break

    return a, b


def loop_dot(x, y):
    result = np.array([np.dot(x_row, y_row) for x_row, y_row in zip(x, y)])
    return result


def compute_angle(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)

    cos_theta = dot_product / (norm_vector1 * norm_vector2)
    theta = np.arccos(
        np.clip(cos_theta, -1.0, 1.0)
    )  # Clip to handle numerical precision issues

    return np.degrees(theta)


def compute_azimuth_elevation(velocity):
    vx, vy, vz = velocity
    v_mag = np.linalg.norm(velocity)

    if v_mag == 0:
        raise ValueError("Zero vector has no defined direction.")

    # Compute angles
    phi = 180 / np.pi * np.arcsin(vz / v_mag)  # Elevation angle
    theta = 180 / np.pi * np.arctan2(vy, vx)  # Azimuth angle

    return phi, theta
