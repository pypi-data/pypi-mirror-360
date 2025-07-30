import autograd.numpy as np

from itertools import product
from .constants import (
    MINIMUM_HORIZONTAL_POSITION,
    MAXIMUM_HORIZONTAL_POSITION,
    MINIMUM_ALTITUDE,
    MAXIMUM_ALTITUDE,
    DEFAULT_ALTITUDE,
    MINIMUM_HORIZONTAL_VELOCITY,
    MAXIMUM_HORIZONTAL_VELOCITY,
    MINIMUM_VERTICAL_VELOCITY,
    MAXIMUM_VERTICAL_VELOCITY,
    DEFAULT_VERTICAL_VELOCITY,
    MINIMUM_SPEED,
    MAXIMUM_SPEED,
    LINEAR_MINIMUM_TIMING,
    LINEAR_MAXIMUM_TIMING,
    LINEAR_MINIMUM_DECELERATION,
    LINEAR_MAXIMUM_DECELERATION,
    NUMBER_INITIAL_GUESSES_PER_VARIABLE,
)
from pybrams.utils.constants import TX_COORD
from pybrams.utils.geometry import compute_specular_points_coordinates


def generate_initial_guesses(velocity_model):
    x = np.linspace(
        MINIMUM_HORIZONTAL_POSITION,
        MAXIMUM_HORIZONTAL_POSITION,
        NUMBER_INITIAL_GUESSES_PER_VARIABLE + 2,
    )[1:-1]
    y = np.linspace(
        MINIMUM_HORIZONTAL_POSITION,
        MAXIMUM_HORIZONTAL_POSITION,
        NUMBER_INITIAL_GUESSES_PER_VARIABLE + 2,
    )[1:-1]
    z = np.array([DEFAULT_ALTITUDE])

    v_x = np.linspace(
        MINIMUM_HORIZONTAL_VELOCITY,
        MAXIMUM_HORIZONTAL_VELOCITY,
        NUMBER_INITIAL_GUESSES_PER_VARIABLE + 2,
    )[1:-1]
    v_y = np.linspace(
        MINIMUM_HORIZONTAL_VELOCITY,
        MAXIMUM_HORIZONTAL_VELOCITY,
        NUMBER_INITIAL_GUESSES_PER_VARIABLE + 2,
    )[1:-1]
    v_z = np.array([DEFAULT_VERTICAL_VELOCITY])

    if velocity_model == "constant":
        return np.array(list(product(x, y, z, v_x, v_y, v_z)))

    elif velocity_model == "linear":
        delta_t0 = np.linspace(
            LINEAR_MINIMUM_TIMING,
            LINEAR_MAXIMUM_TIMING,
            NUMBER_INITIAL_GUESSES_PER_VARIABLE + 2,
        )[1:-1]
        a = np.linspace(
            LINEAR_MINIMUM_DECELERATION,
            LINEAR_MAXIMUM_DECELERATION,
            NUMBER_INITIAL_GUESSES_PER_VARIABLE + 2,
        )[1:-1]
        return np.array(list(product(x, y, z, v_x, v_y, v_z, delta_t0, a)))


def set_lower_solution_bounds(velocity_model):
    lower_solution_bounds = np.array(
        [
            MINIMUM_HORIZONTAL_POSITION,
            MINIMUM_HORIZONTAL_POSITION,
            MINIMUM_ALTITUDE,
            MINIMUM_HORIZONTAL_VELOCITY,
            MINIMUM_HORIZONTAL_VELOCITY,
            MINIMUM_VERTICAL_VELOCITY,
        ]
    )

    if velocity_model == "constant":
        return lower_solution_bounds

    elif velocity_model == "linear":
        return np.concatenate(
            (
                lower_solution_bounds,
                np.array([LINEAR_MINIMUM_TIMING, LINEAR_MINIMUM_DECELERATION]),
            )
        )


def set_upper_solution_bounds(velocity_model):
    upper_solution_bounds = np.array(
        [
            MAXIMUM_HORIZONTAL_POSITION,
            MAXIMUM_HORIZONTAL_POSITION,
            MAXIMUM_ALTITUDE,
            MAXIMUM_HORIZONTAL_VELOCITY,
            MAXIMUM_HORIZONTAL_VELOCITY,
            MAXIMUM_VERTICAL_VELOCITY,
        ]
    )

    if velocity_model == "constant":
        return upper_solution_bounds

    elif velocity_model == "linear":
        return np.concatenate(
            (
                upper_solution_bounds,
                np.array([LINEAR_MAXIMUM_TIMING, LINEAR_MAXIMUM_DECELERATION]),
            )
        )


def set_lower_ineq_constraint_bounds(inputs):
    return np.concatenate(
        (
            np.array([MINIMUM_SPEED]),
            MINIMUM_HORIZONTAL_POSITION * np.ones(len(inputs)),
            MINIMUM_HORIZONTAL_POSITION * np.ones(len(inputs)),
            MINIMUM_ALTITUDE * np.ones(len(inputs)),
        )
    )


def set_upper_ineq_constraint_bounds(inputs):
    return np.concatenate(
        (
            np.array([MAXIMUM_SPEED]),
            MAXIMUM_HORIZONTAL_POSITION * np.ones(len(inputs)),
            MAXIMUM_HORIZONTAL_POSITION * np.ones(len(inputs)),
            MAXIMUM_ALTITUDE * np.ones(len(inputs)),
        )
    )


def ineq_constraints(x, rx_coordinates):
    # Define the inequality constraints for the solving of the time of flight system

    constraints = np.zeros(3 * rx_coordinates.shape[0] + 1)

    start_coordinates = np.array([x[0], x[1], x[2]])
    end_coordinates = np.array([x[0] + x[3], x[1] + x[4], x[2] + x[5]])

    specular_points_coordinates = compute_specular_points_coordinates(
        start_coordinates, end_coordinates, TX_COORD, rx_coordinates
    )

    constraints[0] = np.sqrt(x[3] ** 2 + x[4] ** 2 + x[5] ** 2)
    constraints[1 : rx_coordinates.shape[0] + 1] = specular_points_coordinates[:, 0]
    constraints[
        rx_coordinates.shape[0] + 1 : 2 * rx_coordinates.shape[0] + 1
    ] = specular_points_coordinates[:, 1]
    constraints[2 * rx_coordinates.shape[0] + 1 :] = specular_points_coordinates[:, 2]

    return constraints
