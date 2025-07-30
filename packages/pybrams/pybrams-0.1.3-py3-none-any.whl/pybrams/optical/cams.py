# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 18:05:36 2023

@author: joachimb
"""

import datetime
import autograd.numpy as np
from scipy.optimize import fsolve
from pathlib import Path

from pybrams.trajectory.solver import Solver
from pybrams.utils.constants import TX_COORD, WAVELENGTH
from pybrams.utils.data import Data
from pybrams.utils.geometry import (
    compute_specular_points_coordinates,
    compute_fresnel_geometry,
)
from pybrams.utils.kinematic import (
    compute_exponential_velocity_profile,
    exponential_time_of_flight,
)
from pybrams.utils.coordinates import Coordinates
from pybrams.utils.interval import Interval
import pybrams.brams.location
import logging

from .constants import (
    MINIMUM_HORIZONTAL_POSITION_OPTICAL,
    MAXIMUM_HORIZONTAL_POSITION_OPTICAL,
    MINIMUM_ALTITUDE_OPTICAL,
    MAXIMUM_ALTITUDE_OPTICAL,
    MINIMUM_NUMBER_SYSTEMS_OPTICAL,
)

logger = logging.getLogger(__name__)


class CAMS:
    """
    CAMS (Cameras for Allsky Meteor Surveillance) class for processing meteor
    trajectory data and comparing with BRAMS (Brazilian Meteor Radar) data.

    This class provides methods to:
    - Load and parse CAMS trajectory data
    - Filter trajectories based on geometric constraints
    - Retrieve relevant timing intervals for selected meteors
    - Calculate speed and equivalent range for a radar site
    - Generate a trajectory solution and compare it with BRAMS radar data

    Args:
        args: An argument namespace or object with at least `date` and `number` attributes,
              identifying a specific trajectory to analyze.
    """

    def __init__(self, args):
        self.args = args
        self.load()

    def load(self):
        """
        Load and parse the CAMS trajectory data from the 'SummaryMeteorLog_Cams.txt' file.

        The parsed data is stored as a list of dictionaries in `self.data`.
        """

        input = Data.load(__name__, "SummaryMeteorLog_Cams.txt", False).splitlines()

        header = [
            "number",
            "observed_date",
            "reference_time",
            "TBeg",
            "TEnd",
            "RAinf",
            "RAinf+-",
            "DECinf",
            "DECinf+-",
            "Vinf",
            "Vinf+-",
            "Acc1",
            "Acc1+-",
            "Acc2",
            "Acc2+-",
            "LatBeg",
            "LatBeg+-",
            "LonBeg",
            "LonBeg+-",
            "HBeg",
            "HBeg+-",
            "LatEnd",
            "LatEnd+-",
            "LonEnd",
            "LonEnd+-",
            "HEnd",
            "HEnd+-",
            "Conv",
            "S-Azim",
            "ZenAng",
            "Hmax",
            "Max-mV",
            "Int-mV",
            "F-skew",
            "Cameras",
        ]

        self.data = []

        for line in input[3:-1]:
            trajectory_data = line.split()
            self.data.append(dict((x, y) for x, y in zip(header, trajectory_data)))

    def filter(self):
        """
        Filter out trajectories that do not meet the criteria for specular points
        being within an acceptable altitude and horizontal position range.

        Only trajectories with enough valid specular points are retained in `self.data`.
        """

        brams_location = pybrams.brams.location.all()
        rx_coordinates = np.zeros((len(brams_location), 3))

        for index, location in enumerate(brams_location):
            rx_coordinates[index, :] = [
                brams_location[location].coordinates.dourbocentric.x,
                brams_location[location].coordinates.dourbocentric.y,
                brams_location[location].coordinates.dourbocentric.z,
            ]

        for trajectory in self.data:
            start_coordinates = Coordinates.fromGeodetic(
                float(trajectory["LatBeg"]),
                float(trajectory["LonBeg"]),
                float(trajectory["HBeg"]),
            )
            end_coordinates = Coordinates.fromGeodetic(
                float(trajectory["LatEnd"]),
                float(trajectory["LonEnd"]),
                float(trajectory["HEnd"]),
            )

            start_coordinates = np.array(
                [
                    start_coordinates.dourbocentric.x,
                    start_coordinates.dourbocentric.y,
                    start_coordinates.dourbocentric.z,
                ]
            )
            end_coordinates = np.array(
                [
                    end_coordinates.dourbocentric.x,
                    end_coordinates.dourbocentric.y,
                    end_coordinates.dourbocentric.z,
                ]
            )

            specular_points_coordinates = compute_specular_points_coordinates(
                start_coordinates, end_coordinates, TX_COORD, rx_coordinates
            )

            specular_points_in_range = np.array(
                list(
                    filter(self.is_specular_point_in_range, specular_points_coordinates)
                )
            )

            if len(specular_points_in_range) >= MINIMUM_NUMBER_SYSTEMS_OPTICAL:
                logger.info(
                    f"Number of specular points in range: {len(specular_points_in_range)}"
                )
                logger.info(f"Number = {trajectory['number']}")
                logger.info(f"start coord = {start_coordinates}")
                logger.info(f"end coord = {end_coordinates}")
                logger.info(f"vinf = {trajectory['Vinf']}")
                logger.info(f"vinf+- = {trajectory['Vinf+-']}")
                logger.info(f"Acc1=  {trajectory['Acc1']}")
                logger.info(f"Acc1+- = {trajectory['Acc1+-']}")
                logger.info(f"Acc2= {trajectory['Acc2']}")
                logger.info(f"Acc2+- = {trajectory['Acc2+-']}")

            else:
                self.data.remove(trajectory)

    def is_specular_point_in_range(self, array):
        """
        Check if a specular point falls within the configured spatial boundaries.

        Args:
            array (np.ndarray): A 3D point in dourbocentric coordinates.

        Returns:
            bool: True if the point is within the spatial range; False otherwise.
        """

        return (
            array[0] > MINIMUM_HORIZONTAL_POSITION_OPTICAL
            and array[0] < MAXIMUM_HORIZONTAL_POSITION_OPTICAL
            and array[1] > MINIMUM_HORIZONTAL_POSITION_OPTICAL
            and array[1] < MAXIMUM_HORIZONTAL_POSITION_OPTICAL
            and array[2] > MINIMUM_ALTITUDE_OPTICAL
            and array[2] < MAXIMUM_ALTITUDE_OPTICAL
        )

    def get_interval(self):
        """
        Retrieve the observation time interval for the selected trajectory.

        Returns:
            Interval: Time interval (start, end) of meteor observation.
        """

        for trajectory in self.data:
            trajectory_number = trajectory["number"].lstrip("0")
            trajectory_date = trajectory["observed_date"]

            if (
                trajectory_date == self.args.date
                and trajectory_number == self.args.number
            ):
                day = trajectory["observed_date"]
                time = trajectory["reference_time"]
                observed_date = datetime.datetime.strptime(
                    day + " " + time, "%Y-%m-%d %H:%M:%S.%f"
                ).replace(tzinfo=datetime.timezone.utc)

                start = observed_date - datetime.timedelta(seconds=1)
                end = observed_date + datetime.timedelta(seconds=4)

                interval = Interval(start, end)

                logger.info(
                    f"CAMS trajectory number = {trajectory['number']} - Time = {time}"
                )

                logger.info(f"Start = {start}")
                logger.info(f"End = {end}")

                return interval

    def get_speed_range(self, rx_location):
        """
        Compute the speed and Fresnel equivalent range for a selected radar receiver.

        Args:
            rx_location: A receiver location object with latitude, longitude, and altitude.

        Returns:
            tuple: (speed [km/s], equivalent Fresnel range [km^2])
        """

        for trajectory in self.data:
            trajectory_number = trajectory["number"].lstrip("0")
            trajectory_date = trajectory["observed_date"]

            if (
                trajectory_date == self.args.date
                and trajectory_number == self.args.number
            ):
                start_coord = (
                    Coordinates.fromGeodetic(
                        float(trajectory["LatBeg"]),
                        float(trajectory["LonBeg"]),
                        float(trajectory["HBeg"]),
                    )
                ).get_dourbocentric_array()
                end_coord = (
                    Coordinates.fromGeodetic(
                        float(trajectory["LatEnd"]),
                        float(trajectory["LonEnd"]),
                        float(trajectory["HEnd"]),
                    )
                ).get_dourbocentric_array()

                velocity_unit = (end_coord - start_coord) / np.linalg.norm(
                    end_coord - start_coord
                )
                velocity = float(trajectory["Vinf"]) * velocity_unit
                speed = np.linalg.norm(velocity)

                rx_coord = (
                    Coordinates.fromGeodetic(
                        rx_location.latitude,
                        rx_location.longitude,
                        rx_location.altitude,
                    )
                ).get_dourbocentric_array()

                cams_K = compute_fresnel_geometry(
                    start_coord, end_coord, TX_COORD, rx_coord
                )

                equiv_range = 2 * cams_K**2

                return speed, equiv_range

    def get_solution(self, brams_data):
        """
        Generate a trajectory solution from CAMS data and compare it against BRAMS radar data.

        This function computes:
        - Specular points
        - Initial velocity vectors
        - Time of flight (constant and exponential)
        - Pseudo-velocity metrics
        - Difference metrics for validation

        Args:
            brams_data: The BRAMS dataset input to be used for comparison and solving.

        Returns:
            np.ndarray: A 6-element solution vector [x, y, z, vx, vy, vz] in dourbocentric coordinates.
        """

        for trajectory in self.data:
            trajectory_number = trajectory["number"].lstrip("0")
            trajectory_date = trajectory["observed_date"]

            if (
                trajectory_date == self.args.date
                and trajectory_number == self.args.number
            ):
                trajectory_start = Coordinates.fromGeodetic(
                    float(trajectory["LatBeg"]),
                    float(trajectory["LonBeg"]),
                    float(trajectory["HBeg"]),
                )
                trajectory_end = Coordinates.fromGeodetic(
                    float(trajectory["LatEnd"]),
                    float(trajectory["LonEnd"]),
                    float(trajectory["HEnd"]),
                )

                start_coordinates = np.array(
                    [
                        trajectory_start.dourbocentric.x,
                        trajectory_start.dourbocentric.y,
                        trajectory_start.dourbocentric.z,
                    ]
                )
                end_coordinates = np.array(
                    [
                        trajectory_end.dourbocentric.x,
                        trajectory_end.dourbocentric.y,
                        trajectory_end.dourbocentric.z,
                    ]
                )

                time_CAMS_record = float(trajectory["TEnd"]) - float(trajectory["TBeg"])
                velocity = (end_coordinates - start_coordinates) / time_CAMS_record
                unit_velocity = velocity / np.linalg.norm(velocity)

                speed_inf = float(trajectory["Vinf"])

                a1 = float(trajectory["Acc1"])
                a2 = float(trajectory["Acc2"])

                speed_0 = speed_inf - a1 * a2
                velocity_0 = speed_0 * unit_velocity

                try:
                    dummy_solver = Solver(brams_data, args=self.args)

                except Exception as e:
                    print(f"Error setting up solver: {e}")
                    return

                specular_points_coordinates = compute_specular_points_coordinates(
                    start_coordinates,
                    end_coordinates,
                    TX_COORD,
                    dummy_solver.rx_coordinates,
                )
                ref_specular_point_coordinates = compute_specular_points_coordinates(
                    start_coordinates,
                    end_coordinates,
                    TX_COORD,
                    dummy_solver.ref_rx_coordinates,
                )

                cams_solution = np.array(
                    [
                        ref_specular_point_coordinates[0],
                        ref_specular_point_coordinates[1],
                        ref_specular_point_coordinates[2],
                        velocity_0[0],
                        velocity_0[1],
                        velocity_0[2],
                    ]
                )

                logger.info("CAMS solution")
                logger.info(f"X [km] = {round(cams_solution[0], 2)}")
                logger.info(f"Y [km] = {round(cams_solution[1], 2)}")
                logger.info(f"Z [km] = {round(cams_solution[2], 2)}")
                logger.info(f"Vx [km/s] = {round(cams_solution[3], 2)}")
                logger.info(f"Vy [km/s] = {round(cams_solution[4], 2)}")
                logger.info(f"Vz [km/s] = {round(cams_solution[5], 2)}")

                cams_constant_times = np.zeros(dummy_solver.rx_coordinates.shape[0])
                cams_exponential_times = np.zeros(dummy_solver.rx_coordinates.shape[0])

                for i in range(dummy_solver.rx_coordinates.shape[0]):
                    specular_point_distance_vector = (
                        specular_points_coordinates[i, :] - start_coordinates
                    )
                    specular_point_distance = np.linalg.norm(
                        specular_point_distance_vector
                    )

                    if np.dot(specular_point_distance_vector, velocity) < 0:
                        specular_point_distance = -specular_point_distance

                    cams_constant_times[i] = specular_point_distance / speed_0
                    cams_exponential_times[i] = fsolve(
                        exponential_time_of_flight,
                        0,
                        args=((speed_inf, a1, a2, specular_point_distance)),
                    )

                cams_speeds = np.zeros_like(cams_exponential_times)
                cams_speeds = compute_exponential_velocity_profile(
                    speed_inf, a1, a2, cams_exponential_times
                )
                cams_K = compute_fresnel_geometry(
                    start_coordinates,
                    end_coordinates,
                    TX_COORD,
                    dummy_solver.rx_coordinates,
                )

                cams_v_pseudo_pre_t0s = cams_speeds / (cams_K * np.sqrt(WAVELENGTH / 2))

                radio_v_pseudo_pre_t0s = np.array(
                    [
                        inner_dict["v_pseudo_pre_t0"]
                        for inner_dict in dummy_solver.inputs.values()
                    ]
                )
                radio_v_pseudo_pre_t0s[radio_v_pseudo_pre_t0s == None] = np.nan

                times_of_flight = (
                    cams_constant_times
                    - cams_constant_times[dummy_solver.ref_system_index]
                )
                dummy_solver.times_of_flight = (
                    dummy_solver.times_of_flight
                    - dummy_solver.times_of_flight[dummy_solver.ref_system_index]
                )

                max_cams_time_of_flight = (
                    float(trajectory["TEnd"])
                    - float(trajectory["TBeg"])
                    - cams_constant_times[dummy_solver.ref_system_index]
                )

                diff_times_of_flight = dummy_solver.times_of_flight - times_of_flight
                diff_v_pseudo_pre_t0s = (
                    100
                    * (radio_v_pseudo_pre_t0s - cams_v_pseudo_pre_t0s)
                    / np.abs(cams_v_pseudo_pre_t0s)
                )

                logger.debug(
                    f"Max CAMS time of flight [ms] = "
                    f"{np.round(1e3 * max_cams_time_of_flight, 2)}"
                )

                for index, system_code in enumerate(dummy_solver.inputs):
                    logger.info(
                        f"{system_code}"
                        f" - Opt time of flight [ms] = "
                        f"{np.round(1e3 * times_of_flight[index], 2)}"
                        f" - Radio time of flight [ms] = "
                        f"{np.round(1e3 * dummy_solver.times_of_flight[index], 2)}"
                        f" - Diff = "
                        f"{np.round(1e3 * diff_times_of_flight[index], 2)}"
                        " ms"
                    )

                for index, system_code in enumerate(dummy_solver.inputs):
                    if not np.isnan(radio_v_pseudo_pre_t0s[index]):
                        logger.info(
                            f"{system_code}"
                            f" - Opt pre-t0 pseudo speed [s⁻¹] = "
                            f"{np.round(cams_v_pseudo_pre_t0s[index],2)}"
                            f" - Radio pre-t0 pseudo speed [s⁻¹] = "
                            f"{np.round(radio_v_pseudo_pre_t0s[index], 2)}"
                            f" - Diff = {np.round(diff_v_pseudo_pre_t0s[index], 2)} % "
                        )

                logger.debug(
                    f"Difference pre-t0 mean [%] = {np.round(np.nanmean(np.abs(diff_v_pseudo_pre_t0s)), 2)}"
                )
                logger.debug(
                    f"Difference pre-t0 median [%] = {np.round(np.nanmedian(np.abs(diff_v_pseudo_pre_t0s)), 2)}"
                )
                logger.debug(
                    f"Difference pre-t0 standard deviation [%] = {np.round(np.nanstd(np.abs(diff_v_pseudo_pre_t0s)), 2)}"
                )

                return cams_solution
