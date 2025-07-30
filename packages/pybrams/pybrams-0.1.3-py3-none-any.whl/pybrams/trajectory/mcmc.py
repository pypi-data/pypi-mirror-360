import numpy as np
import os
import matplotlib.pyplot as plt

from pybrams.utils.cache import Cache
from pybrams.utils import Config
from pybrams.trajectory.solver import Solver
from pybrams.trajectory.scam import Scam
from pybrams.trajectory.scam import autocovariance

from pybrams.utils.geometry import compute_angle
from pybrams.utils.geometry import compute_azimuth_elevation
import logging

logger = logging.getLogger(__name__)


class MCMCAnalyzer:
    """
    Class for analyzing MCMC (Markov Chain Monte Carlo) results applied to meteoroid trajectory fitting.
    It uses the SCAM algorithm to generate posterior distributions from a given solution.

    Parameters
    ----------
    solver_knee : Solver
        Solver object containing the initial solution and related configuration.
    args : Namespace
        Namespace object containing runtime arguments like 'key' and plotting options.
    """

    def __init__(self, solver_knee, args):
        """
        Initialize the MCMCAnalyzer with solver and runtime arguments.
        """

        self.solver_knee = solver_knee
        self.n_samples_mcmc = Config.get(__name__, "n_samples_mcmc")
        self.max_lag_autocovariance = Config.get(__name__, "max_lag_autocovariance")
        self.args = args

    def run(self):
        """
        Run the full MCMC analysis pipeline:
        1. Update solver uncertainties based on normalized residuals.
        2. Launch SCAM MCMC.
        3. Save MCMC results and write diagnostics.
        4. Plot posterior distributions in both parameter and output space.
        """

        self.update_knee_solver()
        self.run_scam()
        self.output_scam()
        self.plot_xyz_posterior()
        self.plot_thetaphi_posterior()
        self.plot_autocovariance()

    def update_knee_solver(self):
        """
        Update the uncertainties (sigmas) used in the solver based on the normalized
        contributions of the pre-t0 and time-of-flight objective terms.
        """

        alpha_pre_t0 = np.sqrt(
            1
            / self.solver_knee.number_inputs_pre_t0
            * self.solver_knee.weight_pre_t0_objective
            * self.solver_knee.pre_t0_fun(self.solver_knee.solution)
        )
        alpha_time_of_flight = np.sqrt(
            1
            / self.solver_knee.number_inputs_time_of_flight
            * (1 - self.solver_knee.weight_pre_t0_objective)
            * self.solver_knee.time_of_flight_fun(self.solver_knee.solution)
        )

        logger.info(f"Alpha pre t0 = {np.round(alpha_pre_t0, 3)}")
        logger.info(f"Alpha time of flight = {np.round(alpha_time_of_flight, 3)}")

        if alpha_time_of_flight > 1:
            self.solver_knee.sigma_times_of_flight *= alpha_time_of_flight

        if alpha_pre_t0 > 1:
            self.solver_knee.sigma_pre_t0s *= alpha_pre_t0

        self.solver_knee.update_cov_hessian(self.solver_knee.solution)

        logger.info(
            f"95% linear CI = {np.round(1.96 * np.sqrt(np.diag(self.solver_knee.cov)), 2)}"
        )

    def run_scam(self):
        """
        Run the Single Component Adaptive Metropolis (SCAM) algorithm to sample from
        the posterior distribution of the trajectory parameters.
        """

        scam_class = Scam(
            0.1 * np.ones(len(self.solver_knee.solution)),
            proposal="custom",
            proposal_cov=self.solver_knee.cov,
        )
        self.chain = scam_class.run(
            self.solver_knee.posterior_fun,
            self.solver_knee.solution,
            self.n_samples_mcmc,
            self.solver_knee.is_valid_fun,
        )

    def output_scam(self):
        """
        Save the MCMC chain, compute statistical summaries (median, ±1σ), and write results to file.
        Also compares to CAMS solution if available and saves all outputs in NumPy and text formats.
        """

        os.makedirs(
            f"{Config.get('pybrams.directories', 'solution')}/{self.args.key}",
            exist_ok=True,
        )

        np.save(
            f"{Config.get('pybrams.directories', 'solution')}/{self.args.key}/markov_chain_{self.args.key}.npy",
            self.chain,
        )

        median_chain = np.median(self.chain, axis=1)

        lower_bound_param = np.percentile(self.chain, 16, axis=1).T
        upper_bound_param = np.percentile(self.chain, 84, axis=1).T

        minus_sigma_param = median_chain - lower_bound_param
        plus_sigma_param = upper_bound_param - median_chain

        thetas = np.zeros(self.chain.shape[1])
        epsilons = np.zeros(self.chain.shape[1])
        v_norm = np.zeros(self.chain.shape[1])

        for i in range(self.chain.shape[1]):
            thetas[i], epsilons[i] = compute_azimuth_elevation(self.chain[3:6, i])
            v_norm[i] = np.linalg.norm(self.chain[3:6, i])

        self.outputs = np.vstack((thetas, epsilons, self.chain[2, :], v_norm))

        theta_solver, epsilon_solver = compute_azimuth_elevation(
            self.solver_knee.solution[3:6]
        )
        v_norm_solver = np.linalg.norm(self.solver_knee.solution[3:6])
        z_solver = self.solver_knee.solution[2]

        self.output_solver = np.array(
            [theta_solver, epsilon_solver, z_solver, v_norm_solver]
        )

        lower_bound_outputs = np.percentile(self.outputs, 16, axis=1).T
        upper_bound_outputs = np.percentile(self.outputs, 84, axis=1).T
        median_outputs = np.median(self.outputs, axis=1)

        minus_sigma_outputs = median_outputs - lower_bound_outputs
        plus_sigma_outputs = upper_bound_outputs - median_outputs

        velocity_chain = median_chain[3:6]
        altitude_chain = median_chain[2]

        if hasattr(self.solver_knee, "cams_solution"):
            cams_solution = self.solver_knee.cams_solution
            velocity_CAMS = cams_solution[3:6]
            altitude_CAMS = cams_solution[2]

            theta_CAMS, epsilon_CAMS = compute_azimuth_elevation(velocity_CAMS)
            v_norm_CAMS = np.linalg.norm(velocity_CAMS)
            z_CAMS = cams_solution[2]

            self.cams_output = np.array([theta_CAMS, epsilon_CAMS, z_CAMS, v_norm_CAMS])

            speed_error_median = (
                1e2
                * (np.linalg.norm(velocity_chain) - np.linalg.norm(velocity_CAMS))
                / np.linalg.norm(velocity_CAMS)
            )
            inclination_error_median = compute_angle(velocity_chain, velocity_CAMS)
            ref_altitude_specular_point_error_median = altitude_chain - altitude_CAMS

        with open(
            f"{Config.get('pybrams.directories', 'solution')}/{self.args.key}/mcmc_solution_{self.args.key}.txt",
            "w",
            encoding="utf-8",
        ) as file:
            # Always write the parameter values without CAMS
            for i in range(len(self.solver_knee.variable_names)):
                file.write(
                    f"Parameter {self.solver_knee.variable_names[i]} = {np.round(median_chain[i], 2)} "
                    f"-\u03c3 = {np.round(minus_sigma_param[i], 2)} "
                    f"+\u03c3 = {np.round(plus_sigma_param[i], 2)}"
                )

                # If CAMS solution exists, write the CAMS values
                if hasattr(self.solver_knee, "cams_solution"):
                    file.write(f" - CAMS = {float(np.round(cams_solution[i], 2))}")

                file.write("\n")

            file.write("\n")
            # Always write the output parameters without CAMS
            for i in range(len(self.solver_knee.output_names)):
                file.write(
                    f"Parameter {self.solver_knee.output_names[i]} = {np.round(median_outputs[i], 2)} "
                    f"-\u03c3 = {np.round(minus_sigma_outputs[i], 2)} "
                    f"+\u03c3 = {np.round(plus_sigma_outputs[i], 2)}"
                )

                # If CAMS solution exists, write the CAMS values for outputs
                if hasattr(self.solver_knee, "cams_solution"):
                    file.write(f" - CAMS = {float(np.round(self.cams_output[i], 2))}")

                file.write("\n")

            if hasattr(self.solver_knee, "cams_solution"):
                file.write("\n")
                file.write(
                    f"Speed error median [%] = {np.round(speed_error_median,2)}\n"
                )
                file.write(
                    f"Inclination error median [\u00b0] = {np.round(inclination_error_median,2)}\n"
                )
                file.write(
                    f"Reference altitude error median [km] = {np.round(ref_altitude_specular_point_error_median,2)}\n"
                )

    def plot_xyz_posterior(self):
        """
        Plot scatter and density plots of the posterior distribution in the original
        parameter space (XYZ, velocity components, etc.).
        Includes median, confidence intervals, solver, and CAMS (if available).
        """

        n_params = self.chain.shape[0]

        fig, axes = plt.subplots(
            n_params, n_params, figsize=(10, 10), subplot_kw=dict(box_aspect=1)
        )
        fig.suptitle("MCMC Posterior Samples - Scatter XYZ", fontsize=16)

        median_chain = np.median(self.chain, axis=1)
        lower_percentile = np.percentile(self.chain, 0.135, axis=1)
        higher_percentile = np.percentile(self.chain, 99.865, axis=1)

        for i in range(n_params):
            for j in range(n_params):
                ax = axes[i, j]

                if i == j:
                    ax.hist(self.chain[i, :], bins=30, color="blue", alpha=0.7)
                    ax.axvline(median_chain[i], color="red")  # Median
                    ax.axvline(
                        self.solver_knee.solution[i], color="cyan"
                    )  # True solution
                    ax.axvline(lower_percentile[i], color="orange", linestyle="--")
                    ax.axvline(higher_percentile[i], color="orange", linestyle="--")

                    if hasattr(self.solver_knee, "cams_solution"):
                        ax.axvline(
                            self.solver_knee.cams_solution[i], color="violet"
                        )  # CAMS solution

                    ax.set_yticks([]) and ax.set_yticklabels([])

                # Hide unused subplots
                else:
                    top_left = (lower_percentile[j], higher_percentile[i])
                    top_right = (higher_percentile[j], higher_percentile[i])
                    bottom_left = (lower_percentile[j], lower_percentile[i])
                    bottom_right = (higher_percentile[j], lower_percentile[i])

                    rectangle = [
                        top_left,
                        top_right,
                        bottom_right,
                        bottom_left,
                        top_left,
                    ]

                    ax.plot(*zip(*rectangle), linestyle="--", color="orange")

                    ax.scatter(
                        self.chain[j, :], self.chain[i, :], s=1, color="blue", alpha=0.5
                    )
                    ax.scatter(
                        median_chain[j], median_chain[i], color="red", s=50, marker="*"
                    )

                    ax.scatter(
                        self.solver_knee.solution[j],
                        self.solver_knee.solution[i],
                        color="cyan",
                        s=50,
                        marker="+",
                    )  # True solution

                    if hasattr(self.solver_knee, "cams_solution"):
                        ax.scatter(
                            self.solver_knee.cams_solution[j],
                            self.solver_knee.cams_solution[i],
                            color="violet",
                            s=50,
                            marker="x",
                        )

                # Set labels
                if i == n_params - 1:  # Bottom row
                    ax.set_xlabel(self.solver_knee.variable_names[j])
                if j == 0:  # Leftmost column
                    ax.set_ylabel(self.solver_knee.variable_names[i])

        # Adjust layout for clarity
        plt.subplots_adjust(wspace=0.5, hspace=0.5)

        plt.savefig(
            f"{Config.get('pybrams.directories', 'solution')}/{self.args.key}/scatter_xyz_{self.args.key}.png",
            dpi=300,
        )  # Higher quality (300 DPI)

        if self.args.plot:
            plt.show()

        plt.close()

        fig, axes = plt.subplots(
            n_params, n_params, figsize=(10, 10), subplot_kw=dict(box_aspect=1)
        )
        fig.suptitle("MCMC Posterior Samples - Density XYZ", fontsize=16)

        # Loop through each subplot
        for i in range(n_params):
            for j in range(n_params):
                ax = axes[i, j]

                # Diagonal: 1D histogram
                if i == j:
                    ax.hist(self.chain[i, :], bins=30, color="blue", alpha=0.7)
                    ax.axvline(median_chain[i], color="red")  # Mean

                    ax.axvline(
                        self.solver_knee.solution[i], color="cyan"
                    )  # True solution
                    ax.axvline(lower_percentile[i], color="orange", linestyle="--")
                    ax.axvline(higher_percentile[i], color="orange", linestyle="--")

                    if hasattr(self.solver_knee, "cams_solution"):
                        ax.axvline(
                            self.solver_knee.cams_solution[i], color="violet"
                        )  # CAMS solution

                    ax.set_yticks([]) and ax.set_yticklabels([])

                # Hide unused subplots
                else:
                    top_left = (lower_percentile[j], higher_percentile[i])
                    top_right = (higher_percentile[j], higher_percentile[i])
                    bottom_left = (lower_percentile[j], lower_percentile[i])
                    bottom_right = (higher_percentile[j], lower_percentile[i])

                    rectangle = [
                        top_left,
                        top_right,
                        bottom_right,
                        bottom_left,
                        top_left,
                    ]

                    ax.plot(*zip(*rectangle), linestyle="--", color="orange")

                    ax.hist2d(self.chain[j, :], self.chain[i, :], bins=30)
                    ax.scatter(
                        median_chain[j], median_chain[i], color="red", s=50, marker="*"
                    )
                    ax.scatter(
                        self.solver_knee.solution[j],
                        self.solver_knee.solution[i],
                        color="cyan",
                        s=50,
                        marker="+",
                    )  # True solution

                    if hasattr(self.solver_knee, "cams_solution"):
                        ax.scatter(
                            self.solver_knee.cams_solution[j],
                            self.solver_knee.cams_solution[i],
                            color="violet",
                            s=50,
                            marker="x",
                        )

                # Set labels
                if i == n_params - 1:  # Bottom row
                    ax.set_xlabel(self.solver_knee.variable_names[j])
                if j == 0:  # Leftmost column
                    ax.set_ylabel(self.solver_knee.variable_names[i])

        # Adjust layout for clarity
        plt.subplots_adjust(wspace=0.5, hspace=0.5)

        plt.savefig(
            f"{Config.get('pybrams.directories', 'solution')}/{self.args.key}/density_xyz_{self.args.key}.png",
            dpi=300,
            bbox_inches="tight",
        )  # Higher quality (300 DPI)

        if self.args.plot:
            plt.show()

        plt.close()

    def plot_thetaphi_posterior(self):
        """
        Plot density plots of the posterior distribution in the derived output space
        (azimuth, elevation, altitude, velocity norm).
        """

        n_outputs = len(self.solver_knee.output_names)

        fig, axes = plt.subplots(
            n_outputs, n_outputs, figsize=(10, 10), subplot_kw=dict(box_aspect=1)
        )
        fig.suptitle("MCMC Posterior Samples - Density theta phi", fontsize=16)

        median_outputs = np.median(self.outputs, axis=1)
        lower_percentile = np.percentile(self.outputs, 0.135, axis=1)
        higher_percentile = np.percentile(self.outputs, 99.865, axis=1)

        for i in range(n_outputs):
            for j in range(n_outputs):
                ax = axes[i, j]

                # Diagonal: 1D histogram
                if i == j:
                    ax.hist(self.outputs[i, :], bins=30, color="blue", alpha=0.7)
                    ax.axvline(median_outputs[i], color="red")  # Mean
                    ax.axvline(self.output_solver[i], color="cyan")  # True solution
                    ax.axvline(lower_percentile[i], color="orange", linestyle="--")
                    ax.axvline(higher_percentile[i], color="orange", linestyle="--")

                    if hasattr(self.solver_knee, "cams_solution"):
                        ax.axvline(self.cams_output[i], color="violet")  # CAMS solution

                    ax.set_yticks([]) and ax.set_yticklabels([])

                # Hide unused subplots
                else:
                    top_left = (lower_percentile[j], higher_percentile[i])
                    top_right = (higher_percentile[j], higher_percentile[i])
                    bottom_left = (lower_percentile[j], lower_percentile[i])
                    bottom_right = (higher_percentile[j], lower_percentile[i])

                    rectangle = [
                        top_left,
                        top_right,
                        bottom_right,
                        bottom_left,
                        top_left,
                    ]

                    ax.plot(*zip(*rectangle), linestyle="--", color="orange")

                    ax.hist2d(self.outputs[j, :], self.outputs[i, :], bins=30)
                    ax.scatter(
                        median_outputs[j],
                        median_outputs[i],
                        color="red",
                        s=50,
                        marker="*",
                    )
                    ax.scatter(
                        self.output_solver[j],
                        self.output_solver[i],
                        color="cyan",
                        s=50,
                        marker="+",
                    )  # True solution

                    if hasattr(self.solver_knee, "cams_solution"):
                        ax.scatter(
                            self.cams_output[j],
                            self.cams_output[i],
                            color="violet",
                            s=50,
                            marker="x",
                        )

                # Set labels
                if i == n_outputs - 1:  # Bottom row
                    ax.set_xlabel(self.solver_knee.output_names[j])
                if j == 0:  # Leftmost column
                    ax.set_ylabel(self.solver_knee.output_names[i])

        # Adjust layout for clarity
        plt.subplots_adjust(wspace=0.5, hspace=0.5)

        plt.savefig(
            f"{Config.get('pybrams.directories', 'solution')}/{self.args.key}/density_thetaphi_{self.args.key}.png",
            dpi=300,
            bbox_inches="tight",
        )  # Higher quality (300 DPI)

        if self.args.plot:
            plt.show()

        plt.close()  # Close the plot to free memory

    def plot_autocovariance(self):
        """
        Plot the autocovariance of the MCMC chain for each parameter to assess chain mixing.
        """

        fig, axes = plt.subplots(self.chain.shape[0], 1, figsize=(10, 15))

        Kv, MC_gamma = autocovariance(
            self.chain, min_k=0, max_k=self.max_lag_autocovariance, number_k=1000
        )
        flat_ax = axes.flatten()
        for vari in range(self.chain.shape[0]):
            ax = flat_ax[vari]
            ax.grid()
            ax.plot(Kv, MC_gamma[vari, :] / MC_gamma[vari, 0])
            ax.set(
                xlabel="Lag",
                ylabel="${\\gamma}_k/{\\gamma}_0$",
                title=f"Autocorrelation for {self.solver_knee.variable_names[vari]}",
            )
        plt.tight_layout()
        plt.savefig(
            f"{Config.get('pybrams.directories', 'solution')}/{self.args.key}/autocorr_{self.args.key}.png",
            dpi=300,
            bbox_inches="tight",
        )

        if self.args.plot:
            plt.show()

        plt.close()
