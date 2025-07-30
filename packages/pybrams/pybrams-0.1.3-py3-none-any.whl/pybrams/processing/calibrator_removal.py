import numpy as np
from scipy.optimize import curve_fit
from .constants import MAD_FACTOR, MAD_SCALE
from .interference_removal import InterferenceRemoval
from .signal import Signal
from pybrams.utils.config import Config


class CalibratorRemoval(InterferenceRemoval):
    """
    Class for removing periodic calibrator interference from a signal.

    This class identifies, fits, and subtracts a sinusoidal calibrator signal
    present in the input using localized FFT and robust curve fitting.

    Inherits from:
        InterferenceRemoval: Provides interval-based FFT structure and fitting utilities.
    """

    def __init__(self, signal: Signal):
        """
        Initialize CalibratorRemoval with signal data and fitting parameters.

        Args:
            signal (Signal): The input signal object containing the raw and cleaned series.
        """

        super().__init__(
            signal,
            Config.get(__name__, "interval_duration"),
            Config.get(__name__, "interval_overlaps"),
        )

    def remove_interference(self):
        """
        High-level method to remove calibrator interference from the signal.

        Steps:
            1. Fit the calibrator sinusoid using STFT peaks.
            2. Reconstruct the sinusoid from fitted parameters.
            3. Subtract the reconstructed calibrator from the signal.
        """

        self.fit_calibrator()
        self.correct_calibrator()
        self.signal.cleaned_series.data -= self.data_calibrator

    def fit_calibrator(self):
        """
        Identify and fit the amplitude, frequency, and phase of the calibrator signal
        in each time-frequency interval using a Hanning-windowed curve fit.
        """

        self.calibrator_min_frequency = self.signal.calibrator_frequency - Config.get(
            __name__, "find_half_range_frequency"
        )  # Minimum frequency for the calibrator reconstruction
        self.calibrator_max_frequency = self.signal.calibrator_frequency + Config.get(
            __name__, "find_half_range_frequency"
        )  # Maximum frequency for the calibrator reconstruction

        self.calibrator_parameters = np.zeros((self.fit_intervals, 4))

        for j in range(self.fit_intervals):
            # Fft computation
            real_fft_interval = self.Zxx[:, j]
            magn_fft_interval = abs(real_fft_interval)
            magn_fft_interval[1:-1] = 2 * abs(magn_fft_interval[1:-1])

            min_calibrator_frequency_index = np.argmin(
                np.abs(self.stft_frequency - self.calibrator_min_frequency)
            )
            max_calibrator_frequency_index = np.argmin(
                np.abs(self.stft_frequency - self.calibrator_max_frequency)
            )

            # Look for the Fft peak inside interval around calibrator frequency
            local_calibrator_frequency_index = np.argmax(
                magn_fft_interval[
                    min_calibrator_frequency_index : max_calibrator_frequency_index + 1
                ]
            )
            calibrator_frequency_index = (
                local_calibrator_frequency_index + min_calibrator_frequency_index
            )

            # Set-up of calibrator fit
            half_number_of_points_calibrator_fit = round(
                Config.get(__name__, "fit_half_range_frequency")
                * self.samples_per_interval
                / self.signal.samplerate
            )
            frequency_indices_to_fit = np.arange(
                calibrator_frequency_index - half_number_of_points_calibrator_fit,
                calibrator_frequency_index + half_number_of_points_calibrator_fit + 1,
            )
            signal_to_fit = magn_fft_interval[
                calibrator_frequency_index
                - half_number_of_points_calibrator_fit : calibrator_frequency_index
                + half_number_of_points_calibrator_fit
                + 1
            ]

            # Initial guess determination
            if (
                magn_fft_interval[calibrator_frequency_index - 1]
                > magn_fft_interval[calibrator_frequency_index + 1]
            ):
                initial_guess_fit = np.array(
                    [
                        magn_fft_interval[calibrator_frequency_index],
                        calibrator_frequency_index - 0.01,
                    ]
                )
            else:
                initial_guess_fit = np.array(
                    [
                        magn_fft_interval[calibrator_frequency_index],
                        calibrator_frequency_index + 0.01,
                    ]
                )

            # Fit
            calibrator_fit_parameters, _ = curve_fit(
                self.hanning_window_function,
                frequency_indices_to_fit,
                signal_to_fit,
                initial_guess_fit,
                method="trf",
                maxfev=Config.get(__name__, "fit_max_evaluations"),
            )
            calibrator_fit_residuals = signal_to_fit - self.hanning_window_function(
                frequency_indices_to_fit, *calibrator_fit_parameters
            )
            calibrator_fit_residuals_norm = np.sum(calibrator_fit_residuals**2)

            # Frequency and amplitude retrieval
            calibrator_amplitude = calibrator_fit_parameters[0]
            calibrator_frequency = (
                calibrator_fit_parameters[1]
                * self.signal.samplerate
                / self.samples_per_interval
            )  # Retrieve the frequency from the best freq index

            # Phase computation
            calibrator_discrete_phase = np.angle(
                real_fft_interval[calibrator_frequency_index]
            )
            calibrator_continuous_phase = (
                calibrator_discrete_phase
                - (calibrator_fit_parameters[1] - calibrator_frequency_index)
                * np.pi
                * (self.samples_per_interval - 1)
                / self.samples_per_interval
            )  # Correction to have phase at continuous max

            # Set output values
            self.calibrator_parameters[j, 0] = calibrator_frequency
            self.calibrator_parameters[j, 1] = calibrator_amplitude
            self.calibrator_parameters[j, 2] = calibrator_continuous_phase
            self.calibrator_parameters[j, 3] = calibrator_fit_residuals_norm

    def correct_calibrator(self):
        """
        Post-process and interpolate fitted calibrator parameters to produce a smooth
        and reliable reconstructed signal.

        Steps:
            - Remove outlier fits using MAD filtering
            - Interpolate frequency, amplitude, and phase across valid intervals
            - Reconstruct a continuous cosine calibrator signal from interpolated parameters
            - Save result in `self.data_calibrator`
        """

        calibrator_frequency = self.calibrator_parameters[:, 0]

        calibrator_amplitude = self.calibrator_parameters[:, 1]

        calibrator_continuous_phase = np.unwrap(self.calibrator_parameters[:, 2])
        calibrator_fit_residual = self.calibrator_parameters[:, 3]
        calibrator_gradient_frequency = np.gradient((calibrator_frequency))

        median_frequency = np.median(calibrator_frequency)
        median_amplitude = np.median(calibrator_amplitude)
        median_residual = np.median(calibrator_fit_residual)
        median_gradient_frequency = np.median(calibrator_gradient_frequency)

        mad_frequency = np.median(np.abs(calibrator_frequency - median_frequency))
        mad_amplitude = np.median(np.abs(calibrator_amplitude - median_amplitude))
        mad_residual = np.median(np.abs(calibrator_fit_residual - median_residual))
        mad_gradient_frequency = np.median(
            np.abs(calibrator_gradient_frequency - median_gradient_frequency)
        )

        mad_residual_limit = median_residual + MAD_FACTOR * MAD_SCALE * mad_residual
        mad_gradient_frequency_limit = (
            median_gradient_frequency - MAD_FACTOR * MAD_SCALE * mad_gradient_frequency
        )

        good_frequency_indices = np.where(
            np.abs(calibrator_frequency - median_frequency)
            < MAD_FACTOR * MAD_SCALE * mad_frequency
        )[0]
        good_amplitude_indices = np.where(
            np.abs(calibrator_amplitude - median_amplitude)
            < MAD_FACTOR * MAD_SCALE * mad_amplitude
        )[0]
        good_residual_indices = np.where(calibrator_fit_residual < mad_residual_limit)[
            0
        ]
        good_gradient_frequency_indices = np.where(
            calibrator_gradient_frequency > mad_gradient_frequency_limit
        )[0]

        good_fit_indices = np.intersect1d(
            good_frequency_indices,
            np.intersect1d(
                good_amplitude_indices,
                np.intersect1d(good_residual_indices, good_gradient_frequency_indices),
            ),
        )

        good_fit_frequency = calibrator_frequency[good_fit_indices]
        good_fit_amplitude = calibrator_amplitude[good_fit_indices]
        good_fit_calibrator_continuous_phase = calibrator_continuous_phase[
            good_fit_indices
        ]

        good_fit_start_fit_time = self.start_fit_time[good_fit_indices]

        bad_fit_indices = np.setdiff1d(np.arange(self.fit_intervals), good_fit_indices)

        corrected_calibrator_frequency = np.interp(
            self.start_fit_time, good_fit_start_fit_time, good_fit_frequency
        )
        corrected_calibrator_amplitude = np.interp(
            self.start_fit_time, good_fit_start_fit_time, good_fit_amplitude
        )

        corrected_calibrator_continuous_phase = np.zeros(self.fit_intervals)
        corrected_calibrator_continuous_phase[
            good_fit_indices
        ] = good_fit_calibrator_continuous_phase

        # Phase interpolation -
        # We move all the phases with reference to the badly fitted interval and then interpolate linearly
        for bad_fit_index in bad_fit_indices:
            greater_indices = good_fit_indices[good_fit_indices > bad_fit_index]
            smaller_indices = good_fit_indices[good_fit_indices < bad_fit_index]

            if greater_indices.any():
                closest_greater_index = greater_indices[
                    np.argmin(np.abs(greater_indices - bad_fit_index))
                ]
                closest_greater_phase = calibrator_continuous_phase[
                    closest_greater_index
                ]

                closest_greater_indices = np.arange(
                    bad_fit_index, closest_greater_index + 1
                )
                closest_greater_frequencies = corrected_calibrator_frequency[
                    closest_greater_indices
                ]
                closest_greater_phase_shifted = closest_greater_phase

                for i in range(len(closest_greater_frequencies) - 1):
                    closest_greater_phase_shifted -= (
                        2
                        * np.pi
                        * (
                            self.start_fit_time[closest_greater_indices[i + 1]]
                            - self.start_fit_time[closest_greater_indices[i]]
                        )
                        * closest_greater_frequencies[i]
                    )  # corrected_calibrator_frequency[bad_fit_index] #closest_greater_frequencies[i]

            if smaller_indices.any():
                closest_smaller_index = smaller_indices[
                    np.argmin(np.abs(smaller_indices - bad_fit_index))
                ]
                closest_smaller_phase = calibrator_continuous_phase[
                    closest_smaller_index
                ]

                closest_smaller_indices = np.arange(
                    closest_smaller_index, bad_fit_index + 1
                )
                closest_smaller_frequencies = corrected_calibrator_frequency[
                    closest_smaller_indices
                ]
                closest_smaller_phase_shifted = closest_smaller_phase

                for i in range(len(closest_smaller_frequencies) - 1):
                    closest_smaller_phase_shifted += (
                        2
                        * np.pi
                        * (
                            self.start_fit_time[closest_smaller_indices[i + 1]]
                            - self.start_fit_time[closest_smaller_indices[i]]
                        )
                        * closest_smaller_frequencies[i]
                    )  # corrected_calibrator_frequency[bad_fit_index] #closest_smaller_frequencies[i]

            if not smaller_indices.any():
                corrected_calibrator_continuous_phase[
                    bad_fit_index
                ] = closest_greater_phase_shifted

            elif not greater_indices.any():
                corrected_calibrator_continuous_phase[
                    bad_fit_index
                ] = closest_smaller_phase_shifted

            else:
                closest_indices = [closest_smaller_index, closest_greater_index]
                closest_phases = np.unwrap(
                    [closest_smaller_phase_shifted, closest_greater_phase_shifted]
                )  # Avoid shift greater than pi
                corrected_calibrator_continuous_phase[bad_fit_index] = np.interp(
                    bad_fit_index, closest_indices, closest_phases
                )

        # Corrected calibrator signal after interpolation
        corrected_calibrator = np.zeros(self.padded_extended_length)
        for j in range(self.fit_intervals):
            corrected_calibrator[
                self.start_fit_indices[j] : self.end_fit_indices[j] + 1
            ] = corrected_calibrator_amplitude[j] * np.cos(
                2
                * np.pi
                * corrected_calibrator_frequency[j]
                * (
                    self.time_vector[
                        self.start_fit_indices[j] : self.end_fit_indices[j] + 1
                    ]
                    - self.time_vector[self.start_fit_indices[j]]
                )
                + corrected_calibrator_continuous_phase[j]
            )

        self.data_calibrator = corrected_calibrator[
            self.samples_per_interval
            // 2 : (-self.pad_width - self.samples_per_interval // 2)
        ]
