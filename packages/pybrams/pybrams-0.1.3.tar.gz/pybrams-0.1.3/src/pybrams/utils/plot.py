import numpy as np

DURATION_PLOT = 3
OVERLAPS_PLOT = 0.9


class Plot:
    @staticmethod
    def spectrogram(
        series: "Series",
        samplerate,
        central_frequency,
        title="Spectrogram",
        half_range_spect=100,
        export=False,
        filename=None,
        subplot=False,
        frame=True,
    ):
        if not central_frequency:
            return

        from scipy.signal import spectrogram
        import matplotlib.pyplot as plt

        fft_points_plot = np.floor(DURATION_PLOT * samplerate).astype(int)
        n_overlap_plot = np.floor(OVERLAPS_PLOT * fft_points_plot).astype(int)

        # Compute spectrogram
        freq_vector, time_vector, spect = spectrogram(
            series.data,
            fs=samplerate,
            window="hann",
            nperseg=fft_points_plot,
            noverlap=n_overlap_plot,
            mode="magnitude",
        )

        spect = np.abs(spect)

        spect_min_frequency = central_frequency - half_range_spect
        spect_max_frequency = central_frequency + half_range_spect

        spect_min_frequency_index = np.argmin(np.abs(freq_vector - spect_min_frequency))
        spect_max_frequency_index = np.argmin(np.abs(freq_vector - spect_max_frequency))

        freq_vector = freq_vector[
            spect_min_frequency_index : spect_max_frequency_index + 1
        ]
        spect = spect[spect_min_frequency_index : spect_max_frequency_index + 1, :]

        # Compute spectrogram stats
        spect_max = np.max(spect)
        spect_mu = np.mean(spect)

        # Display spectrogram in dB.
        if not subplot:
            plt.figure()

        plt.pcolormesh(
            time_vector, freq_vector, 10 * np.log10(spect / spect_max), cmap="jet"
        )

        # Set colorbar limits and display it.
        cmin, cmax = plt.gci().get_clim()
        plt.clim(10 * np.log10(spect_mu / spect_max), cmax)

        if frame:
            plt.colorbar()
            # Set figure title and labels
            plt.title(title)
            plt.grid(True)
            plt.xticks(
                np.arange(
                    0,
                    series.data.size / samplerate,
                    round(series.data.size / (12 * samplerate)),
                )
            )
            plt.xlabel("Time [s]")
            plt.ylabel("Freq [Hz]")

        else:
            plt.axis("off")

        if export:
            save_path = filename if filename else "spectrogram.png"
            plt.savefig(save_path, bbox_inches="tight", pad_inches=0)

        else:
            plt.show()

        plt.close()
