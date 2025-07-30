import os
import pybrams

from pybrams.utils.interval import Interval


def setup_args(subparsers):
    subparser_get = subparsers.add_parser("get")
    subparser_get.add_argument(
        "interval", type=str, help="datetime interval in ISO 8601 format"
    )
    subparser_get.add_argument(
        "systems", type=str, nargs="*", default=[], help="one or multiple BRAMS systems"
    )
    subparser_get.add_argument(
        "-o",
        "--output-dir",
        type=os.path.abspath,
        default=os.path.abspath("."),
        help="output directory path",
    )


def run(args):
    interval_str = args.interval
    systems = args.systems if args.systems else None
    output_dir = args.output_dir

    interval = Interval.from_string(interval_str)
    files = pybrams.file.get(interval, systems)

    if files:
        for _, filelist in files.items():
            for file in filelist:
                file.save_raw(output_dir)
                print(file.wav_name)

    else:
        print("No file retrieved")
