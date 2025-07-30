import autograd.numpy as np
import datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional
from numpy.typing import NDArray
from scipy.signal import filtfilt, find_peaks, hilbert, savgol_filter
from scipy.signal.windows import blackman
from scipy.special import fresnel
from scipy.interpolate import interp1d, LinearNDInterpolator
import scipy.stats as stats
import matplotlib.pyplot as plt
from KDEpy import FFTKDE
from pathlib import Path
import pybrams.brams.file
from pybrams.utils import Config
from pybrams.utils import Data
import logging

logger = logging.getLogger(__name__)


filtering_half_range_frequency = Config.get(__name__, "filtering_half_range_frequency")
filtering_length_kernel = Config.get(__name__, "filtering_length_kernel")
sg_order = Config.get(__name__, "sg_order")


@dataclass
class Meteor:
    """
    Represents the metadata and analysis results of a detected meteor signal
    in a radar signal processing context.
    
    Attributes:
        t0_time_of_flight (Optional[float]): Estimated time-of-flight corrected timestamp.
        t0 (Optional[float]): Final estimated t0 timestamp, may include pre-t0 correction.
        SNR (Optional[float]): Signal-to-noise ratio of the detected meteor.
        sigma_t0 (Optional[float]): Uncertainty of the t0 estimate.
        v_pseudo_pre_t0 (Optional[float]): Estimated pseudo-speed before t0.
        r_value_pre_t0 (Optional[float]): Correlation coefficient for pre-t0 estimate.
        sigma_pre_t0 (Optional[float]): Uncertainty in pre-t0 pseudo-speed estimate.
        fresnel_acceleration (Optional[float]): Estimated Fresnel acceleration (if computed).
        frequency (Optional[float]): Detected frequency of the meteor signal.
    """

    t0_time_of_flight: Optional[float] = None
    t0: Optional[float] = None
    SNR: Optional[float] = None
    sigma_t0: Optional[float] = None
    v_pseudo_pre_t0: Optional[float] = None
    r_value_pre_t0: Optional[float] = None
    sigma_pre_t0: Optional[float] = None
    fresnel_acceleration: Optional[float] = None
    frequency: Optional[float] = None

    def json(self) -> Dict[str, Any]:
        """
        Returns the internal state of the Meteor instance as a JSON-serializable dictionary.
        
        Returns:
            dict: A dictionary representation of the meteor's attributes.
        """

        return self.__dict__

    def extract_infos(
        self,
        start: datetime.datetime,
        end: datetime.datetime,
        file: pybrams.brams.file.File,
        plot: bool,
    ):
        """
        Processes the signal in the given time range to extract meteor-related features,
        including t0 timing, SNR, uncertainty, and optionally pre-t0 velocity.

        Args:
            start (datetime): Start datetime of the signal segment to analyze.
            end (datetime): End datetime of the signal segment to analyze.
            file (pybrams.brams.file.File): Signal data file object.
            plot (bool): If True, plots intermediate signal representations.
        """

        logger.info(f"Extracting meteor information from {file.system.system_code}")

        (
            i_filt_meteor,
            q_filt_meteor,
            times,
            sample_meteor_start,
            sample_meteor_end,
        ) = self.extract_iq(start, end, file, plot=plot)

        meteor_ampl = np.sqrt(i_filt_meteor**2 + q_filt_meteor**2)

        # Timing
        output_t0 = compute_t0_and_SNR(
            meteor_ampl, file.signal.samplerate, times, plot=plot
        )

        if output_t0:
            index_t0, SNR, central_fresnel_duration = output_t0

            sigma_t0 = compute_t0_uncertainty(
                SNR, central_fresnel_duration, file.signal.samplerate, file.type
            )

            logger.info(f"Sigma t0 = {np.round(1E3*sigma_t0,2)} ms")

            if np.isnan(sigma_t0):
                return None

            sample_t0 = index_t0 + sample_meteor_start

            self.t0_time_of_flight = (
                extrapolate_time(
                    sample_t0,
                    file.signal.corrected_pps.timestamps.s,
                    file.signal.corrected_pps.index,
                    file.signal.samplerate,
                )
                - Config.get(__name__, "timing_corrections")[file.type]
            )
            self.t0 = self.t0_time_of_flight
            self.SNR = SNR
            self.sigma_t0 = np.sqrt(
                sigma_t0**2
                + Config.get(__name__, "timing_uncertainties")[file.type] ** 2
            )

            logger.info("Meteor timing successfully determined !")

            # Pre-t0
            corrected_meteor_phase = detrend_doppler_shift(
                i_filt_meteor, q_filt_meteor, self.frequency, times - times[0]
            )

            output_pre_t0 = compute_pre_t0_speed(
                meteor_ampl,
                corrected_meteor_phase,
                index_t0,
                file.signal.samplerate,
                times,
                plot,
            )

            if output_pre_t0:
                (
                    index_pre_t0,
                    v_pseudo_pre_t0,
                    r_value_pre_t0,
                    sigma_pre_t0,
                ) = output_pre_t0

                sample_pre_t0 = index_pre_t0 + sample_meteor_start

                self.t0 = (
                    extrapolate_time(
                        sample_pre_t0,
                        file.signal.corrected_pps.timestamps.s,
                        file.signal.corrected_pps.index,
                        file.signal.samplerate,
                    )
                    - Config.get(__name__, "timing_corrections")[file.type]
                )
                self.v_pseudo_pre_t0 = v_pseudo_pre_t0
                self.r_value_pre_t0 = r_value_pre_t0
                self.sigma_pre_t0 = sigma_pre_t0

    def extract_iq(
        self,
        start: datetime.datetime,
        end: datetime.datetime,
        file: pybrams.brams.file.File,
        plot: bool = False,
    ):
        """
        Extracts and filters I/Q components of the signal between `start` and `end`,
        centered around the expected meteor event. Also computes associated time array.

        Args:
            start (datetime): Start datetime of the extraction window.
            end (datetime): End datetime of the extraction window.
            file (pybrams.brams.file.File): Signal data file object.
            plot (bool, optional): Whether to show signal plots before and after filtering.

        Returns:
            Tuple: Filtered I and Q components, time vector, start and end sample indices.
        """

        shifted_pps = (
            file.signal.corrected_pps.timestamps.s
            - file.signal.corrected_pps.timestamps.s[0]
        )
        index_pps = file.signal.corrected_pps.index

        sample_user_start = round(
            (start - file.start).total_seconds() * file.signal.samplerate
        )

        if sample_user_start < 0:
            return

        sample_user_end = round(
            (end - file.start).total_seconds() * file.signal.samplerate
        )

        user_signal = file.signal.cleaned_series.data[
            sample_user_start : sample_user_end + 1
        ]

        filt_user_signal, _ = filter_signal(
            user_signal,
            file.signal.samplerate,
            file.signal.beacon_frequency,
            filtering_half_range_frequency,
        )

        if plot:
            samples_user = np.arange(sample_user_start, sample_user_end + 1)
            user_times = np.empty(len(user_signal))

            for i in range(len(user_signal)):
                user_times[i] = extrapolate_time(
                    samples_user[i], shifted_pps, index_pps, file.signal.samplerate
                )

            plt.figure()
            plt.title("Time series before bandpass filter")
            plt.plot(user_times, user_signal)
            plt.xlabel("Time [s]")
            plt.ylabel("Signal [-]")
            plt.tight_layout()
            plt.grid(True)
            plt.show()

            plt.figure()
            plt.title("Time series after bandpass filter")
            plt.plot(user_times, filt_user_signal)
            plt.xlabel("Time [s]")
            plt.ylabel("Signal  [-]")
            plt.tight_layout()
            plt.grid(True)
            plt.show()

        hilbert_user_signal = hilbert(filt_user_signal)
        i_user_signal, q_user_signal = (
            np.real(hilbert_user_signal),
            np.imag(hilbert_user_signal),
        )

        user_ampl = np.sqrt(i_user_signal**2 + q_user_signal**2)

        ampl_sg_window_points = round(
            Config.get(__name__, "ampl_sg_window_duration") * file.signal.samplerate
        )
        user_ampl = apply_sg_smoothing(user_ampl, ampl_sg_window_points, sg_order)

        index_meteor_peak = np.argmax(user_ampl)

        sample_meteor_start = (
            sample_user_start
            + index_meteor_peak
            - round(
                Config.get(__name__, "prepadding_duration") * file.signal.samplerate
            )
        )
        sample_meteor_end = (
            sample_user_start
            + index_meteor_peak
            + round(
                Config.get(__name__, "postpadding_duration") * file.signal.samplerate
            )
        )

        meteor_signal = file.signal.cleaned_series.data[
            sample_meteor_start : sample_meteor_end + 1
        ]

        filt_meteor_signal, self.frequency = filter_signal(
            meteor_signal,
            file.signal.samplerate,
            file.signal.beacon_frequency,
            filtering_half_range_frequency,
        )

        hilbert_meteor_signal = hilbert(filt_meteor_signal)
        i_filt_meteor, q_filt_meteor = (
            np.real(hilbert_meteor_signal),
            np.imag(hilbert_meteor_signal),
        )

        samples_meteor = np.arange(sample_meteor_start, sample_meteor_end + 1)
        times = np.empty(len(meteor_signal))

        for i in range(len(meteor_signal)):
            times[i] = extrapolate_time(
                samples_meteor[i], shifted_pps, index_pps, file.signal.samplerate
            )

        if plot:
            meteor_ampl = np.sqrt(i_filt_meteor**2 + q_filt_meteor**2)

            plt.figure()
            plt.title("Amplitude curve")
            plt.plot(times, meteor_ampl / max(meteor_ampl))
            plt.xlabel("Time [s]")
            plt.ylabel("Amplitude [-]")
            plt.tight_layout()
            plt.grid(True)
            plt.show()

        return (
            i_filt_meteor,
            q_filt_meteor,
            times,
            sample_meteor_start,
            sample_meteor_end,
        )


def compute_t0_and_SNR(
    meteor_ampl, samplerate, times: np.array = None, plot: bool = False
):
    """
    Compute the t0 index and signal-to-noise ratio (SNR) of a meteor echo signal.

    This function smooths and normalizes the input meteor amplitude signal, estimates the
    rise and exponential decay portions of the signal (defining the meteor echo), and computes
    the t0 (start time of the meteor echo), SNR, and the central Fresnel zone duration.

    Parameters
    ----------
    meteor_ampl : np.ndarray
        Amplitude of the meteor echo signal.
    samplerate : float
        Sampling rate of the signal in Hz.
    times : np.ndarray, optional
        Time axis corresponding to `meteor_ampl`. If None, it is generated.
    plot : bool, optional
        Whether to display diagnostic plots of the signal components and t0 detection.

    Returns
    -------
    tuple or None
        Returns (index_t0, SNR, central_fresnel_duration) if successful, or None if detection fails.
    
    """

    noise = np.arange(round(Config.get(__name__, "noise_duration") * samplerate))

    norm_meteor_ampl = meteor_ampl / np.max(meteor_ampl)
    power_echo = np.max(norm_meteor_ampl**2)
    power_noise = np.mean(norm_meteor_ampl[noise] ** 2)

    SNR = 10 * np.log10((power_echo - power_noise) / power_noise)

    if times is None:
        times = np.linspace(0, len(meteor_ampl) / samplerate, len(meteor_ampl))

    ampl_sg_window_points = round(
        Config.get(__name__, "ampl_sg_window_duration") * samplerate
    )

    smooth_meteor_ampl = apply_sg_smoothing(
        meteor_ampl, ampl_sg_window_points, sg_order
    )
    norm_smooth_meteor_ampl = smooth_meteor_ampl / max(smooth_meteor_ampl)

    mean_noise = np.mean(norm_smooth_meteor_ampl[noise])

    index_global_max_ampl = np.argmax(norm_smooth_meteor_ampl)
    index_ref_max_ampl = index_global_max_ampl

    local_indices_max_ampl, _ = find_peaks(
        norm_smooth_meteor_ampl[noise[-1] : index_global_max_ampl],
        height=mean_noise
        + Config.get(__name__, "min_peak_height_ampl")
        * (norm_smooth_meteor_ampl[index_global_max_ampl] - mean_noise),
    )

    if any(local_indices_max_ampl):
        index_ref_max_ampl = min(noise[-1] + local_indices_max_ampl)

    start_rise = -1
    condition_min = (
        norm_smooth_meteor_ampl[noise[-1] : index_ref_max_ampl + 1] < mean_noise
    )
    local_indices_min_ampl = np.where(condition_min)[0]

    if any(local_indices_min_ampl):
        start_rise = noise[-1] + local_indices_min_ampl[-1]

    else:
        start_rise = noise[-1]

    indices = np.arange(len(norm_smooth_meteor_ampl))

    rise = np.where((indices <= index_global_max_ampl) & (indices >= start_rise))[0]

    if len(rise) == 0:
        logger.info("No rise found")
        return None

    start_exponential = index_global_max_ampl
    local_end_exponential = np.argmax(
        norm_smooth_meteor_ampl[start_exponential:] < mean_noise
    )

    if local_end_exponential == 0:
        end_exponential = len(norm_smooth_meteor_ampl)

    else:
        end_exponential = start_exponential + local_end_exponential

    exponential = np.arange(start_exponential, end_exponential)

    echo = np.concatenate((rise, exponential))
    not_echo = np.setdiff1d(indices, echo)

    target_t0_ampl = mean_noise + Config.get(__name__, "t0_ampl") * (
        norm_smooth_meteor_ampl[index_ref_max_ampl] - mean_noise
    )
    index_t0_in_rise = np.argmax(norm_smooth_meteor_ampl[rise] > target_t0_ampl)

    if index_t0_in_rise == 0:
        logger.info(f"T0 too soon")
        return None

    index_t0 = index_t0_in_rise + rise[0]

    index_end_central_fresnel = np.argmax(
        norm_smooth_meteor_ampl[rise]
        >= (
            mean_noise
            + Config.get(__name__, "max_central_fresnel_ampl")
            * (norm_smooth_meteor_ampl[index_ref_max_ampl] - mean_noise)
        )
    )
    index_beg_central_fresnel = np.argmax(
        norm_smooth_meteor_ampl[rise]
        >= (
            mean_noise
            + Config.get(__name__, "min_central_fresnel_ampl")
            * (norm_smooth_meteor_ampl[index_ref_max_ampl] - mean_noise)
        )
    )
    central_fresnel_duration = (
        index_end_central_fresnel - index_beg_central_fresnel
    ) / samplerate

    index_meteor_90 = np.argmax(
        norm_smooth_meteor_ampl[rise]
        >= (
            mean_noise
            + 0.9 * (norm_smooth_meteor_ampl[index_ref_max_ampl] - mean_noise)
        )
    )
    index_meteor_10 = np.argmax(
        norm_smooth_meteor_ampl[rise]
        >= (
            mean_noise
            + 0.1 * (norm_smooth_meteor_ampl[index_ref_max_ampl] - mean_noise)
        )
    )
    rise_duration = (index_meteor_90 - index_meteor_10) / samplerate

    index_meteor_90 = np.argmax(
        norm_smooth_meteor_ampl[rise]
        >= (
            mean_noise
            + 0.9 * (norm_smooth_meteor_ampl[index_ref_max_ampl] - mean_noise)
        )
    )
    index_meteor_10 = np.argmax(
        norm_smooth_meteor_ampl[rise]
        >= (
            mean_noise
            + 0.1 * (norm_smooth_meteor_ampl[index_ref_max_ampl] - mean_noise)
        )
    )

    if plot:
        # Plot split signal
        plt.figure()
        plt.plot(times[rise], norm_smooth_meteor_ampl[rise], ".g", label="Rise")
        plt.plot(
            times[exponential],
            norm_smooth_meteor_ampl[exponential],
            ".b",
            label="Exponential",
        )
        plt.plot(
            times[not_echo], norm_smooth_meteor_ampl[not_echo], ".r", label="Not echo"
        )
        plt.plot(
            times[index_t0],
            norm_smooth_meteor_ampl[index_t0],
            "*",
            markersize=14,
            label=r"$t_{0}$",
        )
        plt.plot(
            times[index_ref_max_ampl],
            norm_smooth_meteor_ampl[index_ref_max_ampl],
            "d",
            markersize=14,
            label="Ref max",
        )
        plt.grid(True)
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude [-]")
        plt.legend(loc="best")
        plt.title(f"Amplitude curve - SNR = {np.round(SNR)}")
        plt.tight_layout()
        plt.show()

    if (
        SNR < Config.get(__name__, "min_snr")
        or central_fresnel_duration
        < Config.get(__name__, "min_central_fresnel_duration")
        or central_fresnel_duration
        > Config.get(__name__, "max_central_fresnel_duration")
        or rise_duration < Config.get(__name__, "min_rise_duration")
        or rise_duration > Config.get(__name__, "max_rise_duration")
    ):
        logger.info("No meteor detected")

        return None

    return index_t0, SNR, central_fresnel_duration


def compute_t0_uncertainty(SNR, central_fresnel_duration, samplerate, file_type):
    """
    Estimate the uncertainty of the t0 (start time) measurement based on SNR and Fresnel duration.

    This function loads precomputed uncertainty data and interpolates to estimate the timing 
    uncertainty of the t0 detection based on the measured SNR and central Fresnel duration.

    Parameters
    ----------
    SNR : float
        Signal-to-noise ratio of the meteor echo in dB.
    central_fresnel_duration : float
        Duration of the central Fresnel zone in seconds.
    samplerate : float
        Sampling rate of the signal in Hz.
    file_type : str
        Type of data file (e.g., "ICOM", "AR", or others) to determine the correct reference dataset.

    Returns
    -------
    float
        Estimated uncertainty (standard deviation) of the t0 value in seconds.
    """

    t0_uncertainty_file = (
        "snr_rise_time_db_fine_10000_5512.json"
        if file_type == "ICOM" or file_type == "AR"
        else "snr_rise_time_db_fine_10000_6048.json"
    )

    (
        SNR_db,
        central_fresnel_duration_db,
        bias_t0_db,
        sigma_t0_db,
        skew_t0_db,
        kurtosis_t0_db,
    ) = query_all_data(t0_uncertainty_file)
    sigma_t0_db /= samplerate

    inbound_indices = np.where(
        (SNR >= Config.get(__name__, "min_snr"))
        & (
            central_fresnel_duration_db
            >= Config.get(__name__, "min_central_fresnel_duration")
        )
        & (
            central_fresnel_duration_db
            <= Config.get(__name__, "max_central_fresnel_duration")
        )
    )[0]
    SNR_inbound = SNR_db[inbound_indices]
    central_fresnel_duration_inbound = central_fresnel_duration_db[inbound_indices]
    sigma_t0_inbound = sigma_t0_db[inbound_indices]

    uncertainty_interpolator = LinearNDInterpolator(
        list(zip(SNR_inbound, central_fresnel_duration_inbound)),
        sigma_t0_inbound,
        fill_value=Config.get(__name__, "t0_fill_value"),
    )
    sigma_t0 = uncertainty_interpolator(SNR, central_fresnel_duration)

    return sigma_t0.item()


def query_all_data(filename: str):
    """
    Load and extract meteor signal statistics from a JSON data file.

    Parameters
    ----------
    filename : str
        Name of the JSON file containing the SNR and rise time data.

    Returns
    -------
    tuple of np.ndarray
        snr : array of signal-to-noise ratio values.
        central_fresnel_duration : array of rise time values (central Fresnel durations).
        bias_t0 : array of bias values for the time zero estimation.
        sigma_t0 : array of standard deviations for the time zero estimation.
        skew_t0 : array of skewness values for the time zero distribution.
        kurtosis_t0 : array of kurtosis values for the time zero distribution.
    """

    data = Data.load(__name__, filename)
    snr_rise_time_data = data["snr_rise_time"]

    snr = np.array([entry["SNR"] for entry in snr_rise_time_data])
    central_fresnel_duration = np.array(
        [entry["rise_time"] for entry in snr_rise_time_data]
    )
    bias_t0 = np.array([entry["bias_t0"] for entry in snr_rise_time_data])
    sigma_t0 = np.array([entry["sigma_t0"] for entry in snr_rise_time_data])
    skew_t0 = np.array([entry["skew_t0"] for entry in snr_rise_time_data])
    kurtosis_t0 = np.array([entry["kurtosis_t0"] for entry in snr_rise_time_data])

    return snr, central_fresnel_duration, bias_t0, sigma_t0, skew_t0, kurtosis_t0


def detrend_doppler_shift(i_filt_meteor, q_filt_meteor, frequency, shifted_times):
    """
    Detrend the Doppler shift phase of a meteor echo signal.

    This function unwraps the meteor phase computed from I/Q components,
    removes a linear trend corresponding to a fixed frequency, and
    smooths the corrected phase using Savitzky-Golay filtering.

    Parameters
    ----------
    i_filt_meteor : np.ndarray
        In-phase filtered meteor signal.
    q_filt_meteor : np.ndarray
        Quadrature filtered meteor signal.
    frequency : float
        Frequency used to remove linear phase trend.
    shifted_times : np.ndarray
        Time array aligned with the meteor signal.

    Returns
    -------
    np.ndarray
        Smoothed, detrended meteor phase in radians.
    """

    meteor_phase = np.arctan2(q_filt_meteor, i_filt_meteor)
    meteor_phase_unwrapped = np.unwrap(meteor_phase)

    corrected_meteor_phase = meteor_phase_unwrapped - (
        2 * np.pi * frequency * shifted_times
    )
    corrected_meteor_phase = apply_sg_smoothing(
        corrected_meteor_phase, Config.get(__name__, "phase_sg_window"), sg_order
    )

    return corrected_meteor_phase


def compute_pre_t0_speed(
    meteor_ampl,
    corrected_meteor_phase,
    index_t0,
    samplerate: float,
    times: Optional[NDArray] = None,
    plot: bool = False,
):
    """
    Estimate the pre-t0 speed of a meteor echo using phase and amplitude analysis.

    The function identifies key phase points around the meteor event, aligns the phase
    curve with Fresnel integrals, detects 'knee' and 'elbow' points in phase progression,
    and performs correlation analyses to estimate a pseudo speed before the time zero (t0).
    Optional plotting provides visual diagnostics of intermediate steps.

    Parameters
    ----------
    meteor_ampl : np.ndarray
        Amplitude array of the meteor signal.
    corrected_meteor_phase : np.ndarray
        Phase array of the meteor signal after detrending.
    index_t0 : int
        Index of the specular point t0 based on amplitude.
    samplerate : float
        Sampling rate of the meteor signal in Hz.
    times : Optional[np.ndarray], optional
        Time array corresponding to the meteor data. If None, it is generated.
    plot : bool, optional
        Whether to display diagnostic plots. Default is False.

    Returns
    -------
    tuple or None
        Returns a tuple of
        (index_t0_pre_t0, v_pseudo_pre_t0, r_value_pre_t0, sigma_pre_t0), where:
            - index_t0_pre_t0 (int): Estimated pre-t0 time index.
            - v_pseudo_pre_t0 (float): Estimated pseudo speed before t0.
            - r_value_pre_t0 (float): Correlation coefficient for pre-t0 speed estimation.
            - sigma_pre_t0 (float): Estimated uncertainty (standard deviation) of pre-t0 speed.
        Returns None if estimation fails or insufficient data.
    """

    if times is None:
        times = np.linspace(
            0, len(corrected_meteor_phase) / samplerate, len(corrected_meteor_phase)
        )

    index_global_max_ampl = np.argmax(meteor_ampl)

    indices_min_phase, _ = find_peaks(
        -corrected_meteor_phase, prominence=Config.get(__name__, "prominence_phase")
    )
    index_min_phase = find_closest_smaller(indices_min_phase, index_t0)

    if index_t0 > index_global_max_ampl:
        return None

    index_max_phase = index_t0 + np.argmax(
        corrected_meteor_phase[index_t0 : index_global_max_ampl + 1]
    )

    shifted_meteor_phase = corrected_meteor_phase - (
        corrected_meteor_phase[index_max_phase]
        - Config.get(__name__, "max_phase_value")
    )

    index_t0_pre_t0 = index_max_phase

    if plot:
        plt.figure()
        plt.plot(times, shifted_meteor_phase)
        plt.title("Phase curve")
        plt.xlabel("Time [s]")
        plt.ylabel("Phase [rad]")
        plt.grid()
        plt.show()

    while shifted_meteor_phase[index_t0_pre_t0] > -np.pi / 4:
        index_t0_pre_t0 = index_t0_pre_t0 - 1

        if index_t0_pre_t0 <= 0:
            return None

    if abs(shifted_meteor_phase[index_t0_pre_t0] + np.pi / 4) > abs(
        shifted_meteor_phase[index_t0_pre_t0] + np.pi / 4
    ):
        index_t0_pre_t0 = index_t0_pre_t0 + 1

    if index_t0_pre_t0 <= index_min_phase:
        logger.info("Index t0 from pre-t0 algorithm < Index min phase")
        return None

    cropped_meteor_phase = shifted_meteor_phase[index_min_phase : index_max_phase + 1]

    fresnel_parameters_to_max_phase = np.linspace(
        Config.get(__name__, "min_fresnel_parameter"),
        Config.get(__name__, "fresnel_parameter_at_max_phase"),
        Config.get(__name__, "number_fresnel_parameters"),
    )

    fresnel_reference_point = -0.5 - 0.5j

    fresnel_sine, fresnel_cosine = fresnel(fresnel_parameters_to_max_phase)
    fresnel_integral = fresnel_cosine + 1j * fresnel_sine
    fresnel_phase = np.unwrap(np.angle(fresnel_integral - fresnel_reference_point))
    fresnel_phase = -fresnel_phase

    index_max_fresnel_phase = np.argmax(fresnel_phase)
    fresnel_phase = fresnel_phase - (
        fresnel_phase[index_max_fresnel_phase] - Config.get(__name__, "max_phase_value")
    )

    cropped_fresnel_parameters = interp1d(
        fresnel_phase,
        fresnel_parameters_to_max_phase,
        kind="linear",
        fill_value="extrapolate",
    )(cropped_meteor_phase)

    index_knee_local = find_knee(cropped_fresnel_parameters)
    index_knee = index_knee_local + index_min_phase

    index_elbow_local = find_elbow(
        times[index_min_phase : index_max_phase + 1], cropped_fresnel_parameters
    )
    index_elbow = index_elbow_local + index_min_phase

    if plot:
        plt.figure()
        plt.title("Cropped phase ")
        plt.plot(
            times[index_min_phase : index_global_max_ampl + 1],
            shifted_meteor_phase[index_min_phase : index_global_max_ampl + 1],
        )
        plt.plot(
            times[index_max_phase],
            shifted_meteor_phase[index_max_phase],
            "s",
            color="orange",
            markersize=8,
            linewidth=2,
            label="Max phase",
        )
        plt.plot(
            times[index_global_max_ampl],
            shifted_meteor_phase[index_global_max_ampl],
            "+r",
            markersize=14,
            linewidth=2,
            label="Max amplitude",
        )
        plt.plot(
            times[index_t0],
            shifted_meteor_phase[index_t0],
            "d",
            color="#7E2F8E",
            markersize=10,
            linewidth=2,
            label=r"Specular point t$_0$ from amplitude",
        )
        plt.plot(
            times[index_t0_pre_t0],
            shifted_meteor_phase[index_t0_pre_t0],
            "*",
            markersize=12,
            label=r"t$_0$ guess from Mazur et al. (2020)",
        )
        plt.plot(
            times[index_knee],
            shifted_meteor_phase[index_knee],
            "xg",
            markersize=12,
            label="Knee",
        )
        plt.plot(
            times[index_elbow],
            shifted_meteor_phase[index_elbow],
            "or",
            markersize=12,
            label="Elbow",
        )
        plt.ylabel("Phase [rad]")
        plt.xlabel("Time [s]")
        plt.grid(True)
        plt.legend()
        plt.show()

    if plot:
        norm_meteor_ampl = meteor_ampl / np.max(meteor_ampl)

        fig, ax = plt.subplots()
        twin = ax.twinx()
        plt.title("Phase and amplitude around pre-t0 specular point")
        plt.xlabel("Time [s]")
        plt.grid(True)
        (p1,) = ax.plot(
            times[index_t0_pre_t0 - 2000 : index_t0_pre_t0 + 2000],
            corrected_meteor_phase[index_t0_pre_t0 - 2000 : index_t0_pre_t0 + 2000],
            label="Phase",
            color="red",
        )
        ax.set_ylabel("Phase [rad]")
        (p2,) = twin.plot(
            times[index_t0_pre_t0 - 2000 : index_t0_pre_t0 + 2000],
            norm_meteor_ampl[index_t0_pre_t0 - 2000 : index_t0_pre_t0 + 2000],
            label="Amplitude",
            color="blue",
        )
        twin.set_ylabel("Amplitude [-]")
        plt.legend(handles=[p1, p2])
        plt.grid(True)
        plt.show()

    offsets_min_phase = np.arange(
        -round(Config.get(__name__, "guess_duration_min_phase") * samplerate),
        round(Config.get(__name__, "guess_duration_min_phase") * samplerate) + 1,
        1,
    )
    v_pseudo_pre_t0s = np.zeros((len(offsets_min_phase),))
    r_value_pre_t0s = np.zeros((len(offsets_min_phase),))
    indices_t0_pre_t0 = np.zeros((len(offsets_min_phase),), dtype=np.int32)

    for i in range(len(offsets_min_phase)):
        offset_min_phase = offsets_min_phase[i]

        try:
            (
                r_value_pre_t0s[i],
                v_pseudo_pre_t0s[i],
                indices_t0_pre_t0[i],
            ) = get_pre_t0_speed_correlation(
                index_knee,
                index_min_phase + offset_min_phase,
                shifted_meteor_phase,
                times,
                fresnel_phase,
                fresnel_parameters_to_max_phase,
                samplerate,
                plot=False,
            )

        except:
            continue

    if not r_value_pre_t0s.size:
        logger.info("No good r value for pre-t0")
        return

    logger.info(f"Max r value for pre-t0 = {np.round(max(r_value_pre_t0s),5)}")

    if max(r_value_pre_t0s) < Config.get(__name__, "min_r_value_pre_t0"):
        logger.info("Too small pre-t0 correlation")
        return

    r_value_pre_t0, best_r_value_pre_t0_index = (
        np.max(r_value_pre_t0s),
        np.argmax(r_value_pre_t0s),
    )
    v_pseudo_pre_t0 = v_pseudo_pre_t0s[best_r_value_pre_t0_index]
    best_index_t0_pre_t0 = indices_t0_pre_t0[best_r_value_pre_t0_index]

    if plot:
        plt.figure()
        plt.plot(
            times[index_min_phase : index_max_phase + 1], cropped_fresnel_parameters
        )
        plt.plot(
            times[index_t0],
            cropped_fresnel_parameters[index_t0 - index_min_phase],
            "d",
            color="#7E2F8E",
            markersize=10,
            linewidth=2,
            label=r"Specular point t$_0$ from amplitude",
        )
        plt.plot(
            times[index_t0_pre_t0],
            cropped_fresnel_parameters[index_t0_pre_t0 - index_min_phase],
            "*",
            markersize=12,
            label=r"t$_0$ guess from Mazur et al. (2020)",
        )
        plt.plot(
            times[index_knee],
            cropped_fresnel_parameters[index_knee_local],
            "xg",
            markersize=12,
            label="Knee",
        )
        # plt.plot(times[best_index_t0_pre_t0], cropped_fresnel_parameters[best_index_t0_pre_t0-index_min_phase], 'og', markersize=12, label = r"Optimal t$_0$")
        plt.ylabel("Fresnel parameter [-]")
        plt.xlabel("Time [s]")
        plt.grid(True)
        plt.legend()
        plt.title(r"t$_0$ identification")
        plt.tight_layout()
        plt.show()

    best_index_min_phase = (
        index_min_phase + offsets_min_phase[best_r_value_pre_t0_index]
    )

    if plot:
        plt.figure()
        plt.title(f"Phase curve")
        plt.plot(
            times[best_index_min_phase:best_index_t0_pre_t0],
            shifted_meteor_phase[best_index_min_phase:best_index_t0_pre_t0],
        )
        plt.ylabel("Phase [rad]")
        plt.xlabel("Time [s]")
        plt.grid(True)
        plt.show()

    _, _, _ = get_pre_t0_speed_correlation(
        best_index_t0_pre_t0,
        best_index_min_phase,
        shifted_meteor_phase,
        times,
        fresnel_phase,
        fresnel_parameters_to_max_phase,
        samplerate,
        plot=plot,
    )

    (
        v_pseudo_pre_t0_pssst,
        std_v_pseudo_pre_t0_pssst,
        median_r_value_pre_t0_pssst,
        fwhm_pre_t0_pssst,
        index_t0_pre_t0_pssst,
    ) = check_pre_t0_speed_histograms_pssst(
        [best_index_min_phase],
        [best_index_t0_pre_t0],
        shifted_meteor_phase,
        times,
        fresnel_phase,
        fresnel_parameters_to_max_phase,
        plot=plot,
    )
    sigma_pre_t0 = fwhm_pre_t0_pssst / (2 * np.sqrt(2 * np.log(2)))

    logger.info(f"V pseudo pre-t0 = {np.round(v_pseudo_pre_t0,2)} s⁻¹")
    logger.info(f"Sigma pre-t0 = {np.round(sigma_pre_t0,2)} s⁻¹")

    index_t0_pre_t0 = best_index_t0_pre_t0

    return index_t0_pre_t0, v_pseudo_pre_t0, r_value_pre_t0, sigma_pre_t0


def get_pre_t0_speed_correlation(
    index_t0,
    index_min_phase,
    shifted_meteor_phase,
    times,
    fresnel_phase,
    fresnel_parameters_to_max_phase,
    samplerate,
    plot: bool = False,
):
    """
    Estimate the pseudo speed before time t0 by fitting a linear model to the Fresnel parameter
    as a function of time over a range of candidate t0 indices.

    The function searches over a range around the provided `index_t0` to find the segment that
    maximizes the linear correlation (r-value) between time and Fresnel parameter distance.
    Optionally plots the best linear fit.

    Parameters
    ----------
    index_t0 : int
        The primary index corresponding to time t0 in the time series.
    index_min_phase : int
        The start index of the phase segment to consider.
    shifted_meteor_phase : np.ndarray
        The meteor phase data, shifted and unwrapped, from which a segment is selected.
    times : np.ndarray
        The array of time stamps corresponding to the phases.
    fresnel_phase : np.ndarray
        Array of Fresnel phases used as the independent variable for interpolation.
    fresnel_parameters_to_max_phase : np.ndarray
        Fresnel parameters mapped to their max phases, used to interpolate Fresnel distances.
    samplerate : float
        Sampling rate of the time series data in Hz.
    plot : bool, optional
        If True, plots the best linear fit and corresponding Fresnel parameter distances (default False).

    Returns
    -------
    best_r_value_pre_t0 : float
        The highest correlation coefficient (r-value) found for the pre-t0 linear fit.
    best_v_pseudo_pre_t0 : float
        The pseudo speed (slope) corresponding to the best linear fit.
    best_index_t0_pre_t0 : int
        The index corresponding to the best pre-t0 time segment.

    """

    v_pseudo_pre_t0s = np.array([])
    r_value_pre_t0s = np.array([])
    indices_t0_pre_t0 = np.array([], dtype=np.int32)

    guess_duration_t0 = Config.get(__name__, "guess_duration_t0")

    index_t0_pre_t0_guesses = np.arange(
        index_t0 - round(guess_duration_t0 * samplerate),
        index_t0 + round(guess_duration_t0 * samplerate) + 1,
        1,
    )

    if plot:
        index_t0_pre_t0_guesses = np.array([index_t0])

    for index_t0_pre_t0_guess in index_t0_pre_t0_guesses:
        if index_t0_pre_t0_guess - index_min_phase + 1 < Config.get(
            __name__, "min_length_sliding_slope"
        ):
            continue

        sliding_slope_times = times[index_min_phase : index_t0_pre_t0_guess + 1]

        sliding_slope_meteor_phase = shifted_meteor_phase[
            index_min_phase : index_t0_pre_t0_guess + 1
        ]
        sliding_slope_meteor_phase = (
            sliding_slope_meteor_phase - sliding_slope_meteor_phase[-1] - np.pi / 4
        )

        if np.min(sliding_slope_meteor_phase) > Config.get(__name__, "min_phase_value"):
            continue

        try:
            sliding_slope_fresnel_parameters = interp1d(
                fresnel_phase,
                fresnel_parameters_to_max_phase,
                kind="linear",
                fill_value="extrapolate",
            )(sliding_slope_meteor_phase)
        except:
            continue

        sliding_slope_fresnel_distance = sliding_slope_fresnel_parameters

        speed, intercept, r_value_pre_t0, _, _ = stats.linregress(
            sliding_slope_times, sliding_slope_fresnel_distance
        )

        v_pseudo_pre_t0s = np.append(v_pseudo_pre_t0s, speed)
        r_value_pre_t0s = np.append(r_value_pre_t0s, r_value_pre_t0)
        indices_t0_pre_t0 = np.append(indices_t0_pre_t0, index_t0_pre_t0_guess)

    best_r_value_pre_t0, best_r_value_pre_t0_index = (
        np.max(r_value_pre_t0s),
        np.argmax(r_value_pre_t0s),
    )
    best_v_pseudo_pre_t0 = v_pseudo_pre_t0s[best_r_value_pre_t0_index]
    best_index_t0_pre_t0 = indices_t0_pre_t0[best_r_value_pre_t0_index]

    if plot:
        plt.figure()
        plt.plot(sliding_slope_times, sliding_slope_fresnel_distance, label="Distances")
        plt.plot(
            sliding_slope_times,
            speed * sliding_slope_times + intercept,
            label="Linear fit - r = " + str(np.round(r_value_pre_t0, 5)),
        )
        plt.xlabel("Time [s]")
        plt.ylabel(r"Fresnel parameter [-]")
        plt.title(
            r"Distance as a function of time - Pre-$t_0$ pseudo speed = "
            + str(np.round(speed, 3))
            + r" s$^{-1}$"
        )
        plt.grid(True)
        plt.legend()
        plt.show()

    return best_r_value_pre_t0, best_v_pseudo_pre_t0, best_index_t0_pre_t0


def check_pre_t0_speed_histograms_pssst(
    indices_start_phase,
    indices_t0_pre_t0,
    shifted_meteor_phase,
    times,
    fresnel_phase,
    fresnel_parameters_to_max_phase,
    plot: bool = False,
):
    """
    Analyze pseudo speeds before t0 using a sliding window approach and compute statistics
    based on speed histograms derived from many linear fits to Fresnel parameters.

    This function performs multiple linear regressions on sub-windows of meteor phase data,
    aggregates pseudo speeds that meet a minimum correlation threshold, then estimates
    uncertainty and peak values of these speeds using kernel density estimation.
    Optionally plots histograms with KDE overlay.

    Parameters
    ----------
    indices_start_phase : np.ndarray
        Array of start indices defining the beginning of phase segments.
    indices_t0_pre_t0 : np.ndarray
        Array of indices corresponding to estimated t0 times prior to main t0.
    shifted_meteor_phase : np.ndarray
        Meteor phase data, shifted and unwrapped.
    times : np.ndarray
        Time stamps corresponding to the meteor phase data.
    fresnel_phase : np.ndarray
        Array of Fresnel phases used for interpolation.
    fresnel_parameters_to_max_phase : np.ndarray
        Fresnel parameters mapped to max phases, used for interpolation.
    plot : bool, optional
        If True, plots the speed histograms with kernel density estimates (default False).

    Returns
    -------
    final_v_pseudo_pre_t0 : float
        The best estimate of the pseudo speed before t0, based on histogram peak and minimal uncertainty.
    final_std_v_pseudo_pre_t0 : float
        The standard deviation of the pseudo speed distribution for uncertainty estimation.
    final_median_r_value_pre_t0 : float
        The median correlation coefficient for accepted linear fits.
    final_fwhm_pre_t0 : float
        Full width at half maximum (FWHM) of the kernel density estimate, representing speed distribution spread.
    final_index_t0_pre_t0 : int
        The index corresponding to the best pre-t0 segment chosen based on minimal speed uncertainty.

    """
     
    best_v_pseudo_pre_t0s = np.array([])
    std_v_pseudo_pre_t0s = np.array([])
    median_r_value_pre_t0s = np.array([])
    fwhm_pre_t0s = np.array([])

    for i in range(len(indices_start_phase)):
        index_start_phase = indices_start_phase[i]
        index_t0_pre_t0 = indices_t0_pre_t0[i]

        if index_t0_pre_t0 - index_start_phase + 1 < Config.get(
            __name__, "min_length_sliding_slope"
        ):
            continue

        sliding_slope_meteor_phase = shifted_meteor_phase[
            index_start_phase : index_t0_pre_t0 + 1
        ]
        sliding_slope_meteor_phase = (
            sliding_slope_meteor_phase - sliding_slope_meteor_phase[-1] - np.pi / 4
        )

        sliding_slope_times = times[index_start_phase : index_t0_pre_t0 + 1]

        if np.min(sliding_slope_meteor_phase) > Config.get(__name__, "min_phase_value"):
            continue

        try:
            sliding_slope_fresnel_parameters = interp1d(
                fresnel_phase,
                fresnel_parameters_to_max_phase,
                kind="linear",
                fill_value="extrapolate",
            )(sliding_slope_meteor_phase)
        except:
            continue

        sliding_slope_fresnel_distance = sliding_slope_fresnel_parameters

        max_window_length = len(sliding_slope_meteor_phase)
        min_window_length = Config.get(__name__, "min_length_pssst_uncertainty")

        window_lengths = np.arange(min_window_length, max_window_length + 1)

        # Preallocate lists instead of using np.append()
        v_pseudo_pre_t0_histogram_list = []
        r_value_pre_t0s_list = []

        linregress_func = stats.linregress  # Store function reference for faster lookup

        for window_length in window_lengths:
            max_start = max_window_length - window_length + 1

            for window_start in range(max_start):
                # Use NumPy slicing
                window_fresnel_distance = sliding_slope_fresnel_distance[
                    window_start : window_start + window_length
                ]
                window_times = sliding_slope_times[
                    window_start : window_start + window_length
                ]

                window_speed, _, window_r_value_pre_t0, _, _ = linregress_func(
                    window_times, window_fresnel_distance
                )

                if window_r_value_pre_t0 > Config.get(__name__, "min_r_value_pre_t0"):
                    v_pseudo_pre_t0_histogram_list.append(window_speed)
                    r_value_pre_t0s_list.append(window_r_value_pre_t0)

        # Convert lists to NumPy arrays after the loop
        v_pseudo_pre_t0_histogram = np.array(v_pseudo_pre_t0_histogram_list)
        r_value_pre_t0s = np.array(r_value_pre_t0s_list)

        if len(v_pseudo_pre_t0_histogram) >= Config.get(__name__, "min_size_histogram"):
            # kde = stats.gaussian_kde(v_pseudo_pre_t0_histogram, bw_method='scott', weights=None)
            # kde_speeds = np.linspace(np.min(v_pseudo_pre_t0_histogram), np.max(v_pseudo_pre_t0_histogram), 10000)
            # kde_speed_density = kde(kde_speeds)

            kde_speeds, kde_speed_density = (
                FFTKDE(kernel="gaussian", bw="scott")
                .fit(v_pseudo_pre_t0_histogram)
                .evaluate()
            )

            max_value = max(kde_speed_density)
            half_max = max_value / 2

            indices = np.where(np.diff(np.sign(kde_speed_density - half_max)))[0]

            if len(indices) >= 2:
                x1, x2 = kde_speeds[indices[0]], kde_speeds[indices[1]]
                fwhm = x2 - x1
            else:
                logger.warning("Unable to calculate FWHM. Check data or KDE bandwidth.")
                continue

            peak_speeds_index = np.argmax(kde_speed_density)
            peak_speed = kde_speeds[peak_speeds_index]

            best_v_pseudo_pre_t0s = np.append(best_v_pseudo_pre_t0s, peak_speed)
            std_v_pseudo_pre_t0s = np.append(
                std_v_pseudo_pre_t0s, np.std(v_pseudo_pre_t0_histogram)
            )
            median_r_value_pre_t0s = np.append(
                median_r_value_pre_t0s, np.median(r_value_pre_t0s)
            )
            fwhm_pre_t0s = np.append(fwhm_pre_t0s, fwhm)

        if plot:
            plt.figure()
            plt.hist(
                v_pseudo_pre_t0_histogram,
                bins=500,
                density=True,
                label="Speed histogram",
            )
            plt.plot(kde_speeds, kde_speed_density, label="Kernel density estimation")
            # plt.axvline(x=81.66, color='g', linestyle='--', linewidth = 3, label = r"Speed of linear fit")
            plt.ylabel("Density [-]")
            plt.xlabel(r"Pseudo speed [s$^{-1}$]")
            plt.title(r"Uncertainty determination of pre-$t_0$ pseudo speed")
            plt.legend()
            plt.grid(True)
            plt.show()

    final_std_v_pseudo_pre_t0, index_min_std_v_pseudo_pre_t0s = (
        np.min(std_v_pseudo_pre_t0s),
        np.argmin(std_v_pseudo_pre_t0s),
    )
    final_v_pseudo_pre_t0 = best_v_pseudo_pre_t0s[index_min_std_v_pseudo_pre_t0s]
    final_median_r_value_pre_t0 = median_r_value_pre_t0s[index_min_std_v_pseudo_pre_t0s]
    final_fwhm_pre_t0 = fwhm_pre_t0s[index_min_std_v_pseudo_pre_t0s]
    final_index_t0_pre_t0 = indices_t0_pre_t0[index_min_std_v_pseudo_pre_t0s]

    return (
        final_v_pseudo_pre_t0,
        final_std_v_pseudo_pre_t0,
        final_median_r_value_pre_t0,
        final_fwhm_pre_t0,
        final_index_t0_pre_t0,
    )


def filter_signal(
    signal,
    samplerate,
    beacon_frequency,
    filtering_half_range_frequency=filtering_half_range_frequency,
    filtering_length_kernel=filtering_length_kernel,
):
    """
    Apply a bandpass filter to isolate a frequency range around a beacon frequency in the input signal.

    The function computes the FFT of the input signal, identifies the strongest frequency component
    near the beacon frequency, and applies a Blackman window filter centered around that frequency.

    Parameters
    ----------
    signal : np.ndarray
        Input time-domain signal to be filtered.
    samplerate : float
        Sampling rate of the signal in Hz.
    beacon_frequency : float
        Central frequency of the beacon in Hz to filter around.
    filtering_half_range_frequency : float, optional
        Half-width of the frequency band around the detected signal frequency for filtering (default from global config).
    filtering_length_kernel : int, optional
        Length of the Blackman filter kernel to apply (default from global config).

    Returns
    -------
    filt_signal : np.ndarray
        Filtered time-domain signal after bandpass filtering.
    signal_frequency : float
        Frequency in Hz of the strongest component near the beacon frequency detected in the signal.
    """

    identification_half_range_frequency = Config.get(
        __name__, "identification_half_range_frequency"
    )

    real_fft_signal = np.fft.rfft(signal, len(signal)) / len(signal)
    real_fft_signal_freq = np.fft.rfftfreq(len(signal), d=1 / samplerate)

    indices_signal_range = np.argwhere(
        (real_fft_signal_freq >= beacon_frequency - identification_half_range_frequency)
        & (
            real_fft_signal_freq
            <= beacon_frequency + identification_half_range_frequency
        )
    )

    real_fft_signal = real_fft_signal[indices_signal_range]
    real_fft_signal_freq = real_fft_signal_freq[indices_signal_range]
    signal_index = np.argmax(abs(real_fft_signal))

    signal_frequency = real_fft_signal_freq[signal_index][0]

    signal_fc_low = (signal_frequency + filtering_half_range_frequency) / samplerate
    signal_fc_high = (signal_frequency - filtering_half_range_frequency) / samplerate

    filt_signal = apply_blackman_filter(
        signal, signal_fc_low, signal_fc_high, filtering_length_kernel
    )

    return filt_signal, signal_frequency


def apply_blackman_filter(signal, fc_low, fc_high, N):
    """
    Apply a bandpass Blackman filter to the input signal.

    The filter is constructed by convolving a low-pass and a high-pass Blackman windowed sinc filter,
    effectively passing frequencies between `fc_low` and `fc_high`. The filtered signal is obtained
    using zero-phase filtering with `filtfilt` to avoid phase distortion.

    Parameters
    ----------
    signal : np.ndarray
        Input 1D time-domain signal to be filtered.
    fc_low : float
        Normalized cutoff frequency (0 to 0.5) for the low-pass filter edge.
    fc_high : float
        Normalized cutoff frequency (0 to 0.5) for the high-pass filter edge.
    N : int
        Length of the filter kernel (number of taps). Will be incremented to next odd if even.

    Returns
    -------
    filt_signal_blackman : np.ndarray
        Filtered signal after applying the bandpass Blackman filter.
    """

    if N % 2 == 0:
        N = N + 1

    n = np.arange(N)

    # Low-pass Blackman filter
    low_blackman_filter = np.sinc(2 * fc_low * (n - (N - 1) / 2.0)) * blackman(N)
    low_blackman_filter = low_blackman_filter / np.sum(low_blackman_filter)

    # High-pass Blackman filter
    high_blackman_filter = np.sinc(2 * fc_high * (n - (N - 1) / 2.0)) * blackman(N)
    high_blackman_filter = high_blackman_filter / np.sum(high_blackman_filter)
    high_blackman_filter = -high_blackman_filter  # Convert to high-pass
    high_blackman_filter[int(np.floor(N / 2))] = (
        high_blackman_filter[int(np.floor(N / 2))] + 1
    )

    # Convolution between high-pass and low-pass filters
    blackman_filter = np.convolve(low_blackman_filter, high_blackman_filter)

    b = blackman_filter
    a = np.array([1.0])

    filt_signal_blackman = filtfilt(b, a, signal, axis=0, padtype="odd")

    return filt_signal_blackman


def apply_sg_smoothing(array, window, order, deriv=0, mode="mirror"):
    if window > order:
        return savgol_filter(array, window, order, deriv=deriv, mode=mode)

    return array


def extrapolate_time(sample, timestamps, sample_numbers, fs):
    """
    Estimate the continuous time corresponding to a given sample index.

    Given an array of discrete sample indices and their associated timestamps,
    this function finds the nearest known sample to the target sample, then linearly
    extrapolates the exact time for the target sample based on the sampling frequency.

    Parameters
    ----------
    sample : int or float
        The sample index for which to find the corresponding time.
    timestamps : np.ndarray
        Array of timestamps corresponding to discrete samples.
    sample_numbers : np.ndarray
        Array of sample indices corresponding to `timestamps`.
    fs : float
        Sampling frequency in Hz.

    Returns
    -------
    float
        Estimated time (in seconds) corresponding to the input sample index.
    """

    index = find_nearest(sample_numbers, sample)
    closest_timestamp = timestamps[index]
    time = closest_timestamp + (sample - sample_numbers[index]) / fs
    return time


def find_closest_smaller(arr, value):
    limit = float("-inf")
    closest = 0
    for num in arr:
        if num < value and num > limit:
            closest = num
    return closest


def find_nearest(array, value):
    return (np.abs(array - value)).argmin()


def find_elbow(x, y):
    """
    Identify the 'elbow' point in a curve defined by x and y data points.

    The elbow is detected as the point of maximum curvature, calculated using
    numerical derivatives of the input data.

    Parameters
    ----------
    x : np.ndarray
        Array of x-coordinates.
    y : np.ndarray
        Array of y-coordinates.

    Returns
    -------
    int
        Index of the elbow point (maximum curvature) in the input arrays.
    """

    dx = np.gradient(x)
    dy = np.gradient(y)
    ddx = np.gradient(dx)
    ddy = np.gradient(dy)

    # Compute curvature
    curvature = np.abs(ddx * dy - ddy * dx) / (dx**2 + dy**2) ** (3 / 2)

    # Find index of max curvature (elbow)
    elbow_index = np.argmax(curvature)
    return elbow_index


def find_knee(signal):
    """
    Detect the 'knee' point in a signal, where the signal's behavior changes abruptly.

    This is done by partitioning the signal at each point and computing the sum
    of squared residuals from linear fits on both partitions. The index minimizing
    this sum is considered the knee.

    Parameters
    ----------
    signal : np.ndarray
        1D signal array.

    Returns
    -------
    int
        Index of the detected knee point in the signal.
    """

    residual = np.zeros(len(signal) - 2)
    for i in range(len(signal) - 2):
        signal1, signal2 = [signal[: i + 2], signal[i + 1 :]]
        sse1, sse2 = sum_squared_diff(signal1), sum_squared_diff(signal2)
        residual[i] = sse1 + sse2
    index_knee = np.argmin(residual) + 1
    return index_knee


def sum_squared_diff(signal):
    """
    Compute the sum of squared differences between a signal and its linear regression fit.

    Fits a straight line to the input signal and returns the total squared deviation.

    Parameters
    ----------
    signal : np.ndarray
        Input signal array.

    Returns
    -------
    float
        Sum of squared residuals of the linear fit.
    """
    
    x = np.arange(len(signal))
    y = signal
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]
    y_pred = m * x + c
    deviation = np.sum((y - y_pred) ** 2)
    return deviation
