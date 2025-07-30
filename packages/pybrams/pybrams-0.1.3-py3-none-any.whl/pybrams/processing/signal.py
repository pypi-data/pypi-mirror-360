from typing import Dict, Any, Union, Optional
import copy
import numpy as np

from .pps import PPS
from .series import Series
from pybrams.brams.system import System
from pybrams.utils import Config, Plot


class Signal:
    """
    Represents a full signal acquisition containing time-domain data,
    timestamp synchronization (PPS), and associated metadata.

    Provides methods for preprocessing, spectral analysis, and plotting.

    Attributes
    ----------
    series : Series
        The raw time-series data.
    pps : PPS
        Pulse-per-second timestamps used for synchronization.
    samplerate : float
        Sampling rate in Hz.
    system : System
        Hardware or software system descriptor.
    type : str
        Type of signal, default inferred from sampling rate.
    beacon_frequency : Optional[float]
        Estimated beacon frequency from FFT.
    _cleaned_series : Optional[Series]
        Interference-removed version of the time-series.
    _corrected_pps : Optional[PPS]
        Time-corrected PPS timestamps.
    """

    def __init__(
        self,
        series: Series,
        pps: PPS,
        samplerate: float,
        system: System,
        type: Union[str, None] = None,
        properties: Optional[dict[str, Any]] = {},
    ):
        """
        Initialize a Signal object.

        Parameters
        ----------
        series : Series
            Time-domain signal.
        pps : PPS
            PPS synchronization timestamps.
        samplerate : float
            Sampling frequency.
        system : System
            System metadata or configuration.
        type : str or None, optional
            Type of signal (e.g., 'RSP2'), inferred from samplerate if not provided.
        properties : dict, optional
            Optional metadata (e.g., beacon frequency).
        """

        self.series: Series = series
        self.pps: PPS = pps
        self.samplerate: float = samplerate
        self.system: System = system
        self.type: str = type if type else "RSP2" if self.samplerate == 6048 else str()
        self.beacon_frequency = (
            properties.get("beacon_frequency") if properties else None
        )
        self._cleaned_series: Optional[Series] = None
        self._corrected_pps: Optional[PPS] = None

    @property
    def cleaned_series(self):
        if self._cleaned_series is None:
            raise ValueError(
                "The signal needs to be cleaned before accessing the cleaned_series property"
            )
        return self._cleaned_series

    @property
    def corrected_pps(self):
        if self._corrected_pps is None:
            raise ValueError(
                "The PPS needs to be corrected before accessing the corrected_pps property"
            )
        return self._corrected_pps

    def process(self):
        """
        Perform processing pipeline:
        - Deepcopy and correct PPS
        - Compute beacon and calibrator frequencies
        """

        self._corrected_pps = copy.deepcopy(self.pps)
        self.corrected_pps.correct(self.type)
        self.compute_beacon_frequency()
        self.compute_calibrator_frequency()

    def json(self) -> Dict[str, Any]:
        return {
            "samplerate": self.samplerate,
            "beacon_frequency": self.beacon_frequency,
        }

    def __add__(self, other: object) -> "Signal":
        if not isinstance(other, Signal):
            raise TypeError(
                f"Unsupported operand type(s) for +: Signal and {type(other).__name__}"
            )
        if self.system != other.system:
            raise ValueError(
                "Adding Signal objects from different systems is not supported"
            )
        if self.type != other.type:
            raise ValueError(
                "Adding Signal objects with different types is not supported"
            )

        series = self.series + other.series
        pps = PPS(
            np.concatenate(
                (
                    self.pps.index,
                    np.array([i + self.series.data.size for i in other.pps.index]),
                )
            ),
            np.concatenate((self.pps.time, other.pps.time)),
        )
        samplerate = np.mean([self.samplerate, other.samplerate])
        signal = Signal(series, pps, float(samplerate), self.system, self.type)

        if self._corrected_pps:
            signal._corrected_pps = PPS(
                np.concatenate(
                    (
                        self.corrected_pps.index,
                        np.array(
                            [
                                i + self.series.data.size
                                for i in other.corrected_pps.index
                            ]
                        ),
                    )
                ),
                np.concatenate((self.corrected_pps.time, other.corrected_pps.time)),
            )

        if self.beacon_frequency and other.beacon_frequency:
            signal.beacon_frequency = np.mean(
                (self.beacon_frequency, other.beacon_frequency)
            )

        signal._cleaned_series = (
            self.cleaned_series + other.cleaned_series
            if self._cleaned_series and other._cleaned_series
            else None
        )
        return signal

    def __eq__(self, other):
        if isinstance(other, Signal):
            return all(
                (self.series == other.series, self.samplerate == other.samplerate)
            )

        return False

    def compute_beacon_frequency(self):
        """
        Estimate the beacon frequency using FFT and frequency bounds defined in config.
        """

        self.series.compute_fft(self.samplerate)
        indices_beacon_range = np.argwhere(
            (self.series.real_fft_freq >= Config.get(__name__, "beacon_min_frequency"))
            & (
                self.series.real_fft_freq
                <= Config.get(__name__, "beacon_max_frequency")
            )
        )

        reduced_real_fft = self.series.real_fft[indices_beacon_range]
        reduced_real_fft_freq = self.series.real_fft_freq[indices_beacon_range]
        beacon_index = np.argmax(abs(reduced_real_fft))
        self.beacon_frequency = reduced_real_fft_freq[beacon_index][0]

    def compute_calibrator_frequency(self):
        """
        Estimate the calibrator frequency using FFT and config-defined bounds.
        """

        self.series.compute_fft(self.samplerate)
        indices_calibrator_range = np.argwhere(
            (
                self.series.real_fft_freq
                >= Config.get(__name__, "calibrator_min_frequency")
            )
            & (
                self.series.real_fft_freq
                <= Config.get(__name__, "calibrator_max_frequency")
            )
        )

        reduced_real_fft = self.series.real_fft[indices_calibrator_range]
        reduced_real_fft_freq = self.series.real_fft_freq[indices_calibrator_range]
        calibrator_index = np.argmax(abs(reduced_real_fft))
        self.calibrator_frequency = reduced_real_fft_freq[calibrator_index][0]

    def clean(self):
        """
        Clean the signal by removing beacon, calibrator, and airplane interferences.
        Applies operations conditionally based on configuration.
        """

        from .airplane_removal import AirplaneRemoval
        from .beacon_removal import BeaconRemoval
        from .calibrator_removal import CalibratorRemoval

        self._cleaned_series = copy.deepcopy(self.series)

        beacon_removal = BeaconRemoval(self)
        beacon_removal.remove_interference()

        if Config.get(__name__, "calibrator_subtraction"):
            calibrator_removal = CalibratorRemoval(self)
            calibrator_removal.remove_interference()

        if Config.get(__name__, "airplane_subtraction"):
            airplane_removal = AirplaneRemoval(self)
            airplane_removal.remove_interference()

    def plot_raw_spectrogram(
        self,
        title="Raw spectrogram",
        central_frequency=None,
        half_range_spect=100,
        export=False,
        filename=None,
        subplot=False,
        frame=True,
    ):
        """
        Plot the raw spectrogram of the signal.

        Parameters
        ----------
        title : str
            Title of the plot.
        central_frequency : float or None
            Center frequency (defaults to beacon frequency).
        half_range_spect : float
            Frequency span to display around the center.
        export : bool
            Whether to export the plot.
        filename : str or None
            Export filename if `export=True`.
        subplot : bool
            Whether to use subplot style.
        frame : bool
            Whether to display the plot frame.
        """

        Plot.spectrogram(
            self.series,
            self.samplerate,
            central_frequency or self.beacon_frequency,
            title,
            half_range_spect,
            export,
            filename,
            subplot,
            frame,
        )

    def plot_cleaned_spectrogram(
        self,
        title="Clean spectrogram",
        central_frequency=None,
        half_range_spect=100,
        export=False,
        filename=None,
        subplot=False,
        frame=True,
    ):
        """
        Plot the spectrogram of the cleaned signal.
        """
        Plot.spectrogram(
            self.cleaned_series,
            self.samplerate,
            central_frequency or self.beacon_frequency,
            title,
            half_range_spect,
            export,
            filename,
            subplot,
            frame,
        )
