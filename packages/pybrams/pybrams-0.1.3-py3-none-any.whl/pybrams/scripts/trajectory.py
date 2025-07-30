import argparse
import warnings
import pybrams
from .prepare_meteors import get_brams_data
from pybrams.utils import Config


def setup_args(subparsers):
    subparser_trajectory = subparsers.add_parser("trajectory")
    subparser_trajectory_subparsers = subparser_trajectory.add_subparsers(
        dest="trajectory_cmd", required=True
    )

    brams_subparser = subparser_trajectory_subparsers.add_parser(
        "brams", help="process BRAMS trajectory"
    )
    cams_subparser = subparser_trajectory_subparsers.add_parser(
        "cams", help="process CAMS trajectory"
    )

    brams_subparser.add_argument(
        "interval_str", type=str, help="datetime interval in ISO 8601 format"
    )

    cams_subparser.add_argument(
        "date", type=str, help="date of the trajectory to study in ISO 8601 format"
    )
    cams_subparser.add_argument("number", type=str, help="trajectory number")

    for subparser in [brams_subparser, cams_subparser]:
        subparser.add_argument(
            "--recompute_meteors", action="store_true", help="recompute meteor data"
        )

        subparser.add_argument(
            "--recompute_trajectory",
            action="store_true",
            help="recompute trajectory data",
        )

        subparser.add_argument(
            "--uncertainty", action="store_true", help="MCMC uncertainty computation"
        )

        subparser.add_argument("--plot", action="store_true", help="enable plotting")
        subparser.add_argument(
            "--system",
            type=str,
            nargs="+",
            default=None,
            help="optional system parameter",
        )


def run(args: argparse.Namespace):
    if Config.get(__name__, "filter_runtime_warnings"):
        warnings.filterwarnings("ignore", category=RuntimeWarning)

    if args.trajectory_cmd == "cams":
        args.key = f"cams_{args.date}_{args.number}"

        cams = pybrams.optical.cams.CAMS(args)
        args.interval = cams.get_interval()

        if not args.interval:
            print("Need available CAMS date and trajectory. Aborting computation.")
            return

        brams_data = get_brams_data(args)

        if not brams_data:
            print("Aborting computation.")
            return

        cams_solution = cams.get_solution(brams_data)

        print("Solving trajectory...")

        trajectory_analyzer = pybrams.trajectory.analyzer.TrajectoryAnalyzer(
            brams_data, args, cams_solution
        )

        trajectory_analyzer.run()

    elif args.trajectory_cmd == "brams":
        args.key = f"brams_{args.interval_str.replace(':', '_').replace('/', '_')}"

        brams_data = get_brams_data(args)

        if not brams_data:
            print("Aborting computation.")
            return

        print("Solving trajectory...")

        trajectory_analyzer = pybrams.trajectory.analyzer.TrajectoryAnalyzer(
            brams_data, args
        )

        trajectory_analyzer.run()

    print(
        "Processing finished.",
        f"Solution and plots have been added to {Config.get('pybrams.directories', 'solution')}",
    )
