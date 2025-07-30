import copy
from typing import Optional
import autograd.numpy as np
from numpy.typing import NDArray
from .constants import SHORT_TO_FLOAT_FACTOR


class Series:
    """
    Represents a time-series signal with optional FFT capabilities.

    Supports conversion from integer data to float, slicing,
    FFT computation, and series concatenation.

    Attributes
    ----------
    data : NDArray[np.float64]
        The time-domain data of the series in float64 format.
    fft : Optional[NDArray[np.float64]]
        Full FFT result (complex values).
    real_fft_freq : Optional[NDArray[np.float64]]
        Frequencies corresponding to the real FFT.
    real_fft : Optional[NDArray[np.float64]]
        One-sided FFT (real-valued spectrum).
    """

    def __init__(self, data: NDArray[np.float64 | np.int16]):
        self.data: NDArray[np.float64] = (
            data
            if data.dtype == np.float64
            else (data / SHORT_TO_FLOAT_FACTOR).astype(np.float64)
        )
        self.fft: Optional[NDArray[np.float64]] = None
        self.real_fft_freq: Optional[NDArray[np.float64]] = None
        self.real_fft: Optional[NDArray[np.float64]] = None

    def compute_fft(self, samplerate: float):
        self.fft = np.fft.fft(self.data) / self.data.size
        self.real_fft_freq = np.fft.rfftfreq(self.data.size, d=1 / samplerate)
        self.real_fft = np.fft.rfft(self.data) / self.data.size

    def __getitem__(self, index):
        series = copy.deepcopy(self)
        if isinstance(index, slice):
            series.data = series.data[index.start : index.stop : index.step]
            self.fft = None
            self.real_fft = None
            self.real_fft_freq = None
        else:
            series.data = series.data[index]
        return series

    def __deepcopy__(self, memo):
        return Series(np.copy(self.data))

    def __str__(self):
        fft_status = "Computed" if self.fft is not None else "Not computed"
        return (
            f"Series(data={self.data[:2]} ... {self.data[int(self.data.size / 2)]} ... {self.data[-2:]} (size={self.data.size}), "
            f"FFT: {fft_status})"
        )

    def __add__(self, other: object) -> "Series":
        if not isinstance(other, Series):
            raise TypeError(
                f"Unsupported operand type(s) for +: Series and {type(other).__name__}"
            )
        if self.data.dtype != other.data.dtype:
            raise TypeError(
                f"Adding Series objects from different dtype is not supported : {type(self.data.dtype).__name__} and {type(other.data.dtype).__name__}"
            )

        series = Series(np.concatenate((self.data, other.data)))
        return series
