import autograd.numpy as np
import datetime
import matplotlib.pyplot as plt
import copy

from numpy.typing import NDArray


class Timestamps:
    """
    A helper class for managing and converting time data represented in microseconds.

    Provides convenient access to the same time data in seconds, milliseconds, or
    raw microseconds, and allows setting time values in different units.
    """

    def __init__(self, data):
        self.data = data

    @property
    def s(self):
        return np.array([x / 1e6 for x in self.data])

    @property
    def ms(self):
        return np.array([x / 1e3 for x in self.data])

    @property
    def us(self):
        return self.data

    def set_s(self, data):
        self.data = np.array([x * 1e6 for x in data])

    def set_ms(self, data):
        self.data = np.array([x * 1e3 for x in data])

    def set_us(self, data):
        self.data = data


class PPS:
    """
    Class to represent and analyze Pulse Per Second (PPS) timing data.

    Attributes
    ----------
    index : NDArray
        Sample indices associated with each PPS signal.
    time : NDArray
        Timestamps corresponding to each sample, in microseconds.
    timestamps : Timestamps
        Timestamps object managing conversions between time units.
    datetime : list of datetime.datetime
        Absolute datetime values based on UNIX epoch.
    dt : NDArray
        Differences between consecutive timestamps.
    di : NDArray
        Differences between consecutive sample indices.
    shifted_timestamps : NDArray
        Time values shifted to start at 0 seconds.
    slope : float
        Estimated slope from linear regression of time vs. index.
    intercept_time : float
        Intercept of linear fit.
    residual_pps : NDArray
        Residuals between observed and fitted PPS values.
    """

    def __init__(self, index: NDArray, time: NDArray):
        self.index: NDArray = index
        self.time: NDArray = time
        self.timestamps = Timestamps(self.time)
        self.update_properties()

    def __str__(self):
        return (
            f"Index={self.index[:2]} ... {self.index[int(self.index.size / 2)]} ... {self.index[-2:]} (size={self.index.size}), "
            f"Time(data={self.time[:2]} ... {self.time[int(self.time.size / 2)]} ... {self.time[-2:]} (size={self.time.size}), "
        )

    def __deepcopy__(self, memo):
        new_instance = PPS(np.copy(self.index), np.copy(self.time))
        new_instance.timestamps = copy.deepcopy(self.timestamps, memo)
        return new_instance

    def correct(self, file_type: str) -> None:
        """
        Apply correction to timestamps for specific file types.

        For "RSP2" file types, a linear fit is used to remove drift
        in the PPS timing data.

        Parameters
        ----------
        file_type : str
            Type of the input data file (e.g., "RSP2").
        """

        if file_type == "RSP2":
            indices = self.index
            times = self.timestamps.us
            p = np.polyfit(indices, times - times[0], 1)
            new_timestamps = times[0] + np.polyval(p, indices)

            self.timestamps.set_us(
                [int(round(new_timestamp)) for new_timestamp in new_timestamps]
            )
            self.time = np.array(self.timestamps.us)
            self.update_properties()

    def update_properties(self):
        """
        Recalculate internal properties such as datetime conversion,
        time differences, and linear regression metrics.
        """

        self.datetime = [
            datetime.datetime(1970, 1, 1) + datetime.timedelta(microseconds=int(x))
            for x in self.time
        ]
        self.dt = np.diff(self.time)
        self.di = np.diff(self.index)
        self.shifted_timestamps = self.timestamps.s - self.timestamps.s[0]
        self.slope, self.intercept_time = np.polyfit(
            self.index, self.shifted_timestamps, 1
        )
        self.residual_pps = self.shifted_timestamps - (
            self.slope * self.index + self.intercept_time
        )

    def plot_uncertainty(self) -> None:
        """
        Plot PPS timing uncertainty and residuals.

        Generates three plots:
        1. PPS timing over sample indices.
        2. Residual timing errors in milliseconds.
        3. Histogram of residuals.
        """

        plt.figure()
        plt.plot(self.index - self.index[0], self.shifted_timestamps, "*-")
        plt.xlabel("Sample index")
        plt.ylabel("PPS timing [s] ")
        plt.title("PPS timing as a function of sample number ")
        plt.tight_layout()
        plt.show()

        plt.figure()
        plt.plot(self.shifted_timestamps, 1e3 * self.residual_pps, "*-")
        plt.xlabel("PPS timing [s]")
        plt.ylabel("Residual [ms]")
        plt.title(
            f"PPS residual - Number of PPS = {len(self.index)} - $\\mu$ = {np.round(1e6 * np.mean(np.abs(self.residual_pps)), 2)} µs - $\\sigma$ = {np.round(1e6 * np.std(np.abs(self.residual_pps)), 2)} µs "
        )
        plt.tight_layout()
        plt.show()

        _, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
        axs.hist(self.residual_pps)
        plt.show()
