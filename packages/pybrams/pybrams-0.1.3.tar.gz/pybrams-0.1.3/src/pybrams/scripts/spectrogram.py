import os
from pybrams.brams import formats
from pybrams import processing
from pybrams.brams import system
from pybrams.brams.system import System


def setup_args(subparsers):
    subparser_spectrogram = subparsers.add_parser("spectrogram")
    subparser_spectrogram.add_argument(
        "--path",
        type=os.path.abspath,
        default=os.path.abspath("."),
        help="directory path containing WAV files (default is current directory).",
    )


def run(args):
    path = args.path
    files = os.listdir(path)
    for file in files:
        if file.endswith(".wav"):
            wav_file_path = os.path.join(path, file)
            metadata, series, pps = formats.Wav.read(wav_file_path)
            ftype = (
                "AR"
                if "BEHUMA" in metadata.station_code
                else "RSP2"
                if metadata.samplerate == 6048
                else "ICOM"
            )

            s = processing.Signal(
                series,
                pps,
                metadata.samplerate,
                system.get(
                    f"{metadata.station_code}_SYS{str(metadata.ant_id).zfill(3)}"
                ),
            )
            s.process()
            spectrogram_filename = f"{file[:-4]}.png"
            s.plot_raw_spectrogram(
                export=True, title=file[:-4], filename=spectrogram_filename
            )
            print(spectrogram_filename)
