from rich.table import Table
from rich.console import Console
from pybrams.optical import cams


def setup_args(subparsers):
    subparser_cams = subparsers.add_parser("cams")
    subparser_cams_subparsers = subparser_cams.add_subparsers(
        dest="cams_cmd", required=True
    )

    subparser_cams_subparsers.add_parser("list", help="list all CAMS trajectories")


def run(args):
    if args.cams_cmd == "list":
        cams_handler = cams.CAMS(None)
        data = cams_handler.data
        console = Console()
        table = Table(title="CAMS trajectories")

        table.add_column("Trajectory", justify="center", style="cyan", no_wrap=True)
        table.add_column("Observed Date", justify="center", style="magenta")
        table.add_column("Reference Time", justify="center", style="green")

        for trajectory in data:
            table.add_row(
                str(int(trajectory.get("number", 0))),
                trajectory.get("observed_date", ""),
                trajectory.get("reference_time", ""),
            )

        console.print(table)
