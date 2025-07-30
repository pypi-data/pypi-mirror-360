import argparse
import os
import sys
from importlib.metadata import version
import pybrams
import pybrams.scripts.get
import pybrams.scripts.cache
import pybrams.scripts.config
import pybrams.scripts.trajectory
import pybrams.scripts.wavinfo
import pybrams.scripts.spectrogram
import pybrams.scripts.cams
import pybrams.scripts.availability
import logging


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="PyBRAMS executable",
        epilog=f"Usage : python {os.path.basename(__file__)} command [args...]",
    )

    parser.add_argument("--verbose", action="store_true", help="enable verbose mode")
    parser.add_argument(
        "--version", action="version", version=f"PyBRAMS {version('pybrams')}"
    )
    subparsers = parser.add_subparsers(dest="cmd")
    pybrams.scripts.get.setup_args(subparsers)
    pybrams.scripts.cache.setup_args(subparsers)
    pybrams.scripts.config.setup_args(subparsers)
    pybrams.scripts.trajectory.setup_args(subparsers)
    pybrams.scripts.wavinfo.setup_args(subparsers)
    pybrams.scripts.spectrogram.setup_args(subparsers)
    pybrams.scripts.cams.setup_args(subparsers)
    pybrams.scripts.availability.setup_args(subparsers)

    parsed_args = parser.parse_args(args)
    if not parsed_args.cmd:
        parser.print_help()
        sys.exit(1)
    return parsed_args


def main():
    parsed_args = parse_args()
    commands = {
        "get": pybrams.scripts.get.run,
        "cache": pybrams.scripts.cache.run,
        "config": pybrams.scripts.config.run,
        "trajectory": pybrams.scripts.trajectory.run,
        "wavinfo": pybrams.scripts.wavinfo.run,
        "spectrogram": pybrams.scripts.spectrogram.run,
        "cams": pybrams.scripts.cams.run,
        "availability": pybrams.scripts.availability.run,
    }

    if parsed_args.verbose:
        pybrams.enable_logging(level=logging.INFO)
    else:
        pybrams.enable_logging(level=logging.WARNING)
    if parsed_args.cmd:
        commands[parsed_args.cmd](parsed_args)


if __name__ == "__main__":
    main()
