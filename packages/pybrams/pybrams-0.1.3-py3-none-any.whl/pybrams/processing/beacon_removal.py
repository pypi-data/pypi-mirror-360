import numpy as np
from scipy.optimize import curve_fit
from .constants import MAD_FACTOR, MAD_SCALE
from .interference_removal import InterferenceRemoval
from .signal import Signal
from pybrams.utils.config import Config


class BeaconRemoval(InterferenceRemoval):
    """
    Class for removing narrowband beacon interference from a signal using
    spectral fitting and phase correction techniques.

    Inherits from
    ----------
    InterferenceRemoval : Base class for interference mitigation in signals.

    Parameters
    ----------
    signal : Signal
        The input signal object containing the raw time series data and metadata.
    """

    def __init__(self, signal: Signal):
        """
        Initialize the BeaconRemoval class.

        Parameters
        ----------
        signal : Signal
            The signal object containing the time series data to be cleaned.
        """

        super().__init__(
            signal,
            Config.get(__name__, "interval_duration"),
            Config.get(__name__, "interval_overlaps"),
        )

    def remove_interference(self):
        """
        Perform the full beacon interference removal process.

        This includes:
        - Fitting the beacon parameters (frequency, amplitude, phase)
        - Correcting unreliable fit values
        - Subtracting the reconstructed beacon signal from the original
        """

        self.fit_beacon()
        self.correct_beacon()
        self.signal.cleaned_series.data -= self.data_beacon

    def fit_beacon(self):
        """
        Fit the beacon signal's amplitude, frequency, and phase over intervals.

        This method performs the following steps for each interval:
        - Identifies the dominant frequency component near the expected beacon frequency
        - Fits a Hanning-shaped peak to refine the frequency estimate
        - Computes the amplitude and continuous phase of the beacon signal
        - Stores the results and residuals for later correction
        """

        self.beacon_min_frequency = self.signal.beacon_frequency - Config.get(
            __name__, "find_half_range_frequency"
        )  # Minimum frequency for the beacon reconstruction
        self.beacon_max_frequency = self.signal.beacon_frequency + Config.get(
            __name__, "find_half_range_frequency"
        )  # Maximum frequency for the beacon reconstruction

        self.beacon_parameters = np.zeros((self.fit_intervals, 4))

        for j in range(self.fit_intervals):
            # Fft computation
            real_fft_interval = self.Zxx[:, j]
            magn_fft_interval = abs(real_fft_interval)
            magn_fft_interval[1:-1] = 2 * abs(magn_fft_interval[1:-1])

            min_beacon_frequency_index = np.argmin(
                np.abs(self.stft_frequency - self.beacon_min_frequency)
            )
            max_beacon_frequency_index = np.argmin(
                np.abs(self.stft_frequency - self.beacon_max_frequency)
            )

            # Look for the Fft peak inside interval around beacon frequency
            local_beacon_frequency_index = np.argmax(
                magn_fft_interval[
                    min_beacon_frequency_index : max_beacon_frequency_index + 1
                ]
            )
            beacon_frequency_index = (
                local_beacon_frequency_index + min_beacon_frequency_index
            )

            # Set-up of beacon fit
            half_number_of_points_beacon_fit = round(
                Config.get(__name__, "fit_half_range_frequency")
                * self.samples_per_interval
                / self.signal.samplerate
            )
            frequency_indices_to_fit = np.arange(
                beacon_frequency_index - half_number_of_points_beacon_fit,
                beacon_frequency_index + half_number_of_points_beacon_fit + 1,
            )
            signal_to_fit = magn_fft_interval[
                beacon_frequency_index
                - half_number_of_points_beacon_fit : beacon_frequency_index
                + half_number_of_points_beacon_fit
                + 1
            ]

            # Initial guess determination
            if (
                magn_fft_interval[beacon_frequency_index - 1]
                > magn_fft_interval[beacon_frequency_index + 1]
            ):
                initial_guess_fit = np.array(
                    [
                        magn_fft_interval[beacon_frequency_index],
                        beacon_frequency_index - 0.01,
                    ]
                )
            else:
                initial_guess_fit = np.array(
                    [
                        magn_fft_interval[beacon_frequency_index],
                        beacon_frequency_index + 0.01,
                    ]
                )

            # Fit
            beacon_fit_parameters, _ = curve_fit(
                self.hanning_window_function,
                frequency_indices_to_fit,
                signal_to_fit,
                initial_guess_fit,
                method="trf",
                maxfev=Config.get(__name__, "fit_max_evaluations"),
            )
            beacon_fit_residuals = signal_to_fit - self.hanning_window_function(
                frequency_indices_to_fit, *beacon_fit_parameters
            )
            beacon_fit_residuals_norm = np.sum(beacon_fit_residuals**2)

            # Frequency and amplitude retrieval
            beacon_amplitude = beacon_fit_parameters[0]
            beacon_frequency = (
                beacon_fit_parameters[1]
                * self.signal.samplerate
                / self.samples_per_interval
            )  # Retrieve the frequency from the best freq index

            # Phase computation
            beacon_discrete_phase = np.angle(real_fft_interval[beacon_frequency_index])
            beacon_continuous_phase = (
                beacon_discrete_phase
                - (beacon_fit_parameters[1] - beacon_frequency_index)
                * np.pi
                * (self.samples_per_interval - 1)
                / self.samples_per_interval
            )  # Correction to have phase at continuous max

            # Set output values
            self.beacon_parameters[j, 0] = beacon_frequency
            self.beacon_parameters[j, 1] = beacon_amplitude
            self.beacon_parameters[j, 2] = beacon_continuous_phase
            self.beacon_parameters[j, 3] = beacon_fit_residuals_norm

    def correct_beacon(self):
        """
        Correct and interpolate beacon parameters across time intervals.

        This method:
        - Identifies "good" fits based on median absolute deviation (MAD)
        - Interpolates frequency and amplitude for "bad" fits
        - Interpolates phase values while accounting for unwrapping and phase continuity
        - Reconstructs the full beacon signal from the corrected parameters
        - Stores the final beacon signal for subtraction
        """

        beacon_frequency = self.beacon_parameters[:, 0]

        beacon_amplitude = self.beacon_parameters[:, 1]
        beacon_continuous_phase = np.unwrap(self.beacon_parameters[:, 2])
        beacon_fit_residual = self.beacon_parameters[:, 3]
        beacon_gradient_frequency = np.gradient((beacon_frequency))

        median_frequency = np.median(beacon_frequency)
        median_amplitude = np.median(beacon_amplitude)
        median_residual = np.median(beacon_fit_residual)
        median_gradient_frequency = np.median(beacon_gradient_frequency)

        mad_frequency = np.median(np.abs(beacon_frequency - median_frequency))
        mad_amplitude = np.median(np.abs(beacon_amplitude - median_amplitude))
        mad_residual = np.median(np.abs(beacon_fit_residual - median_residual))
        mad_gradient_frequency = np.median(
            np.abs(beacon_gradient_frequency - median_gradient_frequency)
        )

        mad_residual_limit = median_residual + MAD_FACTOR * MAD_SCALE * mad_residual
        mad_gradient_frequency_limit = (
            median_gradient_frequency - MAD_FACTOR * MAD_SCALE * mad_gradient_frequency
        )

        good_frequency_indices = np.where(
            np.abs(beacon_frequency - median_frequency)
            < MAD_FACTOR * MAD_SCALE * mad_frequency
        )[0]
        good_amplitude_indices = np.where(
            np.abs(beacon_amplitude - median_amplitude)
            < MAD_FACTOR * MAD_SCALE * mad_amplitude
        )[0]
        good_residual_indices = np.where(beacon_fit_residual < mad_residual_limit)[0]
        good_gradient_frequency_indices = np.where(
            beacon_gradient_frequency > mad_gradient_frequency_limit
        )[0]

        good_fit_indices = np.intersect1d(
            good_frequency_indices,
            np.intersect1d(
                good_amplitude_indices,
                np.intersect1d(good_residual_indices, good_gradient_frequency_indices),
            ),
        )
        good_fit_indices = good_residual_indices

        good_fit_frequency = beacon_frequency[good_fit_indices]
        good_fit_amplitude = beacon_amplitude[good_fit_indices]
        good_fit_beacon_continuous_phase = beacon_continuous_phase[good_fit_indices]

        good_fit_start_fit_time = self.start_fit_time[good_fit_indices]

        bad_fit_indices = np.setdiff1d(np.arange(self.fit_intervals), good_fit_indices)

        corrected_beacon_frequency = np.interp(
            self.start_fit_time, good_fit_start_fit_time, good_fit_frequency
        )
        corrected_beacon_amplitude = np.interp(
            self.start_fit_time, good_fit_start_fit_time, good_fit_amplitude
        )

        corrected_beacon_continuous_phase = np.zeros(self.fit_intervals)
        corrected_beacon_continuous_phase[
            good_fit_indices
        ] = good_fit_beacon_continuous_phase

        # Phase interpolation -
        # We move all the phases with reference to the badly fitted interval and then interpolate linearly
        for bad_fit_index in bad_fit_indices:
            greater_indices = good_fit_indices[good_fit_indices > bad_fit_index]
            smaller_indices = good_fit_indices[good_fit_indices < bad_fit_index]

            if greater_indices.any():
                closest_greater_index = greater_indices[
                    np.argmin(np.abs(greater_indices - bad_fit_index))
                ]
                closest_greater_phase = beacon_continuous_phase[closest_greater_index]

                closest_greater_indices = np.arange(
                    bad_fit_index, closest_greater_index + 1
                )
                closest_greater_frequencies = corrected_beacon_frequency[
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
                    )  # corrected_beacon_frequency[bad_fit_index] #closest_greater_frequencies[i]

            if smaller_indices.any():
                closest_smaller_index = smaller_indices[
                    np.argmin(np.abs(smaller_indices - bad_fit_index))
                ]
                closest_smaller_phase = beacon_continuous_phase[closest_smaller_index]

                closest_smaller_indices = np.arange(
                    closest_smaller_index, bad_fit_index + 1
                )
                closest_smaller_frequencies = corrected_beacon_frequency[
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
                    )  # corrected_beacon_frequency[bad_fit_index] #closest_smaller_frequencies[i]

            if not smaller_indices.any():
                corrected_beacon_continuous_phase[
                    bad_fit_index
                ] = closest_greater_phase_shifted

            elif not greater_indices.any():
                corrected_beacon_continuous_phase[
                    bad_fit_index
                ] = closest_smaller_phase_shifted

            else:
                closest_indices = [closest_smaller_index, closest_greater_index]
                closest_phases = np.unwrap(
                    [closest_smaller_phase_shifted, closest_greater_phase_shifted]
                )  # Avoid shift greater than pi
                corrected_beacon_continuous_phase[bad_fit_index] = np.interp(
                    bad_fit_index, closest_indices, closest_phases
                )

        # Corrected beacon signal after interpolation
        corrected_beacon = np.zeros(self.padded_extended_length)
        for j in range(self.fit_intervals):
            corrected_beacon[
                self.start_fit_indices[j] : self.end_fit_indices[j] + 1
            ] = corrected_beacon_amplitude[j] * np.cos(
                2
                * np.pi
                * corrected_beacon_frequency[j]
                * (
                    self.time_vector[
                        self.start_fit_indices[j] : self.end_fit_indices[j] + 1
                    ]
                    - self.time_vector[self.start_fit_indices[j]]
                )
                + corrected_beacon_continuous_phase[j]
            )

        self.data_beacon = corrected_beacon[
            self.samples_per_interval
            // 2 : (-self.pad_width - self.samples_per_interval // 2)
        ]
