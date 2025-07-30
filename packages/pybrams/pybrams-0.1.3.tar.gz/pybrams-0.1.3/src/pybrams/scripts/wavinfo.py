from pybrams.brams import formats
import argparse


def setup_args(subparsers):
    subparser_wavinfo = subparsers.add_parser("wavinfo")
    subparser_wavinfo.add_argument(
        "filepath", type=str, help="file path to the BRAMS WAVfile."
    )
    subparser_wavinfo.add_argument(
        "--header",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="toggle header",
    )
    subparser_wavinfo.add_argument(
        "--pps", action=argparse.BooleanOptionalAction, default=False, help="toggle PPS"
    )
    subparser_wavinfo.add_argument(
        "--data",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="toggle data",
    )


def run(args):
    filepath = args.filepath

    if filepath.endswith(".wav"):
        metadata, series, pps = formats.Wav.read(filepath)
        if args.header:
            print("Header")
            print(metadata)
        if args.pps:
            print("PPS")
            print(pps)
        if args.data:
            print("Data")
            print(series)
