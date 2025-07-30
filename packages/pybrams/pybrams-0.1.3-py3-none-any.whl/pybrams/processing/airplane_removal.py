from __future__ import annotations

from scipy.optimize import curve_fit
from scipy.special import erfcinv
from scipy.signal import stft, istft

from skimage import measure, util
from skimage.morphology import binary_erosion
from skimage.draw import rectangle

import matplotlib.pyplot as plt
import numpy as np


from .interference_removal import InterferenceRemoval
from .signal import Signal
from pybrams.utils.config import Config
from .constants import MAD_FACTOR, MAD_SCALE


class AirplaneRemoval(InterferenceRemoval):
    """
    Class for removing airplane Doppler-shift interference from a signal.

    This class processes spectrogram images to identify and remove Doppler trails
    caused by airplanes using morphological image processing and short-time Fourier transforms (STFT)

    Inherits from:
        InterferenceRemoval: Provides core time-frequency and signal processing utilities.
    """

    def __init__(self, signal: Signal):
        """
        Initialize AirplaneRemoval with signal data and analysis parameters.

        Args:
            signal (Signal): The input signal object containing raw and cleaned time series.
        """

        super().__init__(
            signal,
            Config.get(__name__, "interval_duration"),
            Config.get(__name__, "interval_overlaps"),
        )
        self.min_columns = int(
            np.ceil(
                Config.get(__name__, "min_duration") / self.apparent_time_resolution
            )
        )
        self.min_region_orientation = np.arctan(
            1
            / Config.get(__name__, "max_doppler_shift_derivative")
            * self.frequency_resolution
            / self.apparent_time_resolution
        )
        self.max_rows = int(
            np.floor(
                Config.get(__name__, "max_spectral_width") / self.frequency_resolution
            )
        )
        self.max_columns_meteor = int(
            np.floor(
                Config.get(__name__, "meteor_max_duration")
                / self.apparent_time_resolution
            )
        )
        self.min_rows_meteor = int(
            np.ceil(
                Config.get(__name__, "meteor_min_spectral_width")
                / self.frequency_resolution
            )
        )
        self.columns_interpolation = int(
            np.round(
                Config.get(__name__, "interpolation_duration")
                / self.apparent_time_resolution
            )
        )
        self.extra_columns_crossing = int(
            np.round(
                Config.get(__name__, "crossing_extra_duration")
                / self.apparent_time_resolution
            )
        )
        self.extra_rows_crossing = int(
            np.round(
                Config.get(__name__, "crossing_extra_spectral_width")
                / self.frequency_resolution
            )
        )
        self.min_rows_interpolation_distance = int(
            np.ceil(
                (2 * Config.get(__name__, "fit_half_range_frequency") + 1)
                / self.frequency_resolution
            )
        )

    def remove_interference(self):
        """
        Execute the full pipeline for removing airplane interference.

        Steps:
            1. Build binary image of potential airplane signals.
            2. Filter and clean this binary image.
            3. Interpolate across detected airplane trails.
            4. Subtract estimated airplane contribution from cleaned signal.
            5. Plot intermediate results for debugging and validation.
        """

        self.build_binary_image()

        self.filter_binary_image()

        self.correct_airplanes()

        self.signal.cleaned_series.data -= self.data_airplane

        self.plot_airplane_interference()

    def plot_airplane_interference(self):
        _, axes = plt.subplots(8, 1, figsize=(6, 32))

        axes[0].imshow(self.signal_image, cmap="gray", aspect="auto")
        axes[0].set_title("Thresholded image")

        axes[1].imshow(self.locally_filtered_image, cmap="gray", aspect="auto")
        axes[1].set_title("Locally filtered image")

        axes[2].imshow(self.eroded_meteor_image, cmap="gray", aspect="auto")
        axes[2].set_title("Vertically eroded image")

        axes[3].imshow(self.eroded_image, cmap="gray", aspect="auto")
        axes[3].set_title("Horizontally eroded image")

        axes[4].imshow(self.eroded_intersection_image, cmap="gray", aspect="auto")
        axes[4].set_title("Intersection eroded image")

        axes[5].imshow(self.meteor_crossing_image, cmap="gray", aspect="auto")
        axes[5].set_title("Meteor crossing image")

        axes[6].imshow(self.airplane_image, cmap="gray", aspect="auto")
        axes[6].set_title("Airplane only image")

        axes[7].imshow(self.corrected_image, cmap="gray", aspect="auto")
        axes[7].set_title("Corrected image")

        plt.tight_layout()
        plt.show()

    def build_binary_image(self):
        """
        Construct a binary spectrogram image flagging potential airplane signals.

        The method:
            - Restricts frequency to expected airplane Doppler range.
            - Applies a magnitude threshold based on noise level.
            - Flags pixels (time-frequency bins) exceeding the threshold.
        """

        self.airplane_min_frequency = self.signal.beacon_frequency - Config.get(
            __name__, "find_half_range_frequency"
        )
        self.airplane_max_frequency = self.signal.beacon_frequency + Config.get(
            __name__, "find_half_range_frequency"
        )

        self.airplane_min_frequency_index = np.argmin(
            np.abs(self.stft_frequency - self.airplane_min_frequency)
        )
        self.airplane_max_frequency_index = np.argmin(
            np.abs(self.stft_frequency - self.airplane_max_frequency)
        )

        self.airplane_frequency_indices = np.arange(
            self.airplane_min_frequency_index, self.airplane_max_frequency_index + 1
        )

        self.number_of_rows_signal_image = (
            self.airplane_max_frequency_index - self.airplane_min_frequency_index + 1
        )

        self.signal_image = np.zeros(
            (self.number_of_rows_signal_image, self.fit_intervals), dtype=bool
        )

        self.image_frequency = self.stft_frequency[
            self.airplane_frequency_indices[::-1]
        ]

        for j in range(self.fit_intervals):
            # Fft computation
            real_fft_interval = self.Zxx[:, j]
            magn_fft_interval = abs(real_fft_interval)
            magn_fft_interval[1:-1] = 2 * abs(magn_fft_interval[1:-1])

            # Airplane detection
            signal_peaks_indices = np.argwhere(magn_fft_interval > self.noise_limits[j])
            potential_airplane_peaks_indices = signal_peaks_indices[
                np.isin(signal_peaks_indices, self.airplane_frequency_indices)
            ]

            if potential_airplane_peaks_indices.any():
                self.signal_image[
                    self.airplane_max_frequency_index
                    - potential_airplane_peaks_indices,
                    j,
                ] = True

    def filter_binary_image(self):
        """
        Apply morphological and logical operations to clean the binary spectrogram image.

        This involves:
            - Kernel construction for orientation filtering.
            - Local filtering to suppress noise and highlight features.
            - Erosion operations to isolate potential airplane trails.
            - Meteor crossing and trail separation logic.
        """

        self.build_image_kernel()

        self.filter_image_locally()

        self.erode_binary_image()

        self.build_meteor_crossing()

        self.interpolate_meteor_crossing()

    def build_image_kernel(self):
        kernel_size = 2 * self.min_columns + 1

        self.kernel = np.zeros((kernel_size, kernel_size), dtype=bool)

        # Define the reference point (center of the matrix)
        center_x, center_y = kernel_size // 2, kernel_size // 2

        # Calculate angles for each point in the matrix with respect to the center
        for i in range(kernel_size):
            for j in range(kernel_size):
                # Calculate the angle of the current point with respect to the center
                angle = np.arctan2(j - center_x, i - center_y)

                # Set the quadrant based on the specified angle range
                if (
                    np.pi / 2 >= angle >= self.min_region_orientation
                    or (-np.pi + self.min_region_orientation) <= angle <= -np.pi / 2
                ):
                    self.kernel[i, j] = True

        self.kernel[center_x, center_y] = True

    def filter_image_locally(self):
        """
        Applies the kernel to the binary signal image locally.

        This operation enhances regions that meet minimum length and orientation
        criteria, helping distinguish airplane signals from noise and short events.
        """

        padded_signal_image = np.pad(self.signal_image, pad_width=(self.min_columns,))
        windowed_padded_signal_image = util.shape.view_as_windows(
            padded_signal_image, self.kernel.shape
        )
        self.locally_filtered_image = np.zeros_like(self.signal_image)
        nonzero_rows_image = np.argwhere(self.signal_image)

        for nonzero_index in nonzero_rows_image:
            row_index, column_index = nonzero_index
            kerneled_image = (
                windowed_padded_signal_image[row_index, column_index] * self.kernel
            )
            labeled_image = measure.label(
                kerneled_image, connectivity=2
            )  # Connectivity = 2 -> region
            regions = measure.regionprops(labeled_image)

            for region in regions:
                region_columns = region.bbox[3] - region.bbox[1]

                if (
                    region_columns >= self.min_columns
                    and region.orientation >= self.min_region_orientation
                ):
                    self.locally_filtered_image[row_index, column_index] = True
                    continue

    def erode_binary_image(self):
        """
        Performs erosion on the binary image to separate airplane tracks from
        meteor events.

        Uses both vertical and orientation-aware erosion footprints to refine
        the binary image based on the expected geometry of airplane signals.
        """

        self.eroded_meteor_image = binary_erosion(
            self.signal_image, footprint=np.ones((self.min_rows_meteor, 1))
        )

        orientations = np.linspace(
            self.min_region_orientation,
            np.pi / 2,
            Config.get(__name__, "number_erosion_footprints"),
        )
        max_rows_meteor = np.array(
            [
                int(np.floor((self.max_columns_meteor - 1) * np.cos(orientation)))
                for orientation in orientations
            ]
        )
        eroded_images = []

        for i in range(Config.get(__name__, "number_erosion_footprints")):
            orientation = orientations[i]
            max_row_meteor = max_rows_meteor[i]
            footprint = np.zeros(
                (max_row_meteor + 1, self.max_columns_meteor), dtype=bool
            )

            for column in range(self.max_columns_meteor):
                row = int(np.floor(column * np.cos(orientation)))
                footprint[row, column] = True

            eroded_images.append(
                binary_erosion(self.locally_filtered_image, footprint=footprint)
            )

        self.eroded_image = np.zeros_like(self.eroded_meteor_image)

        for i in range(len(eroded_images)):
            self.eroded_image = np.logical_or(self.eroded_image, eroded_images[i])

    def build_meteor_crossing(self):
        """
        Identifies and isolates regions where airplane tracks cross meteor signals.

        Filters out regions too close to the beacon frequency, expands them to
        account for interpolation margins, and classifies them into meteor
        crossing or beacon-related.
        """

        self.eroded_intersection_image = np.logical_and(
            self.eroded_meteor_image, self.eroded_image
        )

        self.eroded_intersection_labeled_image = measure.label(
            self.eroded_intersection_image, connectivity=2
        )
        eroded_intersection_regions = measure.regionprops(
            self.eroded_intersection_labeled_image
        )

        self.meteor_crossing_image = np.zeros_like(self.eroded_intersection_image)
        self.beacon_crossing_image = np.zeros_like(self.eroded_intersection_image)

        for region in eroded_intersection_regions:
            label = region.label

            centroid_frequency = self.image_frequency[int(round(region.centroid[0]))]

            # Region too close to beacon frequency
            if np.abs(centroid_frequency - self.signal.beacon_frequency) < Config.get(
                __name__, "fit_half_range_frequency"
            ) + Config.get(
                "pybrams.processing.beacon_removal", "fit_half_range_frequency"
            ) + Config.get(
                "pybrams.processing.beacon_removal", "find_half_range_frequency"
            ):
                self.beacon_crossing_image[
                    self.eroded_intersection_labeled_image == label
                ] = True
                continue

            min_row, min_column, max_row, max_column = region.bbox
            start_region = (
                min_row - self.extra_rows_crossing,
                min_column - self.extra_columns_crossing,
            )
            end_region = (
                max_row + self.extra_rows_crossing - 1,
                max_column + self.extra_columns_crossing - 1,
            )
            rows, columns = rectangle(
                start=start_region,
                end=end_region,
                shape=self.meteor_crossing_image.shape,
            )
            self.meteor_crossing_image[rows, columns] = True

    def interpolate_meteor_crossing(self):
        """
        Interpolates airplane signals over detected meteor crossings.

        Interpolation is only applied if matching regions are found on both sides
        of the crossing. The result is used to reconstruct airplane traces that
        are temporarily obscured.
        """

        self.meteor_crossing_labeled_image = measure.label(
            self.meteor_crossing_image, connectivity=2
        )
        to_interpolate_regions = measure.regionprops(self.meteor_crossing_labeled_image)

        self.Zxx_corrected = np.copy(self.Zxx)

        for to_interpolate_region in to_interpolate_regions:
            label = to_interpolate_region.label

            max_column_airplane_left = to_interpolate_region.bbox[1] - 1
            min_column_airplane_left = (
                max_column_airplane_left - self.columns_interpolation + 1
            )

            airplane_left_regions = self.get_neighbor_airplane_regions(
                to_interpolate_region,
                min_column_airplane_left,
                max_column_airplane_left,
            )

            min_column_airplane_right = to_interpolate_region.bbox[3]
            max_column_airplane_right = (
                min_column_airplane_right + self.columns_interpolation - 1
            )

            airplane_right_regions = self.get_neighbor_airplane_regions(
                to_interpolate_region,
                min_column_airplane_right,
                max_column_airplane_right,
            )

            # No airplane on one side, or different numbers of airplanes on both sides
            if (
                (not airplane_left_regions)
                or (not airplane_right_regions)
                or (len(airplane_left_regions) != len(airplane_right_regions))
            ):
                self.meteor_crossing_image[
                    self.meteor_crossing_labeled_image == label
                ] = False
                continue

            pair_airplane_regions = self.pair_airplane_regions(
                airplane_left_regions, airplane_right_regions
            )

            self.compute_interpolated_airplane_signal(
                to_interpolate_region, pair_airplane_regions
            )

        self.airplane_image = np.logical_or(
            self.eroded_image, self.beacon_crossing_image
        )

    def get_neighbor_airplane_regions(
        self, to_interpolate_region, min_column_airplane, max_column_airplane
    ):
        """
        Finds airplane regions adjacent to a meteor crossing.

        Filters regions based on location, size, and frequency separation to ensure
        valid interpolation targets.

        Parameters:
            to_interpolate_region (RegionProperties): The region to interpolate over.
            min_column_airplane (int): Minimum column index for the search window.
            max_column_airplane (int): Maximum column index for the search window.

        Returns:
            list: List of valid airplane region objects.
        """

        neighbor_airplane_image = np.zeros_like(self.eroded_image)
        neighbor_airplane_image[
            :, min_column_airplane : max_column_airplane + 1
        ] = self.eroded_image[:, min_column_airplane : max_column_airplane + 1]

        neighbor_airplane_labeled_image = measure.label(
            neighbor_airplane_image, connectivity=2
        )
        airplane_regions = measure.regionprops(neighbor_airplane_labeled_image)

        airplane_regions_to_return = []

        for airplane_region in airplane_regions:
            airplane_column_span = airplane_region.bbox[3] - airplane_region.bbox[1]
            airplane_row_span = airplane_region.bbox[2] - airplane_region.bbox[0]

            airplane_row_coords = airplane_region.coords[:, 0]

            # Regions not in the good location or with the good dimensions
            if (airplane_row_span <= self.max_rows) and (
                np.all(
                    np.logical_and(
                        airplane_row_coords >= to_interpolate_region.bbox[0],
                        airplane_row_coords < to_interpolate_region.bbox[2],
                    )
                )
            ):
                airplane_regions_to_return.append(airplane_region)

        airplane_mean_rows = [
            airplane_region.centroid[0]
            for airplane_region in airplane_regions_to_return
        ]

        # Regions not too close
        if np.all(
            np.abs(np.diff(airplane_mean_rows)) > self.min_rows_interpolation_distance
        ):
            return airplane_regions_to_return

        return []

    def pair_airplane_regions(self, airplane_left_regions, airplane_right_regions):
        """
        Pairs corresponding airplane regions on the left and right sides
        of a meteor crossing.

        Regions are paired by minimizing vertical (frequency) distance between
        their centroids.

        Parameters:
            airplane_left_regions (list): Regions to the left of the crossing.
            airplane_right_regions (list): Regions to the right of the crossing.

        Returns:
            list: List of tuples, each containing a paired left and right region.
        """

        pairing = []

        for airplane_left_region in airplane_left_regions:
            row_distance = self.meteor_crossing_image.shape[0]
            airplane_right_region = None

            for right_region in airplane_right_regions:
                current_row_distance = np.abs(
                    airplane_left_region.centroid[0] - right_region.centroid[0]
                )

                if current_row_distance < row_distance:
                    airplane_right_region = right_region
                    row_distance = current_row_distance

            pairing.append((airplane_left_region, airplane_right_region))

        return pairing

    def compute_interpolated_airplane_signal(
        self, to_interpolate_region, pair_airplane_regions
    ):
        """
        Interpolates and reconstructs the airplane signal over a specified region.

        This method zeroes out the original STFT coefficients in the airplane crossing region,
        then fits and interpolates airplane signal properties (amplitude, frequency, phase)
        from pairs of airplane regions to reconstruct the signal in time domain.
        The reconstructed signal is then transformed back to STFT coefficients to update
        the corrected STFT matrix `Zxx_corrected`.

        Parameters
        ----------
        to_interpolate_region : RegionProperties
            The region where interpolation of the airplane signal is needed.

        pair_airplane_regions : list of list of RegionProperties
        List of pairs of airplane regions used for interpolation.
        """

        crossing_column_start = to_interpolate_region.bbox[1]
        crossing_column_end = to_interpolate_region.bbox[3] - 1

        crossing_columns = np.arange(crossing_column_start, crossing_column_end + 1)

        crossing_row_start = to_interpolate_region.bbox[0]
        crossing_row_end = to_interpolate_region.bbox[2] - 1

        crossing_row_Zxx_start = self.airplane_max_frequency_index - crossing_row_end
        crossing_row_Zxx_end = self.airplane_max_frequency_index - crossing_row_start

        self.Zxx_corrected[
            crossing_row_Zxx_start : (crossing_row_Zxx_end + 1), crossing_columns
        ] = 0

        for pair_airplane_region in pair_airplane_regions:
            pair_properties = []

            for airplane_region in pair_airplane_region:
                column_start = airplane_region.bbox[1]

                start_fit_index = self.start_fit_indices[column_start]
                end_fit_index = self.end_fit_indices[column_start]

                # Fft computation
                real_fft_interval = self.Zxx[:, column_start]
                magn_fft_interval = abs(real_fft_interval)
                magn_fft_interval[1:-1] = 2 * abs(magn_fft_interval[1:-1])

                min_airplane_frequency_index = np.argmin(
                    np.abs(
                        self.stft_frequency
                        - self.image_frequency[airplane_region.bbox[2] - 1]
                    )
                )
                max_airplane_frequency_index = np.argmin(
                    np.abs(
                        self.stft_frequency
                        - self.image_frequency[airplane_region.bbox[0]]
                    )
                )

                # Look for the Fft peak inside interval around airplane frequency
                local_airplane_frequency_index = np.argmax(
                    magn_fft_interval[
                        min_airplane_frequency_index : max_airplane_frequency_index + 1
                    ]
                )
                airplane_frequency_index = (
                    local_airplane_frequency_index + min_airplane_frequency_index
                )

                # Set-up of airplane fit
                half_number_of_points_airplane_fit = round(
                    Config.get(__name__, "fit_half_range_frequency")
                    * self.samples_per_interval
                    / self.signal.samplerate
                )
                frequency_indices_to_fit = np.arange(
                    airplane_frequency_index - half_number_of_points_airplane_fit,
                    airplane_frequency_index + half_number_of_points_airplane_fit + 1,
                )
                signal_to_fit = magn_fft_interval[
                    airplane_frequency_index
                    - half_number_of_points_airplane_fit : airplane_frequency_index
                    + half_number_of_points_airplane_fit
                    + 1
                ]

                # Initial guess determination
                if (
                    magn_fft_interval[airplane_frequency_index - 1]
                    > magn_fft_interval[airplane_frequency_index + 1]
                ):
                    initial_guess_fit = np.array(
                        [
                            magn_fft_interval[airplane_frequency_index],
                            airplane_frequency_index - 0.01,
                        ]
                    )
                else:
                    initial_guess_fit = np.array(
                        [
                            magn_fft_interval[airplane_frequency_index],
                            airplane_frequency_index + 0.01,
                        ]
                    )

                # Fit
                airplane_fit_parameters, _ = curve_fit(
                    self.hanning_window_function,
                    frequency_indices_to_fit,
                    signal_to_fit,
                    initial_guess_fit,
                    method="trf",
                )

                # Frequency and amplitude retrieval
                airplane_amplitude = airplane_fit_parameters[0]
                airplane_frequency = (
                    airplane_fit_parameters[1]
                    * self.signal.samplerate
                    / self.samples_per_interval
                )  # Retrieve the frequency from the best freq index

                # Phase computation
                airplane_discrete_phase = np.angle(
                    real_fft_interval[airplane_frequency_index]
                )
                airplane_continuous_phase = (
                    airplane_discrete_phase
                    - (airplane_fit_parameters[1] - airplane_frequency_index)
                    * np.pi
                    * (self.samples_per_interval - 1)
                    / self.samples_per_interval
                )  # Correction to have phase at continuous max

                pair_properties.append(
                    (
                        airplane_amplitude,
                        airplane_frequency,
                        airplane_continuous_phase,
                        start_fit_index,
                        end_fit_index,
                    )
                )

            crossing_signal = self.padded_extended_data

            pair_amplitudes = np.array([pair_properties[0][0], pair_properties[1][0]])
            pair_frequencies = np.array([pair_properties[0][1], pair_properties[1][1]])
            pair_phases = np.array([pair_properties[0][2], pair_properties[1][2]])

            pair_mid_fit_indices = np.array(
                [
                    (pair_properties[0][3] + pair_properties[0][4]) // 2,
                    (pair_properties[1][3] + pair_properties[1][4]) // 2,
                ]
            )

            interp_start_index = pair_properties[0][3]
            interp_end_index = pair_properties[1][4]

            interp_indices = np.arange(interp_start_index, interp_end_index + 1)

            interp_amplitude = np.interp(
                interp_indices, pair_mid_fit_indices, pair_amplitudes
            )
            interp_frequency = np.interp(
                interp_indices, pair_mid_fit_indices, pair_frequencies
            )

            interp_phase = np.zeros(len(interp_indices))
            interp_phase[0] = pair_phases[0]

            for i in range(1, len(interp_phase)):
                interp_phase[i] = interp_phase[i - 1] + 2 * np.pi * np.trapz(
                    interp_frequency[i - 1 : i + 1],
                    x=self.time_vector[interp_indices[i - 1 : i + 1]],
                )

            interp_signal = interp_amplitude * np.cos(interp_phase)

            crossing_signal[interp_indices] = interp_signal

            corrected_crossing_signal = crossing_signal[
                self.samples_per_interval
                // 2 : (-self.pad_width - self.samples_per_interval // 2)
            ]

            _, _, new_stft = stft(
                corrected_crossing_signal,
                fs=self.signal.samplerate,
                nperseg=self.samples_per_interval,
                noverlap=self.overlaps_per_interval,
            )

            self.Zxx_corrected[
                crossing_row_Zxx_start : (crossing_row_Zxx_end + 1), crossing_columns
            ] += new_stft[
                crossing_row_Zxx_start : (crossing_row_Zxx_end + 1), crossing_columns
            ]

    def correct_airplanes(self):
        self.corrected_image = np.logical_or(
            self.airplane_image, self.meteor_crossing_image
        )
        """
        Generates a corrected time-domain signal by removing airplane and meteor crossing artifacts.

        This method combines airplane and meteor crossing binary masks to filter the STFT matrix,
        extracts the airplane frequency band, zeros out other frequencies,
        and reconstructs the filtered signal using inverse STFT.

        The result is stored in `data_airplane` attribute as the cleaned time-domain data.
        """

        self.flipped_filtered_image = self.corrected_image[::-1, :]

        self.Zxx_local = self.Zxx_corrected[self.airplane_frequency_indices, :].copy()
        self.Zxx_local = np.where(self.flipped_filtered_image, self.Zxx_local, 0)

        self.Zxx_filtered = np.zeros_like(self.Zxx_corrected)
        self.Zxx_filtered[
            self.airplane_min_frequency_index : self.airplane_max_frequency_index + 1, :
        ] = self.Zxx_local

        _, self.padded_filtered_airplane = istft(
            self.Zxx_filtered,
            fs=self.signal.samplerate,
            nperseg=self.samples_per_interval,
            noverlap=self.overlaps_per_interval,
        )
        self.data_airplane = self.padded_filtered_airplane[: self.samples]

    def compute_airplanes_dict(self):
        """
        Computes airplane signal parameters dictionary from eroded airplane image regions.

        Iterates over time intervals with airplane signals, identifies contiguous frequency bands,
        fits a Hanning-window-based model to each frequency component to extract amplitude,
        frequency, phase, and residuals, and stores the best fits in `airplanes_dict`.

        After fitting, displays comparison images of the original binary airplane detection
        and the refined airplane frequency-time map.

        """

        self.airplanes_dict = {}

        for j in range(self.fit_intervals):
            if np.any(self.eroded_image[:, j] != 0):
                start_index = self.start_fit_indices[j]
                end_index = self.end_fit_indices[j]

                # Fft computation
                real_fft_interval = self.Zxx[:, j]
                magn_fft_interval = abs(real_fft_interval)
                magn_fft_interval[1:-1] = 2 * abs(magn_fft_interval[1:-1])

                # Identify non-zero elements
                non_zero_indices = np.nonzero(self.eroded_image[:, j])[0]

                airplane_indices = np.sort(
                    self.airplane_frequency_indices[-1] - non_zero_indices
                )

                jump_positions = np.where(np.diff(airplane_indices) != 1)[0] + 1

                # Split the array based on jump positions
                split_airplane_indices = np.split(airplane_indices, jump_positions)

                half_number_of_points_airplane_fit = round(
                    Config.get(__name__, "fit_half_range_frequency")
                    * self.samples_per_interval
                    / self.signal.samplerate
                )

                for local_airplane_indices in split_airplane_indices:
                    local_airplane_parameters = np.zeros(
                        (len(local_airplane_indices), 4)
                    )

                    for local_index, airplane_frequency_index in np.ndenumerate(
                        local_airplane_indices
                    ):
                        frequency_indices_to_fit = np.arange(
                            airplane_frequency_index
                            - half_number_of_points_airplane_fit,
                            airplane_frequency_index
                            + half_number_of_points_airplane_fit
                            + 1,
                        )
                        signal_to_fit = magn_fft_interval[
                            airplane_frequency_index
                            - half_number_of_points_airplane_fit : airplane_frequency_index
                            + half_number_of_points_airplane_fit
                            + 1
                        ]

                        # Initial guess determination
                        if (
                            magn_fft_interval[airplane_frequency_index - 1]
                            > magn_fft_interval[airplane_frequency_index + 1]
                        ):
                            initial_guess_fit = np.array(
                                [
                                    magn_fft_interval[airplane_frequency_index],
                                    airplane_frequency_index - 0.01,
                                ]
                            )
                        else:
                            initial_guess_fit = np.array(
                                [
                                    magn_fft_interval[airplane_frequency_index],
                                    airplane_frequency_index + 0.01,
                                ]
                            )

                        # Fit
                        airplane_fit_parameters, _ = curve_fit(
                            self.hanning_window_function,
                            frequency_indices_to_fit,
                            signal_to_fit,
                            initial_guess_fit,
                            method="trf",
                            maxfev=Config.get(
                                "pybrams.processing.beacon_removal",
                                "fit_max_evaluations",
                            ),
                        )
                        airplane_fit_residuals = (
                            signal_to_fit
                            - self.hanning_window_function(
                                frequency_indices_to_fit, *airplane_fit_parameters
                            )
                        )
                        airplane_fit_residuals_norm = np.sum(
                            airplane_fit_residuals**2
                        )

                        # Frequency and amplitude retrieval
                        airplane_amplitude = airplane_fit_parameters[0]
                        airplane_frequency = (
                            airplane_fit_parameters[1]
                            * self.signal.samplerate
                            / self.samples_per_interval
                        )  # Retrieve the frequency from the best freq index

                        # Phase computation
                        airplane_discrete_phase = np.angle(
                            real_fft_interval[airplane_frequency_index]
                        )
                        airplane_continuous_phase = (
                            airplane_discrete_phase
                            - (airplane_fit_parameters[1] - airplane_frequency_index)
                            * np.pi
                            * (self.samples_per_interval - 1)
                            / self.samples_per_interval
                        )  # Correction to have phase at continuous max
                        local_airplane_parameters[local_index, :] = [
                            airplane_frequency,
                            airplane_amplitude,
                            airplane_continuous_phase,
                            airplane_fit_residuals_norm,
                        ]

                    index_min_residuals = np.argmin(local_airplane_parameters[:, 3])

                    self.airplanes_dict[
                        j, local_airplane_indices[index_min_residuals]
                    ] = local_airplane_parameters[index_min_residuals]

        final_image = np.zeros_like(self.eroded_image)
        for key in self.airplanes_dict.keys():
            final_image[self.airplane_frequency_indices[-1] - key[1], key[0]] = 1

        fig, axes = plt.subplots(2, 1)
        fig.set_size_inches(10.5, 10.5)
        axes[0].imshow(self.signal_image, cmap="gray", aspect="auto")
        axes[0].set_title("Original Binary Image")

        axes[1].imshow(final_image, cmap="gray", aspect="auto")
        axes[1].set_title("Final Image")

        plt.tight_layout()
        plt.show()
