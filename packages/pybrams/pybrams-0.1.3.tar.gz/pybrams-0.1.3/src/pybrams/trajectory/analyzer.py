import numpy as np
import dill
import matplotlib.pyplot as plt

from pybrams.utils import Config
from pybrams.trajectory.solver import Solver
from pybrams.utils.cache import Cache

from pybrams.utils.geometry import compute_angle

from .mcmc import MCMCAnalyzer

import os
import logging

logger = logging.getLogger(__name__)


class TrajectoryAnalyzer:
    """
    Class to perform trajectory analysis based on BRAMS meteor data.

    The analyzer solves for meteor trajectories using multiple weightings of pre-t0 objectives,
    performs a Pareto front analysis to select the best trade-off ("knee" point), and optionally
    performs MCMC-based uncertainty quantification.

    Attributes:
        brams_data (object): The BRAMS observation data.
        args (Namespace): Command-line or configuration arguments for controlling behavior.
        cams_solution (np.ndarray, optional): Reference trajectory solution (e.g., from CAMS).
        weights_pre_t0_objective (list): Weightings for the pre-t0 objective function.
        solvers (list): List of Solver instances for each weighting.
        cached_dill (bytes): Cached solution in Dill format (if available).
    """

    def __init__(self, brams_data, args, cams_solution=None):
        """
        Initialize the TrajectoryAnalyzer.

        Args:
            brams_data (object): Input BRAMS observation data.
            args (Namespace): Arguments used to control behavior.
            cams_solution (np.ndarray, optional): Optional reference trajectory to compute errors against.
        """

        self.brams_data = brams_data
        self.args = args
        self.cams_solution = cams_solution
        self.weights_pre_t0_objective = getattr(
            args,
            "weights_pre_t0_objective",
            Config.get(__name__, "weights_pre_t0_objective"),
        )
        self.solvers = []
        self.cached_dill = Cache.get(f"trajectory_{self.args.key}.dill", json=False)

    def run(self):
        """
        Main entry point to run the trajectory analysis.

        - Runs solver if no cached result is found or recomputation is requested.
        - Computes and stores the best solution (knee).
        - Optionally runs MCMC uncertainty quantification.
        """

        if (
            not self.cached_dill
            or self.args.recompute_trajectory
            or self.args.recompute_meteors
        ):
            self.run_solvers()

            self.unpack_solvers()
            self.get_pareto_front_solvers()
            self.get_solver_knee()
            self.output_solver_knee()

            self.plot_pareto_front()
            self.plot_total_cost_fun()
            self.plot_errors()

        else:
            print("Nothing was done here. Trajectory already computed.")
            self.solver_knee = dill.loads(self.cached_dill)

        if self.args.uncertainty:
            print("MCMC uncertainty quantification...")
            self.run_MCMC()

    def run_solvers(self):
        """
        Runs trajectory solvers with different pre-t0 objective weights.

        - Uses a reference solver to detect outliers if multiple weights are provided.
        - Removes outliers for each subsequent solver run (if required).
        - Computes errors against reference CAMS solution if provided.
        """

        if len(self.weights_pre_t0_objective) > 1:
            self.args.outlier_removal = True

            try:
                ref_solver = Solver(self.brams_data, args=self.args)
                ref_solver.print_inputs()

                print("Call reference solver with default weight")

                ref_solver.solve()

            except Exception as e:
                print(f"Error during trajectory solving: {e}")

        for i, weight_pre_t0_objective in enumerate(self.weights_pre_t0_objective):
            self.args.weight_pre_t0_objective = weight_pre_t0_objective

            if len(self.weights_pre_t0_objective) > 1:
                self.args.outlier_removal = False

                solver = Solver(self.brams_data, args=self.args)
                solver.remove_inputs(
                    ref_solver.outlier_system_codes,
                    ref_solver.outlier_pre_t0_system_codes,
                )

            else:
                self.args.outlier_removal = True
                solver = Solver(self.brams_data, args=self.args)

                solver.print_inputs()

            print(
                f"Call solver {i + 1} out of {len(self.weights_pre_t0_objective)} | "
                f"Weight pre-t0 = {self.args.weight_pre_t0_objective}"
            )

            try:
                solver.solve()
            except Exception as e:
                print(f"Error during trajectory solving: {e}")

            radio_velocity = np.array(
                [solver.solution[3], solver.solution[4], solver.solution[5]]
            )

            if self.cams_solution is not None:
                solver.speed_error = (
                    1e2
                    * (
                        np.linalg.norm(radio_velocity)
                        - np.linalg.norm(self.cams_solution[3:6])
                    )
                    / np.linalg.norm(self.cams_solution[3:6])
                )
                solver.inclination_error = compute_angle(
                    self.cams_solution[3:6], radio_velocity
                )
                solver.ref_altitude_specular_point_error = (
                    solver.solution[2] - self.cams_solution[2]
                )

                solver.cams_solution = self.cams_solution

                logger.info(f"Speed error [%] = {np.round(solver.speed_error, 2)}")
                logger.info(
                    f"Inclination error [\u00b0] = {np.round(solver.inclination_error, 2)}"
                )
                logger.info(
                    f"Reference altitude error [km] = {np.round(solver.ref_altitude_specular_point_error, 2)}"
                )

            self.solvers.append(solver)

    def unpack_solvers(self):
        """
        Unpacks solver outputs into arrays for analysis and plotting.

        Extracts cost functions, weights, and error metrics (if CAMS solution is available).
        """

        speeds_error = []
        inclinations_error = []
        ref_altitude_specular_point_error = []
        target_time_of_flight = []
        target_pre_t0 = []
        weight_pre_t0 = []
        solutions = []
        number_inputs_pre_t0 = []
        number_inputs_time_of_flight = []

        for solver in self.solvers:
            target_time_of_flight.append(solver.target_time_of_flight)
            target_pre_t0.append(solver.target_pre_t0)
            weight_pre_t0.append(solver.weight_pre_t0_objective)
            solutions.append(solver.solution)
            number_inputs_pre_t0.append(solver.number_inputs_pre_t0)
            number_inputs_time_of_flight.append(solver.number_inputs_time_of_flight)

            if self.cams_solution is not None:
                speeds_error.append(solver.speed_error)
                inclinations_error.append(solver.inclination_error)
                ref_altitude_specular_point_error.append(
                    solver.ref_altitude_specular_point_error
                )

        self.target_time_of_flight = np.array(target_time_of_flight)
        self.target_pre_t0 = np.array(target_pre_t0)
        self.weight_pre_t0 = np.array(weight_pre_t0)
        self.solutions = np.array(solutions)
        self.number_inputs_pre_t0 = np.array(number_inputs_pre_t0)
        self.number_inputs_time_of_flight = np.array(number_inputs_time_of_flight)

        if self.cams_solution is not None:
            self.speeds_error = np.array(speeds_error)
            self.inclinations_error = np.array(inclinations_error)
            self.ref_altitude_specular_point_error = np.array(
                ref_altitude_specular_point_error
            )

    def get_pareto_indices(self):
        """
        Compute indices of non-dominated solutions (Pareto front).

        Returns:
            np.ndarray: Indices of non-dominated solutions in the solvers list.
        """

        return np.array(
            [
                i
                for i in range(len(self.target_time_of_flight))
                if not self.is_dominated(i)
            ]
        )

    def get_pareto_front_solvers(self):
        """
        Filters solvers to retain only those on the Pareto front.

        If CAMS data is provided, also filters the associated error metrics.
        """

        if len(self.solvers) > 1:
            indices_to_keep = self.get_pareto_indices()

            self.target_time_of_flight = self.target_time_of_flight[indices_to_keep]
            self.target_pre_t0 = self.target_pre_t0[indices_to_keep]
            self.weight_pre_t0 = self.weight_pre_t0[indices_to_keep]
            self.solutions = self.solutions[indices_to_keep]
            self.number_inputs_pre_t0 = self.number_inputs_pre_t0[indices_to_keep]
            self.number_inputs_time_of_flight = self.number_inputs_time_of_flight[
                indices_to_keep
            ]
            self.solvers = [
                d for i, d in enumerate(self.solvers) if i in indices_to_keep
            ]

            if self.cams_solution is not None:
                self.speeds_error = self.speeds_error[indices_to_keep]
                self.inclinations_error = self.inclinations_error[indices_to_keep]
                self.ref_altitude_specular_point_error = (
                    self.ref_altitude_specular_point_error[indices_to_keep]
                )

    def get_solver_knee(self):
        """
        Identifies the 'knee' (elbow) point on the Pareto front, which offers the best trade-off
        between the two objectives.

        Sets:
            self.knee_index (int): Index of the knee point.
            self.solver_knee (Solver): The solver corresponding to the knee point.
        """

        if len(self.solvers) > 1:
            # Compute first and second derivatives
            dx = np.gradient(np.log10(self.target_time_of_flight))
            dy = np.gradient(np.log10(self.target_pre_t0))
            ddx = np.gradient(dx)
            ddy = np.gradient(dy)

            # Compute curvature
            curvature = np.abs(ddx * dy - ddy * dx) / (dx**2 + dy**2) ** (3 / 2)

            # Find index of max curvature (elbow)
            self.knee_index = np.argmax(curvature)

        else:
            self.knee_index = 0

        self.solver_knee = self.solvers[self.knee_index]

    def is_dominated(self, index):
        """
        Checks if a solution is dominated by another.

        Args:
            index (int): Index of the solution to check.

        Returns:
            bool: True if the solution is dominated; False otherwise.
        """

        for j in range(len(self.target_time_of_flight)):
            if (
                j != index
                and all(
                    [
                        self.target_time_of_flight[j]
                        <= self.target_time_of_flight[index],
                        self.target_pre_t0[j] <= self.target_pre_t0[index],
                    ]
                )
                and any(
                    [
                        self.target_time_of_flight[j]
                        < self.target_time_of_flight[index],
                        self.target_pre_t0[j] < self.target_pre_t0[index],
                    ]
                )
            ):
                return True
        return False

    def output_solver_knee(self):
        """
        Outputs the best solution (knee) to a file and caches it using Dill.

        Also writes errors relative to the CAMS solution if provided.
        """

        os.makedirs(
            f"{Config.get('pybrams.directories', 'solution')}/{self.args.key}",
            exist_ok=True,
        )

        Cache.cache(
            f"trajectory_{self.args.key}.dill", dill.dumps(self.solver_knee), False
        )

        solution_path = f"{Config.get('pybrams.directories', 'solution')}/{self.args.key}/solver_solution_{self.args.key}.txt"

        text_linear_uncertainty = self.solver_knee.to_txt()

        velocity_map = self.solver_knee.solution[3:6]
        altitude_map = self.solver_knee.solution[2]

        with open(solution_path, "w", encoding="utf-8") as file:
            file.write(text_linear_uncertainty)
            file.write("\n")

            if self.cams_solution is not None:
                cams_solution = self.cams_solution
                velocity_CAMS = cams_solution[3:6]
                altitude_CAMS = cams_solution[2]

                speed_error_map = (
                    1e2
                    * (np.linalg.norm(velocity_map) - np.linalg.norm(velocity_CAMS))
                    / np.linalg.norm(velocity_CAMS)
                )
                inclination_error_map = compute_angle(velocity_map, velocity_CAMS)
                ref_altitude_specular_point_error_map = altitude_map - altitude_CAMS

                file.write("\n")

                file.write(f"Speed error MAP [%] = {np.round(speed_error_map,2)}\n")
                file.write(
                    f"Inclination error MAP [\u00b0] = {np.round(inclination_error_map,2)}\n"
                )
                file.write(
                    f"Reference altitude error MAP [km] = {np.round(ref_altitude_specular_point_error_map,2)}\n"
                )

    def plot_pareto_front(self):
        """
        Plots the Pareto front in log-log space, annotating weights and the knee point.
        Saves the figure to the solution directory.
        """

        plt.figure(figsize=(10, 5))
        plt.plot(
            np.log10(self.target_time_of_flight), np.log10(self.target_pre_t0), "-o"
        )

        for i, xy in enumerate(
            zip(np.log10(self.target_time_of_flight), np.log10(self.target_pre_t0))
        ):
            plt.annotate(str(self.weight_pre_t0[i]), xy=xy, fontsize=8)

        plt.plot(
            np.log10(self.target_time_of_flight[self.knee_index]),
            np.log10(self.target_pre_t0[self.knee_index]),
            "go",
            label="Knee",
        )
        plt.xlabel("Time of flight cost function [-]")
        plt.ylabel(r"Pre-$t_{0}$ cost function [-]")
        plt.grid()
        plt.legend()
        plt.title("Pareto front - log scale")
        plt.savefig(
            f"{Config.get('pybrams.directories', 'solution')}/{self.args.key}/pareto_front_{self.args.key}.png",
            dpi=300,
            bbox_inches="tight",
        )  # Higher quality (300 DPI)

        if self.args.plot:
            plt.show()

        plt.close()

    def plot_total_cost_fun(self):
        """
        Plots the total cost function as a function of the pre-t0 weight.
        Highlights the weight that minimizes the total cost.
        """

        target_tot = [
            (1 - self.weight_pre_t0[i]) * self.target_time_of_flight[i]
            + self.weight_pre_t0[i] * self.target_pre_t0[i]
            for i in range(len(self.target_time_of_flight))
        ]
        argmin_target_tot = np.argmin(target_tot)

        plt.figure()
        plt.plot(self.weight_pre_t0, target_tot, "o-")
        plt.plot(
            self.weight_pre_t0[argmin_target_tot],
            target_tot[argmin_target_tot],
            "ro",
            label="Minimum total cost function",
        )
        plt.xlabel(r"Weight pre-$t_{0}$ objective")
        plt.ylabel("Total cost function [-]")
        plt.title(r"Total cost function as a function of pre-$t_{0}$ weight")
        plt.legend()
        plt.grid()
        plt.savefig(
            f"{Config.get('pybrams.directories', 'solution')}/{self.args.key}/total_cost_fun_{self.args.key}.png",
            dpi=300,
            bbox_inches="tight",
        )  # Higher quality (300 DPI)

        if self.args.plot:
            plt.show()

        plt.close()

    def plot_errors(self):
        """
        Plots errors in speed, inclination, and reference altitude as a function of the pre-t0 weight.

        Only executed if a CAMS solution is provided.
        """

        if self.cams_solution is not None:
            _, axes = plt.subplots(3, 1, figsize=(7, 10))

            axes[0].plot(self.weight_pre_t0, self.speeds_error, "o-")
            axes[0].plot(
                self.weight_pre_t0[self.knee_index],
                self.speeds_error[self.knee_index],
                "go",
                label="Knee",
            )
            axes[0].grid()
            axes[0].set_xlabel(r"Weight pre-$t_{0}$ objective")
            axes[0].set_ylabel("Speed error [%]")
            axes[0].set_title(
                f"Speed error - Min = {np.round(np.min(self.speeds_error), 2)} % - Max = {np.round(np.max(self.speeds_error), 2)} % - Knee = {np.round(self.speeds_error[self.knee_index],2)} %"
            )

            axes[1].plot(self.weight_pre_t0, self.inclinations_error, "o-")
            axes[1].plot(
                self.weight_pre_t0[self.knee_index],
                self.inclinations_error[self.knee_index],
                "go",
                label="Knee",
            )
            axes[1].grid()
            axes[1].set_xlabel(r"Weight pre-$t_{0}$ objective")
            axes[1].set_ylabel("Inclination error [\u00b0]")
            axes[1].set_title(
                f"Inclination error - Min = {np.round(np.min(self.inclinations_error), 2)}\u00b0 - Max = {np.round(np.max(self.inclinations_error), 2)}\u00b0 - Knee = {np.round(self.inclinations_error[self.knee_index],2)}\u00b0"
            )

            axes[2].plot(
                self.weight_pre_t0, self.ref_altitude_specular_point_error, "o-"
            )
            axes[2].plot(
                self.weight_pre_t0[self.knee_index],
                self.ref_altitude_specular_point_error[self.knee_index],
                "go",
                label="Knee",
            )
            axes[2].grid()
            axes[2].set_xlabel(r"Weight pre-$t_{0}$ objective")
            axes[2].set_ylabel("Altitude error [km]")
            axes[2].set_title(
                f"Altitude error - Min = {np.round(np.min(self.ref_altitude_specular_point_error), 2)} km - Max = {np.round(np.max(self.ref_altitude_specular_point_error), 2)} km - Knee = {np.round(self.ref_altitude_specular_point_error[self.knee_index],2)} km"
            )

            plt.legend()
            plt.tight_layout()
            plt.savefig(
                f"{Config.get('pybrams.directories', 'solution')}/{self.args.key}/errors_{self.args.key}.png",
                dpi=300,
                bbox_inches="tight",
            )  # Higher quality (300 DPI)

            if self.args.plot:
                plt.show()

            plt.close()

    def run_MCMC(self):
        """
        Runs MCMC uncertainty quantification on the knee solution.

        Uses a separate MCMCAnalyzer class to perform the analysis.
        """

        self.mcmc_analyzer = MCMCAnalyzer(self.solver_knee, self.args)
        self.mcmc_analyzer.run()
