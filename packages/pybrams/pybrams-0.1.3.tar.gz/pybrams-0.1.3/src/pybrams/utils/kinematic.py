import autograd.numpy as np
from .geometry import compute_specular_points_coordinates
from scipy.optimize import fsolve


def compute_times_of_flight(
    solution, TX_COORD, rx_coordinates, ref_rx_coordinates, deceleration_model
):
    """
    Compute the time of flight for specular points between a reference location and multiple receivers.

    Parameters
    ----------
    solution : array_like
        Array containing initial position (x, y, z) and velocity (vx, vy, vz) components, optionally followed by delta_t0 and deceleration parameters.
    TX_COORD : array_like
        Transmitter coordinates.
    rx_coordinates : array_like
        Array of receiver coordinates.
    ref_rx_coordinates : array_like
        Coordinates of the reference receiver.
    deceleration_model : str
        Type of deceleration model to use ("constant" or "linear").

    Returns
    -------
    np.ndarray
        Array of times of flight for each receiver.
    """

    start_coordinates = np.array([solution[0], solution[1], solution[2]])
    end_coordinates = np.array(
        [
            solution[0] + solution[3],
            solution[1] + solution[4],
            solution[2] + solution[5],
        ]
    )

    specular_points_coordinates = compute_specular_points_coordinates(
        start_coordinates, end_coordinates, TX_COORD, rx_coordinates
    )
    ref_specular_point_coordinates = start_coordinates

    times_of_flight = np.array(
        [
            compute_specular_time_of_flight(
                solution,
                specular_point_coordinates,
                ref_specular_point_coordinates,
                deceleration_model,
            )
            for specular_point_coordinates in specular_points_coordinates
        ]
    )

    return times_of_flight


def compute_specular_time_of_flight(
    solution,
    specular_point_coordinates,
    ref_specular_point_coordinates,
    deceleration_model,
):
    """
    Compute the time of flight from a reference point to a given specular point using the specified deceleration model.

    Parameters
    ----------
    solution : array_like
        Array containing position and velocity components, optionally followed by timing and deceleration parameters.
    specular_point_coordinates : array_like
        Coordinates of the current specular reflection point.
    ref_specular_point_coordinates : array_like
        Coordinates of the initial specular point (reference).
    deceleration_model : str
        The deceleration model to use ("constant" or "linear").

    Returns
    -------
    float
        Time of flight to the given specular point.
    """

    velocity = np.array([solution[3], solution[4], solution[5]])
    velocity_norm = np.linalg.norm(velocity)

    specular_point_distance_vector = (
        specular_point_coordinates - ref_specular_point_coordinates
    )
    specular_point_distance = np.linalg.norm(specular_point_distance_vector)

    if specular_point_distance != 0:
        if np.dot(velocity, specular_point_distance_vector) < 0:
            specular_point_distance = -specular_point_distance

        if deceleration_model == "constant":
            time_of_flight = specular_point_distance / velocity_norm

        if deceleration_model == "linear":
            delta_t0 = solution[6]
            a = solution[7]
            time_of_flight = fsolve(
                linear_time_of_flight,
                0,
                args=(velocity_norm, delta_t0, a, specular_point_distance),
            )

    else:
        time_of_flight = 0

    return time_of_flight


def linear_time_of_flight(delta_t, velocity_norm, delta_t0, a, specular_point_distance):
    """
    Residual function to solve the time of flight in the case of linear deceleration.

    Parameters
    ----------
    delta_t : float
        Time duration to evaluate.
    velocity_norm : float
        Initial speed magnitude.
    delta_t0 : float
        Time threshold before deceleration starts.
    a : float
        Linear deceleration rate.
    specular_point_distance : float
        Distance between the reference and specular point.

    Returns
    -------
    float
        The residual value of the time of flight equation.
    """

    if delta_t <= delta_t0:
        return specular_point_distance - delta_t * velocity_norm

    if delta_t > delta_t0:
        return (
            specular_point_distance
            - delta_t * velocity_norm
            + 1 / 2 * a * (delta_t - delta_t0) ** 2
        )


def compute_linear_velocity_profile(velocity_norm, delta_t0, a, times_of_flight):
    """
    Compute the velocity profile assuming a linear deceleration model.

    Parameters
    ----------
    velocity_norm : float
        Initial velocity magnitude.
    delta_t0 : float
        Time threshold before deceleration begins.
    a : float
        Deceleration rate.
    times_of_flight : array_like
        Array of time-of-flight values.

    Returns
    -------
    np.ndarray
        Velocity at each time-of-flight point.
    """

    speeds = np.zeros(times_of_flight.shape[0])

    for index, time_of_flight in enumerate(times_of_flight):
        if time_of_flight <= delta_t0:
            speeds[index] = velocity_norm

        if time_of_flight > delta_t0:
            speeds[index] = velocity_norm - a * (time_of_flight - delta_t0)

    return speeds


def exponential_time_of_flight(delta_t, velocity_norm, a1, a2, specular_point_distance):
    """
    Residual function for exponential deceleration time-of-flight model.

    Parameters
    ----------
    delta_t : float
        Time duration to evaluate.
    velocity_norm : float
        Initial velocity magnitude.
    a1 : float
        Amplitude factor in exponential term.
    a2 : float
        Exponential decay/growth rate.
    specular_point_distance : float
        Distance between the reference and the specular point.

    Returns
    -------
    float
        The residual of the time-of-flight equation under exponential deceleration.
    """

    return (
        specular_point_distance
        - delta_t * velocity_norm
        + np.abs(a1) * np.exp(a2 * delta_t)
    )


def compute_exponential_velocity_profile(velocity_norm, a1, a2, times_of_flight):
    """
    Compute velocity profile for exponential deceleration.

    Parameters
    ----------
    velocity_norm : float
        Initial velocity magnitude.
    a1 : float
        Amplitude coefficient of the exponential decay.
    a2 : float
        Exponential decay rate.
    times_of_flight : array_like
        Array of time-of-flight values.

    Returns
    -------
    np.ndarray
        Velocity at each time-of-flight point.
    """

    speeds = np.zeros(times_of_flight.shape[0])

    for index, time_of_flight in enumerate(times_of_flight):
        if time_of_flight > 0:
            speeds[index] = velocity_norm - np.abs(a1 * a2) * np.exp(
                a2 * time_of_flight
            )

        else:
            speeds[index] = velocity_norm

    return speeds
